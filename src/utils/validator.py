"""
Data validation utilities for the product export system.
"""

from typing import List, Dict, Any

class ProductValidator:
    """Validates product data before API submission"""
    
    def validate_product_data(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate product data and return list of errors"""
        errors = []
        
        # Required fields
        if not product_data.get('title') or len(product_data.get('title', '').strip()) == 0:
            errors.append("Product title is required")
        
        if product_data.get('title') and len(product_data['title']) > 255:
            errors.append("Product title exceeds 255 characters")
        
        # Validate variants
        variants = product_data.get('variants', [])
        if variants:
            for i, variant in enumerate(variants):
                variant_errors = self._validate_variant(variant, i)
                errors.extend(variant_errors)
        else:
            errors.append("At least one variant is required")
        
        # Validate metafields
        metafields = product_data.get('metafields', [])
        if metafields:
            metafield_errors = self._validate_metafields(metafields)
            errors.extend(metafield_errors)
        
        return errors
    
    def _validate_variant(self, variant: Dict[str, Any], index: int) -> List[str]:
        """Validate individual variant"""
        errors = []
        
        if not variant.get('optionValues'):
            errors.append(f"Variant {index}: option_values is required")
        
        if variant.get('price') is not None and variant.get('price', 0) < 0:
            errors.append(f"Variant {index}: price cannot be negative")
        
        if variant.get('sku') and len(variant['sku']) > 255:
            errors.append(f"Variant {index}: SKU exceeds 255 characters")
        
        return errors
    
    def _validate_metafields(self, metafields: List[Dict[str, Any]]) -> List[str]:
        """Validate metafields structure"""
        errors = []
        
        for i, metafield in enumerate(metafields):
            required_fields = ['namespace', 'key', 'type', 'value']
            for field in required_fields:
                if field not in metafield:
                    errors.append(f"Metafield {i}: {field} is required")
        
        return errors
