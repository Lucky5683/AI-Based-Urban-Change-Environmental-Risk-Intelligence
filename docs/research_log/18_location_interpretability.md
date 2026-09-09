# Research Log — Step 23: Location Interpretability & Spatial Boundary Enrichment

## Date
2026-09-06

## Objective
Enhance the geographic and administrative location interpretability of the Environmental Stress Map and Top 100 Hotspots table in the Chittoor Environmental Intelligence Dashboard without modifying any underlying scientific calculations, stress scores, components, quartiles, rankings, or datasets.

---

## 1. Input Datasets & Boundary Provenance
- **1 km Environmental Stress Grid:** `outputs/tables/environmental_stress_grid_1km.csv` ($N = 6,902$ cells, mean stress score $= 0.2213$, peak score $= 0.6771$).
- **Top 100 Hotspots:** `outputs/tables/top_100_environmental_stress_cells.csv` (Ranks 1 to 100, deterministic contract ordering `stress_score DESC, cell_id ASC`).
- **Explainability Dataset:** `outputs/tables/environmental_stress_explainability.csv` ($N = 6,902$ cells).
- **Administrative Boundary Dataset:** `data/raw/boundaries/chittoor_mandals.geojson`
  - *Source:* Official Government of Andhra Pradesh Open Data (`satishvmadala/andhrapradesh_opendata_locations`).
  - *Coverage:* 67 administrative mandals covering the pre-bifurcation unified Chittoor District, exactly matching the 2016–2025 satellite study area bounds ($12.62^\circ\text{N} - 13.78^\circ\text{N}$, $78.20^\circ\text{E} - 79.79^\circ\text{E}$).
  - *Standardization:* Cleaned and formatted mandal names to standard Title Case (e.g., `Punganur`, `Somala`, `Vijayapuram`, `Chittoor`, `Madanapalle`, `Tirupati Urban`, `Tirupati Rural`, `Kuppam`, `Palamaner`, etc.).

---

## 2. Spatial Join Methodology
1. **Centroid Coordinate Representation:**
   Each grid cell represents an aggregated $1\text{ km} \times 1\text{ km}$ spatial analysis unit derived from $100 \times 100$ native $10\text{ m}$ Sentinel-2 pixels. Coordinates represent the exact mathematical centroid of each grid cell:
   $$\text{Lon}_c = \text{TransformX}(\text{col} + 0.5), \quad \text{Lat}_c = \text{TransformY}(\text{row} + 0.5)$$
2. **Point-in-Polygon Spatial Join:**
   Point geometries $(\text{Lon}_c, \text{Lat}_c)$ were spatially joined against the 67 mandal boundary polygons using `geopandas.sjoin(..., predicate='within')` in `EPSG:4326`.
   - **Direct Matches:** $6,872$ out of $6,902$ cells ($99.57\%$) matched strictly inside mandal boundary polygons.
3. **Peripheral Edge Handling:**
   For the remaining 30 peripheral edge cells ($0.43\%$) located along the simplified outer district boundary, `geopandas.sjoin_nearest` was executed in metric UTM Zone 44N projection (`EPSG:32644`):
   - Boundary distances ranged from $2.4\text{ m}$ to $726\text{ m}$ (well within the $1\text{ km}$ cell radius).
   - All 30 edge cells were deterministically assigned to their nearest administrative mandal.
   - **Result:** $100\%$ complete mandal assignment across all 6,902 cells with zero nulls.

---

## 3. Nearest-Settlement Enrichment & Scientific Constraints
Per strict project scientific instructions:
> *"Do NOT invent place names. Do NOT reverse-geocode using an undocumented source. Do NOT silently use random web results. If no suitable settlement dataset is already available, do NOT fabricate this field. In that case, implement latitude/longitude + mandal first and clearly document that nearest-place enrichment requires an additional authoritative source."*

- **Current Status:** Authoritative mandal boundary polygons were acquired and verified. No official, verified point gazetteer of sub-mandal villages/settlements is bundled in the repository.
- **Enrichment Implementation:** `nearest_place` is populated as `"N/A (Requires Authoritative Settlement Gazetteer)"` and `nearest_place_distance_km` as `NaN`, explicitly adhering to scientific standards.
- **Mandatory Geographic Disclaimer Added to UI:**
  > *"Stress scores are calculated for approximately 1-km spatial analysis cells. Administrative and settlement names are provided only as geographic context; they are not stress classifications for those places."*

