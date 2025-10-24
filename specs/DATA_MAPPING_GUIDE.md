# Product Data Mapping Guide

## Overview

This guide explains how data from the `nav_items` and `nav_bom_components` database tables is transformed into structured product details.

## Database Schema

### Table: `nav_items`
Contains product-level information for each SKU.

**Key Fields:**
- `No_` - SKU/Product ID (Primary Key)
- `Item_Category_Code` - Product type (e.g., RING, EARRING)
- `Product_Subgroup_Code` - Setting style code (e.g., 3STONEPLUS)
- `Metal_Stamp` - Metal purity (e.g., 14K, 18K)
- `Metal_Color` - Metal color (WHITE, YELLOW, ROSE)
- `Stone_Weight__Carats_` - Total carat weight
- `Primary_Gem_Material_Type` - Material (MOISSANITE, LGD, NAT)
- `Primary_Gem_Shape` - Shape (EMERALD, ROUND, etc.)
- `Primary_Gem_Grade_Clarity` - Clarity grade
- `Primary_Gem_Diameter_Length_MM` - Length dimension
- `Primary_Gem_Width_MM` - Width dimension
- `Gemstone_Brand` - Brand (FOREVERONE, etc.)

### Table: `nav_bom_components`
Contains component-level information (stones, metals) for each product.

**Key Fields:**
- `Parent_Item_No_` - Links to nav_items.No_
- `RANK` - Component order (0, 1, 2, ...)
- `Metal_Type` - Component type:
  - `0` = Stones/Gems
  - `1` = Precious metal
  - `2` = Platinum
  - `3` = Sterling silver
  - `13` = Alternative materials
- `Primary_Gem_Shape` - Stone shape
- `Primary_Gem_Grade_Clarity` - Clarity code
- `Primary_Gem_Material_Type` - Material type
- `Stone_DEW__Carats_` - Individual stone weight
- `Pieces_Per` - Stone count
- `Primary_Gem_Diameter_Length_MM` - Length
- `Primary_Gem_Width_MM` - Width
- `Description` - Component description

## Data Flow

### 1. Query Product Data
```sql
SELECT * FROM nav_items WHERE No_ = '1099145';
```

### 2. Query Component Data
```sql
SELECT * FROM nav_bom_components 
WHERE Parent_Item_No_ = '1099145' 
ORDER BY `RANK`;
```

### 3. Separate Components
- **Metal Component**: `Metal_Type = '1'` (RANK typically 0)
- **Main Stone**: First stone component (`Metal_Type = '0'`, lowest RANK)
- **Side Stones**: Remaining stone components (`Metal_Type = '0'`)

## Field Mappings

### Product Type
**Source**: `nav_items.Item_Category_Code`

**Transformation**: Convert to title case
- `RING` → `Ring`
- `EARRING` → `Earring`
- `PENDANT` → `Pendant`

### Setting Style
**Source**: `nav_items.Product_Subgroup_Code`

**Transformation**: Map code to descriptive text
- `3STONEPLUS` → `Three-Stone, Hidden Detail, Side-Stone`
- (Additional mappings needed for other codes)

### Metal Type
**Sources**: 
- `nav_items.Metal_Stamp` + `Metal_Color`
- OR `nav_bom_components.Metal_Stamp` + `Metal_Color` (where `Metal_Type = '1'`)

**Transformation**: Combine stamp + color + "Gold"
```
Metal_Stamp: "14K"
Metal_Color: "WHITE"
→ "14K White Gold"
```

**Color Mapping**:
- `WHITE` → `White`
- `YELLOW` → `Yellow`
- `ROSE` → `Rose`

### Total Carat Weight
**Source**: Sum of all stone components

**Calculation**:
```
Total CTW = SUM(Stone_DEW__Carats_ × Pieces_Per) for all Metal_Type = '0'
```

**Format**: `{total}CTW` (e.g., `3.87CTW`)

### Stone Origin (Material Type)
**Source**: `Primary_Gem_Material_Type`

**Mapping**:
- `MOISSANITE` → `Forever One™ Moissanite`
- `LGD` → `Caydia® Lab-Grown Diamond`
- `NAT` → `Natural Diamond`

### Cut Grade
**Source**: `Primary_Gem_Cut`

