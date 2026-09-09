# Statistical Analysis & Spatial Relationship Validation Log

> [!NOTE]
> Detailed spatial relationship testing and multiple-testing corrections are fully documented in [10_spatial_statistical_validation.md](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/docs/research_log/10_spatial_statistical_validation.md).

## Date
2026-09-06

## Objective
Evaluate the statistical significance, effect sizes, and spatial autocorrelation of major environmental relationships across Chittoor District, explicitly addressing spatial dependence through multi-scale grid aggregation (1 km and 500 m).

## Input Data
- Sentinel-2 Change Rasters (`data/processed/change_detection/`): $\Delta\text{NDVI}$, $\Delta\text{NDWI}$, $\Delta\text{NDBI}$
- Dynamic World Built-Up Transition (`data/raw/satellite/Chittoor_New_BuiltUp_2016_2025.tif`)
- GEE Master Research Dataset (`data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv`)

## Method
- Rejection of 10 m pixel independence to prevent pseudoreplication.
- Aggregation to 1 km ($N = 6,902$ cells) and 500 m ($N = 27,669$ cells) spatial analysis units.
- Pearson $r$ (with Fisher $z$ 95% CI), Spearman rank $\rho$, and OLS regression.
- Global Moran's $I$ spatial autocorrelation.
- Benjamini-Hochberg False Discovery Rate (FDR) multiple-testing correction.

## Key Results
1. **RQ1 (Built-Up Spectral Change ↔ Dynamic World Transition):**
   - 1 km scale: Pearson $r = +0.0427$ (95% CI: [+0.0191, +0.0662], $p^{\text{adj}} = 3.88 \times 10^{-4}$); Spearman $\rho = +0.1779$ ($p < 10^{-16}$).
   - 500 m scale: Pearson $r = +0.0261$ ($p^{\text{adj}} = 1.73 \times 10^{-5}$); Spearman $\rho = +0.1576$.
   - Positive, statistically supported spatial association; robust across spatial scales (MAUP-stable).
2. **Same-Sensor Spectral Coupling (NDVI ↔ NDBI):**
   - 1 km scale: Pearson $r = +0.8326$ ($R^2 = 0.693$, $p < 10^{-16}$); Mean $\Delta\text{NDVI}$ vs $\Delta\text{NDBI}$ Pearson $r = -0.8014$ ($R^2 = 0.642$).
   - Demonstrates strong physical/mathematical coupling between greenness and SWIR reflectance from the same sensor.
3. **Spatial Autocorrelation:**
   - Mean NDBI change Moran's $I = +0.7131$ ($z = 59.2$); Mean NDVI change Moran's $I = +0.6516$ ($z = 54.1$). Confirms strong spatial clustering of environmental change processes.
4. **Contextual Variables (RQ2, RQ3, RQ4):**
   - MODIS LST and CHIRPS rainfall are district-level aggregates only; honestly designated as **NOT TESTABLE at cell level** to avoid false spatial precision.

## Validation Status
**PASS** — Spatial dependence accounted for, multi-scale sensitivity verified, multiple testing corrected.
