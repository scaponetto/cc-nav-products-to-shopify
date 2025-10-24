# Shopify Metadata Specification
## Product Attributes for Warranty Database Integration

**Analysis Date**: December 2024  
**Database**: Warranty Database (nav_items & nav_bom_components tables)  
**Total Product Groups Analyzed**: 2,882 unique Web_Product_Group_ID groups

---

## 📊 **Analysis Summary**

### Product Group Distribution
| Product Type | Unique Groups | Avg SKUs per Group | Total SKUs |
|--------------|---------------|-------------------|------------|
| RING | 1,986 | 136.6 | 271,000+ |
| EARRING | 363 | 5.7 | 2,000+ |
| NECKLACE | 348 | 3.8 | 1,300+ |
| BRACELET | 144 | 3.1 | 450+ |
| GEMSTONE | 30 | 30.2 | 900+ |
| SET | 6 | 1.8 | 11 |
| SUPPLIES | 4 | 1.3 | 5 |
| COMPONENT | 1 | 1.0 | 1 |

---

## 🏷️ **RINGS** (1,986 product groups)

### **VARIATION ATTRIBUTES** (Attributes that differ between SKUs within the same Web_Product_Group_ID)
These become **Shopify Product Variants**:

| Attribute | Avg Variations per Group | Variation Type | Shopify Field |
|-----------|-------------------------|----------------|---------------|
| **Ring Size** | 19.6 | Size | `option1` |
| **Metal Type** | 2.5 | Metal | `option2` |
| **Stone Weight (Carats)** | 2.0 | Weight | `option3` |
| **Plating/Coating Type** | 1.8 | Finish | Custom attribute |
| **Stone Dimensions (Length)** | 1.6 | Size | Custom attribute |
| **Stone Dimensions (Width)** | 1.5 | Size | Custom attribute |
| **Clarity Grade** | 1.4 | Quality | Custom attribute |

### **PRODUCT ATTRIBUTES** (Attributes consistent across all SKUs in a group)
These become **Shopify Product Metadata**:

| Attribute | Description | Shopify Field |
|-----------|-------------|---------------|
| **Product Type** | Always "Ring" | `product_type` |
| **Setting Style** | Product_Subgroup_Code | `metafield.setting_style` |
| **Stone Material** | Primary_Gem_Material_Type | `metafield.stone_material` |
| **Stone Shape** | Primary_Gem_Shape | `metafield.stone_shape` |
| **Stone Color** | Primary_Gem_Color | `metafield.stone_color` |
| **Main Setting Type** | Main_Setting_Type | `metafield.main_setting_type` |
| **Collection** | Collection name | `metafield.collection` |
| **Jewelry Brand** | Jewelry_Brand | `metafield.jewelry_brand` |
| **Gemstone Brand** | Gemstone_Brand | `metafield.gemstone_brand` |
| **Style ID** | Style_ID | `metafield.style_id` |
| **Web Descriptor** | Web_Descriptor | `metafield.web_descriptor` |
| **Is Best Seller** | Is_Best_Seller | `metafield.is_best_seller` |
| **Is High ROAS** | Is_High_ROAS | `metafield.is_high_roas` |
| **Is Pinterest** | Is_Pinterest | `metafield.is_pinterest` |

---

## 👂 **EARRINGS** (363 product groups)

### **VARIATION ATTRIBUTES**

| Attribute | Avg Variations per Group | Variation Type | Shopify Field |
|-----------|-------------------------|----------------|---------------|
| **Metal Type** | 2.1 | Metal | `option1` |
| **Stone Weight (Carats)** | 1.9 | Weight | `option2` |
| **Stone Dimensions (Length)** | 1.7 | Size | `option3` |
| **Stone Dimensions (Width)** | 1.7 | Size | Custom attribute |
| **Plating/Coating Type** | 1.7 | Finish | Custom attribute |
| **Clarity Grade** | 1.2 | Quality | Custom attribute |
| **Back Type** | 1.1 | Style | Custom attribute |
| **Ear Nut Type** | 1.1 | Style | Custom attribute |

### **PRODUCT ATTRIBUTES**

