"""
Image handler for product image processing.
Handles fetching images from S3, validation, and preparing for Shopify upload.
"""

from typing import List, Dict, Any, Optional
import concurrent.futures
from src.core.s3_client import S3Client
from src.models.image_data import ImageData
from src.utils.image_logger import ImageLogger


class ImageHandler:
    """Handles product image processing and upload orchestration"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.s3_client = S3Client(config, logger)
        self.image_logger = ImageLogger(logger)
        self.max_workers = config.images.max_workers
        
        # Cache for already-fetched Image_SKUs
        self.image_cache = {}
    
    def collect_image_skus(self, products: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract unique Image_SKUs and map them to product variant SKUs.
        
        Args:
            products: List of product dictionaries from nav_items
        
        Returns:
            Dictionary mapping Image_SKU to list of Product SKUs
            Example: {
                "827749": ["827748", "827753"],
                "692978": ["692968", "692976"]
            }
        """
        image_sku_mapping = {}
        
        for product in products:
            image_sku = product.get('Image_SKU')
            product_sku = str(product.get('No_'))
            
            if not image_sku:
                self.logger.warning(f"Product {product_sku} has no Image_SKU, skipping images")
                continue
            
            if image_sku not in image_sku_mapping:
                image_sku_mapping[image_sku] = []
            
            image_sku_mapping[image_sku].append(product_sku)
        
        self.logger.info(f"Found {len(image_sku_mapping)} unique Image_SKUs across {len(products)} products")
        return image_sku_mapping
    
    def fetch_images_for_group(
        self, 
        image_sku_mapping: Dict[str, List[str]],
        group_id: str
    ) -> Dict[str, List[ImageData]]:
        """
        Batch fetch all images for product group from S3.
        Uses parallel processing for efficiency.
        
        Args:
            image_sku_mapping: Map of Image_SKU to Product SKUs
            group_id: Product group ID for logging
        
        Returns:
            Dictionary mapping Image_SKU to list of ImageData objects
        """
        self.logger.info(f"Fetching images for {len(image_sku_mapping)} unique Image_SKUs")
        
        image_data_map = {}
        
        # Use ThreadPoolExecutor for parallel S3 fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all fetch tasks
            future_to_sku = {
                executor.submit(self._fetch_images_for_sku_cached, image_sku, group_id, product_skus): image_sku
                for image_sku, product_skus in image_sku_mapping.items()
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_sku):
                image_sku = future_to_sku[future]
                try:
                    images = future.result()
                    image_data_map[image_sku] = images
                except Exception as e:
                    self.logger.error(f"Exception fetching images for Image_SKU '{image_sku}': {e}")
                    image_data_map[image_sku] = []
        
        # Log summary
        total_images = sum(len(images) for images in image_data_map.values())
        self.logger.info(f"Successfully fetched {total_images} total images from S3")
        
        return image_data_map
    
    def _fetch_images_for_sku_cached(
        self, 
        image_sku: str, 
        group_id: str, 
        product_skus: List[str]
    ) -> List[ImageData]:
        """
        Fetch images for Image_SKU with caching to avoid redundant S3 calls.
        
        Args:
            image_sku: Image_SKU to fetch
            group_id: Product group ID for logging
            product_skus: List of product SKUs using this Image_SKU
        
        Returns:
            List of ImageData objects
        """
        # Check cache first
        if image_sku in self.image_cache:
            self.logger.debug(f"Using cached images for Image_SKU '{image_sku}'")
            return self.image_cache[image_sku]
        
        # Fetch from S3
        images = self.s3_client.fetch_images_for_sku(image_sku)
        
        # Log missing images
        if not images:
            s3_path = self.s3_client.construct_s3_path(image_sku)
            for product_sku in product_skus:
                self.image_logger.log_missing_images(
                    group_id=group_id,
                    product_sku=product_sku,
                    image_sku=image_sku,
                    s3_path=s3_path,
                    error="No valid images found in S3"
                )
        
        # Cache result
        self.image_cache[image_sku] = images
        
        return images
    
    def process_product_images(
        self, 
        product_data: Dict[str, Any], 
        image_data_map: Dict[str, List[ImageData]]
    ) -> List[Dict[str, Any]]:
        """
        Prepare images for Shopify upload.
        Converts ImageData objects to Shopify media format.
        
        Args:
            product_data: Transformed Shopify product data
            image_data_map: Map of Image_SKU to ImageData list
        
        Returns:
            List of media objects for Shopify ProductSetInput
        """
        media = []
        
        # Collect all unique images for this product
        # Multiple variants may share the same Image_SKU
        unique_images = set()
        
        for variant in product_data.get('variants', []):
            # Each variant should have an Image_SKU stored during transformation
            image_sku = variant.get('_image_sku')
            if not image_sku:
                continue
            
            images = image_data_map.get(image_sku, [])
            for image in images:
                unique_images.add(image)
        
        # Convert to list and sort by variation number
        sorted_images = sorted(list(unique_images))
        
        # Convert to Shopify media format
        for image in sorted_images:
            media_item = {
                'originalSource': image.url,
                'alt': f"{image.image_sku} - Image {image.variation_number}",
                'mediaContentType': 'IMAGE'
            }
            media.append(media_item)
        
        self.logger.info(f"Prepared {len(media)} images for product upload")
        return media
    
    def get_existing_product_images(self, product_id: str, shopify_manager) -> set:
        """
        Query Shopify for existing images (for incremental updates).
        
        Args:
            product_id: Shopify product GID
            shopify_manager: ShopifyManager instance
        
        Returns:
            Set of existing image URLs
        """
        query = """
        query getProductImages($id: ID!) {
            product(id: $id) {
                media(first: 100) {
                    nodes {
                        ... on MediaImage {
                            image {
                                url
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"id": product_id}
        
        try:
            import requests
            response = requests.post(
                shopify_manager.base_url,
                headers=shopify_manager.headers,
                json={'query': query, 'variables': variables},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                media_nodes = result.get('data', {}).get('product', {}).get('media', {}).get('nodes', [])
                existing_urls = set()
                for node in media_nodes:
                    if 'image' in node and 'url' in node['image']:
                        existing_urls.add(node['image']['url'])
                return existing_urls
            else:
                self.logger.error(f"Failed to query existing images: {response.status_code}")
                return set()
                
        except Exception as e:
            self.logger.error(f"Error querying existing product images: {e}")
            return set()
    
    def get_image_logger_summary(self) -> Dict[str, int]:
        """Get summary of image processing issues"""
        return self.image_logger.get_summary()
    
    def print_image_summary(self):
        """Print summary of image processing"""
        self.image_logger.print_summary()
