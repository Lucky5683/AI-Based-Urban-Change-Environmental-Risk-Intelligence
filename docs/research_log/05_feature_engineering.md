# Sentinel-2 Spectral Feature Engineering

## Date
2026-09-06

## Objective
Derive the foundational set of multi-spectral normalized-difference environmental indicators (NDVI, NDWI, NDBI) from multi-temporal Sentinel-2 imagery for Chittoor District (2016 vs. 2025). These indices establish calibrated pixel-level features characterizing vegetative canopy vigor, surface moisture/water presence, and built-up/impervious surface exposure, providing the baseline feature space for subsequent environmental risk and urban change analysis.

## Input Data
The four raw Sentinel-2 Level-2A GeoTIFF files located in `data/raw/satellite/`:
- `Chittoor_Sentinel2_2016_Multispectral-0000000000-0000000000.tif` (Tile 1, Western)
- `Chittoor_Sentinel2_2016_Multispectral-0000000000-0000013568.tif` (Tile 2, Eastern)
- `Chittoor_Sentinel2_2025_Multispectral-0000000000-0000000000.tif` (Tile 1, Western)
- `Chittoor_Sentinel2_2025_Multispectral-0000000000-0000013568.tif` (Tile 2, Eastern)
*(Accessed strictly read-only; no raw data altered).*

## Validity Mask
The four preprocessing-derived 1-band `uint8` valid-pixel masks located in `data/processed/satellite/` were applied:
- `sentinel2_2016_tile1_valid_mask.tif`
- `sentinel2_2016_tile2_valid_mask.tif`
- `sentinel2_2025_tile1_valid_mask.tif`
- `sentinel2_2025_tile2_valid_mask.tif`

Feature calculations were executed **strictly on pixels where `mask == 1`** (pixels where all 6 raw bands are finite and within $[0.0, 1.0]$). Pixels where `mask == 0` were assigned IEEE 754 `NaN` (nodata = `np.nan`). NaN values were never converted to zero.

## Formulas
The canonical project methodology formulas were implemented:

1. **Normalized Difference Vegetation Index (NDVI)**:
   $$\text{NDVI} = \frac{\text{B8} - \text{B4}}{\text{B8} + \text{B4}}$$
   *(B8 = NIR ~842 nm, B4 = Red ~665 nm)*

2. **Normalized Difference Water Index (NDWI, McFeeters 1996)**:
   $$\text{NDWI} = \frac{\text{B3} - \text{B8}}{\text{B3} + \text{B8}}$$
   *(B3 = Green ~560 nm, B8 = NIR ~842 nm)*

3. **Normalized Difference Built-Up Index (NDBI, Zha et al. 2003)**:
   $$\text{NDBI} = \frac{\text{B11} - \text{B8}}{\text{B11} + \text{B8}}$$
   *(B11 = SWIR1 ~1610 nm, B8 = NIR ~842 nm)*

### Numerical Safety:
Before computing each normalized ratio, denominators were verified:
$$\text{Denominator} = B_x + B_y$$
If $\text{Denominator} \le 1\times 10^{-7}$ or is non-finite, the output is set to `NaN` to prevent division-by-zero or floating-point instability.

## Processing Method
- **Memory-Safe Block/Window Streaming**: Processed raw rasters in vertical chunks of 1,024 rows. Only the specific 4 bands needed ($B3, B4, B8, B11$) were loaded per chunk, maintaining peak RAM consumption below 200 MB throughout the entire district-wide generation (~458 million pixels).
- **Concurrent Writer Streams**: Generated all three indices in a single I/O pass per tile, saving disk read bandwidth.
- **Raster Specifications**: Single-band `float32` GeoTIFFs, LZW compression, tiled blocks ($256\times 256$), with native CRS (`EPSG:4326`), pixel dimensions, and spatial bounds strictly preserved from the source rasters.

## Outputs
All 12 feature rasters were created in `data/processed/features/`:

