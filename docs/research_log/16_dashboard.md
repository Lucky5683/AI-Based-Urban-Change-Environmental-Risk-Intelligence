# Research Log 16: Integrated Environmental Intelligence Dashboard

**Stage:** STEP 21 — Integrated Environmental Intelligence Dashboard  
**Date:** September 2026  
**Region:** Chittoor District, Andhra Pradesh, India  
**Scope:** Interactive presentation and decision-support layer consuming validated project outputs.  

---

## 1. Dashboard Objective

The primary objective of Step 21 was to design, construct, test, and run the first complete, unified interactive dashboard for the *AI-Based Urban Change & Environmental Risk Intelligence* project. 

The dashboard functions strictly as an **analytical presentation and interaction layer**. In accordance with scientific governance standards:
- It acts purely as a consumer of existing, validated analytical assets.
- It does not download external satellite imagery, retrain machine learning models, alter thresholds, modify stress weights, or re-run time-series calculations.
- It translates complex multi-source scientific outputs into actionable decision-support tools for urban planners, environmental managers, and district administrators.

---

## 2. Integrated Data Sources

The dashboard seamlessly connects all validated historical, spatial, and predictive outputs:

| Dataset / Table | Location | Description / Purpose in Dashboard |
| :--- | :--- | :--- |
| **Dashboard Data Contract** | `outputs/tables/dashboard_data_contract.csv` | Authoritative contract governing metric definitions, allowed interpretations, and forbidden claims. |
| **Headline Results Audit** | `outputs/tables/final_headline_results_audit.csv` | 19 audited headline findings and exact numerical values. |
| **Units Dictionary** | `outputs/tables/final_units_dictionary.csv` | Authoritative dimensional dictionary defining permitted measurement units and symbols. |
| **Master Research Dataset** | `data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv` | 10-year longitudinal annual time series (2016–2025) of urban extent, NDVI, LST, rainfall, and stress. |
| **Environmental Stress Grid (1 km)**| `outputs/tables/environmental_stress_grid_1km.csv` | 6,902 one-kilometer grid cells with component scores ($C_{urb}$, $C_{veg}$, $C_{wat}$), stress score, and quartile. |
| **Stress Explainability** | `outputs/tables/environmental_stress_explainability.csv` | Cell-level additive decomposition and quartile ranks for transparent explainability. |
| **Top 100 Hotspots** | `outputs/tables/top_100_environmental_stress_cells.csv` | Priority screening cells sorted deterministically by `stress_score DESC, cell_id ASC`. |
| **2026 Built-Up Forecast** | `outputs/tables/builtup_forecast_2026.csv` | Point forecasts ($270.32\text{ km}^2$ total, $70.31\text{ km}^2$ core) and 95% analytical prediction intervals. |
| **Decision Support Matrix** | `outputs/tables/decision_support_matrix.csv` | Thematic operational actions, indicators, confidence levels, and methodological boundaries. |
| **Executive Summary** | `outputs/tables/executive_decision_summary.csv` | Four operational and planning priorities for district leadership. |
| **Sentinel-2 Imagery & Features** | `data/raw/satellite/` & `data/processed/` | 10 m multispectral GeoTIFFs, spectral index rasters, and decadal change layers. |

---

## 3. Dashboard Architecture

The dashboard was implemented in Streamlit using a modular component design:

```
dashboard/
├── app.py                     # Main Streamlit application and page dispatcher
├── requirements.txt           # Minimal runtime dependencies
├── README.md                  # Complete documentation and operator guide
├── assets/
│   └── style.css              # Custom styling, responsive cards, and quartile colors
├── components/
│   ├── __init__.py
│   ├── kpi_cards.py           # Headline indicator cards with validated units
│   ├── charts.py              # Interactive Plotly time-series and correlation plots
│   ├── maps.py                # 1 km stress grid scatter map and Cell Inspector
│   └── tables_view.py         # Deterministic Top 100 hotspots table and decision accordions
├── utils/
│   ├── __init__.py
│   ├── data_loader.py         # Cached data loading with contract enforcement
│   └── raster_helpers.py      # Windowed & downsampled GeoTIFF reading
└── tests/
    ├── __init__.py
    └── test_app.py            # Automated test suite (8 test cases)
```

