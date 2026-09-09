# Research Log: Sentinel-2 Spectral Change Detection (2016 → 2025)

**Study Region:** Chittoor District, Andhra Pradesh, India  
**Stage:** 2016 → 2025 Sentinel-2 Image Change Detection  
**Execution Timestamp:** 2026-09-06T07:01:28Z  
**Execution Script:** `scripts/detect_sentinel2_change.py` (v1.0)  
**Status:** COMPLETE / PASSED  

---

## 1. Objective

The objective of this stage is to compute pixel-level Sentinel-2 spectral change rasters between the 2016 baseline and 2025 observation states for Chittoor District, Andhra Pradesh. This is strictly a **spectral change detection** procedure designed to quantify shifts in normalized spectral indices across the district.

> [!IMPORTANT]
> This stage performs **CHANGE DETECTION ONLY**. No machine learning, deep learning, land-cover classification, predictive forecasting, vulnerability/risk scoring, or spatial hotspot modeling was conducted in this step.

---

## 2. Input Features & Source Files

All 12 derived Sentinel-2 spectral feature rasters in `data/processed/features/` and 4 preprocessing valid-pixel masks in `data/processed/satellite/` were used as direct inputs:

### Western Partition (Tile 1: `0000000000-0000000000`)
- **Dimensions:** 13,568 columns × 12,893 rows (174,932,224 pixels)
- **CRS:** `EPSG:4326` | **Resolution:** ~10 m ($8.98315 \times 10^{-5}$ deg)
- **Bounds:** $[78.199244^\circ\text{E}, 12.623935^\circ\text{N}, 79.418078^\circ\text{E}, 13.782133^\circ\text{N}]$
- **2016 Inputs:** `sentinel2_2016_tile1_{ndvi,ndwi,ndbi}.tif`, mask: `sentinel2_2016_tile1_valid_mask.tif`
- **2025 Inputs:** `sentinel2_2025_tile1_{ndvi,ndwi,ndbi}.tif`, mask: `sentinel2_2025_tile1_valid_mask.tif`

### Eastern Partition (Tile 2: `0000000000-0000013568`)
- **Dimensions:** 4,195 columns × 12,893 rows (54,086,135 pixels)
- **CRS:** `EPSG:4326` | **Resolution:** ~10 m ($8.98315 \times 10^{-5}$ deg)
- **Bounds:** $[79.418078^\circ\text{E}, 12.623935^\circ\text{N}, 79.794921^\circ\text{E}, 13.782133^\circ\text{N}]$
- **2016 Inputs:** `sentinel2_2016_tile2_{ndvi,ndwi,ndbi}.tif`, mask: `sentinel2_2016_tile2_valid_mask.tif`
- **2025 Inputs:** `sentinel2_2025_tile2_{ndvi,ndwi,ndbi}.tif`, mask: `sentinel2_2025_tile2_valid_mask.tif`

---

## 3. Common-Valid Masking & Comparability Rule

To guarantee strict scientific comparability and avoid treating nodata, boundary padding, or unobserved pixels as spurious environmental change:

$$\text{common\_valid} = (\text{mask}_{2016} == 1) \land (\text{mask}_{2025} == 1) \land \text{isfinite}(f_{2016}) \land \text{isfinite}(f_{2025})$$

- **Condition Met:** Pixel difference is calculated directly.
- **Condition Not Met:** Output is strictly encoded as `NaN` (`nodata = np.nan`).
- **Zero-Fill Rule:** Invalid pixels are **NEVER** zero-filled.
- **Data Integrity:** Missing data is completely prevented from biasing change statistics.

---

## 4. Difference Formulas

Differences are calculated as the temporal subtraction of the 2016 baseline state from the 2025 observation state:

$$\Delta\text{NDVI} = \text{NDVI}_{2025} - \text{NDVI}_{2016}$$

$$\Delta\text{NDWI} = \text{NDWI}_{2025} - \text{NDWI}_{2016}$$

$$\Delta\text{NDBI} = \text{NDBI}_{2025} - \text{NDBI}_{2016}$$

- **$\Delta\text{NDVI} > 0$:** Vegetation-related spectral increase; **$\Delta\text{NDVI} < 0$:** Vegetation-related spectral decrease.
- **$\Delta\text{NDWI} > 0$:** Water-related spectral increase; **$\Delta\text{NDWI} < 0$:** Water-related spectral decrease.
- **$\Delta\text{NDBI} > 0$:** Built-up-related spectral increase; **$\Delta\text{NDBI} < 0$:** Built-up-related spectral decrease.

---

## 5. Processing Method & Memory Safety

1. **Block/Window Streaming:** Rasters were processed sequentially in vertical chunk windows of $1024 \text{ rows} \times \text{width}$ using `rasterio`.
2. **RAM Footprint:** Peak memory consumption was maintained below 250 MB throughout the pipeline, completely avoiding full-array loads of the $13,568 \times 12,893$ grids.
3. **Tile Preservation:** Tile 1 and Tile 2 were processed independently. No spatial merging, reprojection, resampling, or resizing was executed.
4. **GeoTIFF Output Profile:** Single-band `float32`, `nodata = np.nan`, LZW compression, internal tiling (`tiled=True`, `blockxsize=256`, `blockysize=256`).

