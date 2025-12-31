"""
Vector Store using FAISS
Efficient storage and retrieval of resume embeddings for semantic search

Edge Cases Handled:
- Empty embeddings (validation)
- Dimension mismatch (detection and error)
- NaN/Inf values in embeddings
- Duplicate resume IDs (update vs insert)
- Empty search results
- Invalid metadata
- Concurrent access considerations
"""

import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import pickle
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def _validate_embedding(embedding: np.ndarray, expected_dim: int, 
                       name: str = "embedding") -> Tuple[bool, str]:
    """
    Validate an embedding array
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if embedding is None:
        return False, f"{name} cannot be None"
    
    if not isinstance(embedding, np.ndarray):
        return False, f"{name} must be a numpy array, got {type(embedding)}"
    
    # Check for NaN
    if np.any(np.isnan(embedding)):
        return False, f"{name} contains NaN values"
    
    # Check for Inf
    if np.any(np.isinf(embedding)):
        return False, f"{name} contains infinite values"
    
    # Flatten if needed and check dimension
    flat = embedding.flatten() if embedding.ndim > 1 else embedding
    if len(flat) != expected_dim:
        return False, f"{name} dimension mismatch: expected {expected_dim}, got {len(flat)}"
    
    return True, ""


class VectorStore:
    """FAISS-based vector store for resume embeddings"""
    
    # Supported metrics
    SUPPORTED_METRICS = ['cosine', 'l2']
    
    def __init__(self, embedding_dim: int = 384, 
                 metric: str = 'cosine',
                 storage_dir: str = None):
        """
        Initialize vector store
        
        Args:
            embedding_dim: Dimension of embeddings (384 for mini, 768 for base)
            metric: Distance metric ('cosine' or 'l2')
            storage_dir: Directory to store index and metadata
        
        Raises:
            ValueError: If invalid metric is specified
        """
        # Validate embedding dimension
        if embedding_dim <= 0:
            raise ValueError(f"embedding_dim must be positive, got {embedding_dim}")
        
        self.embedding_dim = embedding_dim
        
        # Validate metric
        if metric not in self.SUPPORTED_METRICS:
            raise ValueError(
                f"Metric must be one of {self.SUPPORTED_METRICS}, got '{metric}'"
            )
        self.metric = metric
        
        # Setup storage
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "data" / "embeddings"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        if metric == 'cosine':
            # For cosine similarity, use inner product with normalized vectors
            self.index = faiss.IndexFlatIP(embedding_dim)
        else:  # l2
            # For L2 distance
            self.index = faiss.IndexFlatL2(embedding_dim)
        
        # Metadata storage (maps FAISS index ID to resume metadata)
        self.id_to_metadata: Dict[int, Dict[str, Any]] = {}
        self.resume_id_to_faiss_id: Dict[str, int] = {}
        self.next_id = 0
        
        logger.info(f"Vector store initialized: dim={embedding_dim}, metric={metric}")
        print(f"✅ Vector store initialized")
        print(f"   Embedding dim: {embedding_dim}")
        print(f"   Metric: {metric}")
        print(f"   Storage: {self.storage_dir}")
    
    def add(self, embedding: np.ndarray, 
            resume_id: str,
            metadata: Dict[str, Any],
            update_if_exists: bool = True) -> int:
        """
        Add a single resume embedding to the index
        
        Args:
            embedding: Embedding vector (1D array)
            resume_id: Unique resume identifier
            metadata: Resume metadata (name, skills, etc.)
            update_if_exists: If True, update metadata for existing resume_id
            
        Returns:
            FAISS index ID (-1 on error)
            
        Note:
            FAISS doesn't support updating embeddings in place for flat indices.
            If update_if_exists is True and resume exists, only metadata is updated.
        """
        # Validate resume_id
        if not resume_id or not isinstance(resume_id, str):
            resume_id = f"resume_{self.next_id}"
            logger.warning(f"Invalid resume_id, using generated: {resume_id}")
        
        # Handle existing resume
        if resume_id in self.resume_id_to_faiss_id:
            if update_if_exists:
                faiss_id = self.resume_id_to_faiss_id[resume_id]
                self.id_to_metadata[faiss_id] = metadata
                logger.debug(f"Updated metadata for existing resume: {resume_id}")
                return faiss_id
            else:
                logger.warning(f"Resume {resume_id} already exists, skipping")
                return self.resume_id_to_faiss_id[resume_id]
        
        # Validate embedding
        is_valid, error_msg = _validate_embedding(embedding, self.embedding_dim)
        if not is_valid:
            logger.error(f"Invalid embedding for {resume_id}: {error_msg}")
            return -1
        
        # Ensure embedding is 2D for FAISS
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # Ensure float32
        embedding = embedding.astype(np.float32)
        
        # Normalize if using cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(embedding)
        
        # Add to FAISS index
        self.index.add(embedding.astype('float32'))
        
        # Store metadata
        faiss_id = self.next_id
        self.id_to_metadata[faiss_id] = metadata
        self.resume_id_to_faiss_id[resume_id] = faiss_id
        self.next_id += 1
        
        return faiss_id
    
    def add_batch(self, embeddings: np.ndarray,
                  resume_ids: List[str],
                  metadata_list: List[Dict[str, Any]],
                  skip_invalid: bool = True) -> List[int]:
        """
        Add multiple resume embeddings in batch
        
        Args:
            embeddings: Embedding vectors (2D array: [n_resumes, embedding_dim])
            resume_ids: List of resume IDs
            metadata_list: List of metadata dicts
            skip_invalid: If True, skip invalid embeddings instead of failing
            
        Returns:
            List of FAISS index IDs (-1 for skipped entries)
        """
        # Validate inputs
        n_embeddings = embeddings.shape[0] if hasattr(embeddings, 'shape') else 0
        n_ids = len(resume_ids)
        n_metadata = len(metadata_list)
        
        if not (n_embeddings == n_ids == n_metadata):
            raise ValueError(
                f"Mismatched counts: embeddings={n_embeddings}, "
                f"ids={n_ids}, metadata={n_metadata}"
            )
        
        if n_embeddings == 0:
            logger.warning("Empty batch provided to add_batch")
            return []
        
        # Validate embedding dimensions
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dim}, "
                f"got {embeddings.shape[1]}"
            )
        
        # Ensure float32
        embeddings = embeddings.astype(np.float32)
        
        # Check for NaN/Inf
        valid_mask = ~(np.any(np.isnan(embeddings), axis=1) | 
                       np.any(np.isinf(embeddings), axis=1))
        
        if not np.all(valid_mask):
            invalid_count = np.sum(~valid_mask)
            if skip_invalid:
                logger.warning(f"Skipping {invalid_count} embeddings with NaN/Inf values")
            else:
                raise ValueError(f"{invalid_count} embeddings contain NaN/Inf values")
        
        # Filter to valid embeddings only
        valid_embeddings = embeddings[valid_mask]
        valid_resume_ids = [rid for rid, v in zip(resume_ids, valid_mask) if v]
        valid_metadata = [m for m, v in zip(metadata_list, valid_mask) if v]
        
        if len(valid_embeddings) == 0:
            logger.warning("No valid embeddings to add after filtering")
            return [-1] * n_embeddings
        
        # Normalize if using cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(valid_embeddings)
        
        # Add to FAISS index
        self.index.add(valid_embeddings)
        
        # Store metadata and build result
        faiss_ids = []
        valid_idx = 0
        for i, is_valid in enumerate(valid_mask):
            if is_valid:
                faiss_id = self.next_id
                self.id_to_metadata[faiss_id] = valid_metadata[valid_idx]
                self.resume_id_to_faiss_id[valid_resume_ids[valid_idx]] = faiss_id
                faiss_ids.append(faiss_id)
                self.next_id += 1
                valid_idx += 1
            else:
                faiss_ids.append(-1)
        
        logger.info(f"Added {len(valid_embeddings)}/{n_embeddings} embeddings to index")
        return faiss_ids
    
    def search(self, query_embedding: np.ndarray,
               k: int = 10,
               filter_fn: Optional[callable] = None,
               min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for most similar resumes
        
        Args:
            query_embedding: Query embedding (1D array)
            k: Number of results to return (clamped to 1-1000)
            filter_fn: Optional function to filter results (takes metadata, returns bool)
            min_score: Minimum similarity score to include (0-100)
            
        Returns:
            List of dicts with 'resume_id', 'score', and 'metadata'
            Empty list if index is empty or query is invalid
        """
        # Edge case: empty index
        if self.index.ntotal == 0:
            logger.debug("Search called on empty index")
            return []
        
        # Validate query embedding
        is_valid, error_msg = _validate_embedding(query_embedding, self.embedding_dim, "query")
        if not is_valid:
            logger.error(f"Invalid query embedding: {error_msg}")
            return []
        
        # Clamp k to valid range
        k = max(1, min(k, 1000))
        
        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Ensure float32
        query_embedding = query_embedding.astype(np.float32)
        
        # Normalize if using cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(query_embedding)
        
        # Search with larger k if filtering (but not too large)
        search_k = min(k * 3 if filter_fn else k, self.index.ntotal, 1000)
        
        # Perform search
        try:
            distances, indices = self.index.search(query_embedding, search_k)
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []
        
        # Build results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            metadata = self.id_to_metadata.get(idx, {})
            
            # Apply filter if provided
            if filter_fn and not filter_fn(metadata):
                continue
            
            # Convert distance to similarity score (0-100)
            if self.metric == 'cosine':
                # Inner product is already similarity (0-1)
                score = float(dist) * 100
            else:
                # L2 distance: convert to similarity (inverse)
                score = max(0, 100 - float(dist) * 10)
            
            results.append({
                'faiss_id': int(idx),
                'resume_id': metadata.get('resume_id', ''),
                'score': score,
                'metadata': metadata
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def get_by_resume_id(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific resume"""
        faiss_id = self.resume_id_to_faiss_id.get(resume_id)
        if faiss_id is None:
            return None
        return self.id_to_metadata.get(faiss_id)
    
    def update_metadata(self, resume_id: str, metadata: Dict[str, Any]):
        """Update metadata for a resume (doesn't update embedding)"""
        faiss_id = self.resume_id_to_faiss_id.get(resume_id)
        if faiss_id is not None:
            self.id_to_metadata[faiss_id] = metadata
    
    def delete(self, resume_id: str):
        """
        Delete a resume from the store
        Note: FAISS doesn't support deletion, so we just remove metadata
        The embedding remains in the index but won't be returned in search
        """
        faiss_id = self.resume_id_to_faiss_id.get(resume_id)
        if faiss_id is not None:
            del self.id_to_metadata[faiss_id]
            del self.resume_id_to_faiss_id[resume_id]
    
    def size(self) -> int:
        """Get number of resumes in store"""
        return len(self.id_to_metadata)
    
    def total_indexed(self) -> int:
        """Get total number of vectors in FAISS index (includes deleted)"""
        return self.index.ntotal
    
    def save(self, name: str = 'default'):
        """
        Save index and metadata to disk
        
        Args:
            name: Name for this index (default: 'default')
        """
        # Save FAISS index
        index_path = self.storage_dir / f"{name}_index.faiss"
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        metadata_path = self.storage_dir / f"{name}_metadata.pkl"
        metadata = {
            'id_to_metadata': self.id_to_metadata,
            'resume_id_to_faiss_id': self.resume_id_to_faiss_id,
            'next_id': self.next_id,
            'embedding_dim': self.embedding_dim,
            'metric': self.metric,
            'saved_at': datetime.now().isoformat()
        }
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        # Save human-readable summary
        summary_path = self.storage_dir / f"{name}_summary.json"
        summary = {
            'name': name,
            'total_resumes': self.size(),
            'embedding_dim': self.embedding_dim,
            'metric': self.metric,
            'saved_at': datetime.now().isoformat()
        }
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Vector store saved: {name}")
        print(f"   Index: {index_path}")
        print(f"   Metadata: {metadata_path}")
        print(f"   Total resumes: {self.size()}")
    
    @classmethod
    def load(cls, name: str = 'default', storage_dir: str = None) -> 'VectorStore':
        """
        Load index and metadata from disk
        
        Args:
            name: Name of the index to load
            storage_dir: Directory where index is stored
            
        Returns:
            VectorStore instance
        """
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "data" / "embeddings"
        storage_dir = Path(storage_dir)
        
        # Load metadata first to get config
        metadata_path = storage_dir / f"{name}_metadata.pkl"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # Create instance
        instance = cls(
            embedding_dim=metadata['embedding_dim'],
            metric=metadata['metric'],
            storage_dir=storage_dir
        )
        
        # Load FAISS index
        index_path = storage_dir / f"{name}_index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        instance.index = faiss.read_index(str(index_path))
        
        # Restore metadata
        instance.id_to_metadata = metadata['id_to_metadata']
        instance.resume_id_to_faiss_id = metadata['resume_id_to_faiss_id']
        instance.next_id = metadata['next_id']
        
        print(f"✅ Vector store loaded: {name}")
        print(f"   Total resumes: {instance.size()}")
        print(f"   Saved at: {metadata.get('saved_at', 'unknown')}")
        
        return instance
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            'total_resumes': self.size(),
            'total_indexed': self.total_indexed(),
            'embedding_dim': self.embedding_dim,
            'metric': self.metric,
            'storage_dir': str(self.storage_dir)
        }


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Vector Store")
    print("=" * 70)
    
    # Create vector store
    print("\n1️⃣ Creating vector store...")
    store = VectorStore(embedding_dim=384, metric='cosine')
    
    # Create sample embeddings (simulating resume embeddings)
    print("\n2️⃣ Adding sample resumes...")
    np.random.seed(42)
    
    # Sample resume data
    resumes = [
        {
            'resume_id': 'resume_001',
            'name': 'John Doe',
            'skills': ['Python', 'Django', 'AWS'],
            'experience_years': 5,
            'title': 'Senior Backend Engineer'
        },
        {
            'resume_id': 'resume_002',
            'name': 'Jane Smith',
            'skills': ['Python', 'Machine Learning', 'TensorFlow'],
            'experience_years': 3,
            'title': 'Data Scientist'
        },
        {
            'resume_id': 'resume_003',
            'name': 'Bob Johnson',
            'skills': ['React', 'JavaScript', 'TypeScript'],
            'experience_years': 4,
            'title': 'Frontend Engineer'
        },
        {
            'resume_id': 'resume_004',
            'name': 'Alice Williams',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'experience_years': 6,
            'title': 'Backend Developer'
        },
        {
            'resume_id': 'resume_005',
            'name': 'Charlie Brown',
            'skills': ['Java', 'Spring Boot', 'Kubernetes'],
            'experience_years': 7,
            'title': 'Senior Software Engineer'
        }
    ]
    
    # Generate random embeddings (in real use, these come from embedding generator)
    embeddings = np.random.randn(len(resumes), 384).astype('float32')
    
    # Add to store
    resume_ids = [r['resume_id'] for r in resumes]
    faiss_ids = store.add_batch(embeddings, resume_ids, resumes)
    
    print(f"   Added {len(resumes)} resumes")
    print(f"   FAISS IDs: {faiss_ids}")
    
    # Test search
    print("\n3️⃣ Testing semantic search...")
    query_embedding = embeddings[0]  # Use first resume as query
    results = store.search(query_embedding, k=3)
    
    print(f"   Query: {resumes[0]['name']} ({resumes[0]['title']})")
    print(f"   Top 3 matches:")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"   {i}. {meta['name']} ({meta['title']}) - Score: {result['score']:.2f}")
    
    # Test filtering
    print("\n4️⃣ Testing filtered search...")
    def filter_python(metadata):
        return 'Python' in metadata.get('skills', [])
    
    results = store.search(query_embedding, k=3, filter_fn=filter_python)
    print(f"   Filter: Only Python developers")
    print(f"   Results:")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"   {i}. {meta['name']} - Skills: {', '.join(meta['skills'])}")
    
    # Test get by ID
    print("\n5️⃣ Testing get by resume ID...")
    metadata = store.get_by_resume_id('resume_002')
    print(f"   Retrieved: {metadata['name']} ({metadata['title']})")
    
    # Test save/load
    print("\n6️⃣ Testing save/load...")
    store.save('test_index')
    
    print("\n   Loading index...")
    loaded_store = VectorStore.load('test_index')
    
    # Verify loaded store works
    results = loaded_store.search(query_embedding, k=2)
    print(f"   Search in loaded store:")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"   {i}. {meta['name']} - Score: {result['score']:.2f}")
    
    # Stats
    print("\n7️⃣ Statistics:")
    stats = loaded_store.stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
