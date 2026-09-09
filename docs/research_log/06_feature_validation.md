# Sentinel-2 Feature Validation

## Date
2026-09-06

## Objective
Validate the spatial, numerical, and visual integrity of the 12 derived Sentinel-2 spectral feature rasters (NDVI, NDWI, NDBI) across both observation years (2016 and 2025) and tile partitions before performing multi-temporal change detection or predictive risk modeling. This step ensures that no systematic artifacts, edge misalignments, sensor dropouts, or out-of-bounds mathematical anomalies enter downstream modeling pipelines.

## Inputs
The 12 single-band `float32` GeoTIFF feature rasters in `data/processed/features/`:
- **2016**:
  - `sentinel2_2016_tile1_ndvi.tif` (13,568 × 12,893)
  - `sentinel2_2016_tile1_ndwi.tif` (13,568 × 12,893)
  - `sentinel2_2016_tile1_ndbi.tif` (13,568 × 12,893)
  - `sentinel2_2016_tile2_ndvi.tif` (4,195 × 12,893)
  - `sentinel2_2016_tile2_ndwi.tif` (4,195 × 12,893)
  - `sentinel2_2016_tile2_ndbi.tif` (4,195 × 12,893)
- **2025**:
  - `sentinel2_2025_tile1_ndvi.tif` (13,568 × 12,893)
  - `sentinel2_2025_tile1_ndwi.tif` (13,568 × 12,893)
  - `sentinel2_2025_tile1_ndbi.tif` (13,568 × 12,893)
  - `sentinel2_2025_tile2_ndvi.tif` (4,195 × 12,893)
  - `sentinel2_2025_tile2_ndwi.tif` (4,195 × 12,893)
  - `sentinel2_2025_tile2_ndbi.tif` (4,195 × 12,893)

## Metadata Validation
All 12 rasters were verified against their respective raw Sentinel-2 source files:
- **Band Count**: 1 band per file (expected: 1) — **PASS**
- **Data Type**: `float32` across all files (expected: `float32`) — **PASS**
- **Coordinate Reference System**: `EPSG:4326` across all files (expected: `EPSG:4326`) — **PASS**
- **Pixel Resolution**: `8.983152841195215e-05` degrees (~10 m native ground sampling distance) — **PASS**
- **Dimensions**: Tile 1 = 13,568 × 12,893 px; Tile 2 = 4,195 × 12,893 px (identical to source rasters) — **PASS**
- **Geographic Extents**: Preserved exactly from raw inputs without spatial displacement — **PASS**
- **Overall Metadata Verdict**: **PASS**

## Numerical Validation
Full distribution profiling and range checks were conducted:
- **Range Compliance**: All calculated index values fall strictly within the theoretical mathematical bounds of normalized-difference indices: $[-1.0, +1.0]$. Zero values were $< -1.0$ or $> +1.0$.
- **Out-of-Range Count**: 0 across all 12 rasters.
- **Finite / NaN Representation**: Valid pixels are strictly finite; invalid/unobserved areas outside Chittoor District or masked by SCL are correctly encoded as `NaN`.

### Summary Statistics Table:
| Year | Tile | Feature | Finite Pixels | % Finite | Min | Max | Mean | Median | StdDev | p1 | p5 | p25 | p50 | p75 | p95 | p99 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2016 | Tile 1 | NDVI | 250,362 | 36.68% | -0.6851 | 0.8752 | 0.4656 | 0.4573 | 0.1559 | 0.1346 | 0.2284 | 0.3517 | 0.4573 | 0.5807 | 0.7254 | 0.7881 |
| 2016 | Tile 1 | NDWI | 250,362 | 36.68% | -0.7868 | 0.7724 | -0.5079 | -0.5116 | 0.1043 | -0.7046 | -0.6586 | -0.5762 | -0.5116 | -0.4512 | -0.3493 | -0.2221 |
| 2016 | Tile 1 | NDBI | 250,362 | 36.68% | -0.6339 | 0.6909 | 0.0140 | 0.0327 | 0.1119 | -0.2957 | -0.2005 | -0.0524 | 0.0327 | 0.0967 | 0.1634 | 0.2053 |
| 2016 | Tile 2 | NDVI | 19,905 | 9.44% | -0.7500 | 0.8634 | 0.4847 | 0.4948 | 0.1950 | 0.0213 | 0.1865 | 0.3501 | 0.4948 | 0.6379 | 0.7664 | 0.8164 |
| 2016 | Tile 2 | NDWI | 19,905 | 9.44% | -0.7862 | 0.8168 | -0.5074 | -0.5224 | 0.1491 | -0.7267 | -0.6866 | -0.6010 | -0.5224 | -0.4406 | -0.3062 | 0.0805 |
| 2016 | Tile 2 | NDBI | 19,905 | 9.44% | -0.7048 | 0.6876 | -0.0160 | -0.0063 | 0.1427 | -0.3432 | -0.2617 | -0.1160 | -0.0063 | 0.0920 | 0.1986 | 0.2647 |
| 2025 | Tile 1 | NDVI | 250,363 | 36.68% | -0.5494 | 0.8538 | 0.4675 | 0.4681 | 0.1568 | 0.0947 | 0.2159 | 0.3597 | 0.4681 | 0.5856 | 0.7119 | 0.7667 |
| 2025 | Tile 1 | NDWI | 250,363 | 36.68% | -0.7656 | 0.6898 | -0.4960 | -0.5080 | 0.1133 | -0.6778 | -0.6378 | -0.5661 | -0.5080 | -0.4476 | -0.3210 | -0.1276 |
| 2025 | Tile 1 | NDBI | 250,363 | 36.68% | -0.7586 | 0.5889 | 0.0235 | 0.0403 | 0.1163 | -0.2766 | -0.1913 | -0.0520 | 0.0403 | 0.1120 | 0.1845 | 0.2243 |
| 2025 | Tile 2 | NDVI | 19,911 | 9.44% | -1.0000 | 0.8762 | 0.5317 | 0.5569 | 0.1916 | -0.0766 | 0.2113 | 0.4233 | 0.5569 | 0.6724 | 0.7765 | 0.8076 |
| 2025 | Tile 2 | NDWI | 19,911 | 9.44% | -0.7973 | 1.0000 | -0.5139 | -0.5379 | 0.1538 | -0.6961 | -0.6678 | -0.6068 | -0.5379 | -0.4641 | -0.2886 | 0.1929 |
| 2025 | Tile 2 | NDBI | 19,911 | 9.44% | -0.6575 | 1.0000 | -0.0444 | -0.0424 | 0.1275 | -0.3162 | -0.2482 | -0.1370 | -0.0424 | 0.0506 | 0.1455 | 0.2066 |