---

## 4. Page Structure & Interactive Features

The dashboard consists of seven dedicated pages accessible via sidebar navigation:

1. **Executive Overview:**
   - Displays the 6 mandatory headline KPI cards (2025 Built-Up: $259.21\text{ km}^2$, Decadal Increase: $+99.81\text{ km}^2 / +62.6\%$, 2025 NDVI: $0.4566$, 2025 LST: $28.56^\circ\text{C}$, 2025 Rainfall: $1,158.41\text{ mm}$, Decadal Relative Stress: $0.2213$ mean / $0.6771$ peak).
   - Interactive historical trend selector with Plotly curves.
   - Validated bivariate statistical relationships with Pearson $r$, $p$-values, and non-causal disclosures.
2. **Satellite Image Intelligence:**
   - Multi-tab viewer (Sentinel-2 2016, Sentinel-2 2025, NDVI, NDWI, NDBI, Decadal Change Detection).
   - Displays True Color (B4/B3/B2) and False Color (B8/B4/B3) composites.
   - Predefined Regions of Interest (Chittoor Municipal Core, Tirupati Transit Corridor, Western Agricultural Basin, Central Valley).
   - Explicit screening language: *"Spectral screening area"*, not *"confirmed land conversion"*.
3. **Historical Analytics:**
   - In-depth longitudinal analytics across urban expansion, vegetation swings (including the 2019 drought dip), land surface temperature, and CHIRPS precipitation.
   - Multi-indicator standardized anomaly comparisons ($Z$-scores).
   - District-level Pearson correlation matrix.
4. **Environmental Stress Map & Hotspots:**
   - Interactive 1 km spatial map displaying 6,902 cells color-coded by quartile ($Q_1$–$Q_4$) using OpenStreetMap carto-positron tiles.
   - Interactive **Cell Inspector**: Users select any cell ID to deconstruct its stress score into $C_{urb}$, $C_{veg}$, and $C_{wat}$ with bar charts and dominant evidence summaries.
   - **Top 100 Hotspots Table**: Filterable by rank range, stress cutoff, and evidence strength, strictly enforcing deterministic tie-break sorting (`stress_score DESC, cell_id ASC`).
5. **2026 Built-Up Forecast:**
   - Presents the 1-year-ahead point forecast ($270.32\text{ km}^2$) and 95% prediction interval ($[250.02, 290.62]\text{ km}^2$).
   - Displays walk-forward backtesting performance ($\text{MAE} = 8.07\text{ km}^2$, $+44.1\%$ over baseline).
   - Enforces mandatory policy language: *"Estimated continuation of the historical built-up expansion trajectory; forecasts are uncertain estimates, not guaranteed future construction."* Zero spatial construction maps are generated.
6. **Decision Support & Action Prioritization:**
   - Four Executive Priority Cards (Urgent Field Inspections, Infrastructure Uncertainty Factoring, Hydrological Audits, Methodological Governance).
   - Expandable thematic decision support accordions with Spatial, Temporal, and Forecast Indicators, Recommended Monitoring Actions, and Limitations.
   - Non-prescriptive recommendations (monitoring, assessment, inspection).
7. **Methodology, Datasets & Traceability:**
   - Ten-step pipeline flowchart.
   - Comprehensive provenance metadata table for Sentinel-2, Dynamic World, MODIS, and CHIRPS.
   - Data traceability matrix linking dashboard metrics directly to source files.
   - Full legal and scientific disclaimer.

---

## 5. Authoritative Data Contract Integration

