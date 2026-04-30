# OpenMUSIC Project Status

**Date:** 2026-04-30  
**Status:** Phase 1 Complete - Parser Foundation Operational

## Summary

OpenMUSIC is an open-source parser and auditor for MUSIC (Model for Urban Stormwater Improvement Conceptualisation) .sqz files. It enables QA/QC of MUSIC models without requiring the MUSIC software or dongle.

## What Has Been Built

### 1. Core Parser Library (`src/openmusic/`)

| Module | Purpose | Status |
|--------|---------|--------|
| `extractor.py` | ZIP extraction from .sqz files | [x] Working |
| `parser.py` | Binary format parsing (Delphi T2DDF) | [x] Working |
| `exporter.py` | JSON, CSV, Excel export | [x] Working |
| `visualizer.py` | Graphviz DOT, ASCII diagrams | [x] Working |

### 2. Command-Line Tools (`scripts/`)

| Script | Purpose | Status |
|--------|---------|--------|
| `audit_sqz.py` | Complete audit with exports | [x] Working |
| `test_parser.py` | Test suite for example files | [x] Working |
| `inspect_binary.py` | Binary format inspector | [x] Working |
| `find_sqz_files.py` | J/V drive scanner (background) | [~] Running |

### 3. File Format Discovery

**MUSIC .sqz Structure:**
```
.sqz file (ZIP archive)
└── MusicDataFile (810KB typical)
    ├── Header: 0x06 0x05 T2DDF
    ├── DCGRAPH container
    │   ├── TDCVertex nodes
    │   ├── TReceivingNode (outfall)
    │   ├── TUrbanSourceNode (roof, road, land use)
    │   ├── TPondNode, TWetlandNode, etc.
    │   └── Pollutant flux labels (TN, TP, TSS, Gross Pollutants)
    └── Rainfall time series (if embedded)
```

## Example File Analysis Results

| File | Size | Nodes | Types |
|------|------|-------|-------|
| Test_Canberra.sqz | 81KB | 4 | 1 Receiving, 3 Urban Sources |
| 2066-02_Solar_EXG_and_DEV.sqz | 3.8MB | 16 | 10 UrbanSource, 6 Pond |
| 2066-02_BESS_EXG_and_DEV.sqz | 3.9MB | 20 | 11 UrbanSource, 9 Pond |
| Brisbane 1980 6min.sqz | 7MB | 0 | Rainfall data only |
| Ipswich 1990 6min.sqz | 7MB | 0 | Rainfall data only |

## Usage Examples

### Audit a single file
```powershell
cd d:\GitRepos\OpenMUSIC
python scripts\audit_sqz.py data\example\Test_Canberra.sqz -o data\outputs
```

**Outputs:**
- `Test_Canberra.json` - Full model data
- `Test_Canberra.csv` - Node summary table
- `Test_Canberra.xlsx` - Excel workbook
- `Test_Canberra_topology.dot` - Graphviz diagram
- `Test_Canberra_topology.txt` - ASCII topology

### Batch audit all files in a directory
```powershell
python scripts\audit_sqz.py "J:\Projects\MUSIC" -o data\outputs -r
```

### Background scan J/V drives
```powershell
python scripts\find_sqz_files.py -d J,V -o data\sqz_inventory.csv
```

## QA/QC Workflow

For a Principal reviewing a MUSIC model report:

1. **Extract model data** without needing MUSIC:
   ```python
   from openmusic import SQZExtractor, MusicFileParser
   
   with SQZExtractor() as extractor:
       music_file = extractor.extract("model.sqz")
       parser = MusicFileParser(music_file)
       model = parser.parse()
       print(f"Found {len(model.nodes)} nodes")
   ```

2. **Verify node counts** match report claims
3. **Check areas and parameters** in exported CSV/Excel
4. **Visualize topology** to confirm flow paths

## Technical Notes

### Known Limitations
- Node names still contain some binary artifacts (parsing refinement needed)
- Coordinates not yet extracted
- Node connections (edges) inferred from types, not explicit links
- Rainfall time series not yet decoded

### Next Steps
1. Refine string parsing to clean node names fully
2. Extract actual node parameters (area, coefficients)
3. Decode rainfall time series data
4. Parse treatment node parameters (pond size, wetland area)
5. Implement topology edge extraction

## Project Structure

```
OpenMUSIC/
├── README.md                    # Project documentation
├── PROJECT_STATUS.md           # This file
├── requirements.txt             # Python dependencies
├── src/openmusic/              # Parser library
│   ├── __init__.py
│   ├── extractor.py            # ZIP extraction
│   ├── parser.py               # Binary format parser
│   ├── exporter.py             # Export formats
│   └── visualizer.py           # Diagram generation
├── scripts/                    # CLI tools
│   ├── audit_sqz.py            # Main audit tool
│   ├── test_parser.py          # Test suite
│   ├── inspect_binary.py       # Binary inspector
│   └── find_sqz_files.py       # J/V drive scanner
├── data/
│   ├── example/                # Example .sqz files
│   └── outputs/                # Generated exports
└── .windsurf/plans/            # Planning documents
```

## Installation

```bash
cd d:\GitRepos\OpenMUSIC
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Contact

OpenMUSIC Project - For QA/QC without the dongle.