### 2016 Feature Rasters:
- `sentinel2_2016_tile1_ndvi.tif` (269.6 MB, float32, 13,568 × 12,893)
- `sentinel2_2016_tile1_ndwi.tif` (264.8 MB, float32, 13,568 × 12,893)
- `sentinel2_2016_tile1_ndbi.tif` (293.5 MB, float32, 13,568 × 12,893)
- `sentinel2_2016_tile2_ndvi.tif` (22.8 MB, float32, 4,195 × 12,893)
- `sentinel2_2016_tile2_ndwi.tif` (22.4 MB, float32, 4,195 × 12,893)
- `sentinel2_2016_tile2_ndbi.tif` (24.6 MB, float32, 4,195 × 12,893)

### 2025 Feature Rasters:
- `sentinel2_2025_tile1_ndvi.tif` (270.8 MB, float32, 13,568 × 12,893)
- `sentinel2_2025_tile1_ndwi.tif` (266.6 MB, float32, 13,568 × 12,893)
- `sentinel2_2025_tile1_ndbi.tif` (294.0 MB, float32, 13,568 × 12,893)
- `sentinel2_2025_tile2_ndvi.tif` (23.3 MB, float32, 4,195 × 12,893)
- `sentinel2_2025_tile2_ndwi.tif` (22.6 MB, float32, 4,195 × 12,893)
- `sentinel2_2025_tile2_ndbi.tif` (24.7 MB, float32, 4,195 × 12,893)

### Metadata Manifest:
- `data/metadata/sentinel2_feature_manifest.json`

## Quality Control & Numerical Results
Full-census statistics across all 12 generated feature rasters:

| Raster Filename | Total Pixels | Finite Valid | % Finite | Min | Max | Mean | Median | StdDev | p1 | p99 | % > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **2016 Tile 1 NDVI** | 174,932,224 | 64,152,494 | 36.67% | -0.7285 | 0.9031 | 0.4655 | 0.4571 | 0.1718 | 0.0886 | 0.7937 | 99.75% |
| **2016 Tile 1 NDWI** | 174,932,224 | 64,152,494 | 36.67% | -0.8286 | 0.8197 | -0.5080 | -0.5117 | 0.1477 | -0.7816 | -0.1197 | 0.30% |
| **2016 Tile 1 NDBI** | 174,932,224 | 64,152,494 | 36.67% | -0.7466 | 0.8418 | 0.0140 | 0.0326 | 0.1491 | -0.3478 | 0.3040 | 60.99% |
| **2016 Tile 2 NDVI** | 54,086,135 | 5,103,779 | 9.44% | -0.9843 | 0.8932 | 0.4849 | 0.4961 | 0.1691 | 0.0638 | 0.8037 | 98.99% |
| **2016 Tile 2 NDWI** | 54,086,135 | 5,103,779 | 9.44% | -0.8048 | 0.9903 | -0.5073 | -0.5223 | 0.1555 | -0.7884 | -0.0653 | 1.15% |
| **2016 Tile 2 NDBI** | 54,086,135 | 5,103,779 | 9.44% | -0.8055 | 0.9570 | -0.0156 | -0.0063 | 0.1593 | -0.3957 | 0.3168 | 48.38% |
| **2025 Tile 1 NDVI** | 174,932,224 | 64,153,381 | 36.67% | -0.5807 | 0.9037 | 0.4674 | 0.4681 | 0.1592 | 0.0967 | 0.7788 | 99.50% |
| **2025 Tile 1 NDWI** | 174,932,224 | 64,153,381 | 36.67% | -0.8186 | 0.7182 | -0.4961 | -0.5079 | 0.1417 | -0.7675 | -0.1197 | 0.68% |
| **2025 Tile 1 NDBI** | 174,932,224 | 64,153,381 | 36.67% | -0.7900 | 0.6706 | 0.0235 | 0.0406 | 0.1382 | -0.3134 | 0.2878 | 62.17% |
| **2025 Tile 2 NDVI** | 54,086,135 | 5,105,619 | 9.44% | -1.0000 | 0.8955 | 0.5322 | 0.5567 | 0.1691 | 0.0717 | 0.8197 | 98.75% |
| **2025 Tile 2 NDWI** | 54,086,135 | 5,105,619 | 9.44% | -0.8061 | 1.0000 | -0.5141 | -0.5387 | 0.1539 | -0.7937 | -0.0759 | 1.54% |
| **2025 Tile 2 NDBI** | 54,086,135 | 5,105,619 | 9.44% | -0.7638 | 1.0000 | -0.0444 | -0.0426 | 0.1561 | -0.4206 | 0.2871 | 38.24% |

