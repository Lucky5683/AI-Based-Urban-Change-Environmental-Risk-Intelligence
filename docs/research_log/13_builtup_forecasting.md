# Research Log: 1-Year-Ahead Built-Up Forecast Implementation & Validation

**Study Region:** Chittoor District, Andhra Pradesh, India  
**Stage:** 1-Year-Ahead Built-Up Forecast Implementation and Validation  
**Execution Timestamp:** 2026-09-06T08:16:22Z  
**Execution Script:** [`scripts/forecast_builtup_2026.py`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/scripts/forecast_builtup_2026.py) (v1.0)  
**Status:** COMPLETE / PASSED  

---

## 1. Objective

The objective of this stage is to implement the single forecasting task demonstrated to be scientifically defensible in the preceding feasibility assessment: **1-year-ahead district-level built-up area forecasting for 2026** with rigorous analytical 95% prediction intervals.

In strict compliance with the foundational project principle:
> [!IMPORTANT]
> **GOVERNING RESEARCH DIRECTIVE: NO FAKE AI OR SCOPE EXPANSION.**  
> - We implement forecasts **strictly** for candidate targets that passed the feasibility audit (`built_up_km2` and `strong_built_up_km2`).
> - We do **NOT** forecast stochastic meteorological targets (`NDVI`, `LST_C`, `rainfall_mm`).
> - We do **NOT** train deep learning models (LSTM, CNN, U-Net) on annual series or image pairs.
> - We do **NOT** generate synthetic spatial pixel maps claiming to predict future land-use conversion at individual 10 m pixels.
> - The model estimates aggregate district-level secular expansion based on validated empirical inertia.

---

## 2. Historical Data

The forecasting pipeline utilizes the verified longitudinal annual series from [`data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv):

- **Temporal Coverage:** 2016 to 2025 (10 continuous annual observations, zero missing records).
- **Primary Data Source:** Google Dynamic World Land Cover (derived from 10 m Copernicus Sentinel-2 MSI).
- **Target 1 (`built_up_km2`):** Total district built-up extent (expanded from $159.40\text{ km}^2$ in 2016 to $259.21\text{ km}^2$ in 2025; $+62.6\%$ increase).
- **Target 2 (`strong_built_up_km2`):** High-confidence core built-up extent (expanded from $36.49\text{ km}^2$ in 2016 to $69.01\text{ km}^2$ in 2025; $+89.1\%$ increase).

### Historical Trend Reproduction Verification:
- **Total Built-Up Area:**
  $$\text{Slope} = +11.0931\text{ km}^2/\text{year}, \quad \text{Intercept} = 159.39\text{ km}^2, \quad R^2 = 0.9600, \quad p = 7.09 \times 10^{-7}$$
- **Strong Built-Up Core:**
  $$\text{Slope} = +3.5138\text{ km}^2/\text{year}, \quad \text{Intercept} = 35.17\text{ km}^2, \quad R^2 = 0.9698, \quad p = 2.30 \times 10^{-7}$$
- **Audit Verdict:** Reproduces previous feasibility benchmarks exactly ($\Delta R^2 < 0.0001$).

---

## 3. Selected Model & Mathematical Formulation

The selected model is **Ordinary Least Squares (OLS) Linear Trend Extrapolation with Analytical Prediction Intervals**:

$$y_t = \beta_0 + \beta_1 t + \epsilon_t, \quad \epsilon_t \overset{\text{iid}}{\sim} \mathcal{N}(0, \sigma^2)$$

For a 1-year-ahead forecast at time index $t_{\text{pred}} = 10$ (year 2026, where $t \in [0, 9]$ spans 2016–2025):
$$\hat{y}_{2026} = \hat{\beta}_0 + \hat{\beta}_1 \times 10$$

### Exact Analytical 95% Prediction Interval:
Unlike a confidence interval (which reflects uncertainty of the mean trend), a **prediction interval** quantifies uncertainty regarding a specific future individual observation. It incorporates both parameter estimation error and intrinsic observation variance:

$$SE(\hat{y}_{\text{pred}}) = s \sqrt{1 + \frac{1}{n} + \frac{(t_{\text{pred}} - \bar{t})^2}{\sum_{i=1}^n (t_i - \bar{t})^2}}$$

$$\text{Margin of Error} = t_{n-2, \, 0.975} \times SE(\hat{y}_{\text{pred}})$$
$$\text{PI}_{95\%} = \left[ \hat{y}_{\text{pred}} - t_{\text{crit}} \cdot SE, \; \hat{y}_{\text{pred}} + t_{\text{crit}} \cdot SE \right]$$

Where:
- $n = 10$ historical observations
- Degrees of freedom: $df = n - 2 = 8$
- Critical $t$-value: $t_{8, \, 0.975} = 2.306004$
- Mean time index: $\bar{t} = 4.5$
- $\sum_{i=0}^9 (t_i - \bar{t})^2 = 82.5$

---

## 4. Why This Model Was Selected

1. **Physical Soundness:** Urban built-up land once paved or constructed rarely reverts to barren land or natural vegetation. It possesses structural physical inertia and cumulative secular momentum.
2. **Occam's Razor & Parameter Parsimony:** With $N=10$, estimating only 2 parameters ($\beta_0, \beta_1$) preserves $df = 8$ residual degrees of freedom. Highly parameterized ML algorithms (Random Forest, GBDT) or deep neural networks (LSTM, CNN) immediately overfit or collapse.
3. **Empirical Out-of-Sample Superiority:** In walk-forward testing, OLS linear trend beat naive persistence by $44.1\%$ for total built-up and $37.6\%$ for strong built-up core.

---

## 5. Chronological Walk-Forward Validation

To strictly avoid data leakage, validation was executed using an expanding rolling-origin framework across 4 out-of-sample years ($2022, 2023, 2024, 2025$):

- **2022:** Trained on 2016–2021 ($n=6$) $\rightarrow$ Predict 2022 ($t=6$)
- **2023:** Trained on 2016–2022 ($n=7$) $\rightarrow$ Predict 2023 ($t=7$)
- **2024:** Trained on 2016–2023 ($n=8$) $\rightarrow$ Predict 2024 ($t=8$)
- **2025:** Trained on 2016–2024 ($n=9$) $\rightarrow$ Predict 2025 ($t=9$)

### Walk-Forward Error Log:
| Target | Validation Year | Actual ($\text{km}^2$) | Forecast ($\text{km}^2$) | Forecast Error | Abs Error | Naive Forecast | Naive Error | Naive Abs Error |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Built-Up** | 2022 | $219.74$ | $215.88$ | $-3.86$ | $3.86$ | $201.46$ | $-18.28$ | $18.28$ |
| **Total Built-Up** | 2023 | $241.74$ | $226.62$ | $-15.12$ | $15.12$ | $219.74$ | $-22.00$ | $22.00$ |
| **Total Built-Up** | 2024 | $256.40$ | $243.13$ | $-13.27$ | $13.27$ | $241.74$ | $-14.66$ | $14.66$ |
| **Total Built-Up** | 2025 | $259.21$ | $259.24$ | $+0.03$ | $0.03$ | $256.40$ | $-2.80$ | $2.80$ |
| **Strong Core** | 2022 | $55.73$ | $52.31$ | $-3.42$ | $3.42$ | $49.12$ | $-6.62$ | $6.62$ |
| **Strong Core** | 2023 | $60.91$ | $56.79$ | $-4.13$ | $4.13$ | $55.73$ | $-5.18$ | $5.18$ |
| **Strong Core** | 2024 | $63.21$ | $61.74$ | $-1.48$ | $1.48$ | $60.91$ | $-2.30$ | $2.30$ |
| **Strong Core** | 2025 | $69.01$ | $65.62$ | $-3.39$ | $3.39$ | $63.21$ | $-5.80$ | $5.80$ |

The full walk-forward table is archived in [`outputs/tables/builtup_forecast_validation.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/builtup_forecast_validation.csv).

