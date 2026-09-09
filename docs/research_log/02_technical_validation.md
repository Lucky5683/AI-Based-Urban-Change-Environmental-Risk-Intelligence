# Technical GeoTIFF Integrity & Header Validation

## Date
2026-09-06

## Objective
Validate all GeoTIFF files discovered in `data/raw/satellite/` to ensure file readability, header integrity, coordinate reference systems, pixel dimensions, spatial alignment, and stream readability using `rasterio` without modifying, resizing, or merging images.

## Input Data
- `data/raw/satellite/Chittoor_New_BuiltUp_2016_2025.tif`
- `data/raw/satellite/Chittoor_Sentinel2_2016_Multispectral-0000000000-0000000000.tif`
- `data/raw/satellite/Chittoor_Sentinel2_2016_Multispectral-0000000000-0000013568.tif`
- `data/raw/satellite/Chittoor_Sentinel2_2025_Multispectral-0000000000-0000000000.tif`
- `data/raw/satellite/Chittoor_Sentinel2_2025_Multispectral-0000000000-0000013568.tif`

## Data Source
Google Earth Engine export (Copernicus Sentinel-2 Surface Reflectance and urban built-up transition classification).

## Method
- Automated dynamic file discovery for all `.tif`/`.tiff` files strictly inside `data/raw/satellite/` without assuming hardcoded counts or specific filenames.
- Inspected metadata using `rasterio`: driver, dimensions (W x H), band count, CRS, affine transform, spatial bounds, data types, nodata values, block shapes, and tiling.
- Evaluated window stream readability via 16×16 window test without loading full rasters into memory.
- Non-destructive execution: no files modified, resampled, merged, or renamed.

## Results
- **Files Discovered**: 5 GeoTIFF files (4 Sentinel-2 multispectral tiles, 1 thematic built-up change raster).
- **All 5 files passed technical validation.**

### Detailed File Verification Metrics:
1. **`Chittoor_New_BuiltUp_2016_2025.tif`**:
   - File Size: 3.32 MB (3,483,862 bytes)
   - Driver: GTiff
   - Dimensions: 17,763 (W) × 12,893 (H) pixels
   - Band Count: 1
   - Data Type: `uint8`
   - CRS: EPSG:4326
   - Resolution: `(8.983152841195215e-05, 8.983152841195215e-05)` deg (~10 m)
   - Bounds: Left=78.199244, Bottom=12.623935, Right=79.794921, Top=13.782133
   - Stream Readable: True
   - Status: PASSED

2. **`Chittoor_Sentinel2_2016_Multispectral-0000000000-0000000000.tif`**:
   - File Size: 1.27 GB (1,366,324,593 bytes)
   - Driver: GTiff
   - Dimensions: 13,568 (W) × 12,893 (H) pixels
   - Band Count: 6
   - Data Type: `float32` (all 6 bands)
   - CRS: EPSG:4326
   - Resolution: `(8.983152841195215e-05, 8.983152841195215e-05)` deg (~10 m)
   - Bounds: Left=78.199244, Bottom=12.623935, Right=79.418078, Top=13.782133
   - Stream Readable: True
   - Status: PASSED

3. **`Chittoor_Sentinel2_2016_Multispectral-0000000000-0000013568.tif`**:
   - File Size: 103.62 MB (108,656,567 bytes)
   - Driver: GTiff
   - Dimensions: 4,195 (W) × 12,893 (H) pixels
   - Band Count: 6
   - Data Type: `float32` (all 6 bands)
   - CRS: EPSG:4326
   - Resolution: `(8.983152841195215e-05, 8.983152841195215e-05)` deg (~10 m)
   - Bounds: Left=79.418078, Bottom=12.623935, Right=79.794921, Top=13.782133
   - Stream Readable: True
   - Status: PASSED

4. **`Chittoor_Sentinel2_2025_Multispectral-0000000000-0000000000.tif`**:
   - File Size: 1.26 GB (1,355,939,101 bytes)
   - Driver: GTiff
   - Dimensions: 13,568 (W) × 12,893 (H) pixels
   - Band Count: 6
   - Data Type: `float32` (all 6 bands)
   - CRS: EPSG:4326
   - Resolution: `(8.983152841195215e-05, 8.983152841195215e-05)` deg (~10 m)
   - Bounds: Left=78.199244, Bottom=12.623935, Right=79.418078, Top=13.782133
   - Stream Readable: True
   - Status: PASSED

5. **`Chittoor_Sentinel2_2025_Multispectral-0000000000-0000013568.tif`**:
   - File Size: 105.83 MB (110,965,827 bytes)
   - Driver: GTiff
   - Dimensions: 4,195 (W) × 12,893 (H) pixels
   - Band Count: 6
   - Data Type: `float32` (all 6 bands)
   - CRS: EPSG:4326
   - Resolution: `(8.983152841195215e-05, 8.983152841195215e-05)` deg (~10 m)
   - Bounds: Left=79.418078, Bottom=12.623935, Right=79.794921, Top=13.782133
   - Stream Readable: True
   - Status: PASSED

### Spatial Consistency Verification:
- **Width Alignment**: The western tile width (13,568 px) and eastern tile width (4,195 px) sum to exactly 17,763 pixels, precisely matching the district-wide built-up raster width (17,763 px).
- **Height Alignment**: All 5 rasters share an identical pixel height of 12,893 pixels.
- **Latitude Extent**: All 5 rasters share identical north/south bounds (`Top=13.782133`, `Bottom=12.623935`).
- **No data loss or file corruption observed.**

## Validation Status
PASS
All 5 discovered GeoTIFF files satisfy all technical integrity checks, possess valid spatial transforms, compatible CRS, correct data types, and stream readability.

## Scientific Interpretation
- **Observation**: The Sentinel-2 multispectral exports and thematic built-up rasters are geographically co-registered to the same spatial grid at ~10 m ground sampling distance.
- **Inference**: The exact match in pixel dimensions, bounding coordinates, and pixel grid alignment eliminates spatial misalignment artifacts during change detection and risk overlay analyses.

## Limitations
- CRS is in geographic coordinates (EPSG:4326, degrees). While optimal for global data sharing, area/distance calculations must use projected coordinates or geodesic metrics.
- Rasters are partitioned into 2 tiles; processing must maintain tile alignment or handle boundary continuity.

## Decision
Proceed to scientific band validation for the four Sentinel-2 multispectral rasters.

## Reproducibility
- Validation Script: `scripts/validate_satellite.py`
- Environment: Python 3.10 / `rasterio 1.4.4`
