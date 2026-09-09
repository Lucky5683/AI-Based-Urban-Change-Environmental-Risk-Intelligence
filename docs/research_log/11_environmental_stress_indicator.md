# Research Log: Environmental Stress Indicator Construction

**Study Region:** Chittoor District, Andhra Pradesh, India  
**Stage:** Environmental Stress / Risk Indicator Construction  
**Execution Timestamp:** 2026-09-06T07:56:17Z  
**Execution Script:** `scripts/build_environmental_stress_indicator.py` (v1.0)  
**Status:** COMPLETE / PASSED  

---

## 1. Objective

The objective of this stage is to synthesize the validated multi-source spatial evidence into a reproducible, scientifically defensible **Environmental Stress Indicator** for Chittoor District. The indicator identifies geographic areas exhibiting relatively elevated environmental stress based on observed decadal changes (2016 → 2025) across urbanization dynamics, vegetation condition, and surface moisture regimes.

> [!IMPORTANT]
> **Strict Operational Boundary:**  
> This indicator represents **relative environmental stress** based on observed satellite evidence. It is **NOT** a disaster risk map, building-collapse forecast, hazard prediction, or government-certified zoning regulation.

---

## 2. Definition of Environmental Stress

In this research framework, **Environmental Stress** is defined as:
> *"The localized compound pressure exerted on terrestrial ecosystems and hydrological systems resulting from the co-occurrence of anthropogenic built-up expansion, vegetation-related spectral degradation, and water/moisture-related spectral decline."*

The score is explicitly **relative** to the distribution within Chittoor District and bounded within the continuous interval $[0, 1]$.

---

## 3. Spatial Unit of Analysis

As established during the spatial statistical validation stage, millions of 10 m pixels suffer from severe spatial autocorrelation. Therefore:
- **Primary Analysis Scale: 1 km Grid Cells ($100 \times 100$ native 10 m pixels)**
  - Dimension: $\approx 993.3\text{ m} \times 973.5\text{ m} \approx 0.967\text{ km}^2$ per cell ($0.008983^\circ$).
  - Effective Sample Size: **$N = 6,902$ spatial cells** covering Chittoor District (meeting $\ge 50\%$ common-valid coverage).
- **Sensitivity Scale: 500 m Grid Cells ($50 \times 50$ native 10 m pixels)**
  - Dimension: $\approx 496.7\text{ m} \times 486.8\text{ m} \approx 0.242\text{ km}^2$ per cell ($0.004492^\circ$).
  - Sample Size: **$N = 27,669$ spatial cells**.

---

## 4. Input Spatial Indicators

The spatial indicator synthesizes four primary raster assets:
1. **Sentinel-2 NDBI Increase ($\Delta\text{NDBI} > +0.10$):** Built-up and impervious surface-related spectral increase.
2. **Dynamic World Built-Up Transition ($\text{class} == 1$):** Decadal new built-up land-cover emergence.
3. **Sentinel-2 NDVI Decrease ($\Delta\text{NDVI} < -0.10$):** Vegetation-related spectral decrease.
4. **Sentinel-2 NDWI Decrease ($\Delta\text{NDWI} < -0.10$):** Water- and surface moisture-related spectral decrease.

---

## 5. Data Independence & Component Structure

To avoid double counting same-sensor spectral indices while rewarding cross-dataset validation, indicators were structured into three modular components:

$$\text{Component 1: Urbanization Stress } (C_{\text{urb}})$$
$$\text{Component 2: Vegetation Stress } (C_{\text{veg}})$$
$$\text{Component 3: Water/Moisture Stress } (C_{\text{wat}})$$

- **Urbanization Component:** Combines Sentinel-2 NDBI increase and Dynamic World built-up transition, ensuring mutual cross-dataset agreement is evaluated without treating them as independent additive layers.
- **Vegetation Component:** Captures green canopy loss from Sentinel-2 NDVI delta.
- **Water/Moisture Component:** Captures surface water and soil moisture drying from Sentinel-2 NDWI delta.

---

## 6. Normalization Methodology