Outputs generated in `data/processed/change_detection/`:
1. `sentinel2_tile1_ndvi_change_2016_2025.tif` (293.3 MB)
2. `sentinel2_tile2_ndvi_change_2016_2025.tif` (24.7 MB)
3. `sentinel2_tile1_ndwi_change_2016_2025.tif` (285.9 MB)
4. `sentinel2_tile2_ndwi_change_2016_2025.tif` (24.2 MB)
5. `sentinel2_tile1_ndbi_change_2016_2025.tif` (307.7 MB)
6. `sentinel2_tile2_ndbi_change_2016_2025.tif` (25.8 MB)

---

## 6. Quality-Control Statistics

Full-raster quality control statistics were computed across all 229,018,359 pixels:

### Summary of Valid Pixel Counts
- **Total District Pixels (Tile 1 + Tile 2):** 229,018,359
- **Common-Valid Pixels (Both Years Valid):** 69,256,014 (30.24% of bounding box)
- **NaN / Non-Common Pixels:** 159,762,345 (69.76% of bounding box)
- **Tile 1 Valid Pixels:** 64,152,235 (36.67% of Tile 1)
- **Tile 2 Valid Pixels:** 5,103,779 (9.44% of Tile 2)

### Raster Distribution Metrics

| Feature | Tile | Valid Pixels | Min | Max | Mean | Median | Std Dev | p1 | p5 | p25 | p75 | p95 | p99 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NDVI Change** | Tile 1 | 64,152,235 | -1.2261 | +1.2588 | +0.0020 | +0.0025 | 0.1204 | -0.3575 | -0.1895 | -0.0575 | +0.0655 | +0.1925 | +0.3105 |
| **NDVI Change** | Tile 2 | 5,103,779 | -1.7417 | +1.4982 | +0.0473 | +0.0435 | 0.1577 | -0.3995 | -0.2155 | -0.0295 | +0.1355 | +0.2985 | +0.4335 |
| **NDVI District** | **Agg.** | **69,256,014** | **-1.7417** | **+1.4982** | **+0.0053** | **+0.0055** | **0.1235** | **-0.3605** | **-0.1915** | **-0.0555** | **+0.0705** | **+0.2005** | **+0.3205** |
| **NDWI Change** | Tile 1 | 64,152,235 | -1.3133 | +1.3013 | +0.0119 | +0.0065 | 0.0859 | -0.1805 | -0.0995 | -0.0285 | +0.0435 | +0.1365 | +0.2895 |
| **NDWI Change** | Tile 2 | 5,103,779 | -1.4466 | +1.5698 | -0.0068 | -0.0055 | 0.1129 | -0.2815 | -0.1625 | -0.0625 | +0.0405 | +0.1575 | +0.3275 |
| **NDWI District** | **Agg.** | **69,256,014** | **-1.4466** | **+1.5698** | **+0.0105** | **+0.0055** | **0.0882** | **-0.1885** | **-0.1045** | **-0.0315** | **+0.0435** | **+0.1385** | **+0.2925** |
| **NDBI Change** | Tile 1 | 64,152,235 | -1.0852 | +0.8990 | +0.0095 | +0.0165 | 0.0981 | -0.2715 | -0.1585 | -0.0395 | +0.0635 | +0.1515 | +0.2715 |
| **NDBI Change** | Tile 2 | 5,103,779 | -0.9709 | +1.5269 | -0.0288 | -0.0185 | 0.1371 | -0.4045 | -0.2535 | -0.1085 | +0.0475 | +0.1855 | +0.3335 |
| **NDBI District** | **Agg.** | **69,256,014** | **-1.0852** | **+1.5269** | **+0.0067** | **+0.0135** | **0.1014** | **-0.2815** | **-0.1655** | **-0.0445** | **+0.0625** | **+0.1545** | **+0.2765** |

---

## 7. Screening Thresholds & Area Calculations

Screening thresholds of $\pm 0.10$ were evaluated to quantify substantial spectral shifts. Pixel areas are calculated using geodesic WGS84 ellipsoidal area ($96.7725\text{ m}^2 = 9.67725 \times 10^{-5}\text{ km}^2/\text{pixel}$) and nominal $10\text{ m} \times 10\text{ m}$ pixel area ($100\text{ m}^2 = 1.0 \times 10^{-4}\text{ km}^2/\text{pixel}$).

> [!CAUTION]
> **Screening Threshold Note:** These thresholds represent exploratory screening levels. They indicate spectral variations and must **NOT** be equated with definitive physical conversions (e.g., deforestation, construction, or surface water desiccation) without multi-source ground truthing.

### Screening Statistics Table