---

## 6. Naive Baseline Comparison & Model Improvement

The standard benchmark for time-series forecasting is **Naive Last-Value Persistence** ($\hat{y}_t = y_{t-1}$). Under continuous secular growth, naive persistence exhibits systematic negative lag errors.

| Target Variable | OLS Trend MAE | OLS Trend RMSE | OLS Trend MAPE | Naive Baseline MAE | Naive Baseline RMSE | Net Error Reduction | Scientific Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Total Built-Up (`built_up_km2`)** | **$8.07\text{ km}^2$** | **$10.24\text{ km}^2$** | **$3.30\%$** | $14.44\text{ km}^2$ | $16.13\text{ km}^2$ | **$+44.1\%$** | **Superior to Baseline** |
| **Strong Built-Up (`strong_built_up_km2`)** | **$3.10\text{ km}^2$** | **$3.26\text{ km}^2$** | **$5.04\%$** | $4.97\text{ km}^2$ | $5.23\text{ km}^2$ | **$+37.6\%$** | **Superior to Baseline** |

Both targets surpass the project hurdle rule of demonstrating $>30\%$ out-of-sample error reduction over naive persistence.

---

## 7. 2026 Forecast & Uncertainty Quantification

Training the selected model on the complete decadal historical baseline (2016–2025, $n=10$) produces the following 1-year-ahead projections for 2026:

