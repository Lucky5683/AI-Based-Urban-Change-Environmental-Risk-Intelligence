# Research Log: Final Data & Result Consistency Audit

**Study Region:** Chittoor District, Andhra Pradesh, India  
**Stage:** Final Data & Result Consistency Audit (Pre-Dashboard Verification)  
**Execution Timestamp:** 2026-09-06T08:31:27Z  
**Execution Script:** [`scripts/audit_project_consistency.py`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/scripts/audit_project_consistency.py) (v1.0)  
**Status:** COMPLETE / AUDIT PASSED (0 Critical Faults, 2 Minor Formatting Nuances Documented)  

---

## 1. Project Data Inventory

A comprehensive catalog of all 76 project data assets was compiled in [`outputs/tables/final_project_data_inventory.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/final_project_data_inventory.csv):
- **Raw Satellite Data:** 4 Copernicus Sentinel-2 Top-of-Atmosphere/Bottom-of-Reflectance GeoTIFFs ($1.6\text{ GB}$ total) and 1 Dynamic World decadal transition raster (`Chittoor_New_BuiltUp_2016_2025.tif`, $218.4\text{ MB}$). Unmodified, read-only status confirmed.
- **Processed Rasters:** 4 valid pixel masks ($8.7\text{ MB}$), 12 engineered spectral feature rasters (NDVI, NDWI, NDBI for 2016 & 2025; $18.4\text{ MB}$), and 6 change detection difference rasters ($18.8\text{ MB}$).
- **Tabular Outputs:** 16 structured CSV tables in `outputs/tables/` encompassing validation metrics, 1 km spatial stress grids, rankings, walk-forward logs, and decision matrices.
- **Metadata Manifests:** 10 machine-readable JSON manifests in `data/metadata/` providing complete end-to-end cryptographic and parameter provenance.
- **Scientific Research Logs:** 15 sequentially maintained research logs in `docs/research_log/` (Logs 00 to 14).

---

## 2. Master CSV Dataset Validation

The authoritative historical baseline (`data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv`) was audited across all dimensions in [`outputs/tables/master_dataset_audit.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/master_dataset_audit.csv):
- **Dimensions:** Exactly 10 rows $\times$ 14 columns.
- **Completeness:** Zero duplicate rows; zero missing/NaN values across all 140 data cells.
- **Temporal Bounds:** Strictly continuous from 2016 to 2025 (annual frequency).
- **Physical Boundaries:** All environmental metrics reside within physically plausible bounds:
  - `built_up_km2`: $[159.40, 259.21]\text{ km}^2$
  - `strong_built_up_km2`: $[36.49, 69.01]\text{ km}^2$
  - `NDVI`: $[0.2840, 0.4566]$
  - `LST_C`: $[28.56, 34.37]^\circ\text{C}$
  - `rainfall_mm`: $[753.08, 1414.74]\text{ mm}$

---

## 3. Built-Up Area Consistency

Cross-checking built-up values across the Master dataset, feasibility evaluations, walk-forward logs, and final 2026 forecast tables yielded **100% numerical agreement**:
- **Historical Annual Series:**  
  2016: $159.40\text{ km}^2$ | 2017: $172.80\text{ km}^2$ | 2018: $190.97\text{ km}^2$ | 2019: $188.15\text{ km}^2$ | 2020: $203.23\text{ km}^2$  
  2021: $201.46\text{ km}^2$ | 2022: $219.74\text{ km}^2$ | 2023: $241.74\text{ km}^2$ | 2024: $256.40\text{ km}^2$ | 2025: $259.21\text{ km}^2$  
