"""
Metadata mapping logic for transforming warranty database data to Shopify metafields.
"""

from typing import Dict, Any, List
from src.models.database_models import NavItem, NavBomComponent

class MetadataMapper:
    """Maps warranty database product data to Shopify metafields"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def map_metafields(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, Any]]:
        """Map warranty database product data to Shopify metafields"""
        metafields = []
        
        # Product-level metafields
        metafields.extend(self._map_product_metafields(product))
        
        # Component-level metafields
        metafields.extend(self._map_component_metafields(components))
        
        return metafields
    
    def _map_product_metafields(self, product: NavItem) -> List[Dict[str, Any]]:
        """Map product-level attributes to metafields"""
        metafields = []
        
        # Setting style
        if product.get('Product_Subgroup_Code'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'setting_style',
                'type': 'single_line_text_field',
                'value': product['Product_Subgroup_Code']
            })
        
        # Stone material
        if product.get('Primary_Gem_Material_Type'):
            material = self._map_material_type(product['Primary_Gem_Material_Type'])
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'stone_material',
                'type': 'single_line_text_field',
                'value': material
            })
        
        # Stone shape
        if product.get('Primary_Gem_Shape'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'stone_shape',
                'type': 'single_line_text_field',
                'value': product['Primary_Gem_Shape']
            })
        
        # Stone color
        if product.get('Primary_Gem_Color'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'stone_color',
                'type': 'single_line_text_field',
                'value': product['Primary_Gem_Color']
            })
        
        # Main setting type
        if product.get('Main_Setting_Type'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'main_setting_type',
                'type': 'single_line_text_field',
                'value': product['Main_Setting_Type']
            })
        
        # Collection
        if product.get('Collection'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'collection',
                'type': 'single_line_text_field',
                'value': product['Collection']
            })
        
        # Jewelry brand
        if product.get('Jewelry_Brand'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'jewelry_brand',
                'type': 'single_line_text_field',
                'value': product['Jewelry_Brand']
            })
        
        # Gemstone brand
        if product.get('Gemstone_Brand'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'gemstone_brand',
                'type': 'single_line_text_field',
                'value': product['Gemstone_Brand']
            })
        
        # Style ID
        if product.get('Style_ID'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'style_id',
                'type': 'single_line_text_field',
                'value': product['Style_ID']
            })
        
        # Web descriptor
        if product.get('Web_Descriptor'):
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'web_descriptor',
                'type': 'single_line_text_field',
                'value': product['Web_Descriptor']
            })
        
        # Boolean flags
        if product.get('Is_Best_Seller') is not None:
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'is_best_seller',
                'type': 'boolean',
                'value': str(product['Is_Best_Seller']).lower()
            })
        
        if product.get('Is_High_ROAS') is not None:
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'is_high_roas',
                'type': 'boolean',
                'value': str(product['Is_High_ROAS']).lower()
            })
        
        if product.get('Is_Pinterest') is not None:
            metafields.append({
                'namespace': 'custom.product_attributes',
                'key': 'is_pinterest',
                'type': 'boolean',
                'value': str(product['Is_Pinterest']).lower()
            })
        
        return metafields
    
    def _map_component_metafields(self, components: List[NavBomComponent]) -> List[Dict[str, Any]]:
        """Map component-level attributes to metafields"""
        metafields = []
        
        # Group components by type
        stone_components = [c for c in components if c.get('Metal_Type') == '0']
        metal_components = [c for c in components if c.get('Metal_Type') == '1']
        
        # Stone component metafields
        if stone_components:
            main_stone = stone_components[0]  # First stone is typically the main stone
            
            # Stone dimensions
            if main_stone.get('Primary_Gem_Diameter_Length_MM'):
                metafields.append({
                    'namespace': 'custom.variant_attributes',
                    'key': 'stone_dimensions_length',
                    'type': 'number_decimal',
                    'value': str(main_stone['Primary_Gem_Diameter_Length_MM'])
                })
            
            if main_stone.get('Primary_Gem_Width_MM'):
                metafields.append({
                    'namespace': 'custom.variant_attributes',
                    'key': 'stone_dimensions_width',
                    'type': 'number_decimal',
                    'value': str(main_stone['Primary_Gem_Width_MM'])
                })
            
            # Clarity grade
            if main_stone.get('Primary_Gem_Grade_Clarity'):
                metafields.append({
                    'namespace': 'custom.variant_attributes',
                    'key': 'clarity_grade',
                    'type': 'single_line_text_field',
                    'value': main_stone['Primary_Gem_Grade_Clarity']
                })
            
            # Stone count
            if main_stone.get('Pieces_Per'):
                metafields.append({
                    'namespace': 'custom.variant_attributes',
                    'key': 'stone_count',
                    'type': 'number_integer',
                    'value': str(main_stone['Pieces_Per'])
                })
        
        return metafields
    
    def _map_material_type(self, material_type: str) -> str:
        """Map material type to display format"""
        material_map = {
            'LGD': 'Lab-Grown Diamond',
            'MOISSANITE': 'Moissanite',
            'NAT': 'Natural Diamond',
            'CZ': 'Cubic Zirconia',
            'SAPPHIRE': 'Sapphire',
            'RUBY': 'Ruby',
            'EMERALD': 'Emerald',
            'AMETHYST': 'Amethyst'
        }
        return material_map.get(material_type, material_type)
