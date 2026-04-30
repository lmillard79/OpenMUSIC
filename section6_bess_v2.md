# MUSIC Model Report

Generated: 2026-04-30 12:41
Model Version: T2DDF

---

### Executive Summary

This water quality assessment utilises the MUSIC (Model for Urban Stormwater Improvement
Conceptualisation) modelling software to evaluate stormwater quality for the project area.
The model comprises 11 urban source catchments, 9 treatment nodes,
and 443 time series data arrays representing rainfall, runoff, and pollutant loads.

**Model Configuration:**
- MUSIC Version: T2DDF
- Total Nodes: 20
- Time Series Data Points: 443

**Pollutants Assessed:**
- Total Nitrogen (TN)
- Total Phosphorus (TP)
- Total Suspended Solids (TSS)
- Gross Pollutants


---

### Table 6.2 Modelled Water Quality Catchment Description

| Catchment | Total Area (ha) | Description |
|-----------|-----------------|-------------|
| C2 | 14.31 | C2 consists of Construction Compound, Urban, Substation, BESS, Access Track |
| C3 | 19.60 | C3 consists of Access Track, Laydown Area, Construction Compound, Urban |

---

### Treatment Train Specifications

| Catchment/MUSIC Node | Treatment Train | Description/Parameters |
|---------------------|-----------------|------------------------|
| Node_2148883812240 | Pond | area_ha: 3.8162; Pool Volume multipli: 0.0; Pollutants Inflow (k: 0.0 |
| Node_2148883812560 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_2148883812816 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_2148883810960 | Pond | area_ha: 2.227; Inflow (kg)@: 0.0 |
| Node_2148883813072 | Pond | area_ha: 3.8162 |
| Node_2148883813584 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_2148883813456 | Pond | area_ha: 3.8162 |
| Node_2148883813840 | Pond | area_ha: 2.3151; TP Inflow (kg): 0.0; Discharge (kg)@: 0.0 |
| Node_2148883814352 | Pond | area_ha: 641.5851 |

---

### Pollutant Loads

No pollutant load data available in model.

---

### Model Topology

The MUSIC model consists of 20 nodes arranged in the following configuration:

**Source Nodes (11):**
- banSourceNodehC3-Existing Access Track8C (Area: Unknown ha)
- banSourceNodehC2-1 x Construction Compou (Area: Unknown ha)
- banSourceNodehC2-O & M FacilityzD@x@d!Ou (Area: Unknown ha)
- banSourceNodehC2-SubstationH!@pf@d!Outfl (Area: Unknown ha)
- banSourceNodehC2-BESSR@J@d!Outflow (cubi (Area: Unknown ha)
- banSourceNodehC2-Developed Access Track@ (Area: Unknown ha)
- banSourceNodehC3-Developed Access Track= (Area: Unknown ha)
- banSourceNodehC3-2 x Laydown Areas@2@!@d (Area: Unknown ha)
- banSourceNodehC3-Construction Compound(U (Area: Unknown ha)
- banSourceNodehC3-Test BedW@g@d!Outflow ( (Area: Unknown ha)
- banSourceNodehC3-Existing Access Track)= (Area: Unknown ha)

**Treatment Nodes (9):**
- PondNode
- PondNode
- PondNode
- PondNode
- PondNode
- PondNode
- PondNode
- PondNode
- PondNode

**Flow Path:** Source -> Buffer -> Treatment -> Receiving

---

### Model Inputs

**Meteorological Data:**
- Rainfall time series: 265 records
  - rainfall_0: 1477 time steps, total 203423744.0 mm
  - rainfall_2: 1477 time steps, total 203423744.0 mm
  - rainfall_4: 1478 time steps, total 203423757.3 mm

**Catchment Parameters:**
- banSourceNodehC3-Existing Acce: 2.9629 ha
- banSourceNodehC2-1 x Construct: 2.227 ha
- banSourceNodehC2-O & M Facilit: 3.8162 ha
- banSourceNodehC2-SubstationH!@: 2.227 ha
- banSourceNodehC2-BESSR@J@d!Out: 2.227 ha
- banSourceNodehC2-Developed Acc: 3.8162 ha
- banSourceNodehC3-Developed Acc: 3.8162 ha
- banSourceNodehC3-2 x Laydown A: 2.227 ha
- banSourceNodehC3-Construction : 2.9629 ha
- banSourceNodehC3-Test BedW@g@d: 3.8162 ha
- banSourceNodehC3-Existing Acce: 3.8162 ha

---

### Model Results Summary

**Time Series Extracted:**
- Pollutant: 172 series
- Rainfall: 265 series
- Unknown: 6 series

**Pollutant Load Statistics:**
- Total modelled pollutant load: -63,165,793,848.88 kg
- Number of pollutant time series: 172

---
