# Urban Change Detection & Land Transition Log

> [!NOTE]
> Pixel-level Sentinel-2 change detection between 2016 and 2025 has been completed and fully documented in [07_change_detection.md](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/docs/research_log/07_change_detection.md).
>
> This log tracks the upcoming integrated spatial change interpretation, transition quantification, and urban expansion validation.

## Date
2026-09-06

## Objective
Quantify and map urban expansion, land cover conversions, transition matrices, and rate of built-up area change between 2016 and 2025 using the validated Sentinel-2 spectral difference rasters (NDVI, NDWI, NDBI).

## Input Data
- `data/processed/change_detection/sentinel2_tile1_ndvi_change_2016_2025.tif`
- `data/processed/change_detection/sentinel2_tile2_ndvi_change_2016_2025.tif`
- `data/processed/change_detection/sentinel2_tile1_ndwi_change_2016_2025.tif`
- `data/processed/change_detection/sentinel2_tile2_ndwi_change_2016_2025.tif`
- `data/processed/change_detection/sentinel2_tile1_ndbi_change_2016_2025.tif`
- `data/processed/change_detection/sentinel2_tile2_ndbi_change_2016_2025.tif`
- Manifest: `data/metadata/sentinel2_change_detection_manifest.json`

## Method
- Pixel-level spectral change detection: completed via `scripts/detect_sentinel2_change.py`.
- Integrated spatial change interpretation: pending execution in the next stage.

## Validation Status
Spectral Change Detection: **PASSED** (all 6 rasters verified with spatial integrity, common-valid masking, and 0 raw files modified).