To prevent indicators with differing dynamic ranges from arbitrarily dominating the composite score, robust 99th-percentile capping was applied before linear $[0, 1]$ rescaling:

$$\tilde{x}_k = \min \left( 1.0, \frac{x_k}{p_{99}(x_k)} \right)$$

### Normalization Parameters (1 km Grid):
- `prop_ndbi_inc`: $p_{99} = 0.5011$ (50.1% cell coverage)
- `prop_dw_builtup`: $p_{99} = 0.1600$ (16.0% cell coverage)
- `prop_ndvi_dec`: $p_{99} = 0.4859$ (48.6% cell coverage)
- `prop_ndwi_dec`: $p_{99} = 0.3054$ (30.5% cell coverage)

### Component Formulas:
$$C_{\text{urb}} = 0.50 \cdot \tilde{x}_{\text{ndbi\_inc}} + 0.50 \cdot \tilde{x}_{\text{dw\_builtup}}$$
$$C_{\text{veg}} = \tilde{x}_{\text{ndvi\_dec}}$$
$$C_{\text{wat}} = \tilde{x}_{\text{ndwi\_dec}}$$

---

## 7. Weighting Methods Tested

Arbitrary weights were strictly rejected. Two defensible weighting approaches were implemented and compared:

1. **Method A: Transparent Baseline (Equal Weighting)**
   $$w_{\text{urb}} = \frac{1}{3} \approx 0.3333, \quad w_{\text{veg}} = \frac{1}{3} \approx 0.3333, \quad w_{\text{wat}} = \frac{1}{3} \approx 0.3333$$
2. **Method B: Principal Component Analysis (Data-Driven PC1 Loadings)**
   PCA was executed on standardized components $[Z_{\text{urb}}, Z_{\text{veg}}, Z_{\text{wat}}]$.

---

## 8. PCA Results

- **Correlation Matrix:**
  - $\text{Corr}(C_{\text{urb}}, C_{\text{veg}}) = +0.7712$ (Strong positive correlation reflecting land clearing)
  - $\text{Corr}(C_{\text{urb}}, C_{\text{wat}}) = +0.0768$ (Weak correlation)
  - $\text{Corr}(C_{\text{veg}}, C_{\text{wat}}) = +0.1044$ (Weak correlation)
- **Eigenvalues:** $\lambda_1 = 1.7534$, $\lambda_2 = 0.9949$, $\lambda_3 = 0.2517$
- **Variance Explained:** PC1 = **58.5%**, PC2 = 33.2%, PC3 = 8.4%
- **PC1 Absolute Loadings:**
  - Urbanization: $0.6698$
  - Vegetation: $0.6594$
  - Water/Moisture: $0.1315$
- **Derived PCA Weights:**
  $$w_{\text{urb}}^{\text{pca}} = 0.4585, \quad w_{\text{veg}}^{\text{pca}} = 0.4514, \quad w_{\text{wat}}^{\text{pca}} = 0.0900$$

---

## 9. Selected Methodology & Justification

- **Concordance:** The Pearson correlation between the Equal-Weight Baseline and PCA score is **$r = +0.9279$** (Spearman $\rho = +0.9385$).
- **Selection:** The **Transparent Equal-Weight Baseline** was selected as the primary indicator because:
  1. PCA weights down-weight water stress ($w_{\text{wat}} = 0.0900$) solely because water changes occur in localized catchments and tanks rather than district-wide, not because moisture loss is ecologically unimportant.
  2. Equal weighting provides complete scientific transparency, eliminates statistical overfitting, and ensures all three environmental domains contribute equitably to the stress assessment.

---

## 10. Environmental Stress Score Formula

For each 1 km cell $i$:

$$\text{Stress\_Score}_i = \frac{1}{3} C_{\text{urb}, i} + \frac{1}{3} C_{\text{veg}, i} + \frac{1}{3} C_{\text{wat}, i}$$

Bounded strictly in $[0, 1]$.

---

## 11. Categorical Evidence Strength

