"""
Specialized logging for image processing errors and missing images.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional


class ImageLogger:
    """Handles specialized logging for image-related errors"""
    
    def __init__(self, logger, log_dir: str = "logs"):
        self.logger = logger
        self.log_dir = log_dir
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate timestamp for log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.missing_images_log = os.path.join(log_dir, f"missing_images_{timestamp}.log")
        self.upload_failures_log = os.path.join(log_dir, f"image_upload_failures_{timestamp}.log")
        
        # Track stats
        self.missing_count = 0
        self.upload_failure_count = 0
    
    def log_missing_images(
        self, 
        group_id: str, 
        product_sku: str, 
        image_sku: str, 
        s3_path: str, 
        error: str
    ):
        """
        Log products/variants with missing images.
        
        Args:
            group_id: Web_Product_Group_ID
            product_sku: Product No_
            image_sku: Image_SKU being searched
            s3_path: S3 path that was searched
            error: Error description
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"[{timestamp}] "
            f"Product Group: {group_id} | "
            f"Product SKU: {product_sku} | "
            f"Image SKU: {image_sku} | "
            f"S3 Path: {s3_path} | "
            f"Error: {error}\n"
        )
        
        # Write to file
        with open(self.missing_images_log, 'a') as f:
            f.write(log_message)
        
        # Also log to main logger
        self.logger.warning(
            f"Missing images for product {product_sku} (Image SKU: {image_sku}): {error}"
        )
        
        self.missing_count += 1
    
    def log_upload_failure(
        self, 
        product_id: str, 
        image_filename: str, 
        s3_url: str, 
        error: str
    ):
        """
        Log image upload failures to Shopify.
        
        Args:
            product_id: Shopify Product GID
            image_filename: Name of image file
            s3_url: S3 URL of image
            error: Error details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"[{timestamp}] "
            f"Product: {product_id} | "
            f"Image: {image_filename} | "
            f"S3 URL: {s3_url} | "
            f"Error: {error}\n"
        )
        
        # Write to file
        with open(self.upload_failures_log, 'a') as f:
            f.write(log_message)
        
        # Also log to main logger
        self.logger.error(
            f"Failed to upload image {image_filename} for product {product_id}: {error}"
        )
        
        self.upload_failure_count += 1
    
    def log_validation_errors(
        self, 
        image_sku: str, 
        filename: str, 
        errors: List[str]
    ):
        """
        Log image validation errors.
        
        Args:
            image_sku: Image_SKU being processed
            filename: Image filename
            errors: List of validation errors
        """
        error_str = ", ".join(errors)
        self.logger.debug(
            f"Image validation failed for {filename} (Image SKU: {image_sku}): {error_str}"
        )
    
    def get_summary(self) -> Dict[str, int]:
        """
        Get summary of logged errors.
        
        Returns:
            Dictionary with error counts
        """
        return {
            "missing_images": self.missing_count,
            "upload_failures": self.upload_failure_count
        }
    
    def print_summary(self):
        """Print summary of image processing issues"""
        if self.missing_count > 0 or self.upload_failure_count > 0:
            self.logger.warning("\n" + "="*60)
            self.logger.warning("IMAGE PROCESSING SUMMARY")
            self.logger.warning("="*60)
            
            if self.missing_count > 0:
                self.logger.warning(f"Missing images: {self.missing_count}")
                self.logger.warning(f"  See: {self.missing_images_log}")
            
            if self.upload_failure_count > 0:
                self.logger.warning(f"Upload failures: {self.upload_failure_count}")
                self.logger.warning(f"  See: {self.upload_failures_log}")
            
            self.logger.warning("="*60 + "\n")
        else:
            self.logger.info("✅ All images processed successfully!")

