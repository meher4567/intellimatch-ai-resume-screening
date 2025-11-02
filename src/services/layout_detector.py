"""
Layout Detector

Analyzes resume document layout:
- Single vs multi-column detection
- Table detection
- Reading order preservation
- Text block identification
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    """Represents a block of text in the document"""
    text: str
    x0: float  # Left coordinate
    y0: float  # Top coordinate
    x1: float  # Right coordinate
    y1: float  # Bottom coordinate
    page_num: int
    font_size: Optional[float] = None
    font_name: Optional[str] = None
    is_bold: bool = False
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0
    
    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2


@dataclass
class LayoutInfo:
    """Layout information for a document"""
    num_columns: int
    has_tables: bool
    text_blocks: List[TextBlock]
    column_boundaries: List[float]
    page_width: float
    page_height: float
    reading_order: List[int]  # Indices of text_blocks in reading order


class LayoutDetector:
    """Detect and analyze document layout"""
    
    def __init__(self):
        """Initialize layout detector"""
        self.column_threshold = 50  # Minimum gap (points) between columns
        self.min_column_width = 150  # Minimum column width (points)
    
    def detect_layout(self, pdf_path: str) -> Optional[LayoutInfo]:
        """
        Detect layout of PDF document
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            LayoutInfo object or None if error
        """
        if not fitz:
            logger.error("PyMuPDF not available for layout detection")
            return None
        
        try:
            doc = fitz.open(pdf_path)
            
            # Analyze first page (usually representative)
            page = doc[0]
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Extract text blocks with positions
            text_blocks = self._extract_text_blocks(page)
            
            if not text_blocks:
                logger.warning(f"No text blocks found in {pdf_path}")
                return None
            
            # Detect number of columns
            num_columns, column_boundaries = self._detect_columns(text_blocks, page_width)
            
            # Detect tables
            has_tables = self._detect_tables(page)
            
            # Determine reading order
            reading_order = self._determine_reading_order(text_blocks, num_columns, column_boundaries)
            
            doc.close()
            
            layout = LayoutInfo(
                num_columns=num_columns,
                has_tables=has_tables,
                text_blocks=text_blocks,
                column_boundaries=column_boundaries,
                page_width=page_width,
                page_height=page_height,
                reading_order=reading_order
            )
            
            logger.info(f"Detected layout: {num_columns} column(s), "
                       f"tables: {has_tables}, {len(text_blocks)} text blocks")
            
            return layout
            
        except Exception as e:
            logger.error(f"Error detecting layout: {e}")
            return None
    
    def _extract_text_blocks(self, page) -> List[TextBlock]:
        """Extract text blocks with position information"""
        blocks = []
        
        # Get blocks from page
        page_dict = page.get_text("dict")
        
        for block in page_dict.get("blocks", []):
            if block.get("type") == 0:  # Text block
                # Get block bounds
                bbox = block.get("bbox", [0, 0, 0, 0])
                
                # Extract text from lines
                text_parts = []
                font_sizes = []
                font_names = []
                has_bold = False
                
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text_parts.append(span.get("text", ""))
                        font_sizes.append(span.get("size", 0))
                        font_names.append(span.get("font", ""))
                        if "bold" in span.get("font", "").lower():
                            has_bold = True
                
                text = " ".join(text_parts).strip()
                
                if text:  # Only add non-empty blocks
                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else None
                    primary_font = max(set(font_names), key=font_names.count) if font_names else None
                    
                    text_block = TextBlock(
                        text=text,
                        x0=bbox[0],
                        y0=bbox[1],
                        x1=bbox[2],
                        y1=bbox[3],
                        page_num=0,
                        font_size=avg_font_size,
                        font_name=primary_font,
                        is_bold=has_bold
                    )
                    blocks.append(text_block)
        
        logger.debug(f"Extracted {len(blocks)} text blocks")
        return blocks
    
    def _detect_columns(self, blocks: List[TextBlock], page_width: float) -> Tuple[int, List[float]]:
        """
        Detect number of columns and their boundaries
        
        Args:
            blocks: List of text blocks
            page_width: Width of page
            
        Returns:
            Tuple of (num_columns, column_boundaries)
        """
        if not blocks:
            return 1, []
        
        # Get x-coordinates of block centers
        x_positions = sorted([block.center_x for block in blocks])
        
        # Find gaps in x-coordinates
        gaps = []
        for i in range(len(x_positions) - 1):
            gap = x_positions[i + 1] - x_positions[i]
            if gap > self.column_threshold:
                gap_center = (x_positions[i] + x_positions[i + 1]) / 2
                gaps.append((gap, gap_center))
        
        # Sort by gap size (largest first)
        gaps.sort(reverse=True)
        
        # Determine columns based on significant gaps
        if not gaps or gaps[0][0] < self.column_threshold:
            # Single column
            return 1, []
        
        # Check if there's a clear two-column layout
        if len(gaps) >= 1 and gaps[0][0] > self.column_threshold:
            # Two columns
            boundary = gaps[0][1]
            
            # Verify both columns have sufficient content
            left_blocks = [b for b in blocks if b.center_x < boundary]
            right_blocks = [b for b in blocks if b.center_x >= boundary]
            
            if left_blocks and right_blocks:
                logger.debug(f"Detected 2 columns with boundary at x={boundary:.1f}")
                return 2, [boundary]
        
        # Default to single column
        return 1, []
    
    def _detect_tables(self, page) -> bool:
        """
        Detect if page contains tables
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            True if tables detected
        """
        try:
            # Check for table-like structures
            tables = page.find_tables()
            if tables and len(tables.tables) > 0:
                logger.debug(f"Found {len(tables.tables)} table(s)")
                return True
        except Exception as e:
            logger.debug(f"Table detection failed: {e}")
        
        # Fallback: look for patterns indicating tables
        # (multiple aligned text blocks, grid-like structure)
        return False
    
    def _determine_reading_order(
        self,
        blocks: List[TextBlock],
        num_columns: int,
        column_boundaries: List[float]
    ) -> List[int]:
        """
        Determine optimal reading order for text blocks
        
        Args:
            blocks: List of text blocks
            num_columns: Number of columns
            column_boundaries: X-coordinates of column boundaries
            
        Returns:
            List of block indices in reading order
        """
        if not blocks:
            return []
        
        if num_columns == 1:
            # Single column: sort by y-position (top to bottom)
            sorted_indices = sorted(
                range(len(blocks)),
                key=lambda i: (blocks[i].y0, blocks[i].x0)
            )
            return sorted_indices
        
        elif num_columns == 2 and column_boundaries:
            # Two columns: sort left column, then right column
            boundary = column_boundaries[0]
            
            left_blocks = [(i, blocks[i]) for i in range(len(blocks)) 
                          if blocks[i].center_x < boundary]
            right_blocks = [(i, blocks[i]) for i in range(len(blocks)) 
                           if blocks[i].center_x >= boundary]
            
            # Sort each column by y-position
            left_sorted = sorted(left_blocks, key=lambda x: (x[1].y0, x[1].x0))
            right_sorted = sorted(right_blocks, key=lambda x: (x[1].y0, x[1].x0))
            
            # Combine: left column first, then right column
            reading_order = [i for i, _ in left_sorted] + [i for i, _ in right_sorted]
            return reading_order
        
        # Fallback: simple top-to-bottom, left-to-right
        sorted_indices = sorted(
            range(len(blocks)),
            key=lambda i: (blocks[i].y0, blocks[i].x0)
        )
        return sorted_indices
    
    def get_text_in_reading_order(self, layout: LayoutInfo) -> str:
        """
        Get text in proper reading order
        
        Args:
            layout: LayoutInfo object
            
        Returns:
            Text in reading order
        """
        if not layout or not layout.text_blocks:
            return ""
        
        ordered_text = []
        for idx in layout.reading_order:
            if 0 <= idx < len(layout.text_blocks):
                ordered_text.append(layout.text_blocks[idx].text)
        
        return "\n".join(ordered_text)


# Convenience function
def detect_layout(pdf_path: str) -> Optional[LayoutInfo]:
    """
    Detect layout of PDF document
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        LayoutInfo object or None
    """
    detector = LayoutDetector()
    return detector.detect_layout(pdf_path)