Each cell is categorized by its multi-source corroboration level:
- **Baseline / Low ($N = 1,288$ cells):** Zero components exceeding screening threshold ($0.20$).
- **Low (Single Evidence Family, $N = 2,829$ cells):** Stress isolated to a single component.
- **Moderate (Same-Sensor / Compound Signal, $N = 2,059$ cells):** Two components elevated, or same-sensor spectral agreement without external model confirmation.
- **High (Multi-Source Convergence, $N = 726$ cells):** Tri-component stress OR cross-dataset verified built-up expansion directly coinciding with vegetation loss.

---

## 12. Spatial Distribution Statistics (1 km Grid, $N = 6,902$)

| Metric | Value |
| :--- | :---: |
| **Minimum Score** | 0.0000 |
| **Maximum Score** | 0.6771 |
| **Mean Score ($\mu$)** | 0.2213 |
| **Median Score (p50)** | 0.2117 |
| **Standard Deviation ($\sigma$)** | 0.1309 |
| **25th Percentile (Q1 Threshold)** | 0.1175 |
| **75th Percentile (Q3 Threshold)** | 0.3112 |
| **90th Percentile** | 0.3989 |
| **95th Percentile** | 0.4573 |

### Relative Stress Categories:

| Category | Score Range | Cell Count | % of District Grid | Approximate Geodesic Area ($\text{km}^2$) |
| :--- | :---: | :---: | :---: | :---: |
| **Q1: Lower Relative Stress** | $[0.0000, 0.1175]$ | 1,726 | 25.01% | $1,670.3\text{ km}^2$ |
| **Q2: Moderate-Low Relative Stress** | $(0.1175, 0.2117]$ | 1,725 | 24.99% | $1,669.3\text{ km}^2$ |
| **Q3: Moderate-High Relative Stress** | $(0.2117, 0.3112]$ | 1,725 | 24.99% | $1,669.3\text{ km}^2$ |
| **Q4: Higher Relative Stress** | $(0.3112, 0.6771]$ | 1,726 | 25.01% | $1,670.3\text{ km}^2$ |

---

## 13. Top Relative Stress Cells (Sample from Rankings)

From `outputs/tables/environmental_stress_rankings.csv` (Top 5 of 200 ranked cells):

| Rank | Cell ID | Longitude | Latitude | Stress Score | Urban Comp ($C_{\text{urb}}$) | Veg Comp ($C_{\text{veg}}$) | Water Comp ($C_{\text{wat}}$) | Evidence Strength | Dominant Contributing Evidence |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | `C_052_166` | $79.7011^\circ\text{E}$ | $13.3105^\circ\text{N}$ | **0.6771** | 0.5000 | 1.0000 | 0.5312 | High | Tri-component stress: simultaneous built-up expansion, vegetation loss, and moisture decrease. |
| **2** | `C_035_064` | $78.7787^\circ\text{E}$ | $13.4632^\circ\text{N}$ | **0.6761** | 0.4960 | 0.7934 | 0.7388 | High | Tri-component stress: simultaneous built-up expansion, vegetation loss, and moisture decrease. |
| **3** | `C_052_169` | $79.7280^\circ\text{E}$ | $13.3105^\circ\text{N}$ | **0.6670** | 0.5276 | 0.9962 | 0.4771 | High | Tri-component stress: simultaneous built-up expansion, vegetation loss, and moisture decrease. |
| **4** | `C_047_044` | $78.5990^\circ\text{E}$ | $13.3554^\circ\text{N}$ | **0.6610** | 0.9099 | 1.0000 | 0.0730 | High | Cross-dataset validated built-up expansion coinciding with vegetation decrease. |
| **5** | `C_038_055` | $78.6979^\circ\text{E}$ | $13.4362^\circ\text{N}$ | **0.6559** | 0.8040 | 0.7897 | 0.3740 | High | Tri-component stress: simultaneous built-up expansion, vegetation loss, and moisture decrease. |

---

## 14. Sensitivity Analyses

1. **Resolution Sensitivity (1 km vs. 500 m):**
   - 1 km Mean: $0.2213$ ($\sigma = 0.1309$)
   - 500 m Mean: $0.1873$ ($\sigma = 0.1290$)
   - Distribution parameters and spatial hotspots remain closely aligned.