| Attribute | Description | Shopify Field |
|-----------|-------------|---------------|
| **Product Type** | Always "Earring" | `product_type` |
| **Setting Style** | Product_Subgroup_Code | `metafield.setting_style` |
| **Stone Material** | Primary_Gem_Material_Type | `metafield.stone_material` |
| **Stone Shape** | Primary_Gem_Shape | `metafield.stone_shape` |
| **Stone Color** | Primary_Gem_Color | `metafield.stone_color` |
| **Main Setting Type** | Main_Setting_Type | `metafield.main_setting_type` |
| **Collection** | Collection name | `metafield.collection` |
| **Jewelry Brand** | Jewelry_Brand | `metafield.jewelry_brand` |
| **Gemstone Brand** | Gemstone_Brand | `metafield.gemstone_brand` |
| **Style ID** | Style_ID | `metafield.style_id` |
| **Web Descriptor** | Web_Descriptor | `metafield.web_descriptor` |
| **Is Best Seller** | Is_Best_Seller | `metafield.is_best_seller` |
| **Is High ROAS** | Is_High_ROAS | `metafield.is_high_roas` |
| **Is Pinterest** | Is_Pinterest | `metafield.is_pinterest` |

---

## 📿 **NECKLACES** (348 product groups)

### **VARIATION ATTRIBUTES**

| Attribute | Avg Variations per Group | Variation Type | Shopify Field |
|-----------|-------------------------|----------------|---------------|
| **Metal Type** | 2.0 | Metal | `option1` |
| **Stone Weight (Carats)** | 1.5 | Weight | `option2` |
| **Plating/Coating Type** | 1.6 | Finish | `option3` |
| **Clasp Type** | 1.0 | Style | Custom attribute |
| **Chain Type** | 1.0 | Style | Custom attribute |
| **Stone Dimensions (Length)** | 1.3 | Size | Custom attribute |
| **Stone Dimensions (Width)** | 1.3 | Size | Custom attribute |
| **Clarity Grade** | 1.1 | Quality | Custom attribute |

### **PRODUCT ATTRIBUTES**

| Attribute | Description | Shopify Field |
|-----------|-------------|---------------|
| **Product Type** | Always "Necklace" | `product_type` |
| **Setting Style** | Product_Subgroup_Code | `metafield.setting_style` |
| **Stone Material** | Primary_Gem_Material_Type | `metafield.stone_material` |
| **Stone Shape** | Primary_Gem_Shape | `metafield.stone_shape` |
| **Stone Color** | Primary_Gem_Color | `metafield.stone_color` |
| **Main Setting Type** | Main_Setting_Type | `metafield.main_setting_type` |
| **Collection** | Collection name | `metafield.collection` |
| **Jewelry Brand** | Jewelry_Brand | `metafield.jewelry_brand` |
| **Gemstone Brand** | Gemstone_Brand | `metafield.gemstone_brand` |
| **Style ID** | Style_ID | `metafield.style_id` |
| **Web Descriptor** | Web_Descriptor | `metafield.web_descriptor` |
| **Is Best Seller** | Is_Best_Seller | `metafield.is_best_seller` |
| **Is High ROAS** | Is_High_ROAS | `metafield.is_high_roas` |
| **Is Pinterest** | Is_Pinterest | `metafield.is_pinterest` |

---

## 💍 **BRACELETS** (144 product groups)

### **VARIATION ATTRIBUTES**

| Attribute | Avg Variations per Group | Variation Type | Shopify Field |
|-----------|-------------------------|----------------|---------------|
| **Metal Type** | 1.7 | Metal | `option1` |
| **Stone Weight (Carats)** | 1.7 | Weight | `option2` |
| **Plating/Coating Type** | 1.4 | Finish | `option3` |
| **Clasp Type** | 1.1 | Style | Custom attribute |
| **Stone Dimensions (Length)** | 1.4 | Size | Custom attribute |
| **Stone Dimensions (Width)** | 1.4 | Size | Custom attribute |
| **Clarity Grade** | 1.1 | Quality | Custom attribute |

### **PRODUCT ATTRIBUTES**

