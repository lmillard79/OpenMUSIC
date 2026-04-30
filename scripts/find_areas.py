#!/usr/bin/env python3
"""Debug script to find area values in MUSIC binary files."""

import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openmusic import SQZExtractor


def find_areas_in_binary(file_path: Path):
    """Scan binary for float values that could be areas (0.1 to 1000 ha)."""
    data = file_path.read_bytes()
    file_size = len(data)

    print(f"Scanning: {file_path}")
    print(f"Size: {file_size:,} bytes")
    print("=" * 60)

    # Look for UrbanSourceNode positions first
    node_positions = []
    pos = 0
    while True:
        pos = data.find(b'UrbanSourceNode', pos)
        if pos == -1:
            break
        node_positions.append(pos)
        pos += 1

    print(f"\nFound {len(node_positions)} UrbanSourceNode markers")

    # Scan 500 bytes after each node for float values in reasonable range
    for i, node_pos in enumerate(node_positions[:5]):  # Check first 5
        print(f"\n--- Node {i+1} at position 0x{node_pos:06X} ---")

        # Read chunk after node
        chunk_start = node_pos + 20  # Skip marker
        chunk_end = min(chunk_start + 500, file_size)
        chunk = data[chunk_start:chunk_end]

        # Look for floats
        floats_found = []
        for j in range(0, len(chunk) - 4, 4):
            try:
                val = struct.unpack('<f', chunk[j:j+4])[0]
                # Reasonable area range: 0.1 to 1000 ha
                if 0.1 <= val <= 1000 and val == val:  # Not NaN
                    floats_found.append((j, val))
            except:
                pass

        # Also look for doubles (8 bytes)
        for j in range(0, len(chunk) - 8, 8):
            try:
                val = struct.unpack('<d', chunk[j:j+8])[0]
                if 0.1 <= val <= 1000:
                    floats_found.append((j, val))
            except:
                pass

        # Print found values
        if floats_found:
            print(f"Potential area values (offset: value):")
            for offset, val in floats_found[:10]:
                abs_pos = chunk_start + offset
                print(f"  0x{abs_pos:06X}: {val:.4f} ha")

        # Look for strings that might indicate property names
        print("\nStrings in vicinity:")
        for j in range(len(chunk)):
            length = chunk[j]
            if 1 < length < 50:
                try:
                    str_data = chunk[j+1:j+1+length]
                    if all(32 <= b <= 126 for b in str_data):
                        s = str_data.decode('ascii')
                        if 'area' in s.lower() or 'catch' in s.lower():
                            abs_pos = chunk_start + j
                            print(f"  0x{abs_pos:06X} ({length}b): {s}")
                except:
                    pass


def main():
    # Use the BESS model (has areas we know: 25.10, 25.41 ha)
    sqz_path = Path('d:/GitRepos/OpenMUSIC/data/example/2066-02_28022025_BESS_EXG_and_DEV.sqz')

    if not sqz_path.exists():
        print(f"File not found: {sqz_path}")
        return 1

    # Extract
    from openmusic import SQZExtractor
    with SQZExtractor() as extractor:
        music_file = extractor.extract(sqz_path)
        find_areas_in_binary(Path(music_file))

    return 0


if __name__ == '__main__':
    sys.exit(main())
