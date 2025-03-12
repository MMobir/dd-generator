"""DD to CSV converter module."""

import os
import logging
from pathlib import Path
from typing import Optional, Union, Dict
import pandas as pd

from .parser import DDParser
from .exceptions import DDFileError, DDConversionError

# Configure logging
logger = logging.getLogger(__name__)

def convert_dd_to_csv(
    dd_file_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    include_metadata: bool = True
) -> Path:
    """Convert a DD file to CSV format.
    
    Args:
        dd_file_path: Path to the DD file.
        output_path: Optional path for the output CSV file.
        include_metadata: Whether to include metadata columns in output.
        
    Returns:
        Path to the generated CSV file.
        
    Raises:
        DDFileError: If the input file doesn't exist or can't be read.
        DDConversionError: If there's an error during conversion.
    """
    dd_file_path = Path(dd_file_path)
    if not dd_file_path.exists():
        raise DDFileError(f"DD file not found: {dd_file_path}")
        
    try:
        # Determine output path
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = dd_file_path.with_suffix('.csv')
            
        # Read and parse DD file
        with open(dd_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parser = DDParser()
        dataframes = parser.parse(content)
        
        if not dataframes:
            raise DDConversionError(f"No data found in DD file: {dd_file_path}")
            
        # Combine all DataFrames
        combined_df = pd.concat(dataframes.values(), ignore_index=True)
        
        # Handle metadata columns
        if not include_metadata:
            combined_df = combined_df.drop(columns=['table_type'])
            
        # Save to CSV
        combined_df.to_csv(output_path, index=False)
        logger.info(f"Successfully converted {dd_file_path} to {output_path}")
        
        return output_path
        
    except DDFileError:
        raise
    except Exception as e:
        raise DDConversionError(f"Error converting DD file: {str(e)}") from e

def convert_folder_to_csvs(
    input_folder: Union[str, Path],
    output_folder: Optional[Union[str, Path]] = None,
    include_metadata: bool = True
) -> Dict[Path, Path]:
    """Convert all DD files in a folder to CSV format.
    
    Args:
        input_folder: Path to folder containing DD files.
        output_folder: Optional path for output CSV files.
        include_metadata: Whether to include metadata columns in output.
        
    Returns:
        Dictionary mapping input paths to output paths.
        
    Raises:
        DDFileError: If the input folder doesn't exist.
        DDConversionError: If there's an error during conversion.
    """
    input_folder = Path(input_folder)
    if not input_folder.exists():
        raise DDFileError(f"Input folder not found: {input_folder}")
        
    try:
        # Determine output folder
        if output_folder:
            output_folder = Path(output_folder)
        else:
            output_folder = input_folder
            
        # Create output folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Process all DD files
        results = {}
        for dd_file in input_folder.glob('*.dd'):
            output_path = output_folder / dd_file.with_suffix('.csv').name
            try:
                output_path = convert_dd_to_csv(
                    dd_file,
                    output_path,
                    include_metadata=include_metadata
                )
                results[dd_file] = output_path
            except Exception as e:
                logger.error(f"Error converting {dd_file}: {str(e)}")
                continue
                
        if not results:
            raise DDConversionError(f"No DD files found in folder: {input_folder}")
            
        return results
        
    except DDFileError:
        raise
    except Exception as e:
        raise DDConversionError(f"Error converting folder: {str(e)}") from e 