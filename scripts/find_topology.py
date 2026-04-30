#!/usr/bin/env python3
"""Debug script to find topology connections in MUSIC binary files."""

import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openmusic import SQZExtractor


def find_connections_in_binary(file_path: Path):
    """Scan binary for node connection patterns."""
    data = file_path.read_bytes()
    file_size = len(data)

    print(f"Scanning: {file_path}")
    print(f"Size: {file_size:,} bytes")
    print("=" * 60)

    # Look for patterns that might indicate connections
    # Common patterns: integers that could be node indices
    # or special markers between nodes

    # Find all node positions first
    node_types = [
        (b'UrbanSourceNode', 'Source'),
        (b'ReceivingNode', 'Receiving'),
        (b'PondNode', 'Pond'),
        (b'SwaleNode', 'Swale'),
        (b'BufferNode', 'Buffer'),
        (b'JunctionNode', 'Junction'),
        (b'PreDevelopmentNode', 'PreDev'),
        (b'PostDevelopmentNode', 'PostDev'),
    ]

    nodes_found = []

    for pattern, node_type in node_types:
        pos = 0
        while True:
            pos = data.find(pattern, pos)
            if pos == -1:
                break
            nodes_found.append((pos, node_type, pattern))
            pos += 1

    # Sort by position
    nodes_found.sort()

    print(f"\nFound {len(nodes_found)} nodes in order:")
    print("-" * 60)

    for i, (pos, node_type, pattern) in enumerate(nodes_found[:20]):
        print(f"  {i+1:2d}. 0x{pos:06X} - {node_type}")

        # Look at data between this node and next
        if i < len(nodes_found) - 1:
            next_pos = nodes_found[i + 1][0]
            gap = next_pos - pos - len(pattern)

            if gap > 0 and gap < 500:
                chunk = data[pos + len(pattern):next_pos]

                # Look for integers that might be connection indices
                for j in range(0, min(100, len(chunk) - 4), 4):
                    try:
                        val = struct.unpack('<i', chunk[j:j+4])[0]
                        if 0 <= val < len(nodes_found):
                            print(f"      -> Possible connection index: {val} at +{j}")
                    except:
                        pass

                # Look for strings in the gap
                for j in range(len(chunk)):
                    length = chunk[j]
                    if 3 < length < 50:
                        try:
                            str_data = chunk[j+1:j+1+length]
                            if all(32 <= b <= 126 for b in str_data):
                                s = str_data.decode('ascii')
                                print(f"      -> String at +{j}: {s}")
                        except:
                            pass


def main():
    sqz_path = Path('d:/GitRepos/OpenMUSIC/data/example/2066-02_28022025_BESS_EXG_and_DEV.sqz')

    if not sqz_path.exists():
        print(f"File not found: {sqz_path}")
        return 1

    from openmusic import SQZExtractor
    with SQZExtractor() as extractor:
        music_file = extractor.extract(sqz_path)
        find_connections_in_binary(Path(music_file))

    return 0


if __name__ == '__main__':
    sys.exit(main())
