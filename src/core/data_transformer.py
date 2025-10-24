"""
Data transformer for converting warranty database data to Shopify format.
Implements mapping rules from specification documents.
"""

from typing import List, Dict, Any, Optional
from src.mapping.product_mapper import ProductMapper
from src.mapping.variant_mapper import VariantMapper
from src.mapping.metadata_mapper import MetadataMapper
from src.models.database_models import NavItem

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
        
        # Determine dynamic variant attributes first
        dynamic_attributes = self.variant_mapper.get_dynamic_variant_attributes(products)
        
        # Transform to Shopify format
        shopify_product = self.product_mapper.map_product(
            products[0], components_by_product.get(products[0]['No_'], []), dynamic_attributes
        )
        
        # Add variants for all products in group, filtering duplicates
        shopify_product['variants'] = []
        seen_combinations = set()
        
        for product in products:
            variant = self.variant_mapper.map_variant(
                product, components_by_product.get(product['No_'], [])
            )
            
            # Update variant with dynamic attributes
            variant = self._apply_dynamic_attributes(variant, product, dynamic_attributes)
            
            # Create a unique key for this variant combination
            option_values = variant.get('optionValues', [])
            combination_key = tuple(sorted([f'{opt["optionName"]}:{opt["name"]}' for opt in option_values]))
            
            # Only add if we haven't seen this combination before
            if combination_key not in seen_combinations:
                shopify_product['variants'].append(variant)
                seen_combinations.add(combination_key)
            else:
                self.logger.warning(f"Skipping duplicate variant for product {product['No_']}: {combination_key}")
        
        # Add product options based on dynamic attributes
        shopify_product['productOptions'] = self._create_product_options(dynamic_attributes)
        
        # Add metafields
        shopify_product['metafields'] = self.metadata_mapper.map_metafields(
            products[0], components_by_product.get(products[0]['No_'], [])
        )
        
        return shopify_product
    
    def _apply_dynamic_attributes(self, variant: Dict[str, Any], product: NavItem, dynamic_attributes: Dict[str, List[str]]) -> Dict[str, Any]:
        """Apply dynamic attributes to variant based on product data"""
        option_values = []
        
        for attr_name, attr_values in dynamic_attributes.items():
            if attr_name == 'Size' and product.get('Ring_Size'):
                # Ring size
                try:
                    ring_size = float(product['Ring_Size'])
                    option_values.append({"optionName": attr_name, "name": f"{ring_size:.1f}"})
                except (ValueError, TypeError):
                    option_values.append({"optionName": attr_name, "name": str(product['Ring_Size'])})
            
            elif attr_name == 'Metal Type' and product.get('Metal_Stamp') and product.get('Metal_Color'):
                # Metal type
                metal_type = self.variant_mapper._format_metal_type(
                    product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code')
                )
                option_values.append({"optionName": attr_name, "name": metal_type})
            
            elif attr_name == 'Carat Weight' and product.get('Stone_Weight__Carats_'):
                # Stone weight
                try:
                    stone_weight = float(product['Stone_Weight__Carats_'])
                    option_values.append({"optionName": attr_name, "name": f"{stone_weight:.2f} CTW"})
                except (ValueError, TypeError):
                    pass
            
            # Stone Size is now a metadata attribute only, not a variant attribute
            # elif attr_name == 'Stone Size':
            #     # Stone size for non-ring products
            #     length = product.get('Primary_Gem_Diameter_Length_MM')
            #     width = product.get('Primary_Gem_Width_MM')
            #     if length and width:
            #         try:
            #             length_val = float(length)
            #             width_val = float(width)
            #             if length_val == width_val:
            #                 option_values.append({"optionName": attr_name, "name": f"{length_val:.1f}mm"})
            #             else:
            #                 option_values.append({"optionName": attr_name, "name": f"{length_val:.1f}x{width_val:.1f}mm"})
            #         except (ValueError, TypeError):
            #             pass
        
        variant['optionValues'] = option_values
        return variant
    
    def _create_product_options(self, dynamic_attributes: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Create product options from dynamic attributes"""
        product_options = []
        
        for i, (attr_name, attr_values) in enumerate(dynamic_attributes.items(), 1):
            # Convert values to objects with just name
            value_objects = []
            for value in attr_values:
                value_objects.append({
                    'name': value
                })
            
            product_options.append({
                'name': attr_name,
                'position': i,
                'values': value_objects
            })
        
        return product_options
    
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