The dashboard strictly implements the governance rules defined in `outputs/tables/dashboard_data_contract.csv`:
- **Causality Safeguards:** Built-up vs LST correlation ($r = -0.8271, p = 0.0032$) is explicitly labeled an observational association confounded by regional rainfall trends; claims that urbanization cools Chittoor are forbidden.
- **Screening Language:** Stress scores are labeled "Relative Environmental Stress Screening Indicators"; claims of disaster predictions or building collapse ratings are strictly barred.
- **Sensor Non-Independence:** Explicitly clarifies that Dynamic World is derived from Sentinel-2 optical imagery; hence S2 NDBI and DW Built-Up are shared optical evidence, whereas MODIS and CHIRPS are independent.
- **Deterministic Tie-Breaking:** For the Top 100 Hotspots, tied cells (e.g., Rank 77 `C_049_170` and Rank 78 `C_051_035` both at 0.5335) are sorted by `stress_score DESC, cell_id ASC`.

---

## 6. Performance & Memory Management Strategy

To ensure sub-second UI responsiveness and eliminate memory spikes:
1. **Windowed Spatial Reads:** Rather than loading the multi-gigabyte Sentinel-2 scenes ($12,893 \times 13,568$ pixels, $\sim 4.2\text{ GB}$) into RAM, the dashboard utilizes `rasterio.windows.Window` to read localized $800 \times 800$ pixel sub-windows ($\sim 2.5\text{ MB}$, $0.05\text{ s}$ access time).
2. **Streamlit Caching:** All tabular datasets and raster extraction windows are cached using `@st.cache_data`.
3. **Decimation & Slicing:** Multi-band arrays are normalized with percentile contrast stretching on the fly without creating redundant disk files.
4. **Pre-Rendered Overviews:** Leverages existing high-resolution visual assets from `outputs/figures/` for district-scale overviews.

---

## 7. Testing & Verification

Automated verification was implemented via `dashboard/tests/test_app.py` and executed via `scripts/test_dashboard.py`:

- **Test 1 (Imports):** Clean import of all dashboard components, utils, and dependencies.
- **Test 2 (Master CSV):** Verified 10 annual rows spanning 2016–2025.
- **Test 3 (Stress Grid):** Verified 6,902 cells with valid geographic bounds ($12.0^\circ\text{N} \le \text{lat} \le 14.5^\circ\text{N}$, $78.0^\circ\text{E} \le \text{lon} \le 80.5^\circ\text{E}$).
- **Test 4 (Forecast Table):** Verified presence of Total Built-Up and Strong Built-Up targets.
- **Test 5 (Required Columns):** Confirmed all required schema columns across tables.
- **Test 6 (Forecast Numerical Bounds):** Confirmed Total Built-Up 2026 forecast equals $270.32\text{ km}^2$ ($95\%\text{ PI: } [250.02, 290.62]\text{ km}^2$) and Strong Core equals $70.31\text{ km}^2$ ($[64.75, 75.87]\text{ km}^2$).
- **Test 7 (Stress Score Range & Ranking):** Confirmed stress scores within $[0.0, 1.0]$, Peak Cell = `C_052_166` ($0.6771$), and deterministic sorting of tied ranks 77 and 78.
- **Test 8 (Data Immutability):** Confirmed raw satellite GeoTIFFs were untouched.

**Result:** All 8 tests passed in 1.418 seconds with 0 errors and 0 failures. Local HTTP serving was verified with HTTP 200 responses.

---

## 8. Scientific Limitations & Boundaries

1. **Observational Resolution:** Grid-level analysis is conducted at 1 km resolution ($100 \times 100$ Sentinel-2 pixels); it does not provide parcel-level cadastral boundary precision.
2. **Spectral vs Cadastral Land Conversion:** Detected spectral shifts represent candidate areas for field inspection and do not constitute legal evidence of unauthorized construction or land use permits.
3. **Linear Trend Horizon:** The 2026 forecast applies strictly to a 1-year horizon; long-term extrapolation without policy dynamic feedback is scientifically invalid.
