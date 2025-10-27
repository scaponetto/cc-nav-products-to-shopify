"""
AWS S3 client for fetching product images.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Optional
from PIL import Image
import io
from src.models.image_data import ImageData
from src.utils.image_validator import ImageValidator


class S3Client:
    """Handles all AWS S3 interactions for image fetching"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.validator = ImageValidator(config, logger)
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.aws.access_key_id,
                aws_secret_access_key=config.aws.secret_access_key,
                aws_session_token=config.aws.session_token,
                region_name=config.aws.region
            )
            self.bucket = config.aws.bucket
            self.base_directory = config.images.base_directory
            self.logger.info(f"S3 client initialized for bucket: {self.bucket}")
        except (ClientError, NoCredentialsError) as e:
            self.logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def construct_s3_path(self, image_sku: str) -> str:
        """
        Build S3 directory path from Image_SKU.
        
        Args:
            image_sku: e.g., "827749" or "1102192"
        
        Returns:
            e.g., "sorted-media/82/77/49/" or "sorted-media/11/02/19/"
        """
        # Take first 6 characters (or entire SKU if shorter)
        sku_prefix = image_sku[:6] if len(image_sku) >= 6 else image_sku
        
        # Pad to 6 characters if needed
        sku_prefix = sku_prefix.ljust(6, '0')
        
        # Split into 2-character segments
        segment1 = sku_prefix[0:2]
        segment2 = sku_prefix[2:4]
        segment3 = sku_prefix[4:6]
        
        return f"{self.base_directory}/{segment1}/{segment2}/{segment3}/"
    
    def list_images_in_directory(self, s3_path: str) -> List[str]:
        """
        List all files in S3 directory.
        
        Args:
            s3_path: S3 prefix/directory path
        
        Returns:
            List of S3 object keys
        """
        try:
            objects = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.bucket, Prefix=s3_path):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objects.append(obj['Key'])
            
            self.logger.debug(f"Found {len(objects)} objects in {s3_path}")
            return objects
            
        except ClientError as e:
            self.logger.error(f"Error listing S3 objects in {s3_path}: {e}")
            return []
    
    def get_image_metadata(self, s3_key: str) -> Optional[Dict]:
        """
        Get image dimensions without downloading full image.
        
        Args:
            s3_key: S3 object key
        
        Returns:
            Dictionary with width, height, content_type, file_size
        """
        try:
            # Get object metadata
            response = self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            
            metadata = {
                'content_type': response.get('ContentType'),
                'file_size': response.get('ContentLength'),
                'width': None,
                'height': None
            }
            
            # For dimensions, we need to download a small portion or the full image
            # Using byte range to minimize download
            try:
                # Try to get just enough bytes to read image header
                obj_response = self.s3_client.get_object(
                    Bucket=self.bucket,
                    Key=s3_key,
                    Range='bytes=0-50000'  # Get first 50KB for header
                )
                
                image_data = obj_response['Body'].read()
                
                # Try to open with PIL to get dimensions
                with Image.open(io.BytesIO(image_data)) as img:
                    metadata['width'] = img.width
                    metadata['height'] = img.height
                    
            except Exception as e:
                # If partial read fails, try full image
                self.logger.debug(f"Partial read failed for {s3_key}, trying full download: {e}")
                try:
                    obj_response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
                    image_data = obj_response['Body'].read()
                    
                    with Image.open(io.BytesIO(image_data)) as img:
                        metadata['width'] = img.width
                        metadata['height'] = img.height
                except Exception as e2:
                    self.logger.warning(f"Could not get dimensions for {s3_key}: {e2}")
            
            return metadata
            
        except ClientError as e:
            self.logger.error(f"Error getting metadata for {s3_key}: {e}")
            return None
    
    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate temporary URL for Shopify upload.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL or None if error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            self.logger.error(f"Error generating presigned URL for {s3_key}: {e}")
            return None
    
    def fetch_images_for_sku(self, image_sku: str) -> List[ImageData]:
        """
        Fetch all valid images for a given Image_SKU from S3.
        
        Args:
            image_sku: e.g., "827749"
        
        Returns:
            List of ImageData objects, sorted by variation number
        """
        # Construct S3 path
        s3_path = self.construct_s3_path(image_sku)
        self.logger.info(f"Fetching images for Image_SKU '{image_sku}' from {s3_path}")
        
        # List all objects in directory
        s3_keys = self.list_images_in_directory(s3_path)
        
        if not s3_keys:
            self.logger.warning(f"No objects found in {s3_path} for Image_SKU '{image_sku}'")
            return []
        
        valid_images = []
        
        for s3_key in s3_keys:
            # Extract filename from S3 key
            filename = s3_key.split('/')[-1]
            
            # Skip if not a valid image type
            if not self.validator.is_valid_image_type(filename):
                self.logger.debug(f"Skipping non-image file: {filename}")
                continue
            
            # Skip if doesn't match Image_SKU
            if not self.validator.validate_image_sku_match(filename, image_sku):
                self.logger.debug(f"Skipping file that doesn't match Image_SKU '{image_sku}': {filename}")
                continue
            
            # Skip if doesn't match naming pattern
            if not self.validator.validate_filename(filename, image_sku):
                self.logger.debug(f"Skipping file with invalid pattern: {filename}")
                continue
            
            # Extract variation number
            variation_number = self.validator.extract_variation_number(filename)
            if variation_number is None:
                self.logger.debug(f"Could not extract variation number from: {filename}")
                continue
            
            # Get image metadata (dimensions)
            metadata = self.get_image_metadata(s3_key)
            if not metadata:
                self.logger.warning(f"Could not get metadata for {filename}, skipping")
                continue
            
            # Validate dimensions
            if not self.validator.validate_dimensions(metadata['width'], metadata['height']):
                self.logger.debug(
                    f"Skipping image with insufficient dimensions: {filename} "
                    f"({metadata['width']}x{metadata['height']})"
                )
                continue
            
            # Generate presigned URL
            url = self.get_presigned_url(s3_key)
            if not url:
                self.logger.warning(f"Could not generate URL for {filename}, skipping")
                continue
            
            # Create ImageData object
            image_data = ImageData(
                image_sku=image_sku,
                variation_number=variation_number,
                s3_key=s3_key,
                filename=filename,
                url=url,
                width=metadata['width'],
                height=metadata['height'],
                file_size=metadata['file_size'],
                content_type=metadata['content_type']
            )
            
            valid_images.append(image_data)
            self.logger.debug(f"✅ Valid image found: {filename} (variation {variation_number})")
        
        # Sort by variation number
        valid_images.sort()
        
        self.logger.info(
            f"Found {len(valid_images)} valid images for Image_SKU '{image_sku}' "
            f"(out of {len(s3_keys)} total files)"
        )
        
        return valid_images