| Attribute | Description | Shopify Field |
|-----------|-------------|---------------|
| **Product Type** | Always "Bracelet" | `product_type` |
| **Setting Style** | Product_Subgroup_Code | `metafield.setting_style` |
| **Stone Material** | Primary_Gem_Material_Type | `metafield.stone_material` |
| **Stone Shape** | Primary_Gem_Shape | `metafield.stone_shape` |
| **Stone Color** | Primary_Gem_Color | `metafield.stone_color` |
| **Main Setting Type** | Main_Setting_Type | `metafield.main_setting_type` |
| **Collection** | Collection name | `metafield.collection` |
| **Jewelry Brand** | Jewelry_Brand | `metafield.jewelry_brand` |
| **Gemstone Brand** | Gemstone_Brand | `metafield.gemstone_brand` |
| **Style ID** | Style_ID | `metafield.style_id` |
| **Web Descriptor** | Web_Descriptor | `metafield.web_descriptor` |
| **Is Best Seller** | Is_Best_Seller | `metafield.is_best_seller` |
| **Is High ROAS** | Is_High_ROAS | `metafield.is_high_roas` |
| **Is Pinterest** | Is_Pinterest | `metafield.is_pinterest` |

---

## 💎 **GEMSTONES** (30 product groups)

### **VARIATION ATTRIBUTES**

| Attribute | Avg Variations per Group | Variation Type | Shopify Field |
|-----------|-------------------------|----------------|---------------|
| **Stone Weight (Carats)** | 12.3 | Weight | `option1` |
| **Stone Dimensions (Length)** | 10.9 | Size | `option2` |
| **Stone Dimensions (Width)** | 10.7 | Size | `option3` |
| **Clarity Grade** | 2.3 | Quality | Custom attribute |

### **PRODUCT ATTRIBUTES**

| Attribute | Description | Shopify Field |
|-----------|-------------|---------------|
| **Product Type** | Always "Gemstone" | `product_type` |
| **Stone Material** | Primary_Gem_Material_Type | `metafield.stone_material` |
| **Stone Shape** | Primary_Gem_Shape | `metafield.stone_shape` |
| **Stone Color** | Primary_Gem_Color | `metafield.stone_color` |
| **Collection** | Collection name | `metafield.collection` |
| **Jewelry Brand** | Jewelry_Brand | `metafield.jewelry_brand` |
| **Gemstone Brand** | Gemstone_Brand | `metafield.gemstone_brand` |
| **Style ID** | Style_ID | `metafield.style_id` |
| **Web Descriptor** | Web_Descriptor | `metafield.web_descriptor` |

---

## 🔧 **Implementation Guidelines**

### **Shopify Product Structure**

1. **Parent Product**: One product per `Web_Product_Group_ID`
   - Contains all **PRODUCT ATTRIBUTES** as metafields
   - Contains product title, description, images

2. **Product Variants**: One variant per unique SKU within the group
   - Contains all **VARIATION ATTRIBUTES** as variant options
   - Contains SKU, price, inventory, weight

### **Metafield Namespace Structure**

```
custom.product_attributes:
  - setting_style
  - stone_material
  - stone_shape
  - stone_color
  - main_setting_type
  - collection
  - jewelry_brand
  - gemstone_brand
  - style_id
  - web_descriptor
  - is_best_seller
  - is_high_roas
  - is_pinterest

custom.variant_attributes:
  - metal_type (combined Metal_Stamp + Metal_Color + Metal_Code)
  - plating_coating_type
  - stone_dimensions_length
  - stone_dimensions_width
  - clarity_grade
  - back_type (earrings)
  - ear_nut_type (earrings)
  - clasp_type (necklaces/bracelets)
  - chain_type (necklaces)
```

### **Variant Option Mapping**

| Product Type | Option 1 | Option 2 | Option 3 |
|--------------|-----------|----------|----------|
| **RINGS** | Ring Size | Metal Type | Stone Weight |
| **EARRINGS** | Metal Type | Stone Weight | Stone Length |
| **NECKLACES** | Metal Type | Stone Weight | Plating Type |
| **BRACELETS** | Metal Type | Stone Weight | Plating Type |
| **GEMSTONES** | Stone Weight | Stone Length | Stone Width |

### **Data Transformation Rules**

## 🏷️ **Product Name Generation**

### **Product Name Format**
```
[total carat weight] [primary gem shape] [primary stone type] [product group] [item category] in [metal type and color]
```

