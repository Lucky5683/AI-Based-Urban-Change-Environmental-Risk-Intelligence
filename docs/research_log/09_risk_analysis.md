# Environmental Risk Analysis & Vulnerability Mapping Log

> [!NOTE]
> The construction, sensitivity testing, and spatial mapping of the multi-source Environmental Stress Indicator are fully documented in [11_environmental_stress_indicator.md](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/docs/research_log/11_environmental_stress_indicator.md).

## Date
2026-09-06

## Objective
Synthesize validated satellite evidence into an objective, scientifically defensible relative Environmental Stress Indicator across Chittoor District on a 1 km grid unit, evaluating urbanization stress, vegetation stress, and moisture stress.

## Input Data
- Sentinel-2 Change Rasters (`data/processed/change_detection/`): $\Delta\text{NDBI}$, $\Delta\text{NDVI}$, $\Delta\text{NDWI}$
- Dynamic World Built-Up Layer (`data/raw/satellite/Chittoor_New_BuiltUp_2016_2025.tif`)
- Longitudinal GEE Research Dataset (`data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv`)

## Method
- Primary spatial unit: 1 km regular grid ($N = 6,902$ cells).
- Sensitivity spatial unit: 500 m regular grid ($N = 27,669$ cells).
- Three components:
  1. Urbanization Component ($C_{\text{urb}}$) combining NDBI increase and Dynamic World built-up.
  2. Vegetation Component ($C_{\text{veg}}$) from NDVI decrease.
  3. Water/Moisture Component ($C_{\text{wat}}$) from NDWI decrease.
- Robust 99th percentile capping and $[0, 1]$ linear normalization.
- Weighting comparison: Transparent equal-weight baseline vs data-driven PCA loadings ($r = +0.928$).
- Selected model: Transparent equal weighting ($1/3, 1/3, 1/3$).

## Results
- Final stress score range: $[0.0000, 0.6771]$ (Mean = $0.2213$, Median = $0.2117$, Std = $0.1309$).
- Categorized into 4 relative stress quartiles (Q1: Lower, Q2: Moderate-Low, Q3: Moderate-High, Q4: Higher).
- Generated full-district grid CSV, top 200 rankings table, sensitivity comparisons, and 6 diagnostic maps.

## Validation Status
**PASS** — Relative environmental stress indicator constructed without arbitrary weights, with complete sensitivity and uncertainty documentation.
