"""
Main CLI entry point for the product export system.
Handles command-line arguments and orchestrates the export process.
"""

import argparse
import sys
from src.core.group_id_processor import GroupIDProcessor
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description='Export products from warranty DB to Shopify')
    parser.add_argument('group_ids', nargs='*', help='List of group IDs to process')
    parser.add_argument('--all', action='store_true', help='Process all group IDs from database')
    parser.add_argument('--config', default='config/config.yaml', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Validate data without creating products')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(verbose=args.verbose)
    
    # Load configuration
    config = ConfigManager(args.config)
    
    # Initialize processor
    processor = GroupIDProcessor(config, logger)
    
    try:
        if args.all:
            result = processor.process_all_group_ids(dry_run=args.dry_run)
        else:
            if not args.group_ids:
                parser.error("Must provide group IDs or use --all flag")
            result = processor.process_group_ids(args.group_ids, dry_run=args.dry_run)
        
        # Print results
        print_summary(result)
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)

def print_summary(results):
    """Print summary of processing results"""
    print("\n" + "="*50)
    print("PRODUCT EXPORT SUMMARY")
    print("="*50)
    
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"Total processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print(f"\nSuccessful exports:")
        for result in successful:
            print(f"  ✓ {result.group_id} - {result.variants_created} variants, {result.metafields_created} metafields")
    
    if failed:
        print(f"\nFailed exports:")
        for result in failed:
            print(f"  ✗ {result.group_id} - {result.error_message}")
    
    print("="*50)

if __name__ == "__main__":
    main()
