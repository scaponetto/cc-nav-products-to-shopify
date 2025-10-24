"""
Main orchestration class for processing group IDs.
Coordinates database queries, data transformation, and Shopify operations.
"""

from typing import List, Dict, Any, Optional
from src.core.database_manager import DatabaseManager
from src.core.data_transformer import DataTransformer
from src.core.shopify_manager import ShopifyManager
from src.core.image_handler import ImageHandler
from src.utils.error_handler import ErrorHandler
from src.models.product_data import ProcessingResult

class GroupIDProcessor:
    """Main processor for group ID export operations"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.db_manager = DatabaseManager(config, logger)
        self.data_transformer = DataTransformer(config, logger)
        self.shopify_manager = ShopifyManager(config, logger)
        self.image_handler = ImageHandler(config, logger)
        self.error_handler = ErrorHandler(config, logger)
    
    def process_group_ids(self, group_ids: List[str], dry_run: bool = False) -> List[ProcessingResult]:
        """Process a list of group IDs"""
        results = []
        
        for group_id in group_ids:
            try:
                result = self._process_single_group_id(group_id, dry_run)
                results.append(result)
            except Exception as e:
                error_result = ProcessingResult(
                    group_id=group_id,
                    success=False,
                    error_message=str(e)
                )
                results.append(error_result)
                self.logger.error(f"Failed to process {group_id}: {e}")
        
        return results
    
    def process_all_group_ids(self, dry_run: bool = False) -> List[ProcessingResult]:
        """Process all group IDs from the database"""
        group_ids = self.db_manager.get_all_group_ids()
        self.logger.info(f"Found {len(group_ids)} group IDs to process")
        return self.process_group_ids(group_ids, dry_run)
    
    def _process_single_group_id(self, group_id: str, dry_run: bool = False) -> ProcessingResult:
        """Process a single group ID"""
        self.logger.info(f"Processing group ID: {group_id}")
        
        # 1. Query database for group data
        group_data = self.db_manager.get_group_data(group_id)
        if not group_data:
            raise ValueError(f"No data found for group ID: {group_id}")
        
        # 2. Transform data to Shopify format
        shopify_data = self.data_transformer.transform_group_data(group_data)
        
        # 3. Validate transformed data
        validation_errors = self.data_transformer.validate_shopify_data(shopify_data)
        if validation_errors:
            raise ValueError(f"Data validation failed: {validation_errors}")
        
        if dry_run:
            return ProcessingResult(
                group_id=group_id,
                success=True,
                variants_created=len(shopify_data.get('variants', [])),
                metafields_created=len(shopify_data.get('metafields', []))
            )
        
        # 4. Create/update product in Shopify
        shopify_result = self.shopify_manager.create_or_update_product(shopify_data)
        
        return ProcessingResult(
            group_id=group_id,
            success=True,
            product_id=shopify_result.get('product', {}).get('id'),
            variants_created=len(shopify_data.get('variants', [])),
            metafields_created=len(shopify_data.get('metafields', []))
        )
