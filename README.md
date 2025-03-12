# DD to CSV Converter

A Python utility to convert GAMS DD (Data Definition) files to CSV format. This tool can convert both individual DD files and entire folders containing DD files.

## Features

- Converts DD files containing SETs and PARAMETERs to CSV format
- Handles nested data structures with multiple components
- Supports batch conversion of entire folders
- Preserves data structure in a tabular format
- Includes comprehensive error handling and logging

## Installation

1. Clone this repository
2. Install the package and dependencies:
```bash
pip install -r requirements.txt
pip install .  # Install the package itself
```

## Usage

You can use the converter either as a Python package or through the command line.

### Python Package Usage

```python
from dd_converter import convert_dd_to_csv, convert_folder_to_csvs

# Convert a single DD file
output_path = convert_dd_to_csv(
    'path/to/your/file.dd',
    output_path='path/to/output.csv',  # Optional
    include_metadata=True  # Optional
)

# Convert all DD files in a folder
converted_files = convert_folder_to_csvs(
    'path/to/your/folder',
    output_folder='path/to/output',  # Optional
    include_metadata=True  # Optional
)
```

### Command Line Usage

After installation, use either `python -m dd_converter` or the `dd-converter` command:

```bash
# Convert a single DD file
dd-converter path/to/your/file.dd -o output/directory

# Convert a folder of DD files
dd-converter path/to/your/folder -o output/directory -v
```

Options:
- `-o, --output`: Specify output directory for CSV files
- `-v, --verbose`: Enable verbose logging for debugging
- `--no-metadata`: Skip metadata in output CSV files

## Output Format

The generated CSV files contain these columns:
- `component_1`, `component_2`, etc.: Data components
- `table_type`: Type of the data (SET or PARAMETER)
- `value`: The value (for PARAMETERs)

## Testing

### Running Unit Tests
```bash
pytest tests/test_dd_to_csv.py
```

### Testing with Demo Models

The package includes example models in `tests/test_data/demo-model-dd-files/`. Each demo model contains DD files such as:
- `base.dd`: Contains SETs and PARAMETERs for regions, commodities, and processes
- `demos_*_ts.dd`: Contains time series data and settings
- `syssettings.dd`: Contains system-wide parameters and configurations

To test with demos:
```bash
# Test single demo
dd-converter tests/test_data/demo-model-dd-files/DemoS_001 \
    -o output/demo-model-dd-files/DemoS_001

# Test all demos
for demo in DemoS_001 DemoS_002 DemoS_003 DemoS_004 DemoS_004a DemoS_004b DemoS_005 DemoS_005a DemoS_005b DemoS_006 DemoS_006a DemoS_006b DemoS_007 DemoS_007a DemoS_007b DemoS_008 DemoS_008a DemoS_008b DemoS_008c DemoS_011 DemoS_011a DemoS_011b DemoS_011c DemoS_011d DemoS_012 DemoS_012a DemoS_012b DemoS_012c DemoS_012d; do
    mkdir -p output/demo-model-dd-files/$demo
    dd-converter tests/test_data/demo-model-dd-files/$demo \
        -o output/demo-model-dd-files/$demo -v
done
```

## Error Handling

The converter handles common issues including:
- Malformed DD files
- Missing files or directories
- Permission issues
- Invalid data formats

All errors are logged with descriptive messages to help with debugging.
