"""
Test script to debug matching engine issues
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.core.db import SessionLocal
from src.models.resume import Resume
from src.models.job import Job
from src.services.matching_engine import MatchingEngine
import json

def test_matching_engine():
    """Test matching engine with actual database data"""
    
    print("=" * 70)
    print("🧪 Testing Matching Engine with Database Resumes")
    print("=" * 70)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Step 1: Load resumes from database
        print("\n1️⃣ Loading resumes from database...")
        resumes = db.query(Resume).filter(Resume.deleted_at.is_(None)).all()
        print(f"   Found {len(resumes)} resumes in database")
        
        if not resumes:
            print("   ⚠️  No resumes found in database!")
            return
        
        # Step 2: Initialize matching engine
        print("\n2️⃣ Initializing matching engine...")
        engine = MatchingEngine(model_name='mini')
        
        # Step 3: Index resumes
        print("\n3️⃣ Indexing resumes into matching engine...")
        indexed_count = 0
        for resume in resumes:
            try:
                # Get parsed data
                parsed_data = resume.parsed_data_json or {}
                
                # Check if resume has required data
                if not parsed_data:
                    print(f"   ⚠️  Resume {resume.id} has no parsed data, skipping...")
                    continue
                
                # Extract fields for indexing
                resume_data = {
                    'resume_id': resume.id,
                    'id': str(resume.id),
                    'metadata': {
                        'file_name': resume.file_path or f'resume_{resume.id}.pdf',
                        'quality_score': parsed_data.get('quality_score', 0)
                    },
                    'personal_info': {
                        'name': parsed_data.get('name', 'Unknown'),
                        'email': parsed_data.get('contact_info', {}).get('email', ''),
                        'phone': parsed_data.get('contact_info', {}).get('phone', ''),
                        'location': parsed_data.get('contact_info', {}).get('location', '')
                    },
                    # Skills is already a dict with all_skills, by_category, etc. - use directly
                    'skills': parsed_data.get('skills', {}),
                    'experience': parsed_data.get('experience', []),
                    'education': parsed_data.get('education', []),
                    'raw_text': parsed_data.get('text', ''),
                    'summary': parsed_data.get('summary', ''),
                    # Try to get experience years from various possible fields
                    'total_years_experience': parsed_data.get('total_years_experience', 0) or parsed_data.get('experience_years', 0)
                }
                
                # Check if has text content
                if not resume_data['raw_text']:
                    print(f"   ⚠️  Resume {resume.id} ({resume_data['personal_info']['name']}) has no text content, skipping...")
                    continue
                
                # Index resume
                engine.index_resume(resume_data, resume_id=str(resume.id))
                indexed_count += 1
                print(f"   ✅ Indexed resume {resume.id}: {resume_data['personal_info']['name']}")
                
            except Exception as e:
                print(f"   ❌ Error indexing resume {resume.id}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n   ✅ Successfully indexed {indexed_count} out of {len(resumes)} resumes")
        
        if indexed_count == 0:
            print("   ⚠️  No resumes were indexed! Cannot proceed with matching.")
            return
        
        # Step 4: Get a test job from database
        print("\n4️⃣ Loading test job from database...")
        jobs = db.query(Job).filter(
            Job.deleted_at.is_(None),
            Job.status == 'active'
        ).all()
        
        if not jobs:
            print("   ⚠️  No active jobs found, creating test job...")
            test_job_text = """
            Senior Software Engineer
            
            We are looking for a Senior Software Engineer with strong Python skills.
            
            Requirements:
            - 5+ years of software development experience
            - Strong proficiency in Python
            - Experience with machine learning and data science
            - Familiarity with TensorFlow, PyTorch, or similar ML frameworks
            - Experience with cloud platforms (AWS, GCP, or Azure)
            
            Responsibilities:
            - Design and implement machine learning models
            - Build scalable data pipelines
            - Collaborate with cross-functional teams
            
            Education: Bachelor's or Master's degree in Computer Science or related field
            """
            
            job_data = engine.parse_job(test_job_text)
            print(f"   Created test job: {job_data.title}")
        else:
            # Use first active job
            test_job = jobs[0]
            print(f"   Using job: {test_job.title} (ID: {test_job.id})")
            
            # Parse job description
            job_text = test_job.description or test_job.title
            job_data = engine.parse_job(job_text)
        
        # Step 5: Find matches
        print("\n5️⃣ Finding matches...")
        print(f"   Job: {job_data.title}")
        print(f"   Required skills: {', '.join(job_data.required_skills[:5])}")
        
        # Convert JobDescription to dict
        if hasattr(job_data, 'to_dict'):
            job_dict = job_data.to_dict()
        elif hasattr(job_data, '__dict__'):
            job_dict = job_data.__dict__.copy()
        else:
            job_dict = dict(job_data)
        
        matches = engine.find_matches(
            job_data=job_dict,
            top_k=20,
            min_score=0  # No minimum score for debugging
        )
        
        # Step 6: Display results
        print(f"\n6️⃣ Results:")
        print(f"   Found {len(matches)} matching candidates")
        
        if matches:
            print("\n   📊 Top Matches:")
            for i, match in enumerate(matches[:5], 1):
                print(f"\n   {i}. {match.get('name', 'Unknown')}")
                print(f"      Resume ID: {match.get('resume_id')}")
                print(f"      Match Score: {match.get('match_score', 0):.1f}/100")
                print(f"      Quality Score: {match.get('quality_score', 0):.1f}/10")
                print(f"      Experience: {match.get('experience_years', 0)} years")
                print(f"      Skills: {', '.join(match.get('skills', [])[:5])}")
                
                # Show score breakdown
                if 'match_details' in match:
                    details = match['match_details']
                    if 'scores' in details:
                        scores = details['scores']
                        print(f"      Score breakdown:")
                        print(f"        - Semantic: {scores.get('semantic', 0):.1f}/100")
                        print(f"        - Skills: {scores.get('skills', 0):.1f}/100")
                        print(f"        - Experience: {scores.get('experience', 0):.1f}/100")
                        print(f"        - Education: {scores.get('education', 0):.1f}/100")
        else:
            print("\n   ⚠️  No matches found!")
            print("\n   🔍 Debugging information:")
            print(f"      - Resumes indexed: {indexed_count}")
            print(f"      - Vector store size: {engine.vector_store.size()}")
            print(f"      - Job requirements: {job_data.required_skills}")
            
            # Check if semantic search is working
            print("\n   🧪 Testing semantic search directly...")
            try:
                from src.services.skill_extractor import SkillExtractor
                skill_extractor = SkillExtractor()
                
                # Test search with job
                results = engine.semantic_search.search_for_job(
                    job_data=job_dict,
                    k=10
                )
                print(f"      Semantic search returned {len(results)} results")
                
                if results:
                    print(f"      Top result: {results[0].get('name', 'Unknown')} (score: {results[0].get('score', 0):.2f})")
                else:
                    print("      ⚠️  Semantic search returned 0 results!")
                    print("      This indicates a problem with the vector store or embeddings")
                    
            except Exception as e:
                print(f"      ❌ Error in semantic search: {e}")
                import traceback
                traceback.print_exc()
        
        # Step 7: Show engine stats
        print("\n7️⃣ Engine Statistics:")
        stats = engine.get_stats()
        print(f"   Resumes indexed: {stats['resumes_indexed']}")
        print(f"   Jobs processed: {stats['jobs_processed']}")
        print(f"   Matches generated: {stats['matches_generated']}")
        print(f"   Vector store size: {stats['indexed_resumes']}")
        
        print("\n" + "=" * 70)
        print("✅ Test complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_matching_engine()