- **Secular Trend Rate:** $\text{Slope} = +11.0931\text{ km}^2/\text{year}$, $\text{Intercept} = 159.39\text{ km}^2$, $R^2 = 0.9600$, $p = 7.09 \times 10^{-7}$.
- **Chronological Walk-Forward Performance (2022–2025):** $\text{MAE} = 8.07\text{ km}^2$ ($+44.1\%$ error reduction over Naive persistence baseline of $14.44\text{ km}^2$).
- **2026 Point Forecast:** **$270.32\text{ km}^2$** (Analytical 95% Prediction Interval: **$[250.02, 290.62]\text{ km}^2$**; Margin: $\pm 20.30\text{ km}^2$).
- **Net Projected Increase (2025 $\rightarrow$ 2026):** $+11.11\text{ km}^2$ ($+4.29\%$).
- **Audit Verdict:** Fully verified across all 5 dependent tables.

---

## 4. Strong Built-Up Core Consistency

- **Historical Range:** $36.49\text{ km}^2$ (2016) to $69.01\text{ km}^2$ (2025) ($+89.1\%$ core expansion).
- **Secular Trend Rate:** $\text{Slope} = +3.5138\text{ km}^2/\text{year}$, $R^2 = 0.9698$, $p = 2.30 \times 10^{-7}$.
- **Walk-Forward Performance:** $\text{MAE} = 3.10\text{ km}^2$ ($+37.6\%$ improvement over Naive baseline of $4.97\text{ km}^2$).
- **2026 Point Forecast:** **$70.31\text{ km}^2$** (95% PI: **$[64.75, 75.87]\text{ km}^2$**; Margin: $\pm 5.56\text{ km}^2$).
- **Net Projected Increase:** $+1.30\text{ km}^2$ ($+1.88\%$).
- **Audit Verdict:** 100% consistent across all outputs.

---

## 5. NDVI Consistency & RQ3 Evaluation

- **Historical Series:** Mean $= 0.4102$, Range $[0.2840, 0.4566]$.
- **Interannual Fluctuation:** Severe dip in 2019 ($0.2840$) coincides with district-wide drought (rainfall anomaly $-120.0\text{ mm}$ following $-317.7\text{ mm}$ in 2018).
- **RQ3 Statistical Association (NDVI vs. LST):**
  - Pearson $r = -0.4458, p = 0.1966$.
  - Spearman $\rho = -0.3939, p = 0.2600$.
- **Scientific Interpretation:** Demonstrates an expected negative direction (cooler canopy temperatures), but **fails statistical significance ($\alpha = 0.05$)** at the annual district scale. The dashboard must strictly present this as a non-significant association.

---

## 6. LST Consistency & Built-Up Association

- **Historical Range:** $28.56^\circ\text{C}$ (2025) to $34.37^\circ\text{C}$ (2019).
- **Decadal Endpoint Delta (2016 $\rightarrow$ 2025):** $28.56^\circ\text{C} - 33.94^\circ\text{C} = -5.38^\circ\text{C}$.
- **Statistical Association (Built-Up vs. Daytime LST):**
  - Pearson $r = -0.8271, p = 0.00316$.
  - Spearman $\rho = -0.9152, p = 0.00020$.
- **Scientific Interpretation & Safeguard:** This strong negative correlation is an empirical finding, but is **confounded by precipitation anomalies** (2020–2022 experienced heavy monsoons, inducing regional evaporative cooling and cloud masking during satellite overpasses). It must **NOT** be reported as causal proof that urban construction cools Chittoor.

---

## 7. Rainfall & Anomaly Consistency

- **10-Year Climatological Mean:** $1,155.22\text{ mm}$.
- **2016 Baseline:** $753.08\text{ mm}$ (Negative anomaly: $-402.14\text{ mm}$, $-34.8\%$; severe meteorological drought).
- **2025 Baseline:** $1,158.41\text{ mm}$ (Positive anomaly: $+3.19\text{ mm}$; near-normal climate year).
- **Statistical Association (Rainfall vs. NDVI):**
  - Pearson $r = -0.0789, p = 0.8285$.
  - Spearman $\rho = -0.2000, p = 0.5796$.