### **Field Mapping**
| Database Field | Product Name Component | Example |
|----------------|------------------------|---------|
| `Stone_Weight__Carats_` | Total carat weight (entire piece) | "1.50 CTW" or "1.50 CTW DEW" |
| `Primary_Gem_Shape` | Primary gem shape | "Round", "Pear", "Cushion" |
| `Primary_Gem_Material_Type` | Primary stone type | "Lab-Grown Diamond", "Moissanite" |
| `Product_Subgroup_Code` | Product group | "Halo", "Solitaire", "Classic" |
| `Item_Category_Code` | Item category | "Ring", "Earring", "Pendant" |
| `Metal_Stamp + Metal_Color + Metal_Code` | Metal type and color | "14K White Gold", "Platinum" |

### **Material Type Conversions**
| Database Value | Product Name Value |
|----------------|-------------------|
| `LGD` | "Lab-Grown Diamond" |
| `MOISSANITE` | "Moissanite" |
| `NAT` | "Natural Diamond" |
| `CZ` | "Cubic Zirconia" |
| `SAPPHIRE` | "Sapphire" |
| `RUBY` | "Ruby" |
| `EMERALD` | "Emerald" |
| `AMETHYST` | "Amethyst" |

### **Carat Weight Unit Rules**
- **Moissanite**: Use "CTW DEW" (e.g., "1.50 CTW DEW")
- **Lab-Grown Diamond**: Use "CTW" (e.g., "1.50 CTW")
- **Natural Diamond**: Use "CTW" (e.g., "1.50 CTW")
- **Other Stones**: Use "CTW" (e.g., "1.50 CTW")

### **Missing Field Handling**
- **Carat Weight**: Skip if `Stone_Weight__Carats_` is 0, null, or empty
- **Gem Shape**: Skip if `Primary_Gem_Shape` is null or empty
- **Stone Type**: Skip if `Primary_Gem_Material_Type` is null or empty
- **Product Group**: Skip if `Product_Subgroup_Code` is null or empty
- **Item Category**: Always include (required)
- **Metal Type**: Always include (required) - preceded by "in"

### **Product Name Examples**
| Database Data | Generated Product Name |
|---------------|----------------------|
| 1.50ct, ROUND, LGD, HALO, RING, 14K WHITE | "1.50 CTW Round Lab-Grown Diamond Halo Ring in 14K White Gold" |
| 0.50ct, PEAR, MOISSANITE, SOLITAIRE, EARRING, 18K YELLOW | "0.50 CTW DEW Pear Moissanite Solitaire Earring in 18K Yellow Gold" |
| 2.80ct, CUSHION, LGD, FASHION, PENDANT, 925 WHITE | "2.80 CTW Cushion Lab-Grown Diamond Fashion Pendant in White Silver" |
| 0ct, ROUND, LGD, CLASSIC, RING, PT950 WHITE | "Round Lab-Grown Diamond Classic Ring in Platinum" |

## 🔗 **Shopify Handle Generation**

### **Handle Format**
```
[product-name-slug]-[web-product-group-id]
```

### **Handle Creation Rules**
1. **Start with Product Name**: Use the generated product name as the base
2. **Convert to Slug**: 
   - Convert to lowercase
   - Replace spaces with hyphens
   - Remove special characters (keep only letters, numbers, and hyphens)
   - **Remove periods** (e.g., "2.80ct" → "280ct")
   - Remove multiple consecutive hyphens
   - Trim leading/trailing hyphens
3. **Add Web_Product_Group_ID**: Append `-[web_product_group_id]` to the end (lowercase)
4. **Length Limit**: Shopify handles have a 255 character limit

### **Handle Examples**
| Product Name | Web_Product_Group_ID | Generated Handle |
|--------------|----------------------|------------------|
| "1.50 CTW Round Lab-Grown Diamond Halo Ring in 14K White Gold" | "LGD-101704" | "150-ctw-round-lab-grown-diamond-halo-ring-in-14k-white-gold-lgd-101704" |
| "0.50 CTW DEW Pear Moissanite Solitaire Earring in 18K Yellow Gold" | "GID-000000" | "050-ctw-dew-pear-moissanite-solitaire-earring-in-18k-yellow-gold-gid-000000" |
| "2.80 CTW Cushion Lab-Grown Diamond Fashion Pendant in White Silver" | "LGD-102496" | "280-ctw-cushion-lab-grown-diamond-fashion-pendant-in-white-silver-lgd-102496" |
| "15.77 CTW Round Lab-Grown Diamond Halo Earring in 14K White Gold" | "LGD-102077" | "1577-ctw-round-lab-grown-diamond-halo-earring-in-14k-white-gold-lgd-102077" |

