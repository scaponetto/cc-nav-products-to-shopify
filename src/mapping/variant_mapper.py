"""
Variant-level mapping logic for transforming warranty database data to Shopify variant format.
"""

from typing import Dict, Any, List
from src.models.database_models import NavItem, NavBomComponent

class VariantMapper:
    """Maps warranty database product data to Shopify variant format"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def map_variant(self, product: NavItem, components: List[NavBomComponent]) -> Dict[str, Any]:
        """Map warranty database product to Shopify variant format"""
        
        # Generate option values based on product type
        option_values = self._generate_option_values(product, components)
        
        # Generate SKU
        sku = self._generate_sku(product)
        
        # Calculate weight
        weight = self._calculate_weight(product, components)
        
        return {
            'optionValues': option_values,
            'sku': sku,
            'price': 0.0,  # Placeholder - would need pricing logic
            'inventoryQuantity': 0,  # Placeholder - would need inventory logic
            'weight': weight,
            'weightUnit': 'kg'
        }
    
    def _generate_option_values(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, str]]:
        """Generate option values based on product type and variations"""
        option_values = []
        
        # Determine primary variations based on product type
        if product.get('Item_Category_Code') == 'RING':
            # Rings: Size, Metal Type, Stone Weight
            option_values = self._get_ring_options(product, components)
        elif product.get('Item_Category_Code') == 'EARRING':
            # Earrings: Metal Type, Stone Weight, Stone Length
            option_values = self._get_earring_options(product, components)
        elif product.get('Item_Category_Code') == 'NECKLACE':
            # Necklaces: Metal Type, Stone Weight, Plating Type
            option_values = self._get_necklace_options(product, components)
        elif product.get('Item_Category_Code') == 'BRACELET':
            # Bracelets: Metal Type, Stone Weight, Plating Type
            option_values = self._get_bracelet_options(product, components)
        elif product.get('Item_Category_Code') == 'GEMSTONE':
            # Gemstones: Stone Weight, Stone Length, Stone Width
            option_values = self._get_gemstone_options(product, components)
        else:
            # Default: Metal Type, Stone Weight, Stone Shape
            option_values = self._get_default_options(product, components)
        
        return option_values
    
    def _get_ring_options(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, str]]:
        """Get ring-specific option values"""
        options = []
        
        # Option 1: Ring Size (placeholder - would need size data)
        options.append({"optionName": "Size", "name": "7"})
        
        # Option 2: Metal Type
        if product.get('Metal_Stamp') and product.get('Metal_Color'):
            metal_type = self._format_metal_type(product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code'))
            options.append({"optionName": "Metal", "name": metal_type})
        
        # Option 3: Stone Weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                options.append({"optionName": "Stone Weight", "name": f"{stone_weight:.2f} CTW"})
            except (ValueError, TypeError):
                pass
        
        return options
    
    def _get_earring_options(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, str]]:
        """Get earring-specific option values"""
        options = []
        
        # Option 1: Metal Type
        if product.get('Metal_Stamp') and product.get('Metal_Color'):
            metal_type = self._format_metal_type(product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code'))
            options.append({"optionName": "Metal", "name": metal_type})
        
        # Option 2: Stone Weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                options.append({"optionName": "Stone Weight", "name": f"{stone_weight:.2f} CTW"})
            except (ValueError, TypeError):
                pass
        
        # Option 3: Stone Length
        if product.get('Primary_Gem_Diameter_Length_MM'):
            options.append({"optionName": "Stone Length", "name": f"{product['Primary_Gem_Diameter_Length_MM']}mm"})
        
        return options
    
    def _get_necklace_options(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, str]]:
        """Get necklace-specific option values"""
        options = []
        
        # Option 1: Metal Type
        if product.get('Metal_Stamp') and product.get('Metal_Color'):
            metal_type = self._format_metal_type(product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code'))
            options.append({"optionName": "Metal", "name": metal_type})
        
        # Option 2: Stone Weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                options.append({"optionName": "Stone Weight", "name": f"{stone_weight:.2f} CTW"})
            except (ValueError, TypeError):
                pass
        
        # Option 3: Plating Type (placeholder)
        options.append({"optionName": "Plating", "name": "Standard"})
        
        return options
    
    def _get_bracelet_options(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, str]]:
        """Get bracelet-specific option values"""
        options = []
        
        # Option 1: Metal Type
        if product.get('Metal_Stamp') and product.get('Metal_Color'):
            metal_type = self._format_metal_type(product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code'))
            options.append({"optionName": "Metal", "name": metal_type})
        
        # Option 2: Stone Weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                options.append({"optionName": "Stone Weight", "name": f"{stone_weight:.2f} CTW"})
            except (ValueError, TypeError):
                pass
        
        # Option 3: Plating Type (placeholder)
        options.append({"optionName": "Plating", "name": "Standard"})
        
        return options
    
    def _get_gemstone_options(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, str]]:
        """Get gemstone-specific option values"""
        options = []
        
        # Option 1: Stone Weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                options.append({"optionName": "Stone Weight", "name": f"{stone_weight:.2f} CTW"})
            except (ValueError, TypeError):
                pass
        
        # Option 2: Stone Length
        if product.get('Primary_Gem_Diameter_Length_MM'):
            options.append({"optionName": "Stone Length", "name": f"{product['Primary_Gem_Diameter_Length_MM']}mm"})
        
        # Option 3: Stone Width
        if product.get('Primary_Gem_Width_MM'):
            options.append({"optionName": "Stone Width", "name": f"{product['Primary_Gem_Width_MM']}mm"})
        
        return options
    
    def _get_default_options(self, product: NavItem, components: List[NavBomComponent]) -> List[Dict[str, str]]:
        """Get default option values"""
        options = []
        
        # Option 1: Metal Type
        if product.get('Metal_Stamp') and product.get('Metal_Color'):
            metal_type = self._format_metal_type(product['Metal_Stamp'], product['Metal_Color'], product.get('Metal_Code'))
            options.append({"optionName": "Metal", "name": metal_type})
        
        # Option 2: Stone Weight
        stone_weight = product.get('Stone_Weight__Carats_')
        if stone_weight:
            try:
                stone_weight = float(stone_weight)
                options.append({"optionName": "Stone Weight", "name": f"{stone_weight:.2f} CTW"})
            except (ValueError, TypeError):
                pass
        
        # Option 3: Stone Shape
        if product.get('Primary_Gem_Shape'):
            options.append({"optionName": "Stone Shape", "name": product['Primary_Gem_Shape'].title()})
        
        return options
    
    def _generate_sku(self, product: NavItem) -> str:
        """Generate SKU from product data"""
        return product.get('No_')
    
    def _calculate_weight(self, product: NavItem, components: List[NavBomComponent]) -> float:
        """Calculate product weight (placeholder logic)"""
        # This would need actual weight calculation logic
        # For now, return a placeholder value
        return 0.01  # 10 grams
    
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
