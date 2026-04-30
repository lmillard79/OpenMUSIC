#!/usr/bin/env python3
"""Analyze MUSIC files for result data and input parameters.

This script searches binary MUSIC files for:
1. Result/summary data locations
2. Input parameter blocks
3. Time series data patterns
"""

import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def find_float_arrays(data: bytes, min_values: int = 10) -> list:
    """Find sequences of valid floats that could be time series data."""
    results = []
    i = 0

    while i < len(data) - 4:
        # Try to read a float
        try:
            chunk = data[i:i+4]
            if len(chunk) == 4:
                val = struct.unpack('<f', chunk)[0]
                # Look for reasonable numeric ranges
                if 0 < val < 1000000 and val == val:  # Not NaN
                    # Check if followed by more valid floats
                    count = 1
                    j = i + 4
                    while j < len(data) - 4 and count < 1000:
                        try:
                            next_val = struct.unpack('<f', data[j:j+4])[0]
                            if 0 < next_val < 1000000 and next_val == next_val:
                                count += 1
                                j += 4
                            else:
                                break
                        except:
                            break

                    if count >= min_values:
                        results.append({
                            'position': i,
                            'count': count,
                            'first_value': val,
                            'last_value': struct.unpack('<f', data[j-4:j])[0] if j >= 4 else 0
                        })
                        i = j  # Skip past this array
                        continue
        except:
            pass
        i += 1

    return results


def find_parameters(data: bytes) -> dict:
    """Search for common MUSIC parameter patterns."""
    params = {}

    # Known parameter strings in MUSIC
    param_keywords = [
        b'Area', b'area', b'Catchment', b'Impervious',
        b'Slope', b'Length', b'Width', b'Depth',
        b'Rainfall', b'Runoff', b'ET', b'Evap',
        b'TN', b'TP', b'TSS', b'GP',
        b'Inflow', b'Outflow', b'Discharge',
        b'Storage', b'Volume', b'Capacity',
    ]

    for keyword in param_keywords:
        positions = []
        pos = 0
        while True:
            pos = data.find(keyword, pos)
            if pos == -1:
                break
            positions.append(pos)
            pos += 1

        if positions:
            params[keyword.decode('ascii', errors='replace')] = {
                'count': len(positions),
                'positions': positions[:5]  # First 5 occurrences
            }

    return params


def analyze_file(file_path: Path) -> dict:
    """Analyze a MUSIC binary file."""
    data = file_path.read_bytes()

    return {
        'file_size': len(data),
        'float_arrays': find_float_arrays(data, min_values=50),
        'parameters': find_parameters(data),
    }


def main():
    # Analyze the extracted MusicDataFile
    music_file = Path('d:/GitRepos/OpenMUSIC/data/example/extracted/MusicDataFile')

    if not music_file.exists():
        print(f"File not found: {music_file}")
        print("Please run: python scripts/test_parser.py first to extract a file")
        return 1

    print(f"Analyzing: {music_file}")
    print(f"Size: {music_file.stat().st_size:,} bytes")
    print("=" * 60)

    results = analyze_file(music_file)

    # Report float arrays (potential time series)
    print(f"\nFound {len(results['float_arrays'])} float arrays:")
    print("-" * 40)
    for arr in sorted(results['float_arrays'], key=lambda x: x['count'], reverse=True)[:10]:
        print(f"  Position 0x{arr['position']:06X}: {arr['count']} floats")
        print(f"    Range: {arr['first_value']:.4f} to {arr['last_value']:.4f}")

    # Report parameters
    print(f"\nFound {len(results['parameters'])} parameter keywords:")
    print("-" * 40)
    for param, info in sorted(results['parameters'].items()):
        print(f"  {param}: {info['count']} occurrences")
        print(f"    Positions: {[hex(p) for p in info['positions']]}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
