"""
Data transformer for converting warranty database data to Shopify format.
Implements mapping rules from specification documents.
"""

from typing import List, Dict, Any, Optional
from src.mapping.product_mapper import ProductMapper
from src.mapping.variant_mapper import VariantMapper
from src.mapping.metadata_mapper import MetadataMapper

class DataTransformer:
    """Transforms warranty database data to Shopify-compatible format"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.product_mapper = ProductMapper(config, logger)
        self.variant_mapper = VariantMapper(config, logger)
        self.metadata_mapper = MetadataMapper(config, logger)
    
    def transform_group_data(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform group data to Shopify product format"""
        group_id = group_data['group_id']
        products = group_data['products']
        components = group_data['components']
        
        # Group components by product
        components_by_product = {}
        for component in components:
            product_no = component['Parent_Item_No_']
            if product_no not in components_by_product:
                components_by_product[product_no] = []
            components_by_product[product_no].append(component)
        
        # Transform to Shopify format
        shopify_product = self.product_mapper.map_product(
            products[0], components_by_product.get(products[0]['No_'], [])
        )
        
        # Add variants for all products in group
        shopify_product['variants'] = []
        for product in products:
            variant = self.variant_mapper.map_variant(
                product, components_by_product.get(product['No_'], [])
            )
            shopify_product['variants'].append(variant)
        
        # Add metafields
        shopify_product['metafields'] = self.metadata_mapper.map_metafields(
            products[0], components_by_product.get(products[0]['No_'], [])
        )
        
        return shopify_product
    
    def validate_shopify_data(self, shopify_data: Dict[str, Any]) -> List[str]:
        """Validate transformed Shopify data"""
        errors = []
        
        # Validate required fields
        if not shopify_data.get('title'):
            errors.append("Product title is required")
        
        if not shopify_data.get('variants'):
            errors.append("At least one variant is required")
        
        # Validate variants
        for i, variant in enumerate(shopify_data.get('variants', [])):
            if not variant.get('sku'):
                errors.append(f"Variant {i}: SKU is required")
            
            if not variant.get('optionValues'):
                errors.append(f"Variant {i}: Option values are required")
        
        # Validate metafields
        for i, metafield in enumerate(shopify_data.get('metafields', [])):
            required_fields = ['namespace', 'key', 'type', 'value']
            for field in required_fields:
                if field not in metafield:
                    errors.append(f"Metafield {i}: {field} is required")
        
        return errors