### **Handle Best Practices**
- **Uniqueness**: Web_Product_Group_ID ensures uniqueness across product groups
- **SEO Friendly**: Descriptive and keyword-rich
- **Readable**: Clear structure with logical word separation
- **Consistent**: Same format across all products
- **Shopify Compatible**: Follows Shopify's handle requirements

---

## 🔧 **Technical Implementation**

1. **Metal Type**: Combine Metal_Stamp + Metal_Color + Base Metal Type based on color variation:
   - **Gold (14K/18K/10K)**: Always include stamp + color + "Gold" (e.g., "14K White Gold", "18K Yellow Gold")
   - **Silver (925)**: Include color + "Silver" only (e.g., "White Silver", "Yellow Silver", "Rose Silver")
   - **Platinum (PT950/PT900)**: Just "Platinum" (98.5% are white, minimal color variation)
   - **Tantalum**: Include color when present (e.g., "Tantalum", "Tantalum Gray", "Tantalum Black")
   - **Titanium**: Include color when present (e.g., "Titanium", "Titanium Two-Tone", "Titanium Black")
   - **Two-tone metals**: "14K Two-Tone Gold", "Silver Two-Tone", "Tantalum Two-Tone"

### **Metal Type Mapping Examples**

| Metal_Code | Metal_Stamp | Metal_Color | Result |
|------------|--------------|--------------|---------|
| 14K | 14K | WHITE | "14K White Gold" |
| 18K | 18K | YELLOW | "18K Yellow Gold" |
| 10K | 10K | ROSE | "10K Rose Gold" |
| 14K | 14K | TWO-TONE | "14K Two-Tone Gold" |
| SILVER | 925 | WHITE | "White Silver" |
| SILVER | 925 | YELLOW | "Yellow Silver" |
| SILVER | 925 | ROSE | "Rose Silver" |
| SILVER | 925 | TWO-TONE | "Silver Two-Tone" |
| PLAT | PT950 | WHITE | "Platinum" |
| PLAT | PT950 | ROSE | "Platinum Rose" |
| TANTALUM | TANTALUM | (empty) | "Tantalum" |
| TANTALUM | TANTALUM | GRAY | "Tantalum Gray" |
| TANTALUM | TANTALUM | BLACK | "Tantalum Black" |
| TANTALUM | TANTALUM | TWO-TONE | "Tantalum Two-Tone" |
| TITANIUM | TI | (empty) | "Titanium" |
| TITANIUM | TI | TWO-TONE | "Titanium Two-Tone" |
| TITANIUM | TI | BLACK | "Titanium Black" |

2. **Stone Weight**: Format as decimal with 2-4 significant figures
3. **Ring Size**: Use as-is (typically 3-13 with half sizes)
4. **Stone Dimensions**: Format as "Length x Width mm" for non-round stones
5. **Clarity Grade**: Use as-is (VS1, F1, F2, etc.)
6. **Setting Style**: Convert Product_Subgroup_Code to descriptive text

### **Special Considerations**

1. **RINGS**: Ring Size is the primary variation (19.6 avg variations)
2. **EARRINGS**: Metal Type and Stone Weight are primary variations
3. **NECKLACES/BRACELETS**: Metal Type and Stone Weight are primary variations
4. **GEMSTONES**: Stone Weight and Dimensions are primary variations
5. **All Types**: Stone Material, Shape, and Setting Style are consistent within groups

---

## 📋 **Summary**

This specification provides a comprehensive mapping of warranty database attributes to Shopify product structure:

- **2,882 unique product groups** identified
- **Primary variation attributes** mapped to Shopify variant options
- **Consistent attributes** mapped to Shopify metafields
- **Product-type specific** attribute categorization
- **Implementation guidelines** for data transformation

The analysis shows that **RINGS** have the most complex variation structure (primarily ring sizes), while **GEMSTONES** have the most weight/dimension variations. All product types share common attributes like stone material, shape, and setting style as consistent product-level metadata.

---

**Report Generated**: December 2024  
**Database Queries**: 8 comprehensive SQL queries executed  
**Analysis Scope**: 2,882 product groups across 8 product categories