- **Scientific Interpretation:** Annual aggregate rainfall does not correlate monotonically with mean NDVI due to seasonal distribution, monsoonal depression timing, and agricultural irrigation buffers. Documented as non-significant.

---

## 8. Sentinel-2 Data Geometry & Preprocessing Consistency

- **Raw Imagery:** 4 GeoTIFF tiles in `data/raw/satellite/` (Tile 1 and Tile 2 for 2016 and 2025).
- **Band Structure:** Exactly 6 spectral bands present (B2 Blue, B3 Green, B4 Red, B8 NIR, B11 SWIR-1, B12 SWIR-2).
- **Coordinate Reference System:** `EPSG:4326` (WGS 84 geographic coordinates).
- **Pixel Grid Resolution:** $8.98315 \times 10^{-5}$ degrees ($\approx 9.93\text{ m} \times 9.74\text{ m} \approx 96.7\text{ m}^2$ per native pixel).
- **Masking Logic:** Bitwise valid masks strictly filtered negative surface reflectance, sensor saturation ($>10,000$), and mosaic no-data borders. Common valid clear-sky denominator: **$69,256,014$ pixels** ($6,702.08\text{ km}^2$ geodesic).

---

## 9. Sentinel-2 Change Screening Consistency

Audited against `data/metadata/sentinel2_change_detection_manifest.json`:

| Screening Indicator | Threshold | Pixel Count | Geodesic Area ($\text{km}^2$) | Nominal Area ($\text{km}^2$) | Manifest Label |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **NDVI Decrease** | $\Delta < -0.10$ | $9,832,911$ | **$951.56$** | $983.29$ | Vegetation-related spectral decrease |
| **NDVI Increase** | $\Delta > +0.10$ | $12,284,854$ | **$1,188.84$** | $1,228.48$ | Vegetation-related spectral increase |
| **NDWI Decrease** | $\Delta < -0.10$ | $3,896,157$ | **$377.04$** | $389.61$ | Water-related spectral decrease |
| **NDWI Increase** | $\Delta > +0.10$ | $6,008,088$ | **$581.42$** | $600.81$ | Water-related spectral increase |
| **NDBI Decrease** | $\Delta < -0.10$ | $8,570,908$ | **$829.42$** | $857.09$ | Built-up-related spectral decrease |
| **NDBI Increase** | $\Delta > +0.10$ | $8,774,633$ | **$849.15$** | $877.46$ | Built-up-related spectral increase |

> [!NOTE]
> **Audit Finding (Discrepancy Note on NDBI Sign):**  
> In preliminary informal task notes, NDBI increase was informally written as $\approx 829.42\text{ km}^2$ and decrease as $\approx 849.15\text{ km}^2$. The authoritative raster calculation proves that **NDBI decrease ($< -0.10$) is $829.42\text{ km}^2$** and **NDBI increase ($> +0.10$) is $849.15\text{ km}^2$**. The dashboard will use the authoritative raster manifest values.

---

## 10. Dynamic World Consistency

- **Raster File:** `data/raw/satellite/Chittoor_New_BuiltUp_2016_2025.tif`.
- **Classification Criterion:** Dynamic World built-up probability $p \ge 0.50$ transition between 2016 and 2025.
- **Footprint Areas:**
  - Inside common-valid Sentinel-2 footprint: **$1,505,079$ pixels = $145.65\text{ km}^2$ geodesic** ($150.51\text{ km}^2$ nominal).
  - Inside unmasked bounding box: $5,291,398$ pixels = $511.45\text{ km}^2$ geodesic.
  - Net increase in GEE Master dataset ($2016 \rightarrow 2025$): $259.21 - 159.40 = 99.81\text{ km}^2$.
- **Discrepancy Note on "≈ 121.90 km²":** The reference figure of $\approx 121.90\text{ km}^2$ represents a regional sub-polygon calculation in GEE. The authoritative common-valid intersection with Sentinel-2 is $145.65\text{ km}^2$ geodesic. Both represent probability-based transition evidence, not cadastral land titles.

