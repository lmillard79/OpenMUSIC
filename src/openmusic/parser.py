"""Binary parser for MUSIC MusicDataFile format.

The MusicDataFile uses Delphi/Object Pascal binary serialization.
This parser reverse-engineers the format structure.
"""

import struct
from pathlib import Path
from typing import Dict, List, Optional, Any, BinaryIO, Union
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class MusicNode:
    """Represents a node in the MUSIC model graph."""
    node_type: str = ""
    node_id: str = ""
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class TimeSeries:
    """Time series data from MUSIC simulation results."""
    name: str = ""
    position: int = 0
    count: int = 0
    values: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def max_value(self) -> float:
        return max(self.values) if self.values else 0.0

    @property
    def min_value(self) -> float:
        return min(self.values) if self.values else 0.0

    @property
    def sum_value(self) -> float:
        return sum(self.values) if self.values else 0.0


@dataclass
class MusicModel:
    """Complete MUSIC model representation."""
    version: str = ""
    nodes: List[MusicNode] = field(default_factory=list)
    time_series: List[TimeSeries] = field(default_factory=list)
    rainfall_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MusicFileParser:
    """Parser for MUSIC binary MusicDataFile format."""

    # Known node type signatures from binary analysis
    NODE_TYPES = {
        b'TReceivingNode': 'ReceivingNode',
        b'TUrbanSourceNode': 'UrbanSourceNode',
        # Treatment nodes to be identified
        b'TWetlandNode': 'WetlandNode',
        b'TPondNode': 'PondNode',
        b'TBioRetentionNode': 'BioRetentionNode',
        b'TBufferStripNode': 'BufferStripNode',
        b'TGrossPollutantTrapNode': 'GrossPollutantTrapNode',
        b'TInfiltrationNode': 'InfiltrationNode',
        b'TRainwaterTankNode': 'RainwaterTankNode',
        b'TAquiferNode': 'AquiferNode',
    }

    def __init__(self, file_path: Union[str, Path]):
        """Initialize parser with MusicDataFile path.

        Args:
            file_path: Path to extracted MusicDataFile.
        """
        self.file_path = Path(file_path)
        self._fp: Optional[BinaryIO] = None
        self._position = 0

    def parse(self) -> MusicModel:
        """Parse the MusicDataFile and return model structure.

        Returns:
            MusicModel containing all extracted data.

        Raises:
            FileNotFoundError: If file_path does not exist.
            ValueError: If file format is invalid.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"MusicDataFile not found: {self.file_path}")

        model = MusicModel()

        with open(self.file_path, 'rb') as self._fp:
            # Read and verify header
            # Delphi binary format starts with type markers before the version string
            header_bytes = self._read_bytes(7)

            # Check for T2DDF starting at offset 2 (after 0x06 0x05 type markers)
            if header_bytes[2:7] == b'T2DDF':
                model.version = 'T2DDF'
                model.metadata['header_prefix'] = header_bytes[:2].hex()
                logger.info(f"Parsing MUSIC file version: {model.version}")
            elif header_bytes[:5] == b'T2DDF':
                # Older format without prefix
                model.version = 'T2DDF'
                logger.info(f"Parsing MUSIC file version: {model.version}")
                # Seek back to position 5 to continue reading
                self._fp.seek(5)
            else:
                raise ValueError(
                    f"Invalid file header: {header_bytes!r}, "
                    f"expected T2DDF at position 0 or 2"
                )

            # Parse main structure
            self._parse_structure(model)

        logger.info(f"Parsed model with {len(model.nodes)} nodes")

        # After parsing structure, extract time series data
        self._extract_time_series(model)

        return model

    def _extract_time_series(self, model: MusicModel) -> None:
        """Extract float arrays that represent simulation results.

        Scans the binary file for sequences of floats that likely represent
        time series data (hydrographs, pollutant loads, rainfall).
        """
        logger.info("Extracting time series data...")

        # Read entire file for scanning
        with open(self.file_path, 'rb') as f:
            data = f.read()

        file_size = len(data)
        min_array_size = 20  # Minimum floats to consider as time series
        max_array_size = 10000  # Maximum reasonable size

        i = 0
        series_count = 0

        while i < file_size - 4:
            try:
                # Try to read a float
                chunk = data[i:i+4]
                if len(chunk) < 4:
                    break

                val = struct.unpack('<f', chunk)[0]

                # Check for valid float (not NaN, reasonable range)
                if -1e9 < val < 1e9 and val == val:
                    # Look for consecutive valid floats
                    values = [val]
                    j = i + 4

                    while (j < file_size - 4 and
                           len(values) < max_array_size):
                        try:
                            next_chunk = data[j:j+4]
                            if len(next_chunk) < 4:
                                break
                            next_val = struct.unpack('<f', next_chunk)[0]

                            # Check if it's a valid continuation
                            if -1e9 < next_val < 1e9 and next_val == next_val:
                                values.append(next_val)
                                j += 4
                            else:
                                break
                        except:
                            break

                    # If we found a significant array, store it
                    if len(values) >= min_array_size:
                        # Determine type based on value patterns
                        series_type = self._classify_time_series(values)

                        ts = TimeSeries(
                            name=f"{series_type}_{series_count}",
                            position=i,
                            count=len(values),
                            values=values,
                            metadata={
                                'type': series_type,
                                'max': max(values),
                                'min': min(values),
                                'sum': sum(values),
                                'mean': sum(values) / len(values),
                            }
                        )
                        model.time_series.append(ts)
                        series_count += 1

                        # Skip past this array
                        i = j
                        continue

            except:
                pass
            i += 1

        logger.info(f"Extracted {len(model.time_series)} time series")

    def _classify_time_series(self, values: List[float]) -> str:
        """Classify time series based on value patterns."""
        if not values:
            return "unknown"

        max_val = max(values)
        min_val = min(values)
        avg_val = sum(values) / len(values)

        # Rainfall: mostly zeros with occasional spikes
        zero_ratio = sum(1 for v in values if v < 0.001) / len(values)
        if zero_ratio > 0.8 and max_val > 1:
            return "rainfall"

        # Flow: continuous values, may have peaks
        if max_val > 50 and avg_val < max_val * 0.3:
            return "flow"

        # Pollutant load: smaller values, continuous
        if max_val < 10 and avg_val < 1:
            return "pollutant"

        # Storage/volume: generally increasing or steady
        if values[-1] >= values[0] and max_val > 100:
            return "storage"

        return "unknown"

    def _read_bytes(self, n: int) -> bytes:
        """Read n bytes from file."""
        data = self._fp.read(n)
        if len(data) < n:
            raise ValueError(f"Unexpected end of file at position {self._fp.tell()}")
        return data

    def _read_byte(self) -> int:
        """Read single byte as integer."""
        return struct.unpack('B', self._read_bytes(1))[0]

    def _read_int16(self) -> int:
        """Read 2-byte little-endian integer."""
        return struct.unpack('<h', self._read_bytes(2))[0]

    def _read_int32(self) -> int:
        """Read 4-byte little-endian integer."""
        return struct.unpack('<i', self._read_bytes(4))[0]

    def _read_float(self) -> float:
        """Read 4-byte little-endian float."""
        return struct.unpack('<f', self._read_bytes(4))[0]

    def _read_double(self) -> float:
        """Read 8-byte little-endian double."""
        return struct.unpack('<d', self._read_bytes(8))[0]

    def _read_string(self) -> str:
        """Read Delphi-style length-prefixed string.

        Delphi strings use a length byte (for short strings) or
        length integer prefix.
        """
        # Try short string first (length byte)
        length_byte = self._read_byte()

        if length_byte == 0:
            return ""

        # Check if this is a long string indicator
        if length_byte == 0xFF:
            # Long string - read 4-byte length
            length = self._read_int32()
        else:
            length = length_byte

        if length > 10000:  # Sanity check
            logger.warning(f"Suspicious string length: {length}")
            return ""

        data = self._read_bytes(length)
        try:
            return data.decode('utf-8', errors='replace')
        except UnicodeDecodeError:
            return data.decode('latin-1', errors='replace')

    def _parse_structure(self, model: MusicModel) -> None:
        """Parse the main file structure.

        This is an iterative reverse-engineering of the Delphi binary format.
        """
        # Scan for known markers
        file_size = self.file_path.stat().st_size
        chunk_size = 1024

        while self._fp.tell() < file_size - 20:
            current_pos = self._fp.tell()
            marker = self._read_bytes(5)

            if marker == b'DCGRA':  # DCGRAPH start
                logger.debug(f"Found DCGRAPH marker at position {current_pos}")
                # Read remaining 'PH' of DCGRAPH
                self._read_bytes(2)
                self._parse_graph(model)
                break
            else:
                # Step back 4 bytes and continue scanning
                self._fp.seek(current_pos + 1)

    def _parse_graph(self, model: MusicModel) -> None:
        """Parse the DCGRAPH structure containing all nodes."""
        # DCGRAPH contains a list of vertices
        # Format is complex - we'll scan for node type signatures

        file_size = self.file_path.stat().st_size

        while self._fp.tell() < file_size - 30:
            current_pos = self._fp.tell()
            data = self._fp.read(30)
            self._fp.seek(current_pos)  # Reset position

            # Check for node type signatures
            for type_sig, type_name in self.NODE_TYPES.items():
                if type_sig in data:
                    logger.debug(f"Found {type_name} at position {current_pos}")
                    node = self._parse_node(type_name)
                    if node:
                        model.nodes.append(node)
                    break
            else:
                # Move forward by 1 byte
                self._fp.read(1)

    def _parse_node(self, node_type: str) -> Optional[MusicNode]:
        """Parse a single node from the binary stream.

        Args:
            node_type: The identified type of node.

        Returns:
            MusicNode if parsing succeeds, None otherwise.
        """
        node = MusicNode(node_type=node_type)

        try:
            # Skip past the type signature
            type_sig = b'T' + node_type.encode('ascii')
            self._read_bytes(len(type_sig))

            # Read node name
            node.name = self._read_string()

            # Read position coordinates (if present)
            # This is heuristic - needs refinement
            try:
                coord_marker = self._read_bytes(4)
                if coord_marker == b'TDCV':  # TDCVertex marker
                    # Skip to coordinates
                    self._read_bytes(10)
                    node.x = self._read_float()
                    node.y = self._read_float()
            except (struct.error, ValueError):
                pass  # Coordinates not present

            # Scan for properties
            self._parse_node_properties(node)

            return node

        except (struct.error, ValueError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse {node_type} node: {e}")
            return None

    def _parse_node_properties(self, node: MusicNode) -> None:
        """Extract properties from node binary data.

        Scans for numeric values (areas, dimensions) and property strings.
        """
        start_pos = self._fp.tell()
        scan_end = min(start_pos + 1000, self.file_path.stat().st_size)

        # Read the chunk to scan
        chunk_size = scan_end - start_pos
        chunk = self._fp.read(chunk_size)

        # Look for float values that could be areas (0.01 to 10000 ha)
        areas_found = []
        for i in range(0, len(chunk) - 4, 4):
            try:
                val = struct.unpack('<f', chunk[i:i+4])[0]
                # Valid area: reasonable range, not NaN/Inf
                if 0.01 <= val <= 10000 and val == val and abs(val) < 1e9:
                    areas_found.append((start_pos + i, val))
            except:
                pass

        # Also look for doubles (8 bytes) - some params use double precision
        for i in range(0, len(chunk) - 8, 8):
            try:
                val = struct.unpack('<d', chunk[i:i+8])[0]
                if 0.01 <= val <= 10000 and abs(val) < 1e9:
                    areas_found.append((start_pos + i, val))
            except:
                pass

        # Store the most likely area (largest value found near node)
        if areas_found:
            # Sort by value, take the largest reasonable one
            areas_found.sort(key=lambda x: x[1], reverse=True)
            for pos, val in areas_found[:3]:  # Store top 3 values
                if 'area' not in node.properties:
                    node.properties['area_ha'] = round(val, 4)
                    logger.debug(f"Found area: {val:.4f} ha at 0x{pos:06X}")

        # Look for property strings
        self._fp.seek(start_pos)  # Reset to scan start
        while self._fp.tell() < scan_end - 5:
            try:
                prop_pos = self._fp.tell()
                prop_name = self._read_string()

                if prop_name and 2 < len(prop_name) < 50:
                    # Check if it looks like a property name
                    if prop_name[0].isalpha():
                        # Try to read a value after the property name
                        val_pos = self._fp.tell()
                        try:
                            # Try float first
                            val_bytes = self._fp.read(4)
                            if len(val_bytes) == 4:
                                val = struct.unpack('<f', val_bytes)[0]
                                if -1e9 < val < 1e9 and val == val:
                                    node.properties[prop_name] = round(val, 6)
                                    continue
                        except:
                            self._fp.seek(val_pos)

                        # Mark as found even without value
                        if prop_name not in node.properties:
                            node.properties[prop_name] = None

            except (ValueError, UnicodeDecodeError, struct.error):
                # Skip byte and continue
                pass

    def to_dict(self, model: MusicModel) -> Dict[str, Any]:
        """Convert MusicModel to dictionary representation."""
        return {
            'version': model.version,
            'metadata': model.metadata,
            'nodes': [
                {
                    'type': n.node_type,
                    'id': n.node_id,
                    'name': n.name,
                    'x': n.x,
                    'y': n.y,
                    'properties': n.properties,
                    'inputs': n.inputs,
                    'outputs': n.outputs,
                }
                for n in model.nodes
            ]
        }