**Mapping**:
- `5` or `EXCELLENT` → `Excellent`
- `4` or `VERY GOOD` → `Very Good`
- `3` or `GOOD` → `Good`
- `2` or `FAIR` → `Fair`
- `1` or `POOR` → `Poor`
- `0` or empty → `Excellent` (default for moissanite)

### Clarity Grade
**Source**: `Primary_Gem_Grade_Clarity`

**Mapping**:
- `F2` → `IF to VS1`
- `VS1` → `IF to VS1`
- `VS2` → `VS1 to VS2`
- `SI1` → `VS2 to SI1`
- `SI2` → `SI1 to SI2`
- `MEL` → `IF to VS1` (melee stones)

### Color Grade
**Source**: `Primary_Gem_Grade_Clarity` (clarity code often encodes color)

**Mapping**:
- `F2` → `GH`
- `MEL` → `F or better` (melee stones)
- Other codes → Use as-is

### Stone Shape
**Source**: `Primary_Gem_Shape`

**Mapping**: Convert to proper case
- `EMERALD` → `Emerald`
- `HALFMOON` → `Half Moon`
- `ROUND` → `Round`
- `OVAL` → `Oval`
- `CUSHION` → `Cushion`
- `PEAR` → `Pear`
- `MARQUISE` → `Marquise`
- `PRINCESS` → `Princess`
- `RADIANT` → `Radiant`

### Stone Cut (Cut Type)
**Source**: Inferred from `Primary_Gem_Shape`

**Mapping**:
- `EMERALD` → `Step`
- `HALFMOON` → `Brilliant`
- `ROUND` → `Modified Brilliant`
- Others → `Brilliant`

### Stone Count
**Source**: `Pieces_Per`

**Format**: Direct integer value

### Individual Carat Weight
**Source**: `Stone_DEW__Carats_`

**Format**: `{weight} Ct. DEW` with 2-4 significant figures
- Example: `0.36 Ct. DEW`, `0.0225 Ct. DEW`

**Note**: Only shown for side stones with count > 1

### Total Carat Weight (per stone type)
**Calculation**: `Stone_DEW__Carats_ × Pieces_Per`

**Format**: `{total} Ct. Tw. DEW` (Tw. = Total weight)
- Example: `2.52 Ct. Tw. DEW`, `0.72 Ct. Tw. DEW`

### Stone Dimensions
**Sources**: 
- `Primary_Gem_Diameter_Length_MM`
- `Primary_Gem_Width_MM`

**Format**:
- Round stones: `{length}mm` (e.g., `1.8mm`)
- Other shapes: `{length} x {width}mm` (e.g., `9.0 x 7.0mm`)

## Example: SKU 1099145

### Database Query Results

**nav_items (1099145)**:
```
Item_Category_Code: RING
Product_Subgroup_Code: 3STONEPLUS
Metal_Stamp: 14K
Metal_Color: WHITE
Primary_Gem_Material_Type: MOISSANITE
Stone_Weight__Carats_: 3.86880
```

**nav_bom_components (Parent_Item_No_ = 1099145)**:

| RANK | Metal_Type | Shape | Material | Pieces_Per | Stone_DEW | Length | Width |
|------|------------|-------|----------|------------|-----------|--------|-------|
| 0 | 1 | - | - | - | - | - | - |
| 1 | 0 | EMERALD | MOISSANITE | 1 | 2.52 | 9 | 7 |
| 2 | 0 | HALFMOON | MOISSANITE | 2 | 0.36 | 5.5 | 3.5 |
| 3 | 0 | ROUND | MOISSANITE | 14 | 0.0225 | 1.8 | 1.8 |
| 4 | 0 | ROUND | MOISSANITE | 20 | 0.01 | 1.3 | 1.3 |
| 5 | 0 | ROUND | MOISSANITE | 14 | 0.0067 | 1.1 | 1.1 |
| 6 | 0 | ROUND | MOISSANITE | 4 | 0.005 | 1.0 | 1.0 |

### Transformation Logic

1. **Identify Components**:
   - Metal: RANK 0 (Metal_Type = 1)
   - Main stone: RANK 1 (first stone with Metal_Type = 0)
   - Side stones: RANK 2-6 (remaining stones)

