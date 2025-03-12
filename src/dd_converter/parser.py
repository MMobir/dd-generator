"""DD file parser module."""

import re
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple, Any
import pandas as pd
from .exceptions import DDParserError, DDValidationError

logger = logging.getLogger(__name__)

@dataclass
class DDEntry:
    """Represents a parsed DD file entry."""
    name: str
    type: str  # 'SET' or 'PARAMETER'
    description: Optional[str]
    data: List[Union[List[str], Tuple[Any, ...]]]

class DDParser:
    """Parser for GAMS DD files."""
    
    # Regular expressions for parsing
    SET_PATTERN = re.compile(r'SET\s+(\w+)')
    PARAM_PATTERN = re.compile(r'PARAMETER\s*(\w+)?(?:\s*\'([^\']+)\')?')
    DATA_LINE_PATTERN = re.compile(r'\'[^\']+\'|[\d.]+')
    
    def __init__(self):
        """Initialize the parser."""
        self.reset()
    
    def reset(self):
        """Reset parser state."""
        self._current_block = None
        self._current_name = None
        self._current_description = None
        self._in_data_block = False
        self._entries: Dict[str, DDEntry] = {}
        self._pending_parameter = False
    
    def parse(self, content: str) -> Dict[str, pd.DataFrame]:
        """Parse DD file content and return DataFrames.
        
        Args:
            content: The DD file content as string.
            
        Returns:
            Dict mapping table names to pandas DataFrames.
            
        Raises:
            DDParserError: If there's an error parsing the content.
            DDValidationError: If the content is invalid.
        """
        try:
            self.reset()
            lines = [line.strip() for line in content.split('\n') 
                    if line.strip() and not line.strip().startswith('*')]
            
            logger.debug("Parsing lines: %s", lines)
            for line in lines:
                self._parse_line(line)
            
            logger.debug("Final entries: %s", self._entries)
            return self._convert_to_dataframes()
        except Exception as e:
            raise DDParserError(f"Error parsing DD content: {str(e)}") from e
    
    def _parse_line(self, line: str):
        """Parse a single line of DD file content."""
        logger.debug("Parsing line: %s", line)
        logger.debug("Current state: block=%s, name=%s, in_data=%s, pending=%s",
                    self._current_block, self._current_name,
                    self._in_data_block, self._pending_parameter)
        
        # Skip GAMS directives
        if line.startswith('$'):
            return
            
        # Check for SET or PARAMETER declarations
        set_match = self.SET_PATTERN.match(line)
        param_match = self.PARAM_PATTERN.match(line)
        
        if set_match:
            self._handle_set_declaration(set_match)
        elif param_match or (self._pending_parameter and not line.startswith('$')):
            self._handle_parameter_declaration(param_match, line)
        elif line.startswith('/'):
            self._in_data_block = not self._in_data_block
            logger.debug("Data block state changed: %s", self._in_data_block)
        elif line.endswith('/;') or line.endswith(';'):
            self._in_data_block = False
            logger.debug("Data block ended")
        elif self._in_data_block and self._current_name:
            self._handle_data_line(line)
    
    def _handle_set_declaration(self, match):
        """Handle SET declaration line."""
        name = match.group(1)
        self._current_block = 'SET'
        self._current_name = name
        self._current_description = None
        self._entries[name] = DDEntry(name, 'SET', None, [])
        self._pending_parameter = False
        logger.debug("Handling SET declaration: %s", name)
    
    def _handle_parameter_declaration(self, match, line):
        """Handle PARAMETER declaration line."""
        logger.debug("Handling PARAMETER declaration: %s", line)
        logger.debug("Match: %s", match.groups() if match else None)
        
        if match and not match.group(1):
            # Just the PARAMETER keyword
            self._current_block = 'PARAMETER'
            self._pending_parameter = True
            logger.debug("Found PARAMETER keyword, waiting for name")
            return
            
        if self._pending_parameter:
            # Parameter name is on this line
            parts = line.strip().split()
            name = parts[0]
            description = None
            if "'" in line:
                description = re.search(r'\'([^\']+)\'', line)
                if description:
                    description = description.group(1)
            logger.debug("Found pending PARAMETER name: %s, description: %s", name, description)
        else:
            # Everything is on one line
            name = match.group(1)
            description = match.group(2)
            logger.debug("Found PARAMETER on one line: %s, description: %s", name, description)
        
        self._current_block = 'PARAMETER'
        self._current_name = name
        self._current_description = description
        self._entries[name] = DDEntry(name, 'PARAMETER', description, [])
        self._pending_parameter = False
    
    def _handle_data_line(self, line: str):
        """Handle data line within SET or PARAMETER block."""
        logger.debug("Handling data line: %s", line)
        logger.debug("Current block: %s, name: %s", self._current_block, self._current_name)
        
        try:
            line = line.strip().rstrip(';').strip()
            if not line:
                return
                
            if self._current_block == 'SET':
                # Split by dots and remove quotes
                if "'" in line:
                    elements = [e.strip("'") for e in line.split('.')]
                else:
                    elements = [line]
                self._entries[self._current_name].data.append(elements)
                logger.debug("Added SET data: %s", elements)
            else:  # PARAMETER
                # Split into components and value
                parts = line.split()
                logger.debug("PARAMETER parts: %s", parts)
                
                if len(parts) > 1:
                    value = float(parts[-1])
                    # Join all but last part and split by dots
                    components = []
                    current_part = []
                    
                    for part in parts[:-1]:
                        logger.debug("Processing part: %s", part)
                        if part.startswith("'"):
                            if current_part:
                                components.extend(current_part)
                                current_part = []
                            # Split by dots and clean quotes
                            dot_parts = [e.strip("'") for e in part.split('.')]
                            logger.debug("Dot parts: %s", dot_parts)
                            components.extend(dot_parts)
                        else:
                            current_part.append(part)
                    
                    if current_part:
                        components.extend(current_part)
                    
                    entry = (*components, value)
                    logger.debug("Final components: %s", components)
                    logger.debug("Final entry: %s", entry)
                    self._entries[self._current_name].data.append(entry)
                    logger.debug("Added PARAMETER data: %s", entry)
        except (ValueError, IndexError) as e:
            raise DDValidationError(f"Invalid data line: {line}") from e
    
    def _convert_to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert parsed entries to pandas DataFrames."""
        dfs = {}
        for name, entry in self._entries.items():
            logger.debug("Converting entry to DataFrame: %s, type: %s, data: %s",
                        name, entry.type, entry.data)
            
            if not entry.data:
                continue
                
            if entry.type == 'SET':
                # For SET data, create columns based on number of components
                n_components = len(entry.data[0])
                columns = [f'component_{i+1}' for i in range(n_components)]
                df = pd.DataFrame(entry.data, columns=columns)
                df['table_type'] = entry.name
                dfs[name] = df
                logger.debug("Created SET DataFrame: %s", df)
            else:  # PARAMETER
                # For PARAMETER data, last element is value
                if entry.data:
                    n_components = len(entry.data[0]) - 1  # Last element is value
                    columns = [f'component_{i+1}' for i in range(n_components)] + ['value']
                    df = pd.DataFrame(entry.data, columns=columns)
                    df['table_type'] = entry.name
                    dfs[name] = df
                    logger.debug("Created PARAMETER DataFrame: %s", df)
        
        return dfs 