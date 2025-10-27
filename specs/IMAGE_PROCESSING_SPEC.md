# Image Processing & Upload Specification

## 📋 **Overview**

This specification outlines the implementation for fetching product images from AWS S3 and uploading them to Shopify products with proper variant associations. The solution is designed for maximum efficiency with intelligent caching, deduplication, and error recovery.

---

## 🎯 **Objectives**

1. Fetch product images from AWS S3 based on `Image_SKU` values
2. Upload images to Shopify at the product level
3. Associate images with appropriate product variants
4. Handle duplicate Image_SKUs efficiently (multiple variants sharing same images)
5. Support incremental updates (skip existing images on re-run)
6. Provide comprehensive error logging for troubleshooting

---

## 📊 **Data Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMAGE PROCESSING WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

1. Fetch Product Group Data
   ↓
2. Extract Unique Image_SKUs from all variants
   ↓
3. Batch Fetch Images from S3 (parallel)
   ↓
4. Filter & Sort Images (size, naming, variation number)
   ↓
5. Create Product in Shopify with Images (atomic operation)
   ↓
6. Associate Images to Variants
   ↓
7. Log Errors (missing images, upload failures)
```

---

## 🗄️ **Database Schema**

### **nav_items Table**
- **Image_SKU** (varchar): The SKU used to locate images in S3
  - Example: `"827749"`, `"1102192"`
  - Multiple product variants may share the same Image_SKU
  - Used to construct S3 directory path

---

## 🪣 **AWS S3 Structure**

### **Bucket Configuration**
- **Bucket Name**: `production-charlesandcolvard-moissanite2-media-import`
- **Base Directory**: `sorted-media/`

### **Directory Structure**
Images are organized in a nested structure based on Image_SKU:
```
sorted-media/
  ├── [AA]/
  │   ├── [BB]/
  │   │   ├── [CC]/
  │   │   │   ├── [Image_SKU]-1a-[random].[ext]
  │   │   │   ├── [Image_SKU]-2a-[random].[ext]
  │   │   │   ├── [Image_SKU]-3a-[random].[ext]
  │   │   │   └── ...
```

### **Path Construction**
For a given Image_SKU, extract the first 6 characters (or entire SKU if < 6) and split into 2-character segments:

**Example 1: Image_SKU = "827749"**
```
Characters: 8 2 7 7 4 9
Split:      82 / 77 / 49
Path:       sorted-media/82/77/49/
```

**Example 2: Image_SKU = "1102192"**
```
Characters: 1 1 0 2 1 9
Split:      11 / 02 / 19
Path:       sorted-media/11/02/19/
```

### **File Naming Convention**
```
[Image_SKU]-[VariationNumber]-[RandomNumbers].[Extension]

Components:
- Image_SKU: Exact match required (e.g., "827749", "1102192")
- VariationNumber: "1a", "2a", "3a", etc. (only "a" suffix accepted)
- RandomNumbers: Any numeric string
- Extension: .jpg, .jpeg, .png, .gif, .webp, etc.

Valid Examples:
✅ 827749-1a-12345.jpg
✅ 1102192-2a-67890.png
✅ 1102192-10a-54321.jpg

