"""
Image uploader for Shopify operations.
Handles uploading images and associating them with variants.
"""

from typing import List, Dict, Any
import requests


class ImageUploader:
    """Handles Shopify image upload operations"""
    
    def __init__(self, shopify_manager, logger):
        self.shopify_manager = shopify_manager
        self.logger = logger
    
    def associate_images_to_variants(
        self,
        product_id: str,
        variants: List[Dict[str, Any]],
        image_sku_mapping: Dict[str, str],
        image_data_map: Dict[str, List[Any]]
    ):
        """
        Link images to specific variants.
        Associates the primary image (variation 1) to each variant based on Image_SKU.
        
        Args:
            product_id: Shopify Product GID
            variants: List of variant data from Shopify (with IDs and SKUs)
            image_sku_mapping: Map of Product SKU to Image_SKU
            image_data_map: Map of Image_SKU to ImageData list
        """
        self.logger.info(f"Associating images to variants for product {product_id}")
        
        # Get product media to map variation numbers to media IDs
        media_map = self._get_product_media_map(product_id)
        
        if not media_map:
            self.logger.warning("No media found for product, skipping variant association")
            return
        
        for variant in variants:
            variant_sku = variant.get('sku')
            variant_id = variant.get('id')
            
            if not variant_sku or not variant_id:
                continue
            
            # Get Image_SKU for this variant
            image_sku = image_sku_mapping.get(variant_sku)
            if not image_sku:
                self.logger.debug(f"No Image_SKU found for variant {variant_sku}")
                continue
            
            # Get images for this Image_SKU
            images = image_data_map.get(image_sku, [])
            if not images:
                self.logger.debug(f"No images found for Image_SKU '{image_sku}'")
                continue
            
            # Get primary image (variation 1)
            primary_image = next((img for img in images if img.variation_number == 1), None)
            if not primary_image:
                # Fallback to first image if no variation 1
                primary_image = images[0]
            
            # Get media ID for this image
            media_id = media_map.get(primary_image.variation_number)
            if not media_id:
                self.logger.debug(f"No media ID found for variation {primary_image.variation_number}")
                continue
            
            # Associate image to variant
            self._associate_image_to_variant(variant_id, media_id)
    
    def _get_product_media_map(self, product_id: str) -> Dict[int, str]:
        """
        Get map of variation number to media ID.
        
        Args:
            product_id: Shopify Product GID
        
        Returns:
            Dictionary mapping variation number to media ID
        """
        query = """
        query getProductMedia($id: ID!) {
            product(id: $id) {
                media(first: 100) {
                    nodes {
                        ... on MediaImage {
                            id
                            alt
                        }
                    }
                }
            }
        }
        """
        
        variables = {"id": product_id}
        
        try:
            response = requests.post(
                self.shopify_manager.base_url,
                headers=self.shopify_manager.headers,
                json={'query': query, 'variables': variables},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                media_nodes = result.get('data', {}).get('product', {}).get('media', {}).get('nodes', [])
                
                media_map = {}
                for node in media_nodes:
                    # Extract variation number from alt text (format: "[Image_SKU] - Image [N]")
                    alt = node.get('alt', '')
                    try:
                        if ' - Image ' in alt:
                            variation_num = int(alt.split(' - Image ')[1])
                            media_map[variation_num] = node['id']
                    except (ValueError, IndexError):
                        pass
                
                return media_map
            else:
                self.logger.error(f"Failed to query product media: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error querying product media: {e}")
            return {}
    
    def _associate_image_to_variant(self, variant_id: str, media_id: str):
        """
        Associate an image to a specific variant.
        
        Args:
            variant_id: Shopify Variant GID
            media_id: Shopify Media GID
        """
        mutation = """
        mutation productVariantUpdate($input: ProductVariantInput!) {
            productVariantUpdate(input: $input) {
                productVariant {
                    id
                    image {
                        id
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        """
        
        variables = {
            "input": {
                "id": variant_id,
                "mediaId": media_id
            }
        }
        
        try:
            response = requests.post(
                self.shopify_manager.base_url,
                headers=self.shopify_manager.headers,
                json={'query': mutation, 'variables': variables},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                errors = result.get('data', {}).get('productVariantUpdate', {}).get('userErrors', [])
                if errors:
                    self.logger.warning(f"Errors associating image to variant {variant_id}: {errors}")
                else:
                    self.logger.debug(f"✅ Successfully associated image to variant {variant_id}")
            else:
                self.logger.error(f"Failed to associate image to variant: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error associating image to variant {variant_id}: {e}")

