# OpenMUSIC

Open-source parser and auditor for MUSIC (Model for Urban Stormwater Improvement Conceptualisation) .sqz files.

## Purpose

Enable QA/QC of MUSIC models **without requiring the MUSIC software or dongle**. Extract model topology, parameters, and results for verification and reporting.

## Current Status

**Phase 1 Complete**: Basic parser operational
- Extracts .sqz files (ZIP archives containing `MusicDataFile`)
- Parses binary Delphi serialization format
- Identifies node types: `UrbanSourceNode`, `ReceivingNode`, `PondNode`

## File Structure Discovery

```
.sqz file (ZIP archive)
└── MusicDataFile (Delphi binary serialization)
    ├── Header: 0x06 0x05 T2DDF
    ├── DCGRAPH: Graph container
    │   ├── TDCVertex nodes with coordinates
    │   ├── Node parameters (area, rainfall, pollutants)
    │   └── Connection topology
    └── Rainfall time series (if embedded)
```

## Installation

```bash
cd d:\GitRepos\OpenMUSIC
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Parse a single file
```python
from openmusic import SQZExtractor, MusicFileParser

with SQZExtractor() as extractor:
    music_file = extractor.extract("model.sqz")
    parser = MusicFileParser(music_file)
    model = parser.parse()
    
    print(f"Found {len(model.nodes)} nodes")
    for node in model.nodes:
        print(f"  - {node.node_type}: {node.name}")
```

### Test on example files
```bash
python scripts\test_parser.py
```

### Scan J/V drives for .sqz files
```powershell
# Background-friendly scan (below-normal priority)
.\scripts\find_sqz_files.ps1

# Results saved to: data\sqz_inventory.csv
```

## Project Structure

```
OpenMUSIC/
├── src/openmusic/          # Parser library
│   ├── __init__.py
│   ├── extractor.py        # ZIP extraction
│   └── parser.py           # Binary format parser
├── scripts/
│   ├── test_parser.py      # Test on example files
│   └── find_sqz_files.ps1  # J/V drive scanner
├── data/
│   ├── example/            # Example .sqz files
│   └── sqz_inventory.csv   # Scan results
└── requirements.txt
```

## Node Types Identified

- `UrbanSourceNode` - Urban source areas (roof, road, land use types)
- `ReceivingNode` - Model outflow/receiving waters
- `PondNode` - Detention pond
- `WetlandNode` - Constructed wetland
- `BioRetentionNode` - Bio-retention basin
- `BufferStripNode` - Vegetated buffer strip
- `GrossPollutantTrapNode` - GPT/trash rack
- `InfiltrationNode` - Infiltration system
- `RainwaterTankNode` - Rainwater harvesting
- `AquiferNode` - Groundwater/aquifer

## Pollutants Tracked

- TN (Total Nitrogen) - kg
- TP (Total Phosphorus) - kg
- TSS (Total Suspended Solids) - kg
- Gross Pollutants - kg

## Roadmap

1. **Phase 1** [In Progress]: File parser foundation
2. **Phase 2**: Data extraction (parameters, rainfall, topology)
3. **Phase 3**: Output generators (Excel, JSON, visual diagrams)
4. **Phase 4**: J/V drive discovery and pattern analysis
5. **Phase 5**: Engine research (hydraulic/pollutant algorithms)

## License

MIT License - See LICENSE file
