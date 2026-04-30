# MUSIC Model Report

Generated: 2026-04-30 12:50
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

### Table 6.7 MUSIC source node parameter for post-development

| Catchment/MUSIC Node | Project Design Feature | Source Node Type | MUSIC Surface Type | Area (ha) | Effective Impervious Area | Rainfall Threshold (mm) |
|---|---|---|---|---|---|---|
| C2-1 x Construction Compoundsx} | 1 x Construction Compound | Urban | Industrial | 2.23 | 25% | 1.5 |
| C2-O & M FacilityzD | O&M Facility | Urban | Industrial | 3.82 | 25% | 1.5 |
| C2-SubstationH | Substation | Urban | Industrial | 2.23 | 25% | 1.5 |
| C2-BESSR | BESS | Urban | Industrial | 2.23 | 25% | 1.5 |
| C2-Developed Access Track | New Access Track | Urban | Unsealed road | 3.82 | 35% | 1.5 |
| C3-Existing Access Track8 | Existing Access Track | Urban | Unsealed road | 2.96 | 35% | 1.5 |
| C3-Developed Access Track=s | New Access Track | Urban | Unsealed road | 3.82 | 35% | 1.5 |
| C3-2 x Laydown Areas | 2 x Laydown Areas | Urban | Industrial | 2.23 | 25% | 1.5 |
| C3-onstruction Compound( | 1 x Construction Compound | Urban | Industrial | 2.96 | 25% | 1.5 |
| C3-Test BedW | Test Bed | Urban | Industrial | 3.82 | 25% | 1.5 |
| C3-Existing Access Track)=s | Existing Access Track | Urban | Unsealed road | 3.82 | 35% | 1.5 |

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
| Node_2288843652368 | Pond | area_ha: 3.8162; Pool Volume multipli: 0.0; Pollutants Inflow (k: 0.0 |
| Node_2288843651664 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_2288843651344 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_2288843648720 | Pond | area_ha: 2.227; Inflow (kg)@: 0.0 |
| Node_2288843650768 | Pond | area_ha: 3.8162 |
| Node_2288843649360 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_2288843649680 | Pond | area_ha: 3.8162 |
| Node_2288843648336 | Pond | area_ha: 2.3151; TP Inflow (kg): 0.0; Discharge (kg)@: 0.0 |
| Node_2288843648144 | Pond | area_ha: 641.5851 |

---

### Table 6.9 WQ Study Area Comparison: Mean Annual Pollutant Loads

| Pollutant | Pre-development (kg/year) | Post-development (kg/year) | Difference | Load Reduction | Neutral or beneficial effect |
|---|---|---|---|---|---|
| TSS | 0 | 0 | +0 | - | False |
| TP | 0 | 0 | +0 | - | False |
| TN | 0 | 0 | +0 | - | False |
| Gross Pollutants | 0 | 0 | +0 | - | False |

---

### Model Topology

The MUSIC model consists of 20 nodes arranged in the following configuration:

**Source Nodes (11):**
- banSourceNodehC3-Existing Access Track8C (Area: 2.96 ha)
- banSourceNodehC2-1 x Construction Compou (Area: 2.23 ha)
- banSourceNodehC2-O & M FacilityzD@x@d!Ou (Area: 3.82 ha)
- banSourceNodehC2-SubstationH!@pf@d!Outfl (Area: 2.23 ha)
- banSourceNodehC2-BESSR@J@d!Outflow (cubi (Area: 2.23 ha)
- banSourceNodehC2-Developed Access Track@ (Area: 3.82 ha)
- banSourceNodehC3-Developed Access Track= (Area: 3.82 ha)
- banSourceNodehC3-2 x Laydown Areas@2@!@d (Area: 2.23 ha)
- banSourceNodehC3-Construction Compound(U (Area: 2.96 ha)
- banSourceNodehC3-Test BedW@g@d!Outflow ( (Area: 3.82 ha)
- banSourceNodehC3-Existing Access Track)= (Area: 3.82 ha)

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
- banSourceNodehC3-Existing Acce: 2.96 ha
- banSourceNodehC2-1 x Construct: 2.23 ha
- banSourceNodehC2-O & M Facilit: 3.82 ha
- banSourceNodehC2-SubstationH!@: 2.23 ha
- banSourceNodehC2-BESSR@J@d!Out: 2.23 ha
- banSourceNodehC2-Developed Acc: 3.82 ha
- banSourceNodehC3-Developed Acc: 3.82 ha
- banSourceNodehC3-2 x Laydown A: 2.23 ha
- banSourceNodehC3-Construction : 2.96 ha
- banSourceNodehC3-Test BedW@g@d: 3.82 ha
- banSourceNodehC3-Existing Acce: 3.82 ha

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
