# MUSIC Model Report

Generated: 2026-04-30 12:21
Model Version: T2DDF

---

### Executive Summary

This water quality assessment utilises the MUSIC (Model for Urban Stormwater Improvement
Conceptualisation) modelling software to evaluate stormwater quality for the project area.
The model comprises 10 urban source catchments, 6 treatment nodes,
and 402 time series data arrays representing rainfall, runoff, and pollutant loads.

**Model Configuration:**
- MUSIC Version: T2DDF
- Total Nodes: 16
- Time Series Data Points: 402

**Pollutants Assessed:**
- Total Nitrogen (TN)
- Total Phosphorus (TP)
- Total Suspended Solids (TSS)
- Gross Pollutants


---

### Table 6.2 Modelled Water Quality Catchment Description

| Catchment | Total Area (ha) | Description |
|-----------|-----------------|-------------|
| C1 | 0.00 | C1 consists of Access Track, Construction Compound |
| C2 | 0.00 | C2 consists of Laydown Area, Construction Compound, Access Track |
| C3 | 0.00 | C3 consists of Access Track |

---

### Treatment Train Specifications

| Catchment/MUSIC Node | Treatment Train | Description/Parameters |
|---------------------|-----------------|------------------------|
| Node_2800130332688 | Pond | Standard configuration |
| Node_2800130332432 | Pond | Standard configuration |
| Node_2800130334288 | Pond | Standard configuration |
| Node_2800130334544 | Pond | i@: None |
| Node_2800130334032 | Pond | Standard configuration |
| Node_2800130335056 | Pond | Standard configuration |

---

### Pollutant Loads

No pollutant load data available in model.

---

### Model Topology

The MUSIC model consists of 16 nodes arranged in the following configuration:

**Source Nodes (10):**
- banSourceNodehC1-Existing Access TrackHR (Area: Unknown ha)
- banSourceNodehC3-Existing Access Trackh8 (Area: Unknown ha)
- banSourceNodehC1-Existing Access Track7; (Area: Unknown ha)
- banSourceNodehC1-Developed Access Track- (Area: Unknown ha)
- banSourceNodehC1-Construction Compound0@ (Area: Unknown ha)
- banSourceNodehC2-5 x Laydown Areasn@8t@d (Area: Unknown ha)
- banSourceNodehC2-1 x Construction Compou (Area: Unknown ha)
- banSourceNodehC2-Developed Access TrackE (Area: Unknown ha)
- banSourceNodehC3-Developed Access Trackx (Area: Unknown ha)
- banSourceNodehC3-Existing Access Track)) (Area: Unknown ha)

**Treatment Nodes (6):**
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
- Rainfall time series: 232 records
  - rainfall_0: 1478 time steps, total 203423757.3 mm
  - rainfall_1: 43 time steps, total -0.2 mm
  - rainfall_2: 43 time steps, total 131094.1 mm

**Catchment Parameters:**
- banSourceNodehC1-Existing Acce: N/A ha
- banSourceNodehC3-Existing Acce: N/A ha
- banSourceNodehC1-Existing Acce: N/A ha
- banSourceNodehC1-Developed Acc: N/A ha
- banSourceNodehC1-Construction : N/A ha
- banSourceNodehC2-5 x Laydown A: N/A ha
- banSourceNodehC2-1 x Construct: N/A ha
- banSourceNodehC2-Developed Acc: N/A ha
- banSourceNodehC3-Developed Acc: N/A ha
- banSourceNodehC3-Existing Acce: N/A ha

---

### Model Results Summary

**Time Series Extracted:**
- Pollutant: 164 series
- Rainfall: 232 series
- Unknown: 6 series

**Pollutant Load Statistics:**
- Total modelled pollutant load: -63,058,288,497.14 kg
- Number of pollutant time series: 164

---
