# Spatial Analysis & Geospatial Autocorrelation Log

> [!NOTE]
> Grid-level spatial aggregation, Moran's I spatial autocorrelation diagnostics, and multi-scale sensitivity analyses are fully documented in [10_spatial_statistical_validation.md](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/docs/research_log/10_spatial_statistical_validation.md).

## Date
2026-09-06

## Objective
Quantify spatial autocorrelation, spatial clustering, and scale sensitivity of Sentinel-2 spectral indices and Dynamic World built-up transitions across Chittoor District.

## Input Data
- Sentinel-2 Change Rasters (`data/processed/change_detection/`)
- Dynamic World Built-Up Layer (`data/raw/satellite/Chittoor_New_BuiltUp_2016_2025.tif`)

## Spatial Method
- Aggregated 69.26 million valid 10 m pixels to regular 1 km ($N = 6,902$ cells) and 500 m ($N = 27,669$ cells) spatial units.
- Row-standardized Queen contiguity distance-threshold spatial weight matrix ($W$, $d \le 0.015^\circ \approx 1.5\text{ km}$).
- Global Moran's $I$ computation:
  $$I = \frac{N}{S_0} \frac{\sum_i \sum_j w_{ij} (z_i - \bar{z})(z_j - \bar{z})}{\sum_i (z_i - \bar{z})^2}$$
- Evaluated regression residual spatial autocorrelation.

## Results
- **Mean NDBI Change:** Moran's $I = +0.7131$ ($z = 59.2$, $p < 10^{-16}$). Strong positive spatial clustering.
- **Mean NDVI Change:** Moran's $I = +0.6516$ ($z = 54.1$, $p < 10^{-16}$). Strong positive spatial clustering.
- **Dynamic World Built-Up:** Moran's $I = +0.4454$ ($z = 37.0$, $p < 10^{-16}$). Clustered peri-urban growth centers.
- **RQ1 Regression Residuals:** Moran's $I = +0.4462$ ($z = 37.1$).

## Validation Status
**PASS** — Spatial dependence explicitly quantified and documented.
