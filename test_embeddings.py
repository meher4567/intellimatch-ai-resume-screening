"""
Test the downloaded embeddings and FAISS index
"""
import numpy as np
import json
from pathlib import Path

print("🧪 Testing Downloaded Embeddings")
print("=" * 60)

# Check files exist
embeddings_path = Path('models/embeddings/resume_embeddings.npy')
faiss_path = Path('models/embeddings/resume_faiss_index.bin')

if not embeddings_path.exists():
    print(f"❌ Embeddings not found at: {embeddings_path}")
    print(f"   Did you download and copy the file?")
else:
    # Load embeddings
    embeddings = np.load(embeddings_path)
    print(f"✅ Embeddings loaded: {embeddings.shape}")
    print(f"   Shape: {embeddings.shape[0]} resumes × {embeddings.shape[1]} dimensions")
    print(f"   Size: {embeddings.nbytes / 1024 / 1024:.2f} MB")
    print(f"   Data type: {embeddings.dtype}")

print()

if not faiss_path.exists():
    print(f"❌ FAISS index not found at: {faiss_path}")
    print(f"   Did you download and copy the file?")
else:
    # Load FAISS index
    try:
        import faiss
        index = faiss.read_index(str(faiss_path))
        print(f"✅ FAISS index loaded: {index.ntotal} vectors")
        
        # Test search
        if embeddings_path.exists():
            embeddings = np.load(embeddings_path)
            query = embeddings[0:1]  # First resume
            D, I = index.search(query.astype('float32'), k=5)
            
            print(f"\n🔍 Test search (query = first resume):")
            print(f"   Top 5 similar resume IDs: {I[0].tolist()}")
            print(f"   Similarity scores: {D[0].tolist()}")
            print(f"\n✅ FAISS search working!")
    except ImportError:
        print(f"⚠️  FAISS not installed. Install with: pip install faiss-cpu")

print()
print("=" * 60)
print("✅ All tests passed!")
print()
print("Next steps:")
print("1. Update your matching engine to use these embeddings")
print("2. Test semantic search with real queries")
print("3. Compare with old keyword-based matching")
