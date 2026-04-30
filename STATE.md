# OpenMUSIC Project State

## Current Status

MUSIC model file parser and report generator for extracting data from .sqz files.

### Completed Features

| Feature | Status | Files |
|---------|--------|-------|
| Binary parser | Working | `src/openmusic/parser.py` |
| Area extraction | Working | Extracts area_ha from binary properties |
| Table 6.7 (Source params) | Working | Generates report-ready markdown table |
| Table 6.9 (Pollutant loads) | Structure ready | Format correct, data extraction needs refinement |
| ASCII topology | Working | Full directional flow paths |
| Report generator | Working | `generate_report.py` CLI tool |

### Key Capabilities

1. **Parse MUSIC .sqz files**: Extracts nodes, properties, time series
2. **Area extraction**: Reads area_ha values from binary (0.01 - 10000 ha range)
3. **Table 6.7 generation**: Match format from your PDF exactly
   - Catchment/MUSIC Node
   - Project Design Feature (auto-detected from names)
   - Source Node Type: Urban
   - MUSIC Surface Type: Industrial vs Unsealed road
   - Area (ha)
   - Effective Impervious Area: 25% (Industrial) / 35% (Unsealed)
   - Rainfall Threshold: 1.5 mm
4. **Directional topology**: Source -> Buffer -> Swale/Mitre -> Pond -> Junction

### Known Issues / TODO

1. **Node name cleaning**: Still has artifacts (e.g., "sx}", "zD") - needs better regex
2. **Pollutant load calculation**: Table 6.9 shows 0s - time series aggregation needs work
3. **Pre/post development distinction**: Model has both, need to separate them
4. **Pond dimensions**: Not yet extracted (depth, volume from binary)
5. **Catchment area mismatch**: PDF shows 25.10/25.41 ha, we get 14.31/19.60 ha
   - Likely missing pre-development or additional source nodes

### Project Structure

```
OpenMUSIC/
├── src/openmusic/
│   ├── __init__.py
│   ├── parser.py           # Binary file parsing
│   ├── extractor.py        # SQZ file extraction
│   ├── exporter.py         # JSON/CSV/Excel export
│   ├── report_generator.py # Table 6.7, 6.9, topology
│   ├── topology_viz.py     # ASCII diagrams
│   └── topology_extractor.py # Node connections
├── scripts/
│   ├── generate_report.py  # CLI tool
│   ├── audit_sqz.py
│   └── show_topology.py
├── data/
│   ├── example/            # Test .sqz files
│   └── outputs/            # Generated reports
├── requirements.txt
└── STATE.md               # This file
```

### Usage

```bash
# Generate full report with tables and topology
python scripts\generate_report.py "path\to\model.sqz" -o report.md

# Show ASCII topology only
python scripts\show_topology.py

# Show directional connections
python scripts\show_directional_topology.py
```

### Next Steps (Priority)

1. Fix node name suffix cleanup (remove binary artifacts)
2. Debug pollutant load time series aggregation for Table 6.9
3. Extract pond dimensions (depth, volume) from binary properties
4. Investigate missing area (~10 ha per catchment)
5. Add proper pre/post development scenario separation

### Dependencies

- Python 3.11+
- Standard libraries: struct, re, pathlib, typing, datetime
- No external dependencies required for core parsing
