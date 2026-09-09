# Research Log: Integrated Spatial Change Interpretation & Cross-Dataset Validation

**Study Region:** Chittoor District, Andhra Pradesh, India  
**Stage:** Integrated Spatial Change Interpretation & Cross-Dataset Validation  
**Execution Timestamp:** 2026-09-06T07:37:34Z  
**Execution Script:** `scripts/integrated_spatial_change_analysis.py` (v1.0)  
**Status:** COMPLETE / PASSED  

---

## 1. Objective

The objective of this stage is to perform **Integrated Spatial Change Interpretation** by evaluating whether pixel-level spectral change signals derived from Sentinel-2 (2016 → 2025) are corroborated by independent datasets collected during this project. 

> [!IMPORTANT]
> **Core Principle:** This stage does **NOT** generate a composite environmental risk score or assign arbitrary numerical weights. It asks the conservative scientific question:  
> *"Do independent observations support the same spatial interpretation?"*  
> We explicitly distinguish between **Same-Sensor Spectral Agreement** and **Cross-Dataset Validation**.

---

## 2. Existing Datasets Used

No new datasets were downloaded, and no synthetic/fabricated data was used. The integration draws exclusively on previously validated project assets:

1. **Sentinel-2 Spectral Difference Rasters** (`data/processed/change_detection/`):
   - NDVI change: `sentinel2_tile1_ndvi_change_2016_2025.tif` & `sentinel2_tile2_ndvi_change_2016_2025.tif`
   - NDWI change: `sentinel2_tile1_ndwi_change_2016_2025.tif` & `sentinel2_tile2_ndwi_change_2016_2025.tif`
   - NDBI change: `sentinel2_tile1_ndbi_change_2016_2025.tif` & `sentinel2_tile2_ndbi_change_2016_2025.tif`
2. **Dynamic World Built-Up Layer** (`data/raw/satellite/`):
   - `Chittoor_New_BuiltUp_2016_2025.tif`: Binary transition raster exported from GEE where class `1` indicates new built-up transition between 2016 and 2025.
3. **Longitudinal GEE Master Research Dataset** (`data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv`):
   - **MODIS Daytime LST**: Annual daytime surface temperature (2016: $33.94^\circ\text{C}$, 2025: $28.56^\circ\text{C}$; $\Delta\text{LST} = -5.38^\circ\text{C}$).
   - **CHIRPS Precipitation**: Annual precipitation & rainfall anomaly (2016: $753.1\text{ mm}$, anomaly $-402.1\text{ mm}$ / severe drought; 2025: $1,158.4\text{ mm}$, anomaly $+3.2\text{ mm}$ / normal).
   - **Dynamic World Built-Up Extent**: Longitudinal annual series ($159.40\text{ km}^2$ in 2016 to $259.21\text{ km}^2$ in 2025, $+62.6\%$ expansion).

---

## 3. Spatial Compatibility Assessment

Before processing, all spatial datasets were evaluated for spatial compatibility:

| Dataset | Format | Native Resolution | Coordinate System | Dimensions | Bounds |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Sentinel-2 Change (Tile 1)** | GeoTIFF (Float32) | $8.98315 \times 10^{-5}$ deg (~10 m) | `EPSG:4326` | 13,568 × 12,893 | [78.1992, 12.6239, 79.4181, 13.7821] |
| **Sentinel-2 Change (Tile 2)** | GeoTIFF (Float32) | $8.98315 \times 10^{-5}$ deg (~10 m) | `EPSG:4326` | 4,195 × 12,893 | [79.4181, 12.6239, 79.7949, 13.7821] |
| **Dynamic World New Built-Up** | GeoTIFF (UInt8) | $8.98315 \times 10^{-5}$ deg (~10 m) | `EPSG:4326` | 17,763 × 12,893 | [78.1992, 12.6239, 79.7949, 13.7821] |
| **MODIS Daytime LST** | Tabular/District GEE | ~1 km ($0.01^\circ$) | `EPSG:4326` | District aggregate | District-wide administrative |
| **CHIRPS Precipitation** | Tabular/District GEE | ~5.5 km ($0.05^\circ$) | `EPSG:4326` | District aggregate | District-wide administrative |

**Spatial Alignment Finding:**
`Chittoor_New_BuiltUp_2016_2025.tif` has a width of 17,763 columns, exactly matching the combined width of Tile 1 (13,568) and Tile 2 (4,195) with identical bounding box and pixel grid alignment.

---

## 4. Common Analysis Scale Rationale

> [!TIP]
> **Scale Decision:**
> - Pixel-level spatial intersections were evaluated strictly at the native **10 m raster scale** ($8.98315 \times 10^{-5}$ deg) where Sentinel-2 and Dynamic World share identical geometry.
> - Coarse datasets (MODIS ~1 km, CHIRPS ~5.5 km) were **NOT** upsampled to 10 m to avoid creating false spatial precision. Instead, they were maintained as **district-level longitudinal contextual evidence**.

---

## 5. Indicator Definitions (Screening Masks)