*(Statistics profiled across a uniform spatial grid sample of 270,267 to 270,274 pixels per year).*

## Tile Consistency
Horizontal boundary continuity was analyzed between Tile 1 (West) and Tile 2 (East) for both observation years:
- **Same Coordinate System**: `EPSG:4326` across all tiles.
- **Same Pixel Spacing**: `8.983152841195215e-05` deg (~10 m).
- **Same Height**: 12,893 pixels in both tiles.
- **Vertical Alignment**: Top latitude = `13.782133`, Bottom latitude = `12.623935` (exact match).
- **Horizontal Adjacency**: Tile 1 East Boundary = `79.418078`, Tile 2 West Boundary = `79.418078` ($\Delta < 10^{-12}$ deg).
- **Tile Consistency Status**: **PASS**. The two tiles form a gap-free, seamless horizontal mosaic spanning the entire Chittoor District width ($13,568 + 4,195 = 17,763$ px).

## 2016 vs. 2025 Distribution Comparison
- **NDVI**:
  - Tile 1: 2016 Median = `0.4573` vs. 2025 Median = `0.4681` (p25: 0.3517 vs. 0.3597; p75: 0.5807 vs. 0.5856).
  - Tile 2: 2016 Median = `0.4948` vs. 2025 Median = `0.5569` (p25: 0.3501 vs. 0.4233; p75: 0.6379 vs. 0.6724).
- **NDWI**:
  - Tile 1: 2016 Median = `-0.5116` vs. 2025 Median = `-0.5080` (p25: -0.5762 vs. -0.5661; p75: -0.4512 vs. -0.4476).
  - Tile 2: 2016 Median = `-0.5224` vs. 2025 Median = `-0.5379` (p25: -0.6010 vs. -0.6068; p75: -0.4406 vs. -0.4641).
- **NDBI**:
  - Tile 1: 2016 Median = `0.0327` vs. 2025 Median = `0.0403` (p25: -0.0524 vs. -0.0520; p75: 0.0967 vs. 0.1120).
  - Tile 2: 2016 Median = `-0.0063` vs. 2025 Median = `-0.0424` (p25: -0.1160 vs. -0.1370; p75: 0.0920 vs. 0.0506).
- *Scientific Caution*: Distribution shifts between 2016 and 2025 reflect quality-control baseline comparisons. In accordance with methodological protocols, these numbers must NOT yet be interpreted as environmental degradation or urban growth without spatial change detection and phenological adjustment.

## Visual Inspection
Generated 6 overview previews and 3 empirical distribution comparison charts:
- `outputs/figures/sentinel2_features/ndvi_2016_overview.png`
- `outputs/figures/sentinel2_features/ndvi_2025_overview.png`
- `outputs/figures/sentinel2_features/ndwi_2016_overview.png`
- `outputs/figures/sentinel2_features/ndwi_2025_overview.png`
- `outputs/figures/sentinel2_features/ndbi_2016_overview.png`
- `outputs/figures/sentinel2_features/ndbi_2025_overview.png`
- `outputs/figures/sentinel2_features/ndvi_distribution_comparison.png`
- `outputs/figures/sentinel2_features/ndwi_distribution_comparison.png`
- `outputs/figures/sentinel2_features/ndbi_distribution_comparison.png`

**Artifact Observations**:
- No rectangular missing patches or block dropouts inside the valid mask.
- No scanline striping or detector banding visible.
- Tile boundary line at longitude $79.418078^\circ$ displays smooth spatial continuity across forest, agricultural, and urban terrain.
- No extreme single-pixel outliers distorting the color ramp.
- Water bodies (reservoirs, riverbeds) cleanly express as positive NDWI and low NDVI.
- Urban clusters and transport corridors show elevated NDBI.

## Limitations
- Visual previews and sample distributions are qualitative validation aids, not ground truth.
- Normalized difference spectral indices are continuous biophysical proxies; positive NDBI values capture both built structures and dry fallow soil.
- Temporal comparisons must account for the differing number of scenes integrated into the GEE composites (~53 in 2016 vs. ~253 in 2025).
- Formal pixel-level change detection has not yet been executed.

## Final Decision
**PASS**
All 12 feature rasters satisfy every technical, numerical, spatial, and visual validation criterion. The dataset is approved and ready for the next project step.

## Reproducibility
- Validation Script: `scripts/validate_sentinel2_features.py`
- Validation Table: `outputs/tables/sentinel2_feature_validation.csv`
- Validation Manifest: `data/metadata/sentinel2_feature_validation_manifest.json`
- Figures Directory: `outputs/figures/sentinel2_features/`
