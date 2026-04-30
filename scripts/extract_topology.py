#!/usr/bin/env python3
"""Extract topology connections from MUSIC binary."""

import sys
import struct
from pathlib import Path
from typing import List, Tuple, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from openmusic import SQZExtractor, MusicFileParser, MusicModel


def build_topology_from_names(model: MusicModel) -> List[Tuple[str, str, str]]:
    """Build topology by analyzing node names and types.

    In MUSIC, the flow is typically:
    Source -> Buffer -> Swale/Mitre -> Pond -> Junction -> Receiving

    We can infer this from naming patterns and node types.
    """
    connections = []

    # Group nodes by type
    sources = [n for n in model.nodes if 'Source' in n.node_type]
    junctions = [n for n in model.nodes if 'Junction' in n.node_type]
    receiving = [n for n in model.nodes if n.node_type == 'ReceivingNode']

    # For each source, trace the likely flow path
    for src in sources:
        src_name = clean_name(src.name)
        src_id = f"[{src.node_type}] {src_name}"

        # Sources connect to buffers (implied)
        buffer_id = f"[Buffer] Buffer for {src_name}"
        connections.append((src_id, "->", buffer_id))

        # Buffer to treatment (Swale or Pond)
        # Check if source name indicates treatment type
        if 'access' in src_name.lower() or 'track' in src_name.lower():
            treatment = "[Mitre Drain] Drain"
        else:
            treatment = "[Swale] Swale"
        connections.append((buffer_id, "->", treatment))

        # Treatment to pond
        pond = "[Pond] Pond"
        connections.append((treatment, "->", pond))

        # Pond to junction (based on catchment ID)
        catch_id = extract_catchment(src.name)
        junction = f"[Junction] {catch_id} Post-development"
        connections.append((pond, "->", junction))

    # Junctions connect to receiving
    for junc in junctions:
        junc_name = clean_name(junc.name)
        if receiving:
            recv_name = clean_name(receiving[0].name)
            connections.append(
                (f"[Junction] {junc_name}", "->", f"[Receiving] {recv_name}")
            )

    return connections


def clean_name(name: str) -> str:
    """Clean binary artifacts from node names."""
    # Remove binary prefixes
    if 'SourceNode' in name:
        # Extract readable part after SourceNode
        idx = name.find('SourceNode')
        if idx >= 0:
            name = name[idx + len('SourceNode'):]

    # Remove common binary suffixes
    suffixes = ['@d!Outflow', '@d!Inflow', '@pf@d!Outfl', 'hC', 'HR', 'zD@x']
    for suffix in suffixes:
        if suffix in name:
            name = name[:name.find(suffix)]

    # Remove non-printable chars
    clean = ''.join(c for c in name if 32 <= ord(c) <= 126)
    clean = clean.strip('hban')

    return clean.strip() or "Unnamed"


def extract_catchment(name: str) -> str:
    """Extract C1, C2, C3 from name."""
    name = name.upper()
    for prefix in ['C1', 'C2', 'C3', 'C4']:
        if prefix in name:
            return prefix
    return "C?"


def print_ascii_topology(connections: List[Tuple[str, str, str]]):
    """Print ASCII diagram of topology."""
    print("\n" + "=" * 70)
    print("MUSIC Model Topology (ASCII)")
    print("=" * 70)

    # Group by source
    current_source = None
    for src, arrow, dst in connections:
        if '[Source]' in src:
            if current_source:
                print()
            current_source = src
            print(f"\n{src}")

        if arrow == "->":
            indent = "    "
            print(f"{indent}|")
            print(f"{indent}v")
            print(f"{indent}{dst}")

    print("\n" + "=" * 70)


def main():
    sqz_path = Path('d:/GitRepos/OpenMUSIC/data/example/2066-02_28022025_BESS_EXG_and_DEV.sqz')

    if not sqz_path.exists():
        print(f"File not found: {sqz_path}")
        return 1

    print(f"Extracting topology from: {sqz_path.name}")
    print("-" * 70)

    with SQZExtractor() as extractor:
        music_file = extractor.extract(sqz_path)
        parser = MusicFileParser(music_file)
        model = parser.parse()

    print(f"Parsed {len(model.nodes)} nodes")

    # Show node summary
    print("\nNodes found:")
    for node in model.nodes:
        name = clean_name(node.name)
        area = node.properties.get('area_ha', 'N/A')
        print(f"  [{node.node_type}] {name} (Area: {area})")

    # Build and print topology
    connections = build_topology_from_names(model)
    print_ascii_topology(connections)

    # Also save to file
    output = Path('d:/GitRepos/OpenMUSIC/data/outputs/topology.txt')
    with open(output, 'w') as f:
        f.write("MUSIC Model Topology\n")
        f.write("=" * 70 + "\n\n")
        for src, arrow, dst in connections:
            f.write(f"{src} {arrow} {dst}\n")

    print(f"\nSaved topology to: {output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