2. **Calculate Total CTW**:
   ```
   = (1 × 2.52) + (2 × 0.36) + (14 × 0.0225) + (20 × 0.01) + (14 × 0.0067) + (4 × 0.005)
   = 2.52 + 0.72 + 0.315 + 0.20 + 0.0938 + 0.02
   = 3.87 CTW
   ```

3. **Format Each Stone**:
   - Main stone (RANK 1): Emerald, 2.52 ct, 1 piece
   - Side stones (RANK 2-6): Various rounds and half moons

### Generated Output

```
product type: Ring
setting style: Three-Stone, Hidden Detail, Side-Stone
metal type: 14K White Gold
total carat weight: 3.87CTW

main stone:
  origin: Forever One™ Moissanite
  cut grade: Excellent
  clarity grade: IF to VS1
  stone shape: Emerald
  stone cut: Step
  color grade: GH
  stone count: 1
  carat weight: 2.52 Ct. Tw. DEW
  stone dimensions: 9.0 x 7.0mm

side stone:
  origin: Forever One™ Moissanite
  cut grade: Excellent
  clarity grade: IF to VS1
  stone shape: Half Moon
  stone cut: Brilliant
  color grade: GH
  stone count: 2
  individual carat weight: 0.36 Ct. DEW
  carat weight: 0.72 Ct. Tw. DEW
  stone dimensions: 5.5 x 3.5mm

[... additional side stones ...]
```

## Implementation Files

### 1. `product_data_mapper.py`
Full-featured Python class with database connectivity. Requires `mysql-connector-python`.

**Usage**:
```python
from product_data_mapper import ProductDataMapper

db_config = {
    'host': 'localhost',
    'port': 3307,
    'user': 'username',
    'password': 'password',
    'database': 'warranty'
}

mapper = ProductDataMapper(db_config)
output = mapper.generate_output('1099145')
print(output)
```

### 2. `generate_product_details.py`
Standalone formatter with hardcoded data. No database connection required.

**Usage**:
```bash
python3 generate_product_details.py
```

### 3. `product_query.sql`
SQL queries for manual data extraction and analysis.

**Usage**:
```bash
mysql -h localhost -P 3307 -u username -p warranty < product_query.sql
```

## Extending the Solution

### Adding New Material Types
Update the `MATERIAL_TYPE_MAP` dictionary:
```python
MATERIAL_TYPE_MAP = {
    'MOISSANITE': 'Forever One™ Moissanite',
    'LGD': 'Caydia® Lab-Grown Diamond',
    'NAT': 'Natural Diamond',
    'NEW_TYPE': 'New Material Name',
}
```

### Adding New Setting Styles
Add conditions in the setting style logic:
```python
if subgroup == '3STONEPLUS':
    output.append("setting style: Three-Stone, Hidden Detail, Side-Stone")
elif subgroup == 'SOLITAIRE':
    output.append("setting style: Solitaire")
```

### Adding Additional Fields
If the database has additional fields (band width, setting height), add them:
```python
if product.get('Band_Width_MM'):
    output.append(f"average band width: {product['Band_Width_MM']}mm")
```

## SQL Query for Multiple SKUs

To generate data for multiple products:

```sql
SELECT 
    p.No_ AS sku,
    CONCAT(p.Metal_Stamp, ' ', p.Metal_Color, ' Gold') AS metal_type,
    ROUND(SUM(c.Stone_DEW__Carats_ * c.Pieces_Per), 2) AS total_ctw,
    COUNT(CASE WHEN c.Metal_Type = '0' THEN 1 END) AS stone_count
FROM nav_items p
LEFT JOIN nav_bom_components c ON p.No_ = c.Parent_Item_No_
WHERE p.No_ IN ('1099145', '1099146', '1099147')
GROUP BY p.No_;
```

## Notes

1. **RANK = 0**: Usually the metal component, not a stone
2. **RANK = 1**: Typically the main/center stone
3. **RANK > 1**: Side stones, accent stones, or additional details
4. **Metal_Type = '0'**: Identifies stone components
5. **Clarity codes**: F2 and MEL are custom codes in this database
6. **Dimensions**: Round stones only use length, other shapes use length × width

## Testing

Run the demo script to verify output:
```bash
python3 generate_product_details.py
```

Expected output should match the target format exactly.

