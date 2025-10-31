"""
Bulk Download Resume Dataset from GitHub
Downloads hundreds of resume templates from open-source GitHub repositories
"""

import requests
import os
import subprocess
import time
from pathlib import Path
import shutil
from typing import Set, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResumeDatasetDownloader:
    """Download resume dataset from GitHub repositories"""
    
    def __init__(self, output_dir: str = "data/sample_resumes/github_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # GitHub API setup (optional token to avoid rate limits)
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.headers = {}
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
            logger.info("✓ Using GitHub token (higher rate limits)")
        else:
            logger.warning("⚠ No GITHUB_TOKEN set - you may hit rate limits (60 requests/hour)")
            logger.warning("  Set token: $env:GITHUB_TOKEN='your_token_here' (PowerShell)")
        
        # Search terms for finding resume repositories
        self.search_terms = [
            "resume template language:latex",
            "cv template language:latex",
            "awesome-cv stars:>100",
            "altacv language:latex",
            "deedy resume",
            "moderncv language:latex",
            "resume latex overleaf stars:>10",
            "academic cv latex",
            "professional resume template"
        ]
        
        self.repos_found: Set[str] = set()
        self.pdfs_extracted = 0
    
    def search_repositories(self) -> Set[str]:
        """Search GitHub for resume repositories"""
        logger.info(f"\n{'='*80}")
        logger.info("SEARCHING GITHUB FOR RESUME REPOSITORIES")
        logger.info(f"{'='*80}\n")
        
        for term in self.search_terms:
            logger.info(f"🔍 Searching: {term}")
            
            try:
                url = f"https://api.github.com/search/repositories?q={term}&per_page=100&sort=stars"
                response = requests.get(url, headers=self.headers, timeout=30)
                
                # Check rate limit
                remaining = response.headers.get('X-RateLimit-Remaining', '?')
                logger.info(f"   API calls remaining: {remaining}")
                
                response.raise_for_status()
                
                items = response.json().get("items", [])
                logger.info(f"   Found {len(items)} repositories")
                
                for item in items:
                    clone_url = item["clone_url"]
                    stars = item.get("stargazers_count", 0)
                    self.repos_found.add((clone_url, stars, item.get("full_name", "")))
                
                # Rate limiting - be nice to GitHub
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"   ✗ Error searching '{term}': {e}")
                continue
        
        logger.info(f"\n✓ Total unique repositories found: {len(self.repos_found)}")
        return self.repos_found
    
    def clone_and_extract_pdfs(self, max_repos: int = 50):
        """Clone repositories and extract PDF files"""
        logger.info(f"\n{'='*80}")
        logger.info(f"CLONING REPOSITORIES AND EXTRACTING PDFs (Max: {max_repos})")
        logger.info(f"{'='*80}\n")
        
        # Sort by stars (get most popular first)
        sorted_repos = sorted(self.repos_found, key=lambda x: x[1], reverse=True)[:max_repos]
        
        temp_dir = self.output_dir / "temp_clones"
        temp_dir.mkdir(exist_ok=True)
        
        for idx, (clone_url, stars, full_name) in enumerate(sorted_repos, 1):
            logger.info(f"\n[{idx}/{len(sorted_repos)}] Cloning: {full_name} (⭐ {stars})")
            
            repo_name = full_name.replace("/", "_")
            clone_path = temp_dir / repo_name
            
            try:
                # Clone repository (shallow clone for speed)
                if not clone_path.exists():
                    result = subprocess.run(
                        ["git", "clone", "--depth", "1", clone_url, str(clone_path)],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode != 0:
                        logger.warning(f"   ✗ Clone failed: {result.stderr[:100]}")
                        continue
                
                # Find and extract PDF files
                pdf_files = list(clone_path.rglob("*.pdf"))
                
                if pdf_files:
                    logger.info(f"   ✓ Found {len(pdf_files)} PDF files")
                    
                    # Copy PDFs to our dataset
                    for pdf_file in pdf_files:
                        # Skip large files (>5MB - probably not resumes)
                        if pdf_file.stat().st_size > 5 * 1024 * 1024:
                            continue
                        
                        # Create unique filename
                        new_name = f"{repo_name}_{pdf_file.name}"
                        dest = self.output_dir / new_name
                        
                        # Copy file
                        shutil.copy2(pdf_file, dest)
                        self.pdfs_extracted += 1
                        logger.info(f"      → Extracted: {new_name} ({pdf_file.stat().st_size / 1024:.1f} KB)")
                else:
                    logger.info(f"   ⚠ No PDFs found")
                
                # Clean up this clone (save disk space)
                shutil.rmtree(clone_path, ignore_errors=True)
                
                # Rate limiting
                time.sleep(1)
                
            except subprocess.TimeoutExpired:
                logger.warning(f"   ✗ Clone timed out")
                continue
            except Exception as e:
                logger.error(f"   ✗ Error: {e}")
                continue
        
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ EXTRACTION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total PDFs extracted: {self.pdfs_extracted}")
        logger.info(f"Location: {self.output_dir.absolute()}")
    
    def download_popular_templates_direct(self):
        """Download most popular resume templates directly (faster)"""
        logger.info(f"\n{'='*80}")
        logger.info("DOWNLOADING POPULAR TEMPLATES DIRECTLY")
        logger.info(f"{'='*80}\n")
        
        # List of most popular resume repositories with direct PDF links
        popular_repos = [
            {
                "name": "Awesome-CV",
                "url": "https://github.com/posquit0/Awesome-CV",
                "pdf_paths": ["examples/resume.pdf", "examples/cv.pdf", "examples/coverletter.pdf"]
            },
            {
                "name": "AltaCV",
                "url": "https://github.com/liantze/AltaCV",
                "pdf_paths": ["sample.pdf", "altacv.pdf"]
            },
            {
                "name": "Deedy-Resume",
                "url": "https://github.com/deedy/Deedy-Resume",
                "pdf_paths": ["OpenFonts/deedy_resume-openfont.pdf", "MacFonts/deedy_resume.pdf"]
            },
            {
                "name": "ModernCV",
                "url": "https://github.com/moderncv/moderncv",
                "pdf_paths": ["examples/template.pdf"]
            }
        ]
        
        direct_dir = self.output_dir / "popular_templates"
        direct_dir.mkdir(exist_ok=True)
        
        for repo in popular_repos:
            logger.info(f"📥 Downloading from: {repo['name']}")
            
            for pdf_path in repo['pdf_paths']:
                try:
                    # Convert GitHub repo URL to raw content URL
                    raw_url = repo['url'].replace('github.com', 'raw.githubusercontent.com') + f"/master/{pdf_path}"
                    
                    # Try master branch
                    response = requests.get(raw_url, timeout=30)
                    
                    # If master fails, try main branch
                    if response.status_code == 404:
                        raw_url = repo['url'].replace('github.com', 'raw.githubusercontent.com') + f"/main/{pdf_path}"
                        response = requests.get(raw_url, timeout=30)
                    
                    if response.status_code == 200:
                        filename = f"{repo['name']}_{Path(pdf_path).name}"
                        dest = direct_dir / filename
                        dest.write_bytes(response.content)
                        logger.info(f"   ✓ Downloaded: {filename} ({len(response.content) / 1024:.1f} KB)")
                        self.pdfs_extracted += 1
                    else:
                        logger.warning(f"   ✗ Failed to download {pdf_path} (HTTP {response.status_code})")
                
                except Exception as e:
                    logger.warning(f"   ✗ Error downloading {pdf_path}: {e}")
                    continue
            
            time.sleep(1)
    
    def run(self, max_repos: int = 50, include_direct: bool = True):
        """Run complete download pipeline"""
        start_time = time.time()
        
        logger.info(f"\n{'='*80}")
        logger.info("RESUME DATASET BULK DOWNLOADER")
        logger.info(f"{'='*80}\n")
        
        # Option 1: Download popular templates directly (fastest)
        if include_direct:
            self.download_popular_templates_direct()
        
        # Option 2: Search and clone repositories
        self.search_repositories()
        
        if self.repos_found:
            self.clone_and_extract_pdfs(max_repos=max_repos)
        else:
            logger.warning("No repositories found. Check your network connection or GitHub API limits.")
        
        elapsed = time.time() - start_time
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ DOWNLOAD COMPLETE!")
        logger.info(f"{'='*80}")
        logger.info(f"Time elapsed: {elapsed / 60:.1f} minutes")
        logger.info(f"Total PDFs downloaded: {self.pdfs_extracted}")
        logger.info(f"Output directory: {self.output_dir.absolute()}")
        logger.info(f"\nNext step: Test with these resumes!")
        logger.info(f"  python test_parser.py")


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("RESUME DATASET BULK DOWNLOADER")
    print("="*80)
    print("\n⚙️  Configuration:")
    print(f"   • Will download from GitHub repositories")
    print(f"   • Max repositories to clone: 50")
    print(f"   • Output: data/sample_resumes/github_dataset/")
    print(f"\n⚠️  Note: Set GITHUB_TOKEN environment variable to avoid rate limits")
    print(f"   PowerShell: $env:GITHUB_TOKEN='your_token_here'")
    print(f"\n" + "="*80)
    
    response = input("\n📥 Start download? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        downloader = ResumeDatasetDownloader()
        downloader.run(max_repos=50, include_direct=True)
    else:
        print("\n❌ Download cancelled.")


if __name__ == "__main__":
    main()
