#!/usr/bin/env python3
"""Binary inspector for MUSIC MusicDataFile format.

This script helps reverse-engineer the binary format by extracting
readable strings and structure markers.
"""

import sys
import struct
from pathlib import Path


def extract_strings(data: bytes, min_length: int = 4) -> list:
    """Extract readable ASCII strings from binary data."""
    strings = []
    current = []

    for i, byte in enumerate(data):
        if 32 <= byte <= 126:
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                strings.append((i - len(current), ''.join(current)))
            current = []

    if len(current) >= min_length:
        strings.append((len(data) - len(current), ''.join(current)))

    return strings


def find_markers(data: bytes, markers: list) -> list:
    """Find specific byte sequences in data."""
    results = []

    for marker in markers:
        marker_bytes = marker.encode('ascii') if isinstance(marker, str) else marker
        pos = 0
        while True:
            pos = data.find(marker_bytes, pos)
            if pos == -1:
                break
            results.append((pos, marker))
            pos += 1

    return sorted(results)


def analyze_structure(data: bytes) -> dict:
    """Analyze the binary structure."""
    info = {
        'total_size': len(data),
        'header': data[:10].hex(),
        'known_markers': [],
        'strings': [],
    }

    # Look for known markers
    markers = [
        b'T2DDF',
        b'DCGRAPH',
        b'TDCVertex',
        b'TReceivingNode',
        b'TUrbanSourceNode',
        b'TPondNode',
        b'MusicNodeBitmap',
        b'Outflow',
        b'Inflow',
        b'Rainfall',
        b'TN ',
        b'TP ',
        b'TSS',
    ]

    for marker in markers:
        positions = []
        pos = 0
        while True:
            pos = data.find(marker, pos)
            if pos == -1:
                break
            positions.append(pos)
            pos += 1
        if positions:
            info['known_markers'].append({
                'marker': marker.decode('ascii', errors='replace'),
                'count': len(positions),
                'positions': positions[:5],  # First 5 occurrences
            })

    # Extract strings
    strings = extract_strings(data, min_length=5)
    # Filter for likely meaningful strings
    info['strings'] = [
        (pos, s) for pos, s in strings
        if s[0].isalpha() and len(s) < 100
    ][:50]  # First 50

    return info


def main():
    if len(sys.argv) < 2:
        # Use default extracted file
        file_path = Path('d:/GitRepos/OpenMUSIC/data/example/extracted/MusicDataFile')
    else:
        file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return 1

    print(f"Analyzing: {file_path}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    print("=" * 60)

    data = file_path.read_bytes()
    info = analyze_structure(data)

    print(f"\nHeader (first 10 bytes): {info['header']}")

    print("\nKnown Markers Found:")
    print("-" * 40)
    for marker_info in info['known_markers']:
        print(f"  {marker_info['marker']}: {marker_info['count']} occurrences")
        print(f"    Positions: {marker_info['positions']}")

    print("\nSample Strings (first 30):")
    print("-" * 40)
    for pos, s in info['strings'][:30]:
        print(f"  0x{pos:06X}: {s[:50]}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
