"""
Image validation and filtering utilities.
"""

import re
from typing import Optional, List
import os


class ImageValidator:
    """Validates and filters images based on specification rules"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        # Get configuration
        self.min_width = config.images.min_width
        self.min_height = config.images.min_height
        self.accepted_extensions = config.images.accepted_extensions
        self.variation_suffix = config.images.variation_suffix
    
    def validate_filename(self, filename: str, image_sku: str) -> bool:
        """
        Check if filename matches required pattern: [Image_SKU]-[Number]a-[Random].[ext]
        
        Args:
            filename: e.g., "827749-1a-12345.jpg"
            image_sku: e.g., "827749"
        
        Returns:
            True if filename matches pattern and starts with exact Image_SKU
        """
        # Pattern: [Image_SKU]-[Number][variation_suffix]-[Random].[ext]
        # Example: 827749-1a-12345.jpg
        pattern = rf'^{re.escape(image_sku)}-(\d+){self.variation_suffix}-\d+\.\w+$'
        
        return bool(re.match(pattern, filename))
    
    def extract_variation_number(self, filename: str) -> Optional[int]:
        """
        Extract variation number from filename.
        
        Args:
            filename: e.g., "827749-1a-12345.jpg" or "827749-10a-12345.jpg"
        
        Returns:
            Variation number (e.g., 1, 2, 10) or None if not found
        """
        # Pattern to extract number before variation suffix
        pattern = rf'-(\d+){self.variation_suffix}-'
        match = re.search(pattern, filename)
        
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        
        return None
    
    def validate_dimensions(self, width: Optional[int], height: Optional[int]) -> bool:
        """
        Check if image meets minimum size requirements.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
        
        Returns:
            True if dimensions meet minimum requirements
        """
        if width is None or height is None:
            self.logger.warning(f"Missing dimension information: width={width}, height={height}")
            return False
        
        return width >= self.min_width and height >= self.min_height
    
    def is_valid_image_type(self, filename: str) -> bool:
        """
        Check if file extension is a valid image type.
        
        Args:
            filename: e.g., "827749-1a-12345.jpg"
        
        Returns:
            True if extension is in accepted list
        """
        _, ext = os.path.splitext(filename.lower())
        return ext in self.accepted_extensions
    
    def validate_image_sku_match(self, filename: str, image_sku: str) -> bool:
        """
        Verify that filename starts with the exact Image_SKU.
        Critical for cases like:
        - Image_SKU "1102192" should match "1102192-1a-12345.jpg"
        - But NOT "1102193-1a-12345.jpg"
        
        Args:
            filename: Full filename
            image_sku: Expected Image_SKU
        
        Returns:
            True if filename starts with exact Image_SKU followed by "-"
        """
        return filename.startswith(f"{image_sku}-")
    
    def get_validation_errors(self, filename: str, image_sku: str, width: Optional[int] = None, height: Optional[int] = None) -> List[str]:
        """
        Get all validation errors for a given image.
        
        Args:
            filename: Image filename
            image_sku: Expected Image_SKU
            width: Image width (optional)
            height: Image height (optional)
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check file type
        if not self.is_valid_image_type(filename):
            errors.append(f"Invalid file type. Accepted: {self.accepted_extensions}")
        
        # Check Image_SKU match
        if not self.validate_image_sku_match(filename, image_sku):
            errors.append(f"Filename doesn't start with Image_SKU '{image_sku}'")
        
        # Check filename pattern
        if not self.validate_filename(filename, image_sku):
            errors.append(f"Filename doesn't match pattern: [Image_SKU]-[Number]{self.variation_suffix}-[Random].[ext]")
        
        # Check dimensions if provided
        if width is not None and height is not None:
            if not self.validate_dimensions(width, height):
                errors.append(f"Image too small: {width}x{height} (minimum: {self.min_width}x{self.min_height})")
        
        return errors

