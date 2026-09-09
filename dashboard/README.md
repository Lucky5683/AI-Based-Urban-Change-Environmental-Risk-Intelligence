# Chittoor Environmental Intelligence Dashboard

**AI-Based Urban Change & Environmental Risk Intelligence**  
*Study Region:* Chittoor District, Andhra Pradesh, India (6,902 valid 1 km grid cells, 6,702.08 km² common clear-sky footprint)  
*Analysis Period:* 2016–2025  
*Forecast Target:* 2026 Built-Up Area  

---

## 1. Overview & Purpose

The **Chittoor Environmental Intelligence Dashboard** serves as the authoritative, interactive presentation and decision-support layer for the project. It integrates multi-source Earth Observation (EO) intelligence—including Sentinel-2 multispectral imagery, Dynamic World land-cover transitions, MODIS Terra land surface temperature (LST), and CHIRPS precipitation—along with statistical associations, decadal change screening, spatial stress modeling, and 1-year-ahead predictive modeling.

> [!IMPORTANT]
> **Authoritative Data Rule & Scope:**
> The dashboard is a **consumer of validated project outputs only**. It does not download external data, retrain models, recalculate scientific indicators, or modify raw rasters. All visual interpretations strictly adhere to `outputs/tables/dashboard_data_contract.csv`.

---

## 2. Dashboard Architecture

The codebase is organized modularly:

```
dashboard/
├── app.py                     # Main Streamlit application with multi-page navigation
├── requirements.txt           # Minimal runtime dependencies (streamlit, plotly, pandas, etc.)
├── README.md                  # System architecture, user manual, and limitations
├── assets/
│   └── style.css              # Custom styling, KPI cards, badges, and layout rules
├── components/
│   ├── __init__.py
│   ├── kpi_cards.py           # Headline indicator renderers with audited units
│   ├── charts.py              # Interactive Plotly time series, correlations, and forecast charts
│   ├── maps.py                # 1 km Environmental Stress Grid map & Cell Inspector
│   └── tables_view.py         # Top 100 Hotspots table, decision matrices, & data contract
├── utils/
│   ├── __init__.py
│   ├── data_loader.py         # Cached data access, contract validation, and error guards
│   └── raster_helpers.py      # Windowed & downsampled GeoTIFF reading (RGB & indices)
└── tests/
    ├── __init__.py
    └── test_app.py            # Automated test suite (8 integration tests)
```

---

## 3. Seven Integrated Pages

### Page 1 — Executive Overview
- **Headline Indicators:**
  - 2025 Total Built-Up Area: **259.21 km²**
  - Built-Up Expansion (2016→2025): **+99.81 km² (+62.6%)**
  - 2025 Strong Core Urban Area: **69.01 km²**
  - 2025 Mean NDVI: **0.4566**
  - 2025 Mean Daytime LST: **28.56 °C**
  - 2025 Annual Rainfall: **1,158.41 mm**
  - Peak Environmental Stress: **0.6771** (Cell `C_052_166`) / Mean Stress: **0.2213**
- **Longitudinal Trend Chart:** Interactive Plotly switcher for all 7 indicators across 2016–2025.
- **Statistical Associations:** Visualizes district-level correlations (Built-Up vs LST: $r = -0.8271, p = 0.0032$; NDVI vs LST: $r = -0.4458$; Rainfall vs NDVI: $r = -0.0789$). Explicitly notes non-causal precipitation confounding.

### Page 2 — Satellite Image Intelligence
- **Band Composites:**
  - True Color RGB: B4 (Red), B3 (Green), B2 (Blue)
  - False Color NIR: B8 (NIR), B4 (Red), B3 (Green)
- **Spectral Features:** NDVI (Vegetation condition), NDWI (Surface water/moisture), NDBI (Built-up/bare surface).
- **Change Screening:** Decadal spectral shift screening areas (2016→2025). Explicitly labeled *"Spectral screening area"*, not *"confirmed land conversion"*.
- **Performance:** Windowed spatial reading (`rasterio.windows.Window`) across preset ROIs (Chittoor Core, Tirupati Corridor, Western Basin, Central Valley) prevents multi-gigabyte memory consumption.

### Page 3 — Historical Analytics
- **Multi-Parametric Trends:** Urban growth trajectory, vegetation dynamics (including the 2019 drought dip to 0.284), thermal history, and precipitation anomalies.
- **Standardized Anomalies:** Normalized Z-score comparisons across decadal parameters.
- **Correlation Matrix:** Bivariate observational associations across all master variables.

### Page 4 — Environmental Stress Intelligence (Map & Hotspots)
- **1 km Spatial Grid:** 6,902 cells classified into quartiles ($Q_1$–$Q_4$) using OpenStreetMap carto-positron tiles. Labeled *"Relative Environmental Stress"*, not *"absolute risk"*.
- **Cell Inspector:** Interactive deconstruction of any grid cell into additive equal-weight components:
  $$Stress = \frac{1}{3} C_{urb} + \frac{1}{3} C_{veg} + \frac{1}{3} C_{wat}$$
- **Top 100 Hotspots:** Deterministic ranking (`stress_score DESC, cell_id ASC`). Rank slider, score cutoff, and evidence strength filters.

### Page 5 — 2026 Built-Up Forecast
- **Authoritative Forecast:**
  - Total Built-Up Area: **270.32 km²** (95% PI: **[250.02, 290.62] km²**)
  - Strong Core Urban Area: **70.31 km²** (95% PI: **[64.75, 75.87] km²**)
- **Validation:** Walk-forward backtesting MAE = **8.07 km²** (+44.1% over baseline).
- **Governance:** Displays mandatory uncertainty notices: *"Estimated continuation of the historical built-up expansion trajectory. Forecasts are uncertain estimates, not guaranteed future construction."* **No spatial 2026 construction map is generated.**

### Page 6 — Decision Support & Action Prioritization
- **Executive Priorities:**
  1. Urgent Operational Priority: Joint field inspections for Top 100 hotspots.
  2. Regional Planning Priority: Factor 2026 uncertainty interval into master plans.
  3. Natural Resource Monitoring: Hydrological audits in high-decline NDWI zones.
  4. Methodological Governance: Maintain transparent indicator-based screening.
- **Thematic Matrix:** Operational actions framed around *monitoring*, *field verification*, and *planning review*. Prohibits alarmist or punitive mandates.

### Page 7 — Methodology, Datasets & Traceability
- **Architecture Pipeline:** Flowchart from raw EO data to decision support.
- **Data Provenance:** Metadata for Sentinel-2, Dynamic World, MODIS, and CHIRPS.
- **Traceability Table:** Explicit source file and permitted interpretation mapping.

---

## 4. Installation & Local Execution

### Prerequisites
- Python 3.10+
- Activated environment (e.g., `nlrc_env`)

### Install Dependencies
```bash
pip install -r dashboard/requirements.txt
```

### Run Dashboard Locally
```bash
streamlit run dashboard/app.py --server.port 8501
```

Access at `http://localhost:8501`.

### Run Automated Test Suite
```bash
python scripts/test_dashboard.py
```

---

## 5. Performance Strategy
- **Windowed Raster Reads:** Uses `rasterio.windows.Window` to read localized sub-grids rather than multi-GB GeoTIFF scenes into RAM.
- **Decimation & Caching:** All CSV files, metrics, and raster windows are cached with `@st.cache_data`.
- **Pre-generated Vector Graphics:** Leverages pre-computed high-resolution overview maps in `outputs/figures/`.

---

## 6. Scientific Limitations & Disclaimers
1. **Spectral Screening vs Land Use:** Spectral changes indicate optical reflectance shifts, which can stem from seasonal phenology, bare fallow ground, or quarrying, and do not prove legal construction or deforestation.
2. **Relative Stress Index:** The index indicates relative decadal compound pressure across Chittoor District; it is not an engineering hazard rating or disaster forecast.
3. **Forecast Horizon:** The 2026 built-up forecast assumes continuation of secular decadal trends; macroeconomic disruptions or policy interventions may alter trajectory. Spatial downscaling to individual parcels was scientifically rejected.
