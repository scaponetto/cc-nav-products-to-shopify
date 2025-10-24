"""
Data models for product data structures.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ProductData:
    """Complete product representation with all related data"""
    # Core product fields
    title: str
    description: Optional[str] = None
    product_type: Optional[str] = None
    vendor: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str = "ACTIVE"
    handle: Optional[str] = None
    
    # SEO fields
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    
    # Product structure
    product_options: Optional[List[Dict[str, Any]]] = None
    variants: Optional[List['ProductVariant']] = None
    
    # Extended data
    metafields: Optional[List[Dict[str, Any]]] = None
    files: Optional[List[Dict[str, Any]]] = None

@dataclass
class ProductVariant:
    """Product variant with all associated data"""
    option_values: List[Dict[str, str]]
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    inventory_quantity: Optional[int] = None
    weight: Optional[float] = None
    weight_unit: str = "kg"
    
    # Variant-specific data
    metafields: Optional[List[Dict[str, Any]]] = None
    media_src: Optional[List[str]] = None

@dataclass
class ProcessingResult:
    """Result of processing a group ID"""
    group_id: str
    success: bool
    product_id: Optional[str] = None
    error_message: Optional[str] = None
    variants_created: int = 0
    metafields_created: int = 0
