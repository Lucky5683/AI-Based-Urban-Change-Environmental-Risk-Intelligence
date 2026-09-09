# AI-Based Urban Change & Environmental Risk Intelligence for Chittoor District, Andhra Pradesh

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Geospatial](https://img.shields.io/badge/Geospatial-Rasterio%20%7C%20Sentinel--2-2b8236.svg)](https://rasterio.readthedocs.io/)
[![Governance](https://img.shields.io/badge/Scientific%20Governance-Data%20Contract%20Audited-purple.svg)](outputs/tables/dashboard_data_contract.csv)
[![Tests](https://img.shields.io/badge/Tests-15%2F15%20Passing-brightgreen.svg)](dashboard/tests/test_app.py)

---

##  Executive Summary

This project delivers an end-to-end, scientifically grounded **Applied Data Science & Geospatial Intelligence System** for **Chittoor District, Andhra Pradesh, India**. 

The system synthesizes multi-decadal satellite Earth observation imagery (**Copernicus Sentinel-2 MSI**, **Google Dynamic World AI**, **MODIS Terra**, and **CHIRPS pentad**) spanning **2016 to 2025**, combined with geostatistical modeling, decadal spectral change detection, spatial stress indexing, walk-forward time-series backtesting, and an interactive decision-support interface.

### Key Headline Results (2016–2025)
* **Urban Expansion:** Total built-up extent increased from **$159.40\text{ km}^2$** (2016) to **$259.21\text{ km}^2$** (2025), representing a net anthropogenic transformation of **$+99.81\text{ km}^2$ ($+62.6\%$)**.
* **Core Densification:** High-confidence consolidated urban core expanded from **$36.49\text{ km}^2$** to **$69.01\text{ km}^2$ ($+89.1\%$)**, evidencing vigorous infill development.
* **Compound Drought Shock:** 2019 recorded severe compound stress with minimum annual mean NDVI (**$0.2840$**) and peak daytime Land Surface Temperature (**$34.37^\circ\text{C}$**).
* **Spatial Autocorrelation:** The 1 km decadal environmental stress indicator exhibits high, statistically significant spatial clustering (**Global Moran's $I = +0.7131$, $p < 0.0001$**).
* **2026 Predictive Trajectory:** Chronological walk-forward backtested trend models project total built-up extent reaching **$270.32\text{ km}^2$** with an analytical 95% prediction interval of **$[250.02, 290.62]\text{ km}^2$** (an out-of-sample MAE of $8.07\text{ km}^2$, outperforming naive persistence by $+44.1\%$).

---

##  End-to-End Data Science Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. DATA ACQUISITION & INGESTION                                                        │
│    • Sentinel-2 MSI 10 m / 20 m decadal scenes (2016 & 2025)                           │
│    • Dynamic World 10 m annual built-up probabilistic classification (Google/WRI AI)   │
│    • MODIS Terra (MOD11A2) Daytime Land Surface Temperature (1 km)                     │
│    • CHIRPS Pentad gridded precipitation (0.05° / ~5.5 km)                             │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. DATA ENGINEERING, QUALITY & CLOUD SCREENING                                         │
│    • Raster CRS standardization (EPSG:4326), bounding box & resolution verification   │
│    • Multi-temporal valid data masking & common clear-sky footprint (6,702.08 km²)     │
│    • Immutability checksums, data contract validation & schema enforcement             │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. FEATURE ENGINEERING & CHANGE DETECTION                                              │
│    • Native 10 m indices: NDVI (vegetation), NDWI (water/moisture), NDBI (built-up)    │
│    • Decadal spectral change screening (|Δ| > 0.10) across common valid footprint      │
│    • Standardized multi-indicator temporal anomalies (Z-scores)                        │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. STATISTICAL & SPATIAL DATA SCIENCE                                                  │
│    • District-level bivariate correlation analysis (observational association guards)  │
│    • 1 km regularized spatial analysis grid (N = 6,902 cells)                          │
│    • Global Moran's I spatial dependency test (I = +0.7131, p < 1e-4)                  │
│    • Spatial overlay & administrative attribution (Mandal gazetteer join)              │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. MULTI-CRITERIA ENVIRONMENTAL STRESS MODELING                                        │
│    • Additive multi-component formulation: C_urb (1/3) + C_veg (1/3) + C_wat (1/3)     │
│    • 99th-percentile bounded scaling in [0, 1]                                         │
│    • Sensitivity testing: Equal vs PCA (Pearson r = 0.9279, Spearman ρ = 0.9385)       │
│    • Priority hotspot ranking (Top 100 cells with multi-factor explainability)         │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. PREDICTIVE MODELING & UNCERTAINTY QUANTIFICATION                                    │
│    • Rigorous ML feasibility audit (rejects deep learning on N=10 to avoid overfitting)│
│    • Chronological walk-forward rolling-origin backtesting (2022–2025 out-of-sample)   │
│    • Model benchmarking: Naive Persistence vs Mean vs Moving Average vs Holt vs OLS    │
│    • 2026 point forecasts with Student's t 95% analytical prediction intervals         │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 7. DECISION SUPPORT & INTERACTIVE INTELLIGENCE DASHBOARD                               │
│    • Operational monitoring and planning review recommendations                        │
│    • High-performance, memory-safe Streamlit application (windowed raster access)     │
│    • 8 analytical modules: Executive, Explorer, Urban, Environmental, Spatial,         │
│      Forecasting, Decision Support, and Scientific Methodology                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

##  Scientific Methodology & Governance

### 1. The Role of Artificial Intelligence & Machine Learning
This project maintains strict scientific honesty regarding the scope and limits of AI/ML:
* **Deep Learning Foundation:** Google/WRI **Dynamic World** employs a deep Fully Convolutional Neural Network (FCN) trained on millions of Sentinel-2 optical image patches to deliver authoritative 10 m pixel-level land cover class probabilities.
* **Why Deep Learning is NOT Used for Annual Time-Series Extrapolation:** A critical data science milestone was conducting a formal **Prediction Feasibility Assessment** (`outputs/tables/prediction_feasibility_matrix.csv`). With $N = 10$ annual observations (2016–2025), fitting multi-parameter Machine Learning (Random Forest, GBDT) or Deep Learning (LSTM, 1D-CNN) models inevitably induces catastrophic overfitting and parameter memorization.
* **Defensible Model Selection:** Transparent, parsimonious models (**OLS Linear Trend Extrapolation** and **Holt's Linear Exponential Smoothing**) were chosen, rigorously benchmarked against a **Naive Persistence Baseline** ($y_{t-1}$) using **expanding-window walk-forward cross-validation**.

### 2. Spatial Environmental Stress Formulation
The Environmental Stress Indicator ($S_i$) across the 6,902 one-kilometer grid cells synthesizes three distinct environmental dimensions:
$$S_i = w_{urb} C_{urb, i} + w_{veg} C_{veg, i} + w_{wat} C_{wat, i}$$
where:
* $C_{urb, i}$: Decadal urbanization pressure derived from Sentinel-2 NDBI increase and Dynamic World built-up transitions.
* $C_{veg, i}$: Vegetation canopy loss screening derived from decadal NDVI reductions.
* $C_{wat, i}$: Water and moisture decline derived from decadal NDWI reductions.
* $w_{urb} = w_{veg} = w_{wat} = \frac{1}{3}$ (Equal weighting baseline verified against PCA-derived weights; high concordance with Pearson $r = 0.9279$ and Spearman rank correlation $\rho = 0.9385$ confirms high structural ranking stability).

### 3. Non-Causal Language Governance
Per `outputs/tables/dashboard_data_contract.csv`, all findings are governed by strict epistemic guardrails:
* Bivariate relationships (such as Built-Up Area vs. LST, $r = -0.827$) are designated as **observational associations**, acknowledging confounding meteorological factors (regional monsoon precipitation and cloud cover trends) rather than asserting urban cooling.
* Spectral index changes are classified as **"spectral screening areas"**, explicitly noting that ground-truth verification is required before establishing legal or administrative land conversion.

---

##  Repository Structure

```
AI-Based-Urban-Change-Environmental-Risk-Intelligence/
├── dashboard/                              # Interactive Streamlit Analytics Application
│   ├── app.py                              # Main application dispatcher (8 analytical pages)
│   ├── assets/                             # Custom CSS stylesheets (modern design system)
│   ├── components/                         # Modular UI presentation components
│   │   ├── charts.py                       # Plotly figures (trends, anomalies, associations, PI)
│   │   ├── kpi_cards.py                    # Metric cards and headline indicator banners
│   │   ├── maps.py                         # Interactive Mapbox/Carto spatial grid & cell inspector
│   │   └── tables_view.py                  # Hotspot tables, decision matrices, traceability
│   ├── utils/                              # Data loading, caching, and raster handlers
│   │   ├── data_loader.py                  # Contract-enforced CSV loaders with st.cache_data
│   │   └── raster_helpers.py               # Memory-safe windowed GeoTIFF inspection
│   └── tests/                              # Automated test suite
│       └── test_app.py                     # 11 comprehensive integration and data contract tests
├── data/
│   ├── metadata/                           # JSON provenance manifests for all pipeline stages
│   ├── processed/                          # Processed master dataset, features, and masks
│   │   ├── Chittoor_Master_Research_Dataset_2016_2025.csv  # 10-year authoritative time-series
│   │   ├── change_detection/               # GeoTIFF decadal change rasters (NDVI, NDWI, NDBI)
│   │   ├── features/                       # GeoTIFF spectral index rasters (2016 & 2025)
│   │   └── satellite/                      # GeoTIFF valid clear-sky masks
│   └── raw/                                # Foundational raw data (Read-Only)
│       ├── boundaries/chittoor_mandals.geojson  # Mandal administrative boundary polygons
│       └── satellite/                      # Raw multispectral Sentinel-2 & Dynamic World TIFFs
├── docs/
│   ├── research_log/                       # Complete chronological engineering logs (00 to 18)
│   └── Research_Paper/                     # Scientific reference literature
├── notebooks/                              # Runnable Jupyter Notebooks (End-to-End DS Lifecycle)
│   ├── 01_data_validation.ipynb           # Satellite & tabular data validation
│   ├── 02_eda.ipynb                       # Exploratory Data Analysis & longitudinal trends
│   ├── 03_spatial_analysis.ipynb          # 1 km grid spatial analysis & Moran's I
│   ├── 04_temporal_analysis.ipynb         # Time-series dynamics, lag autocorrelation, & inertia
│   ├── 05_change_detection.ipynb          # Decadal spectral change screening (|Δ| > 0.10)
│   ├── 06_risk_analysis.ipynb             # Multi-criteria environmental stress formulation
│   ├── 07_ml_modeling.ipynb               # ML claim audit, degrees of freedom, & feasibility
│   └── 08_forecasting.ipynb               # Walk-forward backtesting & 2026 forecast intervals
├── outputs/
│   ├── figures/                            # Validated charts & maps across all analytical stages
│   └── tables/                             # 26 audited CSV tables (contracts, forecasts, grids)
├── scripts/                                # Standalone reproducible analytical pipeline scripts
│   ├── audit_project_consistency.py        # Comprehensive consistency & data contract audit
│   ├── build_environmental_stress_indicator.py # 1 km spatial grid construction & PCA sensitivity
│   ├── detect_sentinel2_change.py          # Pixel-level spectral change detection
│   ├── enrich_spatial_location.py          # Geographic & administrative gazetteer enrichment
│   ├── evaluate_prediction_feasibility.py  # Systematic ML/DL feasibility analysis
│   ├── forecast_builtup_2026.py            # Walk-forward rolling origin backtesting & OLS forecast
│   ├── generate_sentinel2_features.py      # NDVI, NDWI, NDBI index computation
│   ├── spatial_statistical_validation.py   # Moran's I & bivariate correlation testing
│   └── test_dashboard.py                   # Automated dashboard integrity validator
├── requirements.txt                        # Complete Python project dependencies
└── README.md                               # Authoritative project documentation
```

---

##  Installation & Reproduction Guide

### 1. Prerequisites
* Python 3.10, 3.11, 3.12, or 3.14
* Conda or Python `venv` recommended

### 2. Environment Setup
```bash
# Clone or navigate to the workspace
cd AI-Based-Urban-Change-Environmental-Risk-Intelligence

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run Automated Quality & Regression Tests
```bash
python -m unittest dashboard/tests/test_app.py
```
*Executes 15 automated verification tests checking imports, tabular schemas, coordinate validity, forecast calculations, and scientific constraints.*

### 4. Launch the Interactive Dashboard
```bash
streamlit run dashboard/app.py
```
Open your web browser at `http://localhost:8501`.

---

##  Dashboard Modules Overview

The redesigned dashboard provides 8 analytical modules:
1. **Executive Overview:** High-level executive synthesis of headline KPIs, decadal expansion rates, multi-indicator trajectory selectors, and bivariate relationship scatter plots.
2. **Data Explorer:** Dynamic multidimensional query interface allowing ad-hoc indicator filtering, temporal period comparisons, distribution metrics, and CSV data export.
3. **Urban Change Analytics:** Detailed urban footprint dynamics, annual additions, core vs. peripheral growth, and spectral change screening comparisons.
4. **Environmental Analytics:** Decadal vegetation vigor (NDVI), surface moisture (NDWI), thermal regimes (LST), precipitation anomalies, and standardized $Z$-score anomaly profiles.
5. **Spatial Stress & Hotspots:** Interactive 1 km grid map, quartile filtering, deterministic Top 100 hotspot ranking, and deep-dive Cell Inspector decomposing component drivers.
6. **Forecasting & Model Performance:** Walk-forward backtesting benchmarks (MAE, RMSE, MAPE), candidate model comparisons (OLS, Holt's, MA, Persistence), and 2026 forecast with 95% prediction intervals.
7. **Decision Support:** Structured executive action priorities and thematic decision matrices framed around targeted field verification, planning review, and resource monitoring.
8. **Methodology & Data Quality:** Full scientific architecture pipeline flowchart, remote sensing data provenance, units dictionary, and governance data contracts.

---

##  Scientific Disclaimer & Governance
This project produces **research-oriented environmental screening indicators and statistical projections**. Relative environmental stress scores represent screening prioritizations to direct field inspection and monitoring; they do **NOT** represent structural building collapse forecasts, definitive regulatory hazard ratings, or legally binding determinations.
