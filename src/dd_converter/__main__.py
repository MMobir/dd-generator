"""Command-line interface for DD converter."""

import argparse
import logging
import sys
from pathlib import Path

from .converter import convert_dd_to_csv, convert_folder_to_csvs
from .exceptions import DDConversionError

def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Convert GAMS DD files to CSV format.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'input',
        help='Input DD file or folder path'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output CSV file or folder path'
    )
    
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Exclude metadata columns from output'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    try:
        input_path = Path(args.input)
        if not input_path.exists():
            raise DDConversionError(f"Input path does not exist: {input_path}")
        
        if input_path.is_file():
            if not input_path.suffix == '.dd':
                raise DDConversionError(f"Input file must be a .dd file: {input_path}")
            
            result = convert_dd_to_csv(
                input_path,
                args.output,
                not args.no_metadata
            )
            print(f"Created CSV file: {result}")
            
        else:  # Directory
            result = convert_folder_to_csvs(
                input_path,
                args.output,
                not args.no_metadata
            )
            print(f"Created CSV files in: {result}")
        
        sys.exit(0)
        
    except DDConversionError as e:
        logging.error(str(e))
        sys.exit(1)
    except Exception as e:
        logging.exception("Unexpected error occurred")
        sys.exit(1)

if __name__ == '__main__':
    main() 