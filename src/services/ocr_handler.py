"""
OCR Handler Service - Extract text from scanned/image-based PDFs
Handles detection of scanned PDFs and applies OCR when needed
"""

import io
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# Try to import pytesseract, but don't fail if Tesseract is not installed
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not installed. OCR functionality will be limited.")

# Try to detect Tesseract executable
try:
    if TESSERACT_AVAILABLE:
        pytesseract.get_tesseract_version()
        TESSERACT_INSTALLED = True
except Exception:
    TESSERACT_INSTALLED = False
    logger.warning("Tesseract OCR engine not found. OCR functionality disabled.")


class OCRHandler:
    """
    Handles OCR operations for scanned/image-based PDFs
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR Handler
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        self.tesseract_available = TESSERACT_AVAILABLE and TESSERACT_INSTALLED
        
        if tesseract_cmd and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
        if not self.tesseract_available:
            logger.warning(
                "Tesseract OCR not available. Install Tesseract from: "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
    def is_scanned_pdf(self, pdf_path: str, sample_pages: int = 3) -> Tuple[bool, float]:
        """
        Detect if PDF is scanned (image-based) or has extractable text
        
        Args:
            pdf_path: Path to PDF file
            sample_pages: Number of pages to sample (default: 3)
            
        Returns:
            Tuple of (is_scanned: bool, confidence: float)
            - is_scanned: True if PDF appears to be scanned
            - confidence: 0.0 to 1.0 (higher = more confident it's scanned)
        """
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            pages_to_check = min(sample_pages, total_pages)
            
            text_char_counts = []
            image_counts = []
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                
                # Check text content
                text = page.get_text().strip()
                text_char_counts.append(len(text))
                
                # Check for images
                image_list = page.get_images()
                image_counts.append(len(image_list))
            
            doc.close()
            
            # Analysis
            avg_text_chars = sum(text_char_counts) / len(text_char_counts)
            avg_images = sum(image_counts) / len(image_counts)
            
            # Heuristics for determining if scanned
            # Scanned PDFs typically have: little/no text + images on every page
            is_scanned = False
            confidence = 0.0
            
            if avg_text_chars < 50 and avg_images >= 1:
                # Very likely scanned - very little text, has images
                is_scanned = True
                confidence = 0.9
            elif avg_text_chars < 200 and avg_images >= 1:
                # Probably scanned
                is_scanned = True
                confidence = 0.7
            elif avg_text_chars < 500 and avg_images >= 0.5:
                # Possibly scanned
                is_scanned = True
                confidence = 0.5
            else:
                # Likely text-based PDF
                is_scanned = False
                confidence = 1.0 - min(avg_images / 5, 0.9)  # Less confident if has images
            
            logger.info(
                f"PDF scan detection: is_scanned={is_scanned}, confidence={confidence:.2f} "
                f"(avg_text={avg_text_chars:.0f}, avg_images={avg_images:.1f})"
            )
            
            return is_scanned, confidence
            
        except Exception as e:
            logger.error(f"Error detecting if PDF is scanned: {e}")
            return False, 0.0
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Increase contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            return image
            
        except Exception as e:
            logger.warning(f"Error preprocessing image: {e}")
            return image
    
    def extract_text_from_image(self, image: Image.Image, preprocess: bool = True) -> str:
        """
        Extract text from a single image using OCR
        
        Args:
            image: PIL Image object
            preprocess: Whether to preprocess image (default: True)
            
        Returns:
            Extracted text
        """
        if not self.tesseract_available:
            logger.error("Tesseract OCR not available")
            return ""
        
        try:
            if preprocess:
                image = self.preprocess_image(image)
            
            # Run OCR with configuration for better accuracy
            custom_config = r'--oem 3 --psm 6'  # OEM 3 = LSTM, PSM 6 = assume uniform block of text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_with_ocr(self, pdf_path: str, dpi: int = 300) -> str:
        """
        Extract text from scanned PDF using OCR
        
        Args:
            pdf_path: Path to PDF file
            dpi: DPI resolution for rendering PDF pages (default: 300)
            
        Returns:
            Extracted text from all pages
        """
        if not self.tesseract_available:
            logger.error("Tesseract OCR not available. Cannot extract text from scanned PDF.")
            return ""
        
        try:
            doc = fitz.open(pdf_path)
            full_text = []
            
            logger.info(f"Running OCR on {len(doc)} pages (DPI={dpi})...")
            
            for page_num in range(len(doc)):
                logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                page = doc[page_num]
                
                # Render page to image
                # zoom = dpi / 72 (72 is default DPI)
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Extract text using OCR
                text = self.extract_text_from_image(image)
                full_text.append(text)
                
                logger.info(f"Page {page_num + 1}: Extracted {len(text)} characters")
            
            doc.close()
            
            combined_text = "\n\n".join(full_text)
            logger.info(f"OCR complete. Total characters extracted: {len(combined_text)}")
            
            return combined_text
            
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return ""
    
    def extract_text_smart(self, pdf_path: str, force_ocr: bool = False) -> Tuple[str, str]:
        """
        Smart text extraction - automatically detects if OCR is needed
        
        Args:
            pdf_path: Path to PDF file
            force_ocr: Force OCR even if text is extractable (default: False)
            
        Returns:
            Tuple of (text: str, method: str)
            - text: Extracted text
            - method: 'text' or 'ocr' indicating extraction method used
        """
        try:
            # First, try regular text extraction
            if not force_ocr:
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                
                # Check if we got meaningful text
                if len(text.strip()) > 100:
                    logger.info("PDF has extractable text. Using standard extraction.")
                    return text, "text"
            
            # Check if PDF is scanned
            is_scanned, confidence = self.is_scanned_pdf(pdf_path)
            
            if is_scanned or force_ocr:
                if not self.tesseract_available:
                    logger.warning(
                        "PDF appears to be scanned but OCR not available. "
                        "Returning limited text extraction."
                    )
                    return text if not force_ocr else "", "text_fallback"
                
                logger.info(f"PDF appears to be scanned (confidence: {confidence:.2f}). Using OCR.")
                ocr_text = self.extract_text_with_ocr(pdf_path)
                return ocr_text, "ocr"
            else:
                logger.info("PDF has sufficient text. Using standard extraction.")
                return text, "text"
                
        except Exception as e:
            logger.error(f"Error in smart text extraction: {e}")
            return "", "error"
    
    def get_ocr_confidence(self, image: Image.Image) -> float:
        """
        Get OCR confidence score for an image
        
        Args:
            image: PIL Image object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not self.tesseract_available:
            return 0.0
        
        try:
            # Get detailed OCR data including confidence scores
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                return avg_confidence / 100.0  # Convert to 0-1 range
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error getting OCR confidence: {e}")
            return 0.0


def test_ocr_availability():
    """Test if OCR is available and working"""
    handler = OCRHandler()
    
    if handler.tesseract_available:
        print("✅ Tesseract OCR is available and working!")
        try:
            version = pytesseract.get_tesseract_version()
            print(f"   Version: {version}")
        except:
            pass
        return True
    else:
        print("❌ Tesseract OCR is NOT available")
        print("   Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False


if __name__ == "__main__":
    # Test OCR availability
    test_ocr_availability()
