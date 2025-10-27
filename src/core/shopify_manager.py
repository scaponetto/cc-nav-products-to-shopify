"""
Shopify manager for API interactions.
Handles product creation, updates, and error management.
"""

from typing import Dict, Any, Optional
import requests
from src.utils.rate_limiter import RateLimiter
from src.utils.error_handler import ErrorHandler, RateLimitError
from src.core.image_uploader import ImageUploader

class ShopifyManager:
    """Manages Shopify API interactions"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.rate_limiter = RateLimiter(config)
        self.error_handler = ErrorHandler(config, logger)
        self.base_url = f"https://{config.shopify.shop_domain}/admin/api/{config.shopify.api_version}/graphql.json"
        self.headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': config.shopify.access_token
        }
        
        # Initialize image uploader
        self.image_uploader = ImageUploader(self, logger)
    
    def create_or_update_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a product in Shopify using atomic operations"""
        self.rate_limiter.wait_if_needed()
        
        # Prepare GraphQL mutation
        mutation = self._prepare_product_set_mutation(product_data)
        
        # Execute with retry logic
        result = self.error_handler.execute_with_retry(
            self._execute_graphql_mutation,
            mutation
        )
        
        # If product was created successfully, upload images, publish, and associate
        if result.get('product') and not result.get('userErrors'):
            product_id = result['product']['id']
            
            # Upload images if present
            if 'media' in product_data and product_data['media']:
                self.logger.info(f"Uploading {len(product_data['media'])} images to product")
                upload_result = self._upload_product_images(product_id, product_data['media'])
                if not upload_result:
                    self.logger.warning("Some images failed to upload")
            
            # Publish to Online Store
            publish_result = self._publish_to_online_store(product_id)
            if publish_result.get('userErrors'):
                self.logger.warning(f"Failed to publish product to Online Store: {publish_result['userErrors']}")
            else:
                self.logger.info(f"Successfully published product {product_id} to Online Store")
            
            # Associate images to variants if image data is present
            if '_image_sku_mapping' in product_data and '_image_data_map' in product_data:
                self.logger.info("Associating images to variants")
                
                # Build mapping of variant SKU to Image_SKU
                variant_to_image_sku = {}
                for image_sku, product_skus in product_data['_image_sku_mapping'].items():
                    for product_sku in product_skus:
                        variant_to_image_sku[product_sku] = image_sku
                
                # Get variants from result
                variants = result['product'].get('variants', {}).get('nodes', [])
                
                # Associate images
                self.image_uploader.associate_images_to_variants(
                    product_id,
                    variants,
                    variant_to_image_sku,
                    product_data['_image_data_map']
                )
        
        return result
    
    def _prepare_product_set_mutation(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare productSet mutation for atomic product creation"""
        mutation = """
        mutation productSet($input: ProductSetInput!, $synchronous: Boolean!) {
            productSet(input: $input, synchronous: $synchronous) {
                product {
                    id
                    title
                    handle
                    status
                    variants(first: 100) {
                        nodes {
                            id
                            title
                            price
                            sku
                            selectedOptions {
                                name
                                value
                            }
                        }
                    }
                    metafields(first: 50) {
                        nodes {
                            id
                            namespace
                            key
                            value
                            type
                        }
                    }
                }
                userErrors {
                    field
                    message
                    code
                }
            }
        }
        """
        
        # Extract product options from variants
        product_options = []
        if product_data.get('variants'):
            # Get unique option names and their values from variants
            option_data = {}
            for variant in product_data['variants']:
                if variant.get('optionValues'):
                    for option in variant['optionValues']:
                        option_name = option['optionName']
                        option_value = option['name']
                        if option_name not in option_data:
                            option_data[option_name] = set()
                        option_data[option_name].add(option_value)
            
            # Create product options with values
            for i, (option_name, values) in enumerate(option_data.items(), 1):
                # Convert values to objects with just name
                value_objects = []
                for value in values:
                    value_objects.append({
                        'name': value
                    })
                
                product_options.append({
                    'name': option_name,
                    'position': i,
                    'values': value_objects
                })
        
        # Add product options to the input and clean internal fields
        product_data_with_options = product_data.copy()
        if product_options:
            product_data_with_options['productOptions'] = product_options
        
        # Remove internal fields that shouldn't be sent to Shopify
        # 'media' will be uploaded separately after product creation
        fields_to_remove = ['_image_sku_mapping', '_image_data_map', 'media']
        for field in fields_to_remove:
            product_data_with_options.pop(field, None)
        
        # Remove internal fields from variants
        if 'variants' in product_data_with_options:
            for variant in product_data_with_options['variants']:
                variant.pop('_image_sku', None)
        
        variables = {
            "input": product_data_with_options,
            "synchronous": True
        }
        
        return {
            "query": mutation,
            "variables": variables
        }
    
    def _execute_graphql_mutation(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphQL mutation"""
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=mutation,
            timeout=self.config.shopify.timeout
        )
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 2))
            raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds", retry_after)
        
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('errors'):
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result['data']['productSet']
    
    def _publish_to_online_store(self, product_id: str) -> Dict[str, Any]:
        """Publish product to Online Store sales channel"""
        mutation = """
        mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
            publishablePublish(id: $id, input: $input) {
                publishable {
                    availablePublicationsCount {
                        count
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
            "id": product_id,
            "input": [{
                "publicationId": "gid://shopify/Publication/80554164402"
            }]
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "query": mutation,
                    "variables": variables
                },
                timeout=self.config.shopify.timeout
            )
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 2))
                raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds", retry_after)
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('errors'):
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            return result['data']['publishablePublish']
            
        except Exception as e:
            self.logger.error(f"Failed to publish product to Online Store: {e}")
            return {"userErrors": [{"field": "publish", "message": str(e)}]}
    
    def _upload_product_images(self, product_id: str, media: list) -> bool:
        """Upload images to product using productCreateMedia mutation"""
        mutation = """
        mutation productCreateMedia($productId: ID!, $media: [CreateMediaInput!]!) {
            productCreateMedia(productId: $productId, media: $media) {
                media {
                    ... on MediaImage {
                        id
                        alt
                        image {
                            url
                        }
                    }
                }
                mediaUserErrors {
                    field
                    message
                }
            }
        }
        """
        
        variables = {
            "productId": product_id,
            "media": media
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "query": mutation,
                    "variables": variables
                },
                timeout=self.config.shopify.timeout
            )
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 2))
                raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds", retry_after)
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('errors'):
                self.logger.error(f"GraphQL errors uploading images: {result['errors']}")
                return False
            
            media_errors = result.get('data', {}).get('productCreateMedia', {}).get('mediaUserErrors', [])
            if media_errors:
                self.logger.error(f"Media upload errors: {media_errors}")
                return False
            
            media_created = result.get('data', {}).get('productCreateMedia', {}).get('media', [])
            self.logger.info(f"Successfully uploaded {len(media_created)} images to product {product_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upload images to product: {e}")
            return False