2. **Threshold Sensitivity ($\pm 0.05$ vs. $\pm 0.10$ vs. $\pm 0.15$):**
   - Correlation with $\pm 0.05$ threshold: **$r = +0.9220$**
   - Correlation with $\pm 0.15$ threshold: **$r = +0.9540$**
   - Spatial rankings are stable against variations in screening threshold.
3. **Weighting Sensitivity (Baseline vs. PCA):**
   - Correlation: **$r = +0.9279$**, $\rho = +0.9385$.

---

## 15. District-Level Climatic Context (MODIS & CHIRPS)

Because MODIS Daytime LST and CHIRPS precipitation are available only as district aggregates, they were omitted from cell-level score formulas to prevent pseudoreplication:
- **Thermal Regime:** District daytime LST decreased by $-5.38^\circ\text{C}$ between 2016 ($33.94^\circ\text{C}$) and 2025 ($28.56^\circ\text{C}$).
- **Precipitation Regime:** Annual rainfall transitioned from a severe drought year in 2016 ($753.1\text{ mm}$, $-402.1\text{ mm}$ anomaly) to near-normal conditions in 2025 ($1,158.4\text{ mm}$, $+3.2\text{ mm}$ anomaly).
- **Inference:** Localized environmental stress clusters in Q4 occurred despite higher rainfall in 2025, isolating anthropogenic land conversion and localized hydrological disturbance from macro-climatic drought.

---

## 16. Comparison with Exploratory GEE Baseline Score

- **Previous GEE Baseline (2025):** Recorded a uniform scalar score of $0.347$.
- **New Spatial Indicator:** Provides continuous spatial disaggregation, demonstrating that while the district average is moderate ($\mu = 0.2213$), localized cells in Q4 experience severe compound stress ($\ge 0.50$ to $0.68$), while 50% of the district exhibits low stress ($\le 0.2117$).

---

## 17. Limitations & Scientific Cautions

1. Scores represent relative spatial variation, not absolute disaster probability.
2. Dynamic World built-up transitions are model-derived and carry classification uncertainty.
3. Rapid rural fallow cycles can elevate NDBI and decrease NDVI without structural urban construction.
4. Absence of localized gridded rainfall and micro-LST data limits cell-level hydro-thermal coupling.

---

## 18. Outputs Generated

- **Tables:**
  - [environmental_stress_grid_1km.csv](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/environmental_stress_grid_1km.csv) (Full 6,902-cell dataset)
  - [environmental_stress_rankings.csv](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/environmental_stress_rankings.csv) (Top 200 ranked cells)
  - [environmental_stress_sensitivity.csv](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/environmental_stress_sensitivity.csv) (Sensitivity comparison matrix)
- **Figures:**
  - [environmental_stress_indicator_1km.png](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/environmental_stress/environmental_stress_indicator_1km.png)
  - [environmental_stress_500m_sensitivity.png](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/environmental_stress/environmental_stress_500m_sensitivity.png)
  - [urbanization_stress_component.png](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/environmental_stress/urbanization_stress_component.png)
  - [vegetation_stress_component.png](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/environmental_stress/vegetation_stress_component.png)
  - [water_moisture_stress_component.png](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/environmental_stress/water_moisture_stress_component.png)
  - [stress_score_distribution.png](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/environmental_stress/stress_score_distribution.png)
- **Metadata Manifest:** [environmental_stress_manifest.json](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/data/metadata/environmental_stress_manifest.json)

---

## 19. Final Status Summary

```
============================================================
ENVIRONMENTAL STRESS INDICATOR STATUS
============================================================
Spatial unit: PASS
Indicator definition: PASS
Normalization: PASS
Weighting analysis: PASS
PCA/data-driven analysis: PASS
Baseline comparison: PASS
Sensitivity analysis: PASS
Uncertainty analysis: PASS
Stress grid: PASS
Component maps: PASS
Stress map: PASS
Rankings: PASS
Manifest: PASS
Research log: PASS

Raw data modified: 0
Existing source rasters modified: 0

Overall:
PASS

NEXT PROJECT STEP:
Predictive Modeling / Forecasting Feasibility Assessment
============================================================
```
