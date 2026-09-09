"""Raster Utilities for Memory-Safe Sentinel-2 Imagery & Feature Inspection.

Uses rasterio windowed reads and downsampling to strictly prevent loading
multi-gigabyte GeoTIFFs into system RAM.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import rasterio
from rasterio.windows import Window
import streamlit as st

from dashboard.utils.data_loader import PROJECT_ROOT


# Predefined Regions of Interest (approximate window coordinates [col_off, row_off, width, height])
# Selected across the 12,893 x 13,568 pixel Sentinel-2 scene.
PRESET_ROIS = {
    "Chittoor Municipal Core": {"col_off": 7200, "row_off": 6400, "width": 800, "height": 800, "description": "District administrative center and dense built-up core."},
    "Tirupati Transit Corridor (East)": {"col_off": 10500, "row_off": 3200, "width": 800, "height": 800, "description": "High-expansion pilgrimage and transit development zone."},
    "Western Agricultural Basin": {"col_off": 3000, "row_off": 7000, "width": 800, "height": 800, "description": "Intensive agricultural land showing seasonal vegetation dynamics."},
    "Central Valley & Water Bodies": {"col_off": 5500, "row_off": 5000, "width": 800, "height": 800, "description": "River drainage corridors and surface water reservoirs."},
}

# Image paths relative to project root
RASTER_PATHS = {
    "2016_raw": "data/raw/satellite/Chittoor_Sentinel2_2016_Multispectral-0000000000-0000000000.tif",
    "2025_raw": "data/raw/satellite/Chittoor_Sentinel2_2025_Multispectral-0000000000-0000000000.tif",
    "2016_ndvi": "data/processed/features/sentinel2_2016_tile1_ndvi.tif",
    "2025_ndvi": "data/processed/features/sentinel2_2025_tile1_ndvi.tif",
    "2016_ndwi": "data/processed/features/sentinel2_2016_tile1_ndwi.tif",
    "2025_ndwi": "data/processed/features/sentinel2_2025_tile1_ndwi.tif",
    "2016_ndbi": "data/processed/features/sentinel2_2016_tile1_ndbi.tif",
    "2025_ndbi": "data/processed/features/sentinel2_2025_tile1_ndbi.tif",
    "ndvi_change": "data/processed/change_detection/sentinel2_tile1_ndvi_change_2016_2025.tif",
    "ndwi_change": "data/processed/change_detection/sentinel2_tile1_ndwi_change_2016_2025.tif",
    "ndbi_change": "data/processed/change_detection/sentinel2_tile1_ndbi_change_2016_2025.tif",
}

# Static validated overview figures
FIGURE_OVERVIEWS = {
    "ndvi_2016": "outputs/figures/sentinel2_features/ndvi_2016_overview.png",
    "ndvi_2025": "outputs/figures/sentinel2_features/ndvi_2025_overview.png",
    "ndvi_change": "outputs/figures/change_detection/ndvi_change_2016_2025.png",
    "ndwi_2016": "outputs/figures/sentinel2_features/ndwi_2016_overview.png",
    "ndwi_2025": "outputs/figures/sentinel2_features/ndwi_2025_overview.png",
    "ndwi_change": "outputs/figures/change_detection/ndwi_change_2016_2025.png",
    "ndbi_2016": "outputs/figures/sentinel2_features/ndbi_2016_overview.png",
    "ndbi_2025": "outputs/figures/sentinel2_features/ndbi_2025_overview.png",
    "ndbi_change": "outputs/figures/change_detection/ndbi_change_2016_2025.png",
    "stress_1km": "outputs/figures/environmental_stress/environmental_stress_indicator_1km.png",
    "forecast_chart": "outputs/figures/forecasting/final_builtup_forecast_2026.png",
}


def normalize_rgb(img_array: np.ndarray, lower_p: float = 2.0, upper_p: float = 98.0) -> np.ndarray:
    """Normalize multi-band 3D array (bands, H, W) to (H, W, 3) in [0.0, 1.0] with percentile clip."""
    # Transpose to (H, W, bands)
    if img_array.ndim == 3 and img_array.shape[0] in (3, 4):
        img_array = np.transpose(img_array, (1, 2, 0))
    
    out = np.zeros(img_array.shape, dtype=np.float32)
    for b in range(img_array.shape[-1]):
        band = img_array[..., b]
        valid = band[np.isfinite(band)]
        if valid.size == 0:
            continue
        v_min, v_max = np.percentile(valid, lower_p), np.percentile(valid, upper_p)
        if v_max > v_min:
            scaled = (band - v_min) / (v_max - v_min)
            out[..., b] = np.clip(scaled, 0.0, 1.0)
        else:
            out[..., b] = 0.5
    return out


@st.cache_data(show_spinner=False)
def read_raster_window_rgb(
    year: int,
    roi_key: str = "Chittoor Municipal Core",
    false_color: bool = False,
    decimate: int = 1
) -> Optional[np.ndarray]:
    """Read a small spatial window from Sentinel-2 multispectral GeoTIFF.
    
    Band layout:
    Band 1: B2 (Blue), Band 2: B3 (Green), Band 3: B4 (Red), Band 4: B8 (NIR)
    True Color: Red=B4 (band 3), Green=B3 (band 2), Blue=B2 (band 1)
    False Color: Red=B8 (band 4), Green=B4 (band 3), Blue=B3 (band 2)
    """
    key = f"{year}_raw"
    rel_path = RASTER_PATHS.get(key)
    if not rel_path:
        return None
    full_path = PROJECT_ROOT / rel_path
    if not full_path.is_file():
        return None

    roi = PRESET_ROIS.get(roi_key, PRESET_ROIS["Chittoor Municipal Core"])
    window = Window(roi["col_off"], roi["row_off"], roi["width"], roi["height"])

    band_indices = [4, 3, 2] if false_color else [3, 2, 1]

    try:
        with rasterio.open(full_path) as src:
            # Safe bounds check
            w_clamped = window.intersection(Window(0, 0, src.width, src.height))
            data = src.read(band_indices, window=w_clamped)
            if decimate > 1:
                data = data[:, ::decimate, ::decimate]
            return normalize_rgb(data)
    except Exception as e:
        try:
            st.warning(f"Could not load window from {rel_path}: {e}")
        except Exception:
            pass
        return None


@st.cache_data(show_spinner=False)
def read_feature_window(
    feature_type: str,
    year_or_change: str,
    roi_key: str = "Chittoor Municipal Core",
    decimate: int = 1
) -> Optional[np.ndarray]:
    """Read a small single-band feature window (NDVI, NDWI, NDBI, or change)."""
    if year_or_change == "change":
        key = f"{feature_type.lower()}_change"
    else:
        key = f"{year_or_change}_{feature_type.lower()}"

    rel_path = RASTER_PATHS.get(key)
    if not rel_path:
        return None
    full_path = PROJECT_ROOT / rel_path
    if not full_path.is_file():
        return None

    roi = PRESET_ROIS.get(roi_key, PRESET_ROIS["Chittoor Municipal Core"])
    window = Window(roi["col_off"], roi["row_off"], roi["width"], roi["height"])

    try:
        with rasterio.open(full_path) as src:
            w_clamped = window.intersection(Window(0, 0, src.width, src.height))
            data = src.read(1, window=w_clamped)
            if decimate > 1:
                data = data[::decimate, ::decimate]
            return data
    except Exception as e:
        try:
            st.warning(f"Could not load feature window from {rel_path}: {e}")
        except Exception:
            pass
        return None


def get_figure_path(key: str) -> Optional[Path]:
    """Get absolute path to validated static overview figure."""
    rel = FIGURE_OVERVIEWS.get(key)
    if rel:
        p = PROJECT_ROOT / rel
        if p.is_file():
            return p
    return None