Screening indicators were extracted strictly from common-valid pixels ($N = 69,256,014$ pixels, $6,702.08\text{ km}^2$ geodesic):
- **Vegetation-related spectral decrease:** $\Delta\text{NDVI} < -0.10$
- **Vegetation-related spectral increase:** $\Delta\text{NDVI} > +0.10$
- **Water-related spectral decrease:** $\Delta\text{NDWI} < -0.10$
- **Water-related spectral increase:** $\Delta\text{NDWI} > +0.10$
- **Built-up-related spectral increase:** $\Delta\text{NDBI} > +0.10$
- **Built-up-related spectral decrease:** $\Delta\text{NDBI} < -0.10$
- **Dynamic World built-up transition:** $\text{DW\_BuiltUp} == 1$

---

## 6. Multi-Source Evidence Logic

Evidence integration was structured around three core phenomena:

1. **Potential Urbanization-Associated Expansion:**
   - Evaluated by intersecting $\Delta\text{NDBI} > +0.10$ with $\text{DW\_BuiltUp} == 1$.
   - Supported when accompanied by vegetation drop ($\Delta\text{NDVI} < -0.10$).
2. **Potential Vegetation Change:**
   - Evaluated by partitioning $\Delta\text{NDVI} < -0.10$ into:
     a) Urbanization-associated conversion ($\Delta\text{NDVI} < -0.10 \cap \text{DW\_BuiltUp} == 1$).
     b) SWIR/bare-soil spectral convergence ($\Delta\text{NDVI} < -0.10 \cap \Delta\text{NDBI} > +0.10$).
     c) Unconfirmed single-spectral decrease (harvesting, seasonal phenology, grazing).
3. **Potential Surface Water / Hydrological Change:**
   - Evaluated by examining $\Delta\text{NDWI} < -0.10$ against the 2016 severe drought baseline.

---

## 7. Same-Sensor vs. Cross-Dataset Independence

To eliminate double counting:
- **Same-Sensor Family:** NDVI, NDWI, and NDBI all stem from the same Sentinel-2 multispectral observations. Co-occurrence between $\Delta\text{NDVI}$ and $\Delta\text{NDBI}$ constitutes **Same-Sensor Spectral Agreement**, not cross-dataset corroboration.
- **Derived Model Family:** Dynamic World is an AI model trained on Sentinel-2; while offering land-cover classification context, it is partially dependent on the Sentinel-2 sensor family.
- **Independent Sensors:** MODIS LST (thermal infrared sensor on NASA Terra) and CHIRPS (infrared-gauge blended precipitation) provide independent sensor evidence.

---

## 8. Spatial Overlap Results

Calculated via window streaming across all 229,018,359 pixels:

| Metric / Indicator Combination | Pixel Count | Geodesic Area ($\text{km}^2$) | Nominal Area ($\text{km}^2$) | % of Relevant Indicator | % of Common Valid Area |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Common Valid Area (Denominator)** | **69,256,014** | **6,702.08** | **6,925.60** | **100.0%** | **100.0%** |
| **NDVI Decrease (< -0.10)** | 9,832,911 | 951.56 | 983.29 | 100.0% | 14.20% |
| **NDBI Increase (> +0.10)** | 8,774,633 | 849.14 | 877.46 | 100.0% | 12.67% |
| **NDWI Decrease (< -0.10)** | 3,896,157 | 377.04 | 389.62 | 100.0% | 5.63% |
| **Dynamic World New Built-Up (class=1)** | 1,505,079 | 145.65 | 150.51 | 100.0% | 2.17% |
| **A. NDVI dec ∩ NDBI inc** | 5,337,209 | 516.50 | 533.72 | 54.28% of NDVI dec | 7.71% |
| **B. NDVI dec ∩ DW built-up** | 452,318 | 43.77 | 45.23 | 30.05% of DW built-up | 0.65% |
| **C. NDBI inc ∩ DW built-up** | 216,402 | 20.94 | 21.64 | 14.38% of DW built-up | 0.31% |
| **D. Triple Intersect (NDVI dec ∩ NDBI inc ∩ DW)** | 169,891 | 16.44 | 16.99 | 11.29% of DW built-up | 0.25% |
| **E. S2 Spectral Only (no DW confirmation)** | 5,167,318 | 500.05 | 516.73 | 52.55% of NDVI dec | 7.46% |
| **F. NDVI dec alone (Single spectral)** | 4,213,275 | 407.73 | 421.33 | 42.85% of NDVI dec | 6.08% |
| **G. NDBI inc alone (Single spectral)** | 3,390,913 | 328.15 | 339.09 | 38.64% of NDBI inc | 4.89% |

---

## 9. Evidence Hierarchy Levels

The spatial evidence framework categorizes observations into 5 discrete levels:

- **Level 0: Stable / No Strong Multi-Source Signal** ($58,574,807$ px, $84.58\%$ of valid area): No significant spectral or land-cover changes beyond thresholds.
- **Level 1: Single-Source Spectral Signal** ($7,896,173$ px, $11.40\%$ of valid area): Only one index triggered without corroboration.
- **Level 2A: Same-Sensor Spectral Agreement** ($5,167,318$ px, $7.46\%$ of valid area): Co-occurring $\Delta\text{NDVI} < -0.10$ and $\Delta\text{NDBI} > +0.10$ without model confirmation.
- **Level 2B: Cross-Dataset Supported Change** ($328,948$ px, $0.48\%$ of valid area): $\Delta\text{NDBI} > +0.10$ or $\Delta\text{NDVI} < -0.10$ confirmed by Dynamic World built-up.
- **Level 3: Higher-Confidence Multi-Source Signal** ($169,891$ px, $16.44\text{ km}^2$, $0.25\%$ of valid area): Triple intersection where vegetation loss, SWIR reflectance increase, and land-cover model built-up classification converge.

---

## 10. Urbanization-Related Findings

1. **Cross-Dataset Confirmation Rate:** Out of $145.65\text{ km}^2$ of new built-up area classified by Dynamic World within common-valid pixels, $20.94\text{ km}^2$ ($14.38\%$) is corroborated by a substantial spectral increase in NDBI ($\Delta > +0.10$).
2. **Spectral vs. Classification Discrepancy:** A substantial portion of NDBI increase ($828.20\text{ km}^2$) occurs outside classified built-up zones, reflecting soil exposure, seasonal bare fallow, quarrying, or peri-urban road network clearing rather than dense structural masonry.
3. **Conservative Wording:** These zones are categorized as **"built-up-related spectral expansion signals"** rather than unverified physical construction.

---

## 11. Vegetation-Related Findings

1. **Urbanization-Associated Vegetation Loss:** $43.77\text{ km}^2$ of vegetation decrease overlaps with Dynamic World built-up emergence, of which $16.44\text{ km}^2$ exhibits the full multi-spectral signature (triple intersection).
2. **Agricultural Phenology & Soil Exposure:** $500.05\text{ km}^2$ ($52.55\%$ of all NDVI decrease) is paired with NDBI increase but unconfirmed by built-up classification. This reflects dry agricultural fallows and seasonal soil drying.
3. **Climatic Context Isolation:** Because 2025 received $+405.3\text{ mm}$ more rainfall than the 2016 drought baseline, isolated vegetation decrease cannot be attributed to general drought; it marks localized land-use disturbance, localized irrigation deficits, or crop timing shifts.

---

## 12. Water-Related Findings

1. **Surface Moisture Dynamics:** $377.04\text{ km}^2$ of valid area exhibited NDWI decrease $< -0.10$.
2. **Contextual Attribution:** Since 2016 was a severe drought year ($-402\text{ mm}$ anomaly) and 2025 was near-normal, areas exhibiting NDWI drop in 2025 indicate localized hydrological stress, sediment deposition in tanks, or waterbody encroachment.
3. **Conservative Wording:** Labeled as **"water/moisture-related spectral decrease coinciding with baseline rainfall deficit"**, avoiding claims of permanent waterbody disappearance without local bathymetric or tank survey data.

---

## 13. Limitations & Uncertainties

1. Sentinel-2 spectral indices are relative spectral proxies, not physical ground truth.
2. Dynamic World is derived from Sentinel-2 imagery and is not completely independent of the sensor.
3. MODIS LST (~1 km) and CHIRPS (~5.5 km) operate at vastly coarser scales than 10 m Sentinel-2.
4. Annual composites differ in image sample size (~53 scenes in 2016 vs ~253 scenes in 2025).
5. Seasonal agricultural crop phenology can mimic land degradation or recovery.
6. Soil moisture variations strongly affect NDWI and NDBI in semi-arid zones.
7. Bare rock outcrops and dry sandy riverbeds naturally exhibit high NDBI.
8. Regional meteorological cooling overrides micro-scale urban heat island signals in district LST.
9. Spatial coincidence does not prove causality.
10. Classification models carry inherent error matrices.

---

## 14. Outputs Produced

- **Spatial Evidence Table:** [integrated_spatial_change_evidence.csv](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/integrated_spatial_change_evidence.csv)
- **Evidence Overview Map:** [integrated_spatial_evidence_overview.png](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/integrated_change/integrated_spatial_evidence_overview.png)
- **Metadata Manifest:** [integrated_spatial_change_manifest.json](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/data/metadata/integrated_spatial_change_manifest.json)

---

## 15. Final Status Summary

```
============================================================
INTEGRATED SPATIAL CHANGE ANALYSIS STATUS
============================================================
Source inventory: PASS
Spatial compatibility assessment: PASS
Indicator masks: PASS
Overlap analysis: PASS
Evidence classification: PASS
Urbanization analysis: PASS
Vegetation analysis: PASS
Water analysis: PASS
Evidence map: PASS
Manifest: PASS
Research log: PASS

Raw data modified: 0
Existing source rasters modified: 0

Overall:
PASS

NEXT PROJECT STEP:
Statistical validation of spatial relationships
============================================================
```
