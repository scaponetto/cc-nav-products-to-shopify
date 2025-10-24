"""
Product-level mapping logic for transforming warranty database data to Shopify format.
"""

from typing import Dict, Any, List
from src.models.database_models import NavItem, NavBomComponent

class ProductMapper:
    """Maps warranty database product data to Shopify product format"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        
        # Material type mappings
        self.material_type_map = {
            'LGD': 'Lab-Grown Diamond',
            'MOISSANITE': 'Moissanite',
            'NAT': 'Natural Diamond',
            'CZ': 'Cubic Zirconia',
            'SAPPHIRE': 'Sapphire',
            'RUBY': 'Ruby',
            'EMERALD': 'Emerald',
            'AMETHYST': 'Amethyst'
        }
        
        # Product type mappings
        self.product_type_map = {
            'RING': 'Ring',
            'EARRING': 'Earring',
            'NECKLACE': 'Necklace',
            'BRACELET': 'Bracelet',
            'PENDANT': 'Pendant',
            'GEMSTONE': 'Gemstone'
        }
    
    def map_product(self, product: NavItem, components: List[NavBomComponent]) -> Dict[str, Any]:
        """Map warranty database product to Shopify product format"""
        
        # Generate product title
        title = self._generate_product_title(product, components)
        
        # Generate handle
        handle = self._generate_handle(title, product.get('Web_Product_Group_ID'))
        
        # Map product type
        product_type = self.product_type_map.get(product.get('Item_Category_Code'), product.get('Item_Category_Code'))
        
        return {
            'title': title,
            'handle': handle,
            'productType': product_type,
            'status': 'ACTIVE',
            'vendor': 'Charles Colvard',
            'descriptionHtml': self._generate_description(product, components)
        }
    
    def _generate_product_title(self, product: NavItem, components: List[NavBomComponent]) -> str:
        """Generate product title based on specification"""
        title_parts = []
        
        # Total carat weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                if stone_weight > 0:
                    if product.get('Primary_Gem_Material_Type') == 'MOISSANITE':
                        title_parts.append(f"{stone_weight:.2f} CTW DEW")
                    else:
                        title_parts.append(f"{stone_weight:.2f} CTW")
            except (ValueError, TypeError):
                pass
        
        # Primary gem shape
        if product.get('Primary_Gem_Shape'):
            title_parts.append(product['Primary_Gem_Shape'].title())
        
        # Primary stone type
        if product.get('Primary_Gem_Material_Type'):
            material = self.material_type_map.get(product['Primary_Gem_Material_Type'], product['Primary_Gem_Material_Type'])
            title_parts.append(material)
        
        # Product group (setting style)
        if product.get('Product_Subgroup_Code'):
            title_parts.append(product['Product_Subgroup_Code'].title())
        
        # Item category
        if product.get('Item_Category_Code'):
            title_parts.append(product['Item_Category_Code'].title())
        
        # Metal type
        if product.get('Metal_Stamp') and product.get('Metal_Color'):
            metal_type = self._format_metal_type(product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code'))
            title_parts.append(f"in {metal_type}")
        
        return " ".join(title_parts)
    
    def _generate_handle(self, title: str, group_id: str) -> str:
        """Generate Shopify handle from product title and group ID"""
        # Convert to lowercase and replace spaces with hyphens
        handle = title.lower()
        handle = handle.replace(' ', '-')
        
        # Remove special characters and periods
        import re
        handle = re.sub(r'[^a-z0-9-]', '', handle)
        handle = handle.replace('.', '')
        
        # Remove multiple consecutive hyphens
        handle = re.sub(r'-+', '-', handle)
        
        # Trim leading/trailing hyphens
        handle = handle.strip('-')
        
        # Add group ID
        handle = f"{handle}-{group_id.lower()}"
        
        # Ensure it doesn't exceed 255 characters
        if len(handle) > 255:
            handle = handle[:255]
        
        return handle
    
    def _generate_description(self, product: NavItem, components: List[NavBomComponent]) -> str:
        """Generate product description"""
        description_parts = []
        
        # Basic product info
        if product.get('Primary_Gem_Material_Type'):
            material = self.material_type_map.get(product['Primary_Gem_Material_Type'], product['Primary_Gem_Material_Type'])
            description_parts.append(f"Beautiful {material} jewelry")
        
        # Metal type
        if product.get('Metal_Stamp') and product.get('Metal_Color'):
            metal_type = self._format_metal_type(product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code'))
            description_parts.append(f"crafted in {metal_type}")
        
        # Carat weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                if stone_weight > 0:
                    description_parts.append(f"with {stone_weight:.2f} total carat weight")
            except (ValueError, TypeError):
                pass
        
        return ". ".join(description_parts) + "."
    
    def _format_metal_type(self, metal_stamp: str, metal_color: str, metal_code: str) -> str:
        """Format metal type according to specification"""
        if metal_code == '14K' or metal_code == '18K' or metal_code == '10K':
            return f"{metal_stamp} {metal_color.title()} Gold"
        elif metal_code == 'SILVER':
            return f"{metal_color.title()} Silver"
        elif metal_code == 'PLAT':
            return "Platinum"
        elif metal_code == 'TANTALUM':
            if metal_color:
                return f"Tantalum {metal_color.title()}"
            return "Tantalum"
        elif metal_code == 'TITANIUM':
            if metal_color:
                return f"Titanium {metal_color.title()}"
            return "Titanium"
        else:
            return f"{metal_stamp} {metal_color.title()}"
