"""
PDF Text Extractor
Extracts text content from PDF files using PyMuPDF (fitz) and pdfplumber
"""

# Try imports with fallback
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text from PDF files"""
    
    def __init__(self):
        """Initialize PDF extractor"""
        self.supported_extensions = ['.pdf']
    
    def extract_text_pymupdf(self, file_path: str) -> str:
        """
        Extract text using PyMuPDF (fitz)
        Fast and reliable for most PDFs
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not HAS_PYMUPDF:
            raise ImportError("PyMuPDF not available. Install with: pip install PyMuPDF")
        
        try:
            text_content = []
            
            # Open PDF
            with fitz.open(file_path) as doc:
                logger.info(f"Opening PDF: {file_path} ({doc.page_count} pages)")
                
                # Extract text from each page
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text()
                    if text.strip():
                        text_content.append(text)
                        logger.debug(f"Page {page_num}: Extracted {len(text)} characters")
            
            full_text = "\n\n".join(text_content)
            logger.info(f"PyMuPDF: Extracted {len(full_text)} total characters")
            return full_text
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed for {file_path}: {e}")
            return ""
    
    def extract_text_pdfplumber(self, file_path: str) -> str:
        """
        Extract text using pdfplumber
        Better for complex layouts and tables
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not HAS_PDFPLUMBER:
            raise ImportError("pdfplumber not available. Install with: pip install pdfplumber")
        
        try:
            text_content = []
            
            # Open PDF
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"Opening PDF: {file_path} ({len(pdf.pages)} pages)")
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                        logger.debug(f"Page {page_num}: Extracted {len(text)} characters")
            
            full_text = "\n\n".join(text_content)
            logger.info(f"pdfplumber: Extracted {len(full_text)} total characters")
            return full_text
            
        except Exception as e:
            logger.error(f"pdfplumber extraction failed for {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: str, method: str = "auto") -> Dict[str, str]:
        """
        Extract text from PDF using specified method
        
        Args:
            file_path: Path to PDF file
            method: Extraction method ('pymupdf', 'pdfplumber', or 'auto')
                   'auto' tries PyMuPDF first, falls back to pdfplumber if needed
        
        Returns:
            Dict with 'text' and 'method' keys
        """
        file_path = str(Path(file_path).resolve())
        
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Validate file extension
        if Path(file_path).suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Not a PDF file: {file_path}")
        
        logger.info(f"Extracting text from PDF: {file_path}")
        
        if method == "pymupdf":
            text = self.extract_text_pymupdf(file_path)
            return {"text": text, "method": "pymupdf"}
        
        elif method == "pdfplumber":
            text = self.extract_text_pdfplumber(file_path)
            return {"text": text, "method": "pdfplumber"}
        
        elif method == "auto":
            # Try PyMuPDF first (faster)
            text = self.extract_text_pymupdf(file_path)
            
            # If PyMuPDF returns empty or very short text, try pdfplumber
            if len(text.strip()) < 100:
                logger.warning("PyMuPDF returned insufficient text, trying pdfplumber...")
                text = self.extract_text_pdfplumber(file_path)
                return {"text": text, "method": "pdfplumber"}
            
            return {"text": text, "method": "pymupdf"}
        
        else:
            raise ValueError(f"Unknown extraction method: {method}")
    
    def get_metadata(self, file_path: str) -> Dict:
        """
        Extract metadata from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with metadata (title, author, pages, etc.)
        """
        try:
            with fitz.open(file_path) as doc:
                metadata = {
                    "num_pages": doc.page_count,
                    "title": doc.metadata.get("title", ""),
                    "author": doc.metadata.get("author", ""),
                    "subject": doc.metadata.get("subject", ""),
                    "creator": doc.metadata.get("creator", ""),
                    "producer": doc.metadata.get("producer", ""),
                    "created_date": doc.metadata.get("creationDate", ""),
                    "modified_date": doc.metadata.get("modDate", ""),
                }
                return metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return {}


# Convenience function
def extract_text_from_pdf(file_path: str, method: str = "auto") -> str:
    """
    Convenience function to extract text from PDF
    
    Args:
        file_path: Path to PDF file
        method: Extraction method ('pymupdf', 'pdfplumber', or 'auto')
    
    Returns:
        Extracted text content
    """
    extractor = PDFExtractor()
    result = extractor.extract_text(file_path, method)
    return result["text"]
