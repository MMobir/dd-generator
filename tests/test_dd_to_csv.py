"""Tests for DD to CSV converter."""

import os
import tempfile
import logging
from pathlib import Path
import pytest
import pandas as pd

from dd_converter import convert_dd_to_csv, convert_folder_to_csvs
from dd_converter.exceptions import DDConversionError, DDFileError

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def sample_dd_content():
    """Sample DD file content for testing."""
    return '''$ONEMPTY
$ONEPS
$ONWARNING
$SET RUN_NAME 'TEST'
$SET SCENARIO_NAME 'test'

SET TEST_SET
/
'REG1'.'ELC'
'REG2'.'GAS'
/;

PARAMETER
TEST_PARAM ' '/
'REG1'.2005.'ELC' 0.05
'REG1'.2020.'ELC' 0.2
'REG2'.2005.'GAS' 0.1
/;
'''

@pytest.fixture
def temp_dd_file(tmp_path, sample_dd_content):
    """Create a temporary DD file for testing."""
    dd_file = tmp_path / "test.dd"
    dd_file.write_text(sample_dd_content)
    return dd_file

def test_convert_dd_to_csv(temp_dd_file):
    """Test converting a single DD file to CSV."""
    output_path = convert_dd_to_csv(temp_dd_file)
    assert output_path.exists()
    
    df = pd.read_csv(output_path)
    assert not df.empty
    assert 'table_type' in df.columns
    assert 'TEST_SET' in df['table_type'].values
    assert 'TEST_PARAM' in df['table_type'].values

def test_convert_dd_to_csv_with_output_path(temp_dd_file, tmp_path):
    """Test converting a DD file to CSV with custom output path."""
    output_path = tmp_path / "custom_output.csv"
    result_path = convert_dd_to_csv(temp_dd_file, output_path)
    assert result_path == output_path
    assert result_path.exists()

def test_convert_dd_to_csv_no_metadata(temp_dd_file):
    """Test converting a DD file to CSV without metadata columns."""
    output_path = convert_dd_to_csv(temp_dd_file, include_metadata=False)
    df = pd.read_csv(output_path)
    assert 'table_type' not in df.columns

def test_convert_dd_to_csv_file_not_found():
    """Test error handling for non-existent DD file."""
    with pytest.raises(DDFileError):
        convert_dd_to_csv("nonexistent.dd")

def test_convert_folder_to_csvs(tmp_path, sample_dd_content):
    """Test converting a folder of DD files to CSVs."""
    # Create test files
    (tmp_path / "test1.dd").write_text(sample_dd_content)
    (tmp_path / "test2.dd").write_text(sample_dd_content)
    (tmp_path / "not_a_dd.txt").write_text("This is not a DD file")
    
    results = convert_folder_to_csvs(tmp_path)
    assert len(results) == 2
    
    for input_path, output_path in results.items():
        assert input_path.suffix == '.dd'
        assert output_path.exists()
        assert output_path.suffix == '.csv'
        
        df = pd.read_csv(output_path)
        assert not df.empty
        assert 'table_type' in df.columns

def test_convert_folder_to_csvs_with_output_folder(tmp_path, sample_dd_content):
    """Test converting a folder of DD files with custom output location."""
    input_folder = tmp_path / "input"
    output_folder = tmp_path / "output"
    input_folder.mkdir()
    
    # Create test files
    (input_folder / "test1.dd").write_text(sample_dd_content)
    (input_folder / "test2.dd").write_text(sample_dd_content)
    
    results = convert_folder_to_csvs(input_folder, output_folder)
    assert len(results) == 2
    assert all(str(p).startswith(str(output_folder)) for p in results.values())

def test_convert_folder_to_csvs_folder_not_found():
    """Test error handling for non-existent folder."""
    with pytest.raises(DDFileError):
        convert_folder_to_csvs("nonexistent_folder") 