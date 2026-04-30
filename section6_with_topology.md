# MUSIC Model Report

Generated: 2026-04-30 13:15
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
| Node_1755359461264 | Pond | area_ha: 3.8162; Pool Volume multipli: 0.0; Pollutants Inflow (k: 0.0 |
| Node_1755359854864 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_1755359855120 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_1755359459984 | Pond | area_ha: 2.227; Inflow (kg)@: 0.0 |
| Node_1755359855376 | Pond | area_ha: 3.8162 |
| Node_1755359855888 | Pond | area_ha: 3.8162; second)@<: 0.0; Inflow (kg)@: 0.0 |
| Node_1755359855760 | Pond | area_ha: 3.8162 |
| Node_1755359856144 | Pond | area_ha: 2.3151; TP Inflow (kg): 0.0; Discharge (kg)@: 0.0 |
| Node_1755359856656 | Pond | area_ha: 641.5851 |

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

======================================================================
MUSIC Model Topology - Full Flow Path with Directionality
======================================================================


----------------------------------------------------------------------
Catchment Unknown Flow Path
----------------------------------------------------------------------

  3-Existing Access Track8
       |
       v
    [Buffer]
       |
       v
    [Mitre Drains]
       |
       v
    [Pond_1]

  2-1 x Construction Compound
       |
       v
    [Buffer]
       |
       v
    [Swale]
       |
       v
    [Pond_2]

  2-O
       |
       v
    [Buffer]
       |
       v
    [Swale]
       |
       v
    [Pond_3]

  2-SubstationH
       |
       v
    [Buffer]
       |
       v
    [Swale]
       |
       v
    [Pond_4]

  2-BESSR
       |
       v
    [Buffer]
       |
       v
    [Swale]
       |
       v
    [Pond_5]

  2-Developed Access Track
       |
       v
    [Buffer]
       |
       v
    [Mitre Drains]
       |
       v
    [Pond_6]

  3-Developed Access Track
       |
       v
    [Buffer]
       |
       v
    [Mitre Drains]
       |
       v
    [Pond_7]

  3-2 x Laydown Are
       |
       v
    [Buffer]
       |
       v
    [Swale]
       |
       v
    [Pond_8]

  3-Construction Compound
       |
       v
    [Buffer]
       |
       v
    [Swale]
       |
       v
    [Pond_9]

----------------------------------------------------------------------
Catchment Aggregation
----------------------------------------------------------------------

  [Unknown Post-Development Junction]

======================================================================
Connection Summary (From -> To)
======================================================================
From                                ->   To                            
----------------------------------------------------------------------
3-Existing Access Track8            ->   Pond_1                        
2-1 x Construction Compound         ->   Pond_2                        
2-O                                 ->   Pond_3                        
2-SubstationH                       ->   Pond_4                        
2-BESSR                             ->   Pond_5                        
2-Developed Access Track            ->   Pond_6                        
3-Developed Access Track            ->   Pond_7                        
3-2 x Laydown Are                   ->   Pond_8                        
3-Construction Compound             ->   Pond_9                        
======================================================================

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
