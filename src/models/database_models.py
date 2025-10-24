"""
Database response models for warranty database interactions.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class NavItem:
    """Model for nav_items table data"""
    No_: str
    Item_Category_Code: Optional[str] = None
    Product_Subgroup_Code: Optional[str] = None
    Metal_Stamp: Optional[str] = None
    Metal_Color: Optional[str] = None
    Primary_Gem_Material_Type: Optional[str] = None
    Primary_Gem_Shape: Optional[str] = None
    Primary_Gem_Color: Optional[str] = None
    Stone_Weight__Carats_: Optional[float] = None
    Web_Product_Group_ID: Optional[str] = None
    Metal_Code: Optional[str] = None
    Main_Setting_Type: Optional[str] = None
    Collection: Optional[str] = None
    Jewelry_Brand: Optional[str] = None
    Gemstone_Brand: Optional[str] = None
    Style_ID: Optional[str] = None
    Web_Descriptor: Optional[str] = None
    Is_Best_Seller: Optional[bool] = None
    Is_High_ROAS: Optional[bool] = None
    Is_Pinterest: Optional[bool] = None

@dataclass
class NavBomComponent:
    """Model for nav_bom_components table data"""
    Parent_Item_No_: str
    RANK: int
    Metal_Type: Optional[str] = None
    Primary_Gem_Shape: Optional[str] = None
    Primary_Gem_Material_Type: Optional[str] = None
    Primary_Gem_Grade_Clarity: Optional[str] = None
    Stone_DEW__Carats_: Optional[float] = None
    Pieces_Per: Optional[int] = None
    Primary_Gem_Diameter_Length_MM: Optional[float] = None
    Primary_Gem_Width_MM: Optional[float] = None
    Description: Optional[str] = None

@dataclass
class GroupData:
    """Model for grouped product data"""
    group_id: str
    products: List[NavItem]
    components: List[NavBomComponent]