Invalid Examples (to be ignored):
❌ 827749-1b-12345.jpg        (suffix is "b", not "a")
❌ 1102193-1a-12345.jpg        (Image_SKU doesn't match "1102192")
❌ 827749-thumbnail.jpg        (doesn't match naming pattern)
❌ 827749-1a-12345.txt         (not an image file)
```

---

## 🔍 **Image Filtering Rules**

### **1. File Type Filtering**
- **Accept**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- **Reject**: All non-image files (`.txt`, `.pdf`, `.zip`, etc.)

### **2. Size Filtering**
- **Minimum Size**: 200x200 pixels
- **Action**: Download image metadata, check dimensions, skip if < 200x200

### **3. Naming Pattern Filtering**
- **Required Pattern**: `[Image_SKU]-[Number]a-[Random].[ext]`
- **Variation Suffix**: Must be "a" (e.g., "1a", "2a", "3a")
- **Reject**: "b", "c", or any other suffix variations

### **4. Image_SKU Exact Match**
- **Critical**: Only match files where filename starts with exact Image_SKU
- **Example**: For Image_SKU "1102192", reject "1102193-1a-12345.jpg"

---

## 📤 **Image Processing Logic**

### **Step 1: Extract Unique Image_SKUs**
```python
def collect_image_skus(products: List[NavItem]) -> Dict[str, List[str]]:
    """
    Collect unique Image_SKUs and map them to product variant SKUs.
    
    Returns:
        {
            "827749": ["827748", "827753"],  # Multiple variants share this Image_SKU
            "692978": ["692968", "692976"],
            "799057": ["800761"]
        }
    """
```

**Logic**:
1. Iterate through all product variants in the group
2. Extract `Image_SKU` for each variant
3. Create mapping: `Image_SKU → [Product SKUs]`
4. Deduplicate to avoid fetching same images multiple times

---

### **Step 2: Construct S3 Paths**
```python
def construct_s3_path(image_sku: str) -> str:
    """
    Construct S3 directory path from Image_SKU.
    
    Args:
        image_sku: e.g., "827749" or "1102192"
    
    Returns:
        e.g., "sorted-media/82/77/49/" or "sorted-media/11/02/19/"
    """
    # Take first 6 characters (or entire SKU if shorter)
    sku_prefix = image_sku[:6] if len(image_sku) >= 6 else image_sku
    
    # Pad to 6 characters if needed
    sku_prefix = sku_prefix.ljust(6, '0')
    
    # Split into 2-character segments
    segment1 = sku_prefix[0:2]
    segment2 = sku_prefix[2:4]
    segment3 = sku_prefix[4:6]
    
    return f"sorted-media/{segment1}/{segment2}/{segment3}/"
```

---

### **Step 3: Fetch Images from S3**
```python
def fetch_images_for_sku(image_sku: str, s3_client) -> List[Dict]:
    """
    Fetch all valid images for a given Image_SKU from S3.
    
    Returns:
        [
            {
                "image_sku": "827749",
                "variation_number": 1,
                "s3_key": "sorted-media/82/77/49/827749-1a-12345.jpg",
                "url": "https://s3.amazonaws.com/...",
                "width": 1200,
                "height": 1200
            },
            ...
        ]
    """
    # 1. Construct S3 path
    # 2. List all objects in directory
    # 3. Filter by naming pattern
    # 4. Download metadata to check dimensions
    # 5. Sort by variation number
    # 6. Return structured image data
```

**Optimization Strategies**:
1. **Batch Requests**: Use `list_objects_v2` with pagination
2. **Parallel Processing**: Fetch multiple Image_SKUs concurrently
3. **Metadata Only**: Use `head_object` to check dimensions without downloading full image
4. **Caching**: Cache results within a single product group processing run

---

### **Step 4: Sort Images by Variation Number**
```python
def sort_images_by_variation(images: List[Dict]) -> List[Dict]:
    """
    Sort images by variation number (1a, 2a, 3a, ..., 10a).
    
    The first image (1a) will be the primary/featured image.
    """
    return sorted(images, key=lambda x: x['variation_number'])
```

---

## 🔄 **Shopify Integration**

### **Image Upload Strategy**
Use the `productSet` mutation to upload images atomically with product creation.

#### **GraphQL Mutation Structure**
```graphql
mutation productSet($input: ProductSetInput!) {
    productSet(input: $input) {
        product {
            id
            title
            media(first: 50) {
                nodes {
                    ... on MediaImage {
                        id
                        image {
                            url
                            altText
                        }
                    }
                }
            }
            variants(first: 100) {
                nodes {
                    id
                    sku
                    image {
                        id
                        url
                    }
                }
            }
        }
        userErrors {
            field
            message
        }
    }
}
```

#### **Input Structure**
```json
{
    "input": {
        "title": "Product Title",
        "variants": [...],
        "productOptions": [...],
        "media": [
            {
                "originalSource": "https://s3.amazonaws.com/.../827749-1a-12345.jpg",
                "alt": "827749 - Image 1",
                "mediaContentType": "IMAGE"
            },
            {
                "originalSource": "https://s3.amazonaws.com/.../827749-2a-67890.jpg",
                "alt": "827749 - Image 2",
                "mediaContentType": "IMAGE"
            }
        ]
    }
}
```

---

### **Variant-Image Association**

After product creation, associate images with specific variants using the `productVariantUpdate` mutation.

#### **GraphQL Mutation**
```graphql
mutation productVariantUpdate($input: ProductVariantInput!) {
    productVariantUpdate(input: $input) {
        productVariant {
            id
            image {
                id
                url
            }
        }
        userErrors {
            field
            message
        }
    }
}
```

#### **Association Logic**
```python
def associate_images_to_variants(product_id: str, variants: List[Dict], image_sku_mapping: Dict):
    """
    Associate images to variants based on Image_SKU.
    
    Logic:
    1. For each variant, get its Image_SKU
    2. Find the primary image (variation 1a) for that Image_SKU
    3. Associate the primary image to the variant
    
    Args:
        product_id: Shopify product GID
        variants: List of variant data with SKU and Image_SKU
        image_sku_mapping: Map of Image_SKU to media IDs in Shopify
    """
```

---

## 🔁 **Incremental Updates (Re-run Support)**

When re-running a product group to fix image issues:

### **Check for Existing Images**
```python
def get_existing_product_images(product_id: str) -> Set[str]:
    """
    Query Shopify product to get existing image URLs.
    
    Returns:
        Set of S3 URLs that are already uploaded
    """
```

### **Skip Already-Uploaded Images**
```python
def filter_new_images(s3_images: List[Dict], existing_urls: Set[str]) -> List[Dict]:
    """
    Filter out images that are already uploaded to Shopify.
    
    Returns:
        Only images that need to be uploaded
    """
```

### **Update Flow for Re-runs**
```
1. Query existing product by handle or SKU
2. Fetch existing media/images
3. Compare S3 images with existing images
4. Upload only new/missing images
5. Re-associate images to variants if needed
```

---

## 🔐 **AWS Configuration**

### **Development/Testing Credentials (Hardcoded)**
```yaml
aws:
  access_key_id: "YOUR_AWS_ACCESS_KEY_ID"
  secret_access_key: "YOUR_AWS_SECRET_ACCESS_KEY"
  session_token: "YOUR_AWS_SESSION_TOKEN"
  region: "us-east-1"
  bucket: "production-charlesandcolvard-moissanite2-media-import"
```

**Note**: Actual development credentials will be provided separately and should be added to `config/test_config.yaml` (which is in `.gitignore`).

### **Production Configuration (Environment Variables)**
```bash
# .env file
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_SESSION_TOKEN=your_token_here
AWS_REGION=us-east-1
AWS_S3_BUCKET=production-charlesandcolvard-moissanite2-media-import
```

### **Python Library**
Use `boto3` (AWS SDK for Python):
```bash
pip install boto3
```

---

## 📝 **Error Logging**

### **Missing Images Log**
Create a dedicated log file for products/variants with missing images:

**File**: `logs/missing_images_YYYYMMDD_HHMMSS.log`

**Format**:
```
[2025-10-27 14:23:45] Product Group: LGD-101792 | Product SKU: 800761 | Image SKU: 799057 | Error: No images found in S3
[2025-10-27 14:24:12] Product Group: GID-100288 | Product SKU: 498111 | Image SKU: 498100 | Error: No images matching pattern [Image_SKU]-*a-*
```

**Fields to Log**:
- Timestamp
- Product Group ID (Web_Product_Group_ID)
- Product SKU (No_)
- Image SKU (Image_SKU)
- S3 Path searched
- Error description

---

### **Upload Failure Log**
**File**: `logs/image_upload_failures_YYYYMMDD_HHMMSS.log`

**Format**:
```
[2025-10-27 14:25:33] Product: gid://shopify/Product/123456 | Image: 827749-1a-12345.jpg | Error: HTTP 500 - Internal Server Error
[2025-10-27 14:26:01] Product: gid://shopify/Product/123457 | Image: 692978-2a-67890.jpg | Error: Image dimensions too large (exceeded Shopify limit)
```

**Fields to Log**:
- Timestamp
- Shopify Product ID
- Image filename
- S3 URL
- Error details

---

## 🏗️ **Implementation Architecture**

### **Module Structure**
```
src/
├── core/
│   ├── image_handler.py         # Main image processing logic
│   ├── s3_client.py             # AWS S3 interaction wrapper
│   └── image_uploader.py        # Shopify image upload logic
├── utils/
│   ├── image_validator.py       # Image filtering & validation
│   └── image_logger.py          # Specialized logging for images
└── models/
    └── image_data.py            # Image data structures
```

---

### **Class Structure**

#### **1. S3Client**
```python
class S3Client:
    """Handles all AWS S3 interactions"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.s3_client = boto3.client('s3', ...)
    
    def construct_s3_path(self, image_sku: str) -> str:
        """Build S3 directory path from Image_SKU"""
    
    def list_images_in_directory(self, s3_path: str) -> List[str]:
        """List all files in S3 directory"""
    
    def get_image_metadata(self, s3_key: str) -> Dict:
        """Get image dimensions without downloading"""
    
    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate temporary URL for Shopify upload"""
```

#### **2. ImageValidator**
```python
class ImageValidator:
    """Validates and filters images based on rules"""
    
    def validate_filename(self, filename: str, image_sku: str) -> bool:
        """Check if filename matches required pattern"""
    
    def extract_variation_number(self, filename: str) -> Optional[int]:
        """Extract variation number from filename (e.g., "2a" → 2)"""
    
    def validate_dimensions(self, width: int, height: int) -> bool:
        """Check if image meets minimum size requirements"""
    
    def is_valid_image_type(self, filename: str) -> bool:
        """Check if file extension is a valid image type"""
```

#### **3. ImageHandler (Enhanced)**
```python
class ImageHandler:
    """Main orchestrator for image processing"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.s3_client = S3Client(config, logger)
        self.validator = ImageValidator()
        self.image_logger = ImageLogger()
    
    def collect_image_skus(self, products: List[NavItem]) -> Dict[str, List[str]]:
        """Extract unique Image_SKUs and variant mapping"""
    
    def fetch_images_for_group(self, image_sku_mapping: Dict) -> Dict[str, List[ImageData]]:
        """Batch fetch all images for product group"""
    
    def process_product_images(self, product_data: Dict, image_data: Dict) -> List[Dict]:
        """Prepare images for Shopify upload"""
    
    def get_existing_product_images(self, product_id: str) -> Set[str]:
        """Query Shopify for existing images (for re-runs)"""
```

#### **4. ImageUploader**
```python
class ImageUploader:
    """Handles Shopify image upload operations"""
    
    def __init__(self, shopify_manager, logger):
        self.shopify_manager = shopify_manager
        self.logger = logger
    
    def upload_images_with_product(self, product_data: Dict, images: List[Dict]) -> Dict:
        """Upload images as part of productSet mutation"""
    
    def associate_images_to_variants(self, product_id: str, variants: List[Dict], image_mapping: Dict):
        """Link images to specific variants"""
    
    def upload_missing_images(self, product_id: str, new_images: List[Dict]):
        """Upload only new images (for re-runs)"""
```

---

## 🔄 **Integration with Existing Workflow**

### **Modified DataTransformer Flow**
```python
def transform_group_data(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced to include image processing"""
    
    # 1. Existing product/variant transformation
    shopify_product = self.product_mapper.map_product(...)
    shopify_product['variants'] = self._create_and_sort_variants(...)
    shopify_product['productOptions'] = self._create_product_options(...)
    shopify_product['metafields'] = self.metadata_mapper.map_metafields(...)
    
    # 2. NEW: Image processing
    image_sku_mapping = self.image_handler.collect_image_skus(products)
    image_data = self.image_handler.fetch_images_for_group(image_sku_mapping)
    shopify_product['media'] = self.image_handler.process_product_images(
        shopify_product, image_data
    )
    
    # 3. Store image-to-variant mapping for later association
    shopify_product['_image_variant_mapping'] = self._create_image_variant_mapping(
        variants, image_data
    )
    
    return shopify_product
```

### **Modified ShopifyManager Flow**
```python
def create_or_update_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced to handle images"""
    
    # 1. Create product with images (atomic operation)
    result = self._execute_product_set_with_images(product_data)
    
    if result.get('product'):
        product_id = result['product']['id']
        
        # 2. Publish to Online Store
        self._publish_to_online_store(product_id)
        
        # 3. Associate images to variants
        if '_image_variant_mapping' in product_data:
            self.image_uploader.associate_images_to_variants(
                product_id,
                result['product']['variants']['nodes'],
                product_data['_image_variant_mapping']
            )
    
    return result
```

---

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
# Test S3 path construction
def test_construct_s3_path():
    assert construct_s3_path("827749") == "sorted-media/82/77/49/"
    assert construct_s3_path("1102192") == "sorted-media/11/02/19/"
    assert construct_s3_path("123") == "sorted-media/12/30/00/"

# Test filename validation
def test_validate_filename():
    assert validate_filename("827749-1a-12345.jpg", "827749") == True
    assert validate_filename("827749-1b-12345.jpg", "827749") == False
    assert validate_filename("1102193-1a-12345.jpg", "1102192") == False

# Test variation number extraction
def test_extract_variation_number():
    assert extract_variation_number("827749-1a-12345.jpg") == 1
    assert extract_variation_number("827749-10a-12345.jpg") == 10
    assert extract_variation_number("827749-1b-12345.jpg") == None
```

### **Integration Tests**
```python
# Test with actual test group IDs
def test_image_processing_for_test_groups():
    groups = ["LGD-101792", "GID-100288", "LGD-100040"]
    for group_id in groups:
        # 1. Fetch images from S3
        # 2. Validate filtering logic
        # 3. Verify image count and ordering
        # 4. Check error logging for missing images
```

---

## 📊 **Performance Optimization**

### **1. Caching Strategy**
```python
class ImageCache:
    """Cache S3 responses within a processing run"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, image_sku: str) -> Optional[List[ImageData]]:
        """Get cached images for Image_SKU"""
    
    def set(self, image_sku: str, images: List[ImageData]):
        """Cache images for Image_SKU"""
```

### **2. Parallel Processing**
```python
def fetch_images_parallel(image_skus: List[str]) -> Dict[str, List[ImageData]]:
    """Fetch images for multiple SKUs concurrently"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_images_for_sku, sku): sku 
            for sku in image_skus
        }
        results = {}
        for future in concurrent.futures.as_completed(futures):
            sku = futures[future]
            results[sku] = future.result()
        return results
```

### **3. Batch S3 Operations**
- Use `list_objects_v2` with pagination for directory listing
- Use `head_object` for metadata (faster than downloading)
- Request multiple objects in parallel with ThreadPoolExecutor

### **4. Minimize Shopify API Calls**
- Upload all images in single `productSet` mutation
- Batch variant-image associations where possible
- Use bulk operations for large product sets

---

## 🎯 **Success Criteria**

1. ✅ Images successfully fetched from S3 for all variants
2. ✅ Images uploaded to Shopify at product level
3. ✅ Images correctly associated with variants
4. ✅ Image ordering matches variation numbers (1a → 1st, 2a → 2nd, etc.)
5. ✅ Primary image (1a) set as featured image
6. ✅ Duplicate Image_SKUs handled efficiently (no redundant S3 calls)
7. ✅ Missing images logged with complete context
8. ✅ Re-runs skip existing images (incremental update support)
9. ✅ Processing time < 5 seconds per Image_SKU on average
10. ✅ Error recovery allows product creation even if images fail

---

## 📈 **Monitoring & Metrics**

Track the following metrics:
- **S3 API calls per product group**
- **Images fetched vs. images uploaded**
- **Image upload success rate**
- **Average processing time per Image_SKU**
- **Cache hit rate**
- **Missing image occurrences**

---

## 🚀 **Future Enhancements**

1. **Image CDN**: Optionally proxy images through Shopify CDN
2. **Image Optimization**: Resize/compress images before upload
3. **Lazy Loading**: Upload images asynchronously after product creation
4. **Image Variants**: Support multiple image variations (thumbnail, medium, large)
5. **Video Support**: Extend to handle product videos from S3
6. **Bulk Image Update**: Separate script to update images for existing products

---

## 📚 **Dependencies**

### **New Python Packages**
```txt
# AWS SDK
boto3>=1.28.0
botocore>=1.31.0

# Image processing (for dimension validation)
Pillow>=10.0.0

# Async operations (optional, for performance)
aiohttp>=3.8.0
aioboto3>=11.0.0
```

### **Updated requirements.txt**
```txt
# Existing dependencies
requests>=2.31.0
PyYAML>=6.0
mysql-connector-python>=8.0.33
shopify-python-api>=1.0.1
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
click>=8.1.0
rich>=13.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
structlog>=23.0.0

# NEW: Image processing dependencies
boto3>=1.28.0
botocore>=1.31.0
Pillow>=10.0.0
```

---

## 🔒 **Security Considerations**

1. **AWS Credentials**: Never commit credentials to version control
2. **S3 Presigned URLs**: Use short expiration times (1 hour max)
3. **Image Validation**: Verify file types before upload to prevent malicious files
4. **Rate Limiting**: Respect AWS S3 and Shopify API rate limits
5. **Error Sanitization**: Don't log sensitive data (credentials, tokens)

---

## ✅ **Implementation Checklist**

- [ ] Create `S3Client` class for AWS interactions
- [ ] Create `ImageValidator` class for filtering logic
- [ ] Enhance `ImageHandler` with S3 fetch logic
- [ ] Create `ImageUploader` class for Shopify operations
- [ ] Add image processing to `DataTransformer`
- [ ] Update `ShopifyManager` to handle images
- [ ] Implement image-to-variant association
- [ ] Add specialized image logging
- [ ] Create incremental update support (re-run detection)
- [ ] Add AWS configuration to `config.yaml` and `.env.example`
- [ ] Update `requirements.txt` with new dependencies
- [ ] Write unit tests for image validation logic
- [ ] Write integration tests with test group IDs
- [ ] Test re-run scenario (skip existing images)
- [ ] Performance testing with large product groups
- [ ] Documentation updates

---

## 📝 **Example Usage**

### **Command Line**
```bash
# Process group with images
python3 -m src.main --group-ids LGD-101792 GID-100288 --include-images

# Re-run to add missing images (skip existing)
python3 -m src.main --group-ids LGD-101792 --include-images --incremental

# Process all groups with images
python3 -m src.main --all --include-images
```

### **Programmatic Usage**
```python
from src.core.image_handler import ImageHandler
from src.core.database_manager import DatabaseManager

# Initialize
db_manager = DatabaseManager(config, logger)
image_handler = ImageHandler(config, logger)

# Fetch product data
group_data = db_manager.get_group_data("LGD-101792")

# Process images
image_sku_mapping = image_handler.collect_image_skus(group_data['products'])
image_data = image_handler.fetch_images_for_group(image_sku_mapping)

# Result: Dictionary mapping Image_SKU to sorted image list
# {
#   "799057": [
#     ImageData(variation=1, url="...", width=1200, height=1200),
#     ImageData(variation=2, url="...", width=1200, height=1200)
#   ]
# }
```

---

## 🎓 **Summary**

This specification provides a comprehensive, production-ready approach to:

1. **Efficiently fetch images** from AWS S3 with intelligent caching
2. **Filter and validate** images based on strict naming and size requirements
3. **Upload images atomically** with product creation in Shopify
4. **Associate images** to the correct product variants
5. **Handle re-runs gracefully** by skipping existing images
6. **Log errors comprehensively** for troubleshooting
7. **Optimize performance** with parallel processing and caching

The inline processing approach ensures products are created with images in a single atomic operation, providing the best user experience and operational efficiency.