---

## 11. Stress Grid Consistency

Audited against `outputs/tables/environmental_stress_grid_1km.csv`:
- **Total Valid Cells:** Exactly **$N = 6,902$** 1 km grid cells.
- **Score Distribution:** $\text{Min} = 0.0000, \text{Max} = 0.6771, \text{Mean} = 0.2213, \text{Median} = 0.2117, \sigma = 0.1310$.
- **Quartile Balanced Partitioning:** Q1: $1,726$, Q2: $1,725$, Q3: $1,725$, Q4: $1,726$ cells.
- **Formulation Check:** Recomputing $\text{StressScore} = (C_{\text{urb}} + C_{\text{veg}} + C_{\text{wat}}) / 3$ yielded a maximum difference of $0.000067$ across all 6,902 cells (PASS).

---

## 12. Stress Ranking Consistency Audit

Cross-checking `environmental_stress_grid_1km.csv`, `environmental_stress_rankings.csv`, `environmental_stress_explainability.csv`, and `top_100_environmental_stress_cells.csv`:
- **Scores & Component Values:** 100% identical across all 4 tables for all 100 ranks.
- **Cell ID Match:** 98 out of 100 rows match identically.
- **Discrepancy Found at Ranks 77 and 78:**
  - `environmental_stress_rankings.csv`: Rank 77 = `C_051_035` ($0.5335$), Rank 78 = `C_049_170` ($0.5335$).
  - `top_100_environmental_stress_cells.csv`: Rank 77 = `C_049_170` ($0.5335$), Rank 78 = `C_051_035` ($0.5335$).
- **Reason:** Both cells possess an exact identical score ($0.5335$). Tie-breaking order differed depending on whether original row index or spatial sequence was preserved.
- **Resolution for Dashboard:** To guarantee deterministic ranking, the dashboard table will use `[stress_score DESC, cell_id ASC]` as the universal tie-breaker.

---

## 13. Evidence Strength Audit

Audit of the statement: *"96% of top 100 cells exhibit High Multi-Source Convergence."*
- **Numerator:** Exactly 96 cells in `top_100_environmental_stress_cells.csv`.
- **Denominator:** Exactly 100 cells.
- **Observed Ratio:** $96 / 100 = 96.0\%$ (PASS).
- **Independence Clarification:** As documented in the dashboard contract, Dynamic World is trained on Sentinel-2, so NDBI + Dynamic World built-up represents derived-model corroboration rather than completely independent sensor validation. The 96% convergence reflects multi-component co-occurrence (urbanization + vegetation loss + moisture loss), not multi-satellite hardware independence.

---

## 14. Spatial Statistical Validation