| Spectral Indicator | Screening Criterion | Descriptive Label | Pixel Count | % of Valid Pixels | Geodesic Area ($\text{km}^2$) | Nominal Area ($\text{km}^2$) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **NDVI Change** | $\Delta < -0.10$ | Vegetation-related spectral decrease | 9,832,911 | 14.20% | 951.56 | 983.29 |
| **NDVI Change** | $\Delta > +0.10$ | Vegetation-related spectral increase | 12,284,854 | 17.74% | 1,188.84 | 1,228.48 |
| **NDWI Change** | $\Delta < -0.10$ | Water-related spectral decrease | 3,896,157 | 5.63% | 377.04 | 389.62 |
| **NDWI Change** | $\Delta > +0.10$ | Water-related spectral increase | 6,008,088 | 8.68% | 581.42 | 600.81 |
| **NDBI Change** | $\Delta > +0.10$ | Built-up-related spectral increase | 8,774,633 | 12.67% | 849.15 | 877.46 |
| **NDBI Change** | $\Delta < -0.10$ | Built-up-related spectral decrease | 8,570,908 | 12.38% | 829.42 | 857.09 |

---

## 8. Spatial Results & Visualizations

Lightweight visual overview maps and empirical distribution plots were rendered into `outputs/figures/change_detection/`:

1. **Overview Spatial Previews** (Symmetric display range $[-0.5, +0.5]$, unclipped underlying rasters):
   - `ndvi_change_2016_2025.png`: Bounded overview showing western scrubland and eastern agricultural/forest responses.
   - `ndwi_change_2016_2025.png`: Spatial distribution of moisture and surface-water variations across riverbeds, tanks, and reservoirs.
   - `ndbi_change_2016_2025.png`: Distinct clusters of built-up-related spectral increases around Chittoor, Tirupati, and connecting highway corridors.

2. **Empirical Distribution Plots** (Sampled valid distribution, $N \approx 700,000$ pixels):
   - `ndvi_change_distribution.png`: Symmetric bell-shaped density centered at $\mu = +0.0053$ with 14.2% negative and 17.7% positive tails beyond $\pm 0.10$.
   - `ndwi_change_distribution.png`: Sharp peak around $\mu = +0.0105$ with narrower standard deviation ($\sigma = 0.088$).
   - `ndbi_change_distribution.png`: Well-balanced distribution centered near zero ($\mu = +0.0067$) with balanced positive and negative tails ($12.67\%$ vs $12.38\%$).

---

## 9. Spatial Integrity Verification

Spatial integrity checks were verified for all 6 generated change GeoTIFFs against their respective source inputs:
- **CRS:** Exact match (`EPSG:4326`) across all outputs.
- **Dimensions:** Exact match ($13,568 \times 12,893$ for Tile 1; $4,195 \times 12,893$ for Tile 2).
- **Transform & Resolution:** Exact match ($8.983152841195215 \times 10^{-5}$ deg).
- **Bounds:** Exact match.
- **Tile Adjacency:** Preserved with shared boundary at Longitude $79.418078^\circ\text{E}$ (Tile 1 right == Tile 2 left).
- **Status:** **PASS (100% verified)**.

---

## 10. Temporal Limitation & Scientific Interpretation

> [!WARNING]
> **Important Temporal Limitation:**  
> The 2016 and 2025 Sentinel-2 composites were constructed from different numbers of satellite observations (~53 scenes in 2016 vs ~253 scenes in 2025 due to the launch of Sentinel-2B in 2017).  
> **"2016 → 2025 differences represent differences between the available annual composite states and should not automatically be interpreted as a pure long-term land-cover trend."**

### Scientific Cautions:
1. **No Direct Causality:** Output values represent spectral reflectance shifts between two specific composite states, not proven ecological destruction or physical urban construction.
2. **Confounding Variables:** Spectral index deltas can be significantly influenced by:
   - Seasonality and antecedent precipitation preceding satellite acquisitions.
   - Cloud masking artifacts and residual aerosol variations.
   - Soil background brightness and surface soil moisture variations.
   - Agricultural cropping cycles and fallow land rotation.
   - Ephemeral water-level fluctuations in irrigation tanks and river basins.
   - Sensor geometry, radiometric calibration updates, and processing baseline differences.

---

## 11. Raw Data Protection & Immutability

- **Raw Satellite Imagery (`data/raw/satellite/`):** 5 files inspected, 0 modified.
- **Feature Rasters (`data/processed/features/`):** 12 files inspected, 0 modified.
- **Status:** **PASS (Read-only protection maintained)**.

---

## 12. Final Status Summary

```
==================================================
SENTINEL-2 CHANGE DETECTION STATUS
==================================================
Feature pairs processed: 6
NDVI change: PASS
NDWI change: PASS
NDBI change: PASS
Common-valid masking: PASS
Spatial integrity: PASS
Statistics: PASS
Visualization: PASS
Manifest: PASS
Research log: PASS

Raw data modified: 0

Overall change detection:
PASS

NEXT PROJECT STEP:
Integrated spatial change interpretation
==================================================
```
