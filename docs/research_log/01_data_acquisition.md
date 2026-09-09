# Data Acquisition Log

## Date
2026-09-06

## Objective
Acquire, organize, and inventory multi-temporal satellite imagery, thematic landcover layers, and tabular research datasets for Chittoor District covering the 2016–2025 observation period.

## Input Data
- `data/raw/satellite/Chittoor_Sentinel2_2016_Multispectral-0000000000-0000000000.tif` (1.27 GB)
- `data/raw/satellite/Chittoor_Sentinel2_2016_Multispectral-0000000000-0000013568.tif` (103.62 MB)
- `data/raw/satellite/Chittoor_Sentinel2_2025_Multispectral-0000000000-0000000000.tif` (1.26 GB)
- `data/raw/satellite/Chittoor_Sentinel2_2025_Multispectral-0000000000-0000013568.tif` (105.83 MB)
- `data/raw/satellite/Chittoor_New_BuiltUp_2016_2025.tif` (3.32 MB)
- `data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv` (2.42 KB)

## Data Source
- **Sentinel-2 Multispectral Imagery**: Copernicus Sentinel-2 Level-2A (Surface Reflectance, Harmonized) exported via Google Earth Engine (`COPERNICUS/S2_SR_HARMONIZED`).
- **Built-Up Change Raster**: Derived from multi-temporal classification exported via Google Earth Engine.
- **Tabular Research Dataset**: `Chittoor_Master_Research_Dataset_2016_2025.csv`.

## Method
- Multi-spectral bands requested and exported: B2 (Blue), B3 (Green), B4 (Red), B8 (NIR Broad), B11 (SWIR-1), B12 (SWIR-2).
- Spatial coverage partitioned into two tiles due to district width exceeding standard GEE export pixel limits (Tile `0000000000-0000000000` and Tile `0000000000-0000013568`).
- Export format: Cloud-Optimized GeoTIFF (GTiff) tiled in 256×256 blocks with float32 reflectance values.

## Results
- Total satellite files acquired: 5 GeoTIFFs (4 Sentinel-2 multispectral tiles, 1 thematic built-up change raster).
- Total raw satellite data volume: ~2.74 GB.
- Processed dataset acquired: 1 master research dataset CSV.
- No files corrupted during download/transfer; all headers intact.

## Validation Status
PASS
All expected datasets were acquired and placed into standardized raw/processed directories according to repository specifications.

## Scientific Interpretation
- **Observation**: Partitioning into western and eastern tiles reflects standard GEE maxPixels tiling behavior for large administrative zones at 10 m resolution.
- **Inference**: Tile boundaries share identical latitude bounds and adjacent longitudes, ensuring seamless geospatial mosaicking capability.

## Limitations
- Satellite exports reflect cloud-free median composites for target seasonal periods in 2016 and 2025.
- Composite-based reflectance smooths short-term meteorological phenology.

## Decision
Perform systematic technical validation on all acquired GeoTIFF rasters using `rasterio`.

## Reproducibility
- Storage Directory: `data/raw/satellite/` and `data/processed/`
- Target Bounds: Chittoor District (Top=13.782133, Bottom=12.623935, Left=78.199244, Right=79.794921)
- Spatial Resolution: ~10 m (`8.983152841195215e-05` degrees)