### Value Range & Sanity Verification:
- **Range Sanity**: All 12 feature rasters have values strictly bounded within the theoretical range of $[-1.0, +1.0]$. Zero pixels were out of range (0 values $< -1.0$ or $> +1.0$).
- **Spatial Alignment**: All 12 rasters match source dimensions, CRS (`EPSG:4326`), affine transforms, resolutions (~10 m), and bounding coordinates exactly.
- **Raw Data Integrity**: Zero raw TIFF files were modified or overwritten.

## Scientific Interpretation
1. **NDVI (Vegetation-Related Spectral Indicator)**:
   - High mean/median values (~0.46 to 0.56) and over 98.7% positive values reflect extensive agricultural fields, forested hills (Eastern Ghats / Seshachalam foothills), and dense shrublands across Chittoor District during composite periods.
   - Negative NDVI corresponds to water bodies, quarry excavations, and bare rock outcrops.
2. **NDWI (Water-Related Spectral Indicator under McFeeters formulation)**:
   - Heavily negative mean/median values (~ -0.50 to -0.54) across 98.5%–99.7% of the landscape correctly indicate non-water terrestrial surfaces where NIR reflectance strongly exceeds green reflectance.
   - Positive NDWI values (0.30% to 1.54% of pixels) delineate lakes, reservoirs, irrigation tanks (e.g., Kalyan Revu, local cheruvus), and riverbeds.
3. **NDBI (Built-Up / Urban-Related Spectral Indicator)**:
   - Balanced distribution centered near zero (median -0.04 to +0.04) with 38.2% to 62.2% positive pixels. Positive NDBI identifies settlement built-up areas, concrete infrastructure, transport networks, quarries, and arid/dry bare soil where SWIR1 reflectance exceeds NIR reflectance.

## Limitations
- **Indicators vs. Ground Truth**: These spectral indices are continuous biophysical indicators, not discrete ground-truth land-cover classes.
- **NDBI Sensitivity**: NDBI responds to both built structures and dry bare soil/fallow agricultural fields due to similar SWIR/NIR reflectance ratios; separation requires multi-index fusion or supervised classification.
- **NDVI Background Influence**: In sparse vegetation, soil background reflectance can attenuate NDVI response.
- **NDWI Formulation**: McFeeters NDWI uses Green and NIR; it is sensitive to turbidity and aquatic vegetation.
- **Temporal Comparability**: 2016 and 2025 composites have different annual scene collection densities (~53 vs. ~253 scenes), which influences seasonal composites.
- **No Change Detection**: In accordance with the methodology, zero change detection, subtraction, or thresholding was performed in this stage.

## Decision
All 12 Sentinel-2 spectral feature rasters passed quality control, numerical range verification, and spatial integrity checks. **The dataset is ready for Feature Validation, Visualization, and Image-Intelligence Preparation.**

## Reproducibility
- Script: `scripts/generate_sentinel2_features.py`
- Manifest: `data/metadata/sentinel2_feature_manifest.json`
- Feature Directory: `data/processed/features/`
- Environment: Python 3.10 / `rasterio 1.4.4` / `numpy`
