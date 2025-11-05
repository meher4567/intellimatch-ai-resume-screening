"""
Master script: Run all training steps in sequence
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS = [
    ("01_parse_all_resumes.py", "Parsing all resumes"),
    ("02_build_skill_taxonomy.py", "Building skill taxonomy"),
    ("03_analyze_quality.py", "Analyzing quality patterns"),
]


def run_script(script_name, description):
    """Run a single training script"""
    print("\n" + "="*70)
    print(f"Running: {description}")
    print("="*70)
    
    script_path = Path("scripts") / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n[OK] {description} completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] {description} failed!")
        print(f"Error: {e}")
        return False


def main():
    """Run all training steps"""
    print("\n" + "="*80)
    print(" "*20 + "FULL TRAINING PIPELINE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Steps: {len(SCRIPTS)}")
    
    results = []
    
    for i, (script, description) in enumerate(SCRIPTS, 1):
        print(f"\n\nStep {i}/{len(SCRIPTS)}: {description}")
        success = run_script(script, description)
        results.append((description, success))
        
        if not success:
            print(f"\n[ERROR] Training stopped at step {i}")
            break
    
    # Summary
    print("\n\n" + "="*80)
    print(" "*30 + "SUMMARY")
    print("="*80)
    
    for description, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {description}")
    
    total_success = sum(1 for _, s in results if s)
    print(f"\nCompleted: {total_success}/{len(SCRIPTS)} steps")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if total_success == len(SCRIPTS):
        print("\n[OK] All training complete! Check data/training/ for results.")
    else:
        print("\n[ERROR] Training incomplete. Check errors above.")


if __name__ == "__main__":
    main()