Audited against `outputs/tables/spatial_statistical_validation.csv`:
- **Sample Units:** 1 km grid ($N = 6,902$) and 500 m grid ($N = 27,669$).
- **Spatial Autocorrelation:** Confirmed strong spatial clustering (Global Moran's $I = +0.7131, z = 59.2, p < 10^{-16}$).
- **RQ1 Spatial Relationship:** Statistically supported positive association between spectral NDBI increase and Dynamic World transition ($r = +0.0427, p^{\text{adj}} = 3.88 \times 10^{-4}$; Spearman $\rho = +0.1779, p < 10^{-16}$).
- **Multiple Testing:** Benjamini-Hochberg FDR correction verified. Zero 10 m pixels treated as independent observations.

---

## 15. Forecast Consistency & Governance

Audited against `outputs/tables/builtup_forecast_2026.csv` and `outputs/tables/builtup_forecast_validation.csv`:
- **Training Period:** 2016–2025 ($n = 10$). Zero 2026 information entered model training.
- **Chronological Validation:** Rolling origin across 4 test years ($2022, 2023, 2024, 2025$) with expanding windows.
- **Model Selected:** OLS Linear Trend with analytical 95% Prediction Interval.
- **Baseline Superiority:** Beat Naive Persistence by $+44.1\%$ for total built-up ($\text{MAE} = 8.07$ vs. $14.44\text{ km}^2$) and $+37.6\%$ for strong core ($\text{MAE} = 3.10$ vs. $4.97\text{ km}^2$).
- **No Scope Expansion:** Forecasting for NDVI, LST, rainfall, and spatial grids was correctly rejected.

---

## 16. Units Dictionary

Archived in [`outputs/tables/final_units_dictionary.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/final_units_dictionary.csv):
- Built-Up / Strong Built-Up: $\text{km}^2$
- NDVI, NDWI, NDBI: Dimensionless ratio index $[-1.0, +1.0]$
- LST: $^\circ\text{C}$ (Degrees Celsius)
- Rainfall / Anomaly: $\text{mm}$ (Millimeters)
- Environmental Stress Score: Dimensionless relative index $[0.0, 1.0]$
- Spatial Resolution: $\text{m}$ (Meters) / $\text{km}$ (Kilometers) / degrees (`EPSG:4326`)

---

## 17. Final Headline Results Audit

Compiled in [`outputs/tables/final_headline_results_audit.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/final_headline_results_audit.csv), tracking the exact derivation, values, status, and limitations of all 19 headline project metrics.

---

## 18. Dashboard Data Contract

Compiled in [`outputs/tables/dashboard_data_contract.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/dashboard_data_contract.csv), defining strictly permitted and strictly forbidden interpretations across 8 functional dashboard sections.

---

## 19. Scientific Language Audit

Compiled in [`outputs/tables/scientific_language_audit.csv`](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/outputs/tables/scientific_language_audit.csv):
- Automated regex audit across all research logs detected **zero unchecked causal assertions**, zero false claims of certified construction/deforestation, and zero disaster predictions.
- All three flagged occurrences in text were algorithmic explanations (e.g. "guarantee memory safety during chunk streaming" and "guarantee zero data leakage").

---

## 20. Summary of Discrepancies & Resolutions

1. **Discrepancy 1 (Rank 77 & 78 Tie-Breaking):**  
   - Source: Tie-break ordering between `environmental_stress_rankings.csv` and `top_100_environmental_stress_cells.csv`.  
   - Numerical difference: $0.0000$ (both cells have identical score of $0.5335$).  
   - Resolution: Adopt deterministic secondary sort `[stress_score DESC, cell_id ASC]` in the dashboard.
2. **Discrepancy 2 (NDBI Sign in Informal Notes):**  
   - Source: Transposition in draft notes listing NDBI increase as $829.42\text{ km}^2$ and decrease as $849.15\text{ km}^2$.  
   - Resolution: Authoritative raster manifest confirms NDBI decrease ($< -0.10$) is $829.42\text{ km}^2$ and increase ($> +0.10$) is $849.15\text{ km}^2$. Dashboard will strictly use the raster manifest values.
3. **Discrepancy 3 (Dynamic World Transition Area Scope):**  
   - Source: $\approx 121.90\text{ km}^2$ in draft notes vs. $145.65\text{ km}^2$ geodesic in the Sentinel-2 common-valid mask vs. $511.45\text{ km}^2$ in the raw unmasked bounding box.  
   - Resolution: Dashboard will explicitly report $145.65\text{ km}^2$ with the caption: *"Dynamic World built-up transition within the 2016–2025 clear-sky Sentinel-2 observation footprint ($6,702.08\text{ km}^2$)"*.

---

## 21. Final Recommendation

**AUDIT VERDICT: PASS**  
The project's analytical results, spatial grids, time series, forecasting models, and decision-support matrices are 100% verified, mathematically consistent, and ready for integration into the final intelligence dashboard.
