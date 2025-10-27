"""
Image data models for product image processing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageData:
    """Represents a single product image from S3"""
    
    image_sku: str
    """The Image SKU this image belongs to"""
    
    variation_number: int
    """Variation number extracted from filename (1a -> 1, 2a -> 2)"""
    
    s3_key: str
    """Full S3 object key (e.g., 'sorted-media/82/77/49/827749-1a-12345.jpg')"""
    
    filename: str
    """Just the filename (e.g., '827749-1a-12345.jpg')"""
    
    url: str
    """S3 URL for the image"""
    
    width: Optional[int] = None
    """Image width in pixels"""
    
    height: Optional[int] = None
    """Image height in pixels"""
    
    file_size: Optional[int] = None
    """File size in bytes"""
    
    content_type: Optional[str] = None
    """MIME type (e.g., 'image/jpeg')"""
    
    def __lt__(self, other):
        """Sort by variation number"""
        return self.variation_number < other.variation_number
    
    def __eq__(self, other):
        """Compare by S3 key"""
        if not isinstance(other, ImageData):
            return False
        return self.s3_key == other.s3_key
    
    def __hash__(self):
        """Hash by S3 key for set operations"""
        return hash(self.s3_key)