---

## 4. User Test Cell Verification

The user highlighted specific cells from previous testing:
| Cell ID | Rank | Stress Score | Quartile | Evidence Strength | Mandal | Centroid Lat | Centroid Lon | Dominant Driver |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `C_047_043` | 21 | `0.5967` | Q4 | High (Multi-Source Convergence) | **Punganur** | $13.35540^\circ\text{N}$ | $78.59010^\circ\text{E}$ | Vegetation Spectral Decline |
| `C_042_068` | 24 | `0.5953` | Q4 | High (Multi-Source Convergence) | **Somala** | $13.40030^\circ\text{N}$ | $78.81460^\circ\text{E}$ | Water/Moisture Decline |
| `C_052_166` | 1 | `0.6771` | Q4 | High (Multi-Source Convergence) | **Vijayapuram** | $13.31047^\circ\text{N}$ | $79.70109^\circ\text{E}$ | Multi-Source Spectral Shift |
| `C_035_064` | 2 | `0.6761` | Q4 | High (Multi-Source Convergence) | **Somala** | $13.46319^\circ\text{N}$ | $78.77870^\circ\text{E}$ | Vegetation Spectral Decline |
| `C_052_169` | 3 | `0.6670` | Q4 | High (Multi-Source Convergence) | **Vijayapuram** | $13.31047^\circ\text{N}$ | $79.72804^\circ\text{E}$ | Water/Moisture Decline |

---

## 5. Dashboard Implementation Changes
1. **Enriched Derivative Tables:**
   - `outputs/tables/environmental_stress_grid_1km_enriched.csv`
   - `outputs/tables/top_100_environmental_stress_cells_enriched.csv`
   - `outputs/tables/environmental_stress_explainability_enriched.csv`
2. **Data Loaders (`dashboard/utils/data_loader.py`):**
   Updated `load_stress_grid`, `load_top_100_hotspots`, and `load_stress_explainability` to load `*_enriched.csv` when available, with fallback to original files.
3. **Environmental Stress Map (`dashboard/components/maps.py`):**
   - Added `mandal` to MapLibre hover tooltips.
   - Added `selected_cell_id` visual marker trace using `go.Scattermap` (prominent cyan target ring, size 18) to clearly highlight the selected cell on the spatial map.
   - Enhanced `render_cell_inspector` with a structured **Geographic & Administrative Location Context Box** detailing `1-km stress cell {cell_id}`, Mandal, Centroid Coordinates, Nearest Settlement status, and the mandatory non-prescriptive disclaimer note.
4. **Top 100 Hotspots Table (`dashboard/components/tables_view.py`):**
   Updated column display order: `Rank`, `Cell ID`, `Stress Score`, `Stress Quartile`, `Latitude`, `Longitude`, `Mandal`, `Nearest Place (if available)`, `Evidence Strength`, `Main Evidence Driver`, `Decision Support`.
5. **Harmonized Map Interaction (`dashboard/app.py`):**
   Connected cell selection in `page_stress_map` so selecting a cell from the dropdown immediately centers and highlights its location on the spatial map and updates the inspector below.

---

## 6. Validation Results
- **Automated Test Suite:** Ran `scripts/test_dashboard.py` containing 11 tests. All 11 passed in 3.391s (0 errors, 0 failures).
- **Multi-Page Programmatic Dispatch:** Verified clean execution across all 7 pages (`page_overview`, `page_image_intelligence`, `page_historical_analytics`, `page_stress_map`, `page_forecast`, `page_decision_support`, `page_methodology`).
- **Server Health:** Active Streamlit daemon on `http://localhost:8501` returned HTTP 200 OK.
- **Mathematical Invariance:** 100% verified. Zero changes to original stress scores, component weights ($\frac{1}{3}, \frac{1}{3}, \frac{1}{3}$), PCA values, quartiles, rankings, or raw rasters.