| Forecast Parameter | Total Built-Up Area (`built_up_km2`) | Strong Built-Up Core (`strong_built_up_km2`) |
| :--- | :---: | :---: |
| **Historical Observed 2025** | $259.21\text{ km}^2$ | $69.01\text{ km}^2$ |
| **Historical 10-Year Mean** | $209.31\text{ km}^2$ | $50.98\text{ km}^2$ |
| **OLS Trend Rate (Annual Slope)** | $+11.0931\text{ km}^2/\text{year}$ | $+3.5138\text{ km}^2/\text{year}$ |
| **Standard Error of Regression ($s$)** | $7.2684\text{ km}^2$ | $1.9911\text{ km}^2$ |
| **Prediction Standard Error ($SE_{\text{pred}}$)** | $8.8037\text{ km}^2$ | $2.4118\text{ km}^2$ |
| **Student's $t$ Critical Value ($df=8$)** | $2.306004$ | $2.306004$ |
| **Uncertainty Margin ($\pm t_{\text{crit}} \cdot SE$)** | $\pm 20.30\text{ km}^2$ | $\pm 5.56\text{ km}^2$ |
| **2026 Point Forecast** | **$270.32\text{ km}^2$** | **$70.31\text{ km}^2$** |
| **95% Prediction Interval** | **$[250.02, \; 290.62]\text{ km}^2$** | **$[64.75, \; 75.87]\text{ km}^2$** |
| **Expected 2025 $\rightarrow$ 2026 Net Delta** | **$+11.11\text{ km}^2$** | **$+1.30\text{ km}^2$** |
| **Expected Percentage Expansion** | **$+4.29\%$** | **$+1.88\%$** |

The final forecast summary is archived in [`outputs/tables/builtup_forecast_2026.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/builtup_forecast_2026.csv).

---

## 8. Physical & Scientific Interpretation

1. **Secular Momentum:** The forecast of $270.32\text{ km}^2$ represents an expected annual expansion of $+11.11\text{ km}^2$ ($+4.29\%$). This rate is consistent with regional infrastructure growth along the Bangalore–Tirupati–Chennai economic corridors traversing Chittoor District.
2. **Core Densification:** Strong built-up area is projected to reach $70.31\text{ km}^2$ ($+1.88\%$), indicating infill and consolidation within existing municipal clusters.
3. **Cautious Terminology:** This projection represents an **estimated future indicator under the continuation of historical trend dynamics**, not an unalterable guaranteed realization.

The complete interpretation is archived in [`outputs/tables/builtup_forecast_interpretation.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/builtup_forecast_interpretation.csv).

---

## 9. Visualizations Generated

- [`outputs/figures/forecasting/final_builtup_forecast_2026.png`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/forecasting/final_builtup_forecast_2026.png): Two-panel display showing:
  - Panel A: Complete historical observations (2016–2025), linear trend line, 95% analytical prediction band, and 2026 point forecast with error bars.
  - Panel B: Walk-forward validation (2022–2025) comparing OLS predictions against actuals and naive persistence.
- [`outputs/figures/forecasting/final_strong_builtup_forecast_2026.png`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/figures/forecasting/final_strong_builtup_forecast_2026.png): Parallel two-panel display for the strong built-up core.

---

## 10. Explicit Model Limitations

1. **Short Historical Horizon ($N = 10$):** Exactly 10 annual data points exist. While adequate for 1-step OLS extrapolation, it precludes multi-decadal cyclic modeling or high-order autoregressive terms.
2. **Strict 1-Year Horizon Boundary:** Forecasts beyond 2026 are not supported by the data and would compound uncertainty quadratically.
3. **Probability-Derived Base Data:** Built-up extents are derived from Dynamic World satellite classification ($p \ge 0.50$), subject to spectral confusion around quarry rock, bare soil, and high-reflectance riverbeds.
4. **Assumption of Policy Continuity:** The model assumes ongoing historical urbanization rates without major land-use moratoria, severe economic recessions, or administrative redistricting.
5. **Prediction Interval Boundary:** The $95\%$ interval ($[250.02, 290.62]\text{ km}^2$) accounts for model and observation variance under normal conditions, but cannot absorb extreme external shocks.
6. **No Spatial Pixel Map:** District aggregate built-up growth cannot be downscaled to assign probabilistic development flags to individual 10 m pixels without multi-temporal cadastral labels.

---

## 11. Reproducibility & Sanity Checks

All automated sanity checks executed in `scripts/forecast_builtup_2026.py` passed:
- `all_forecasts_positive`: **PASS**
- `lower_95 < point_forecast < upper_95`: **PASS** ($250.02 < 270.32 < 290.62$ and $64.75 < 70.31 < 75.87$)
- `plausible_district_range`: **PASS** ($270.32\text{ km}^2 \ll 15,152\text{ km}^2$)
- `strong_builtup <= total_builtup`: **PASS** ($70.31\text{ km}^2 < 270.32\text{ km}^2$)
- `chronological_validation_zero_leakage`: **PASS**
- `baseline_superiority`: **PASS** ($+44.1\%$ and $+37.6\%$ improvement)
- `zero_spatial_hallucination`: **PASS**
- `immutability_passed`: **PASS** (zero modifications to `data/raw/` or existing processed rasters)

All execution metadata and exact parameter values are archived in [`data/metadata/builtup_forecast_manifest.json`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/data/metadata/builtup_forecast_manifest.json).
