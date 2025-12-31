"""
Build and persist FAISS index for all resumes
This dramatically reduces cold start time from 15s to < 1s
"""
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.embedding_generator import EmbeddingGenerator
from src.ml.vector_store import VectorStore
from src.utils.logger import get_logger, get_metrics

logger = get_logger("index_builder")


def load_resumes(resume_file: str) -> List[Dict[str, Any]]:
    """Load resumes from JSON file"""
    logger.info("loading_resumes", file=resume_file)
    
    with open(resume_file, 'r', encoding='utf-8') as f:
        resumes = json.load(f)
    
    logger.info("resumes_loaded", count=len(resumes))
    return resumes


def build_index(resumes: List[Dict[str, Any]], 
                model_name: str = 'mini',
                batch_size: int = 32,
                storage_dir: str = 'data/embeddings') -> tuple:
    """
    Build FAISS index for all resumes
    
    Args:
        resumes: List of resume dictionaries
        model_name: Embedding model size (mini/base/large)
        batch_size: Batch size for embedding generation
        storage_dir: Directory to save index files
        
    Returns:
        (embedding_generator, vector_store) tuple
    """
    logger.info("initializing_components", model=model_name)
    
    # Initialize components
    start = time.time()
    embedding_gen = EmbeddingGenerator(model_name=model_name)
    init_time = time.time() - start
    logger.info("embedding_generator_initialized", 
                duration_ms=init_time * 1000,
                embedding_dim=embedding_gen.embedding_dim)
    
    vector_store = VectorStore(
        embedding_dim=embedding_gen.embedding_dim,
        storage_dir=storage_dir
    )
    logger.info("vector_store_initialized")
    
    # Process resumes in batches
    logger.info("building_index", total_resumes=len(resumes), batch_size=batch_size)
    
    processed = 0
    failed = 0
    total_start = time.time()
    
    for i in range(0, len(resumes), batch_size):
        batch = resumes[i:i + batch_size]
        batch_start = time.time()
        
        try:
            # Generate embeddings for batch
            embeddings_list = []
            metadata_list = []
            
            for resume in batch:
                try:
                    # Create text representation
                    text_parts = []
                    
                    # Add name
                    if resume.get('name'):
                        text_parts.append(f"Name: {resume['name']}")
                    
                    # Add skills
                    skills = resume.get('skills', [])
                    if isinstance(skills, dict):
                        skills = skills.get('all_skills', [])
                    if skills:
                        text_parts.append(f"Skills: {', '.join(skills)}")
                    
                    # Add experience
                    experience = resume.get('experience', [])
                    if experience:
                        exp_texts = []
                        for exp in experience:
                            if isinstance(exp, dict):
                                title = exp.get('title', '')
                                company = exp.get('company', '')
                                exp_texts.append(f"{title} at {company}")
                            elif isinstance(exp, str):
                                exp_texts.append(exp)
                        text_parts.append(f"Experience: {'; '.join(exp_texts)}")
                    
                    # Add education
                    education = resume.get('education', [])
                    if education:
                        edu_texts = []
                        for edu in education:
                            if isinstance(edu, dict):
                                degree = edu.get('degree', '')
                                field = edu.get('field', '')
                                edu_texts.append(f"{degree} in {field}" if field else degree)
                            elif isinstance(edu, str):
                                edu_texts.append(edu)
                        text_parts.append(f"Education: {'; '.join(edu_texts)}")
                    
                    resume_text = " | ".join(text_parts)
                    
                    # Generate embedding
                    embedding = embedding_gen.encode(resume_text)
                    
                    # Prepare metadata
                    metadata = {
                        'resume_id': resume.get('id', f"resume_{processed}"),
                        'name': resume.get('name', 'Unknown'),
                        'email': resume.get('email', ''),
                        'skills': skills if isinstance(skills, list) else [],
                        'experience': experience,
                        'education': education,
                        'experience_years': resume.get('experience_years', 0),
                        'text': resume_text
                    }
                    
                    embeddings_list.append(embedding)
                    metadata_list.append(metadata)
                    processed += 1
                    
                except Exception as e:
                    failed += 1
                    logger.warning("resume_processing_failed", 
                                 resume_id=resume.get('id', 'unknown'),
                                 error=str(e))
            
            # Add batch to vector store
            if embeddings_list:
                import numpy as np
                embeddings_batch = np.array(embeddings_list)
                resume_ids_batch = [m['resume_id'] for m in metadata_list]
                vector_store.add_batch(embeddings_batch, resume_ids_batch, metadata_list)
            
            batch_time = (time.time() - batch_start) * 1000
            get_metrics().record('batch_indexing', batch_time)
            
            # Log progress
            progress_pct = (i + len(batch)) / len(resumes) * 100
            logger.info("batch_indexed",
                       batch_num=i // batch_size + 1,
                       batch_size=len(batch),
                       processed=processed,
                       failed=failed,
                       progress_pct=progress_pct,
                       duration_ms=batch_time)
        
        except Exception as e:
            logger.error("batch_indexing_failed",
                        batch_num=i // batch_size + 1,
                        error=str(e))
    
    total_time = time.time() - total_start
    logger.info("index_built",
                total_resumes=len(resumes),
                processed=processed,
                failed=failed,
                total_duration_sec=total_time,
                avg_per_resume_ms=(total_time * 1000) / processed if processed > 0 else 0)
    
    return embedding_gen, vector_store


def save_index(vector_store: VectorStore, output_dir: str):
    """Save FAISS index and metadata to disk"""
    logger.info("saving_index", output_dir=output_dir)
    
    start = time.time()
    # The vector store already has storage_dir set, just use default name
    vector_store.save('resume_index')
    save_time = (time.time() - start) * 1000
    
    logger.info("index_saved",
                output_dir=output_dir,
                index_size=vector_store.size(),
                duration_ms=save_time)


def main():
    parser = argparse.ArgumentParser(description="Build FAISS index for resumes")
    parser.add_argument(
        '--input',
        default='data/training/parsed_resumes_all.json',
        help='Input JSON file with resumes'
    )
    parser.add_argument(
        '--output',
        default='data/embeddings',
        help='Output directory for index'
    )
    parser.add_argument(
        '--model',
        default='mini',
        choices=['mini', 'base', 'large'],
        help='Embedding model size'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for processing'
    )
    
    args = parser.parse_args()
    
    # Set up logging context
    from uuid import uuid4
    logger.set_context(job_id=str(uuid4()), component="index_builder")
    
    logger.info("index_build_started",
                input_file=args.input,
                output_dir=args.output,
                model=args.model,
                batch_size=args.batch_size)
    
    try:
        # Load resumes
        resumes = load_resumes(args.input)
        
        # Build index
        embedding_gen, vector_store = build_index(
            resumes,
            model_name=args.model,
            batch_size=args.batch_size,
            storage_dir=args.output
        )
        
        # Save index
        save_index(vector_store, args.output)
        
        # Print metrics
        metrics = get_metrics()
        batch_stats = metrics.get_stats('batch_indexing')
        
        print("\n" + "="*60)
        print("INDEX BUILD COMPLETE")
        print("="*60)
        print(f"Total Resumes: {vector_store.size():,}")
        print(f"Output Directory: {args.output}")
        print(f"\nBatch Processing Stats:")
        print(f"  Mean: {batch_stats.get('mean', 0):.1f}ms")
        print(f"  P95: {batch_stats.get('p95', 0):.1f}ms")
        print(f"  P99: {batch_stats.get('p99', 0):.1f}ms")
        print("="*60)
        
        logger.info("index_build_completed", success=True)
        
    except Exception as e:
        logger.error("index_build_failed", error=str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
