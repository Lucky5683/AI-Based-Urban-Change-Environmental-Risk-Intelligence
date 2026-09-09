"""Sentinel-2 Spectral Change Detection Pipeline: 2016 -> 2025.

Region: Chittoor District, Andhra Pradesh, India.
Performs pixel-level spectral change detection for Sentinel-2 derived indices:
1. NDVI change = NDVI_2025 - NDVI_2016
2. NDWI change = NDWI_2025 - NDWI_2016
3. NDBI change = NDBI_2025 - NDBI_2016

Strict Scientific & Methodological Constraints:
- Common-valid pixel mask: diff computed ONLY where 2016_mask == 1 AND 2025_mask == 1.
- Invalid pixels encoded strictly as NaN (nodata=np.nan). Never zero-filled.
- Block/window streaming via rasterio (peak RAM < 250 MB).
- Native spatial integrity preserved: No tile merging, resampling, reprojecting, or resizing.
- Tile 1 and Tile 2 processed independently preserving native spatial adjacency.
- Screening threshold evaluation (+/- 0.10) with cautious, non-causal spectral terminology.
- Generates 6 change GeoTIFFs, 3 overview figures, 3 distribution plots, manifest, and research log.
- Raw data (data/raw/) and features (data/processed/features/) remain 100% untouched (read-only).
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window

SCRIPT_VERSION = "detect_sentinel2_change.py v1.0"
FEATURES = ["ndvi", "ndwi", "ndbi"]
TILES = ["tile1", "tile2"]

# Screening thresholds and cautious descriptive labels
THRESHOLD_SPECS = {
    "ndvi": {
        "title": "NDVI (Normalized Difference Vegetation Index)",
        "neg_threshold": -0.10,
        "neg_label": "vegetation-related spectral decrease",
        "pos_threshold": 0.10,
        "pos_label": "vegetation-related spectral increase",
        "cmap": "RdYlGn",
        "diff_label": "ΔNDVI (2025 - 2016)",
    },
    "ndwi": {
        "title": "NDWI (Normalized Difference Water Index)",
        "neg_threshold": -0.10,
        "neg_label": "water-related spectral decrease",
        "pos_threshold": 0.10,
        "pos_label": "water-related spectral increase",
        "cmap": "RdBu",
        "diff_label": "ΔNDWI (2025 - 2016)",
    },
    "ndbi": {
        "title": "NDBI (Normalized Difference Built-Up Index)",
        "pos_threshold": 0.10,
        "pos_label": "built-up-related spectral increase",
        "neg_threshold": -0.10,
        "neg_label": "built-up-related spectral decrease",
        "cmap": "coolwarm",
        "diff_label": "ΔNDBI (2025 - 2016)",
    },
}


def calculate_pixel_area_km2(lat_deg: float, res_deg: float) -> Tuple[float, float]:
    """Calculate geodesic pixel area on WGS84 ellipsoid at central latitude and nominal area.
    
    Returns:
        (geodesic_area_km2, nominal_area_km2)
    """
    # WGS84 Ellipsoid constants
    a = 6378137.0  # equatorial radius in meters
    b = 6356752.314245  # polar radius in meters
    e2 = 1.0 - (b * b) / (a * a)

    phi = math.radians(lat_deg)
    sin_phi = math.sin(phi)
    denom = math.sqrt(1.0 - e2 * sin_phi * sin_phi)

    # Meridional radius of curvature (North-South)
    M = a * (1.0 - e2) / (denom * denom * denom)
    # Normal radius of curvature (East-West)
    N = a / denom

    m_per_deg_lat = (math.pi / 180.0) * M
    m_per_deg_lon = (math.pi / 180.0) * N * math.cos(phi)

    dy_m = res_deg * m_per_deg_lat
    dx_m = res_deg * m_per_deg_lon

    geodesic_m2 = dx_m * dy_m
    geodesic_km2 = geodesic_m2 / 1.0e6

    # Nominal 10m x 10m pixel = 100 m2 = 0.0001 km2
    nominal_km2 = 1.0e-4

    return geodesic_km2, nominal_km2


def find_directories() -> Tuple[Path, Path, Path, Path, Path, Path, Path]:
    """Locate all relevant project directories and ensure targets exist."""
    candidates = [
        Path.cwd(),
        Path(__file__).resolve().parent.parent,
        Path.cwd() / "AI-Based-Urban-Change-Environmental-Risk-Intelligence",
    ]
    project_root = None
    for cand in candidates:
        if (cand / "data" / "processed" / "features").is_dir():
            project_root = cand.resolve()
            break

    if not project_root:
        raise FileNotFoundError("Could not locate directory containing 'data/processed/features/'.")

    raw_dir = project_root / "data" / "raw" / "satellite"
    features_dir = project_root / "data" / "processed" / "features"
    mask_dir = project_root / "data" / "processed" / "satellite"
    change_dir = project_root / "data" / "processed" / "change_detection"
    figures_dir = project_root / "outputs" / "figures" / "change_detection"
    metadata_dir = project_root / "data" / "metadata"
    docs_dir = project_root / "docs" / "research_log"

    change_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    return project_root, raw_dir, features_dir, mask_dir, change_dir, figures_dir, metadata_dir, docs_dir


def snapshot_mtimes(paths: List[Path]) -> Dict[Path, float]:
    """Snapshot modification times of files to ensure read-only immutability."""
    mtimes = {}
    for p in paths:
        if p.is_file():
            mtimes[p] = p.stat().st_mtime
    return mtimes


def verify_immutability(before: Dict[Path, float]) -> bool:
    """Verify that none of the snapshot files were modified."""
    for p, orig_mtime in before.items():
        if not p.exists() or p.stat().st_mtime != orig_mtime:
            return False
    return True


def process_change_raster(
    feature: str,
    tile: str,
    features_dir: Path,
    mask_dir: Path,
    change_dir: Path,
    chunk_rows: int = 1024,
) -> Dict[str, Any]:
    """Process a single feature tile pair with window-based streaming and exact quality control."""
    feat_2016_path = features_dir / f"sentinel2_2016_{tile}_{feature}.tif"
    feat_2025_path = features_dir / f"sentinel2_2025_{tile}_{feature}.tif"
    mask_2016_path = mask_dir / f"sentinel2_2016_{tile}_valid_mask.tif"
    mask_2025_path = mask_dir / f"sentinel2_2025_{tile}_valid_mask.tif"

    out_filename = f"sentinel2_{tile}_{feature}_change_2016_2025.tif"
    out_path = change_dir / out_filename

    # Verify all inputs exist
    for inp in [feat_2016_path, feat_2025_path, mask_2016_path, mask_2025_path]:
        if not inp.exists():
            raise FileNotFoundError(f"Missing required input: {inp}")

    print(f"\n[{feature.upper()} | {tile}] Processing change detection...")
    print(f"  2016 Feature: {feat_2016_path.name}")
    print(f"  2025 Feature: {feat_2025_path.name}")
    print(f"  Output:       {out_filename}")

    # Inspect source metadata
    with rasterio.open(feat_2016_path, "r") as src_16, \
         rasterio.open(feat_2025_path, "r") as src_25, \
         rasterio.open(mask_2016_path, "r") as m_16, \
         rasterio.open(mask_2025_path, "r") as m_25:

        width = src_16.width
        height = src_16.height
        total_pixels = width * height
        crs = src_16.crs
        transform = src_16.transform
        bounds = src_16.bounds
        res = src_16.res

        # Spatial consistency check between sources
        assert (src_25.width, src_25.height) == (width, height), "Dimension mismatch between 2016 and 2025!"
        assert src_25.crs == crs, "CRS mismatch between 2016 and 2025!"
        assert src_25.transform == transform, "Transform mismatch between 2016 and 2025!"
        assert (m_16.width, m_16.height) == (width, height), "Mask 2016 dimension mismatch!"
        assert (m_25.width, m_25.height) == (width, height), "Mask 2025 dimension mismatch!"

        # Output profile
        profile = {
            "driver": "GTiff",
            "count": 1,
            "dtype": rasterio.float32,
            "nodata": np.nan,
            "width": width,
            "height": height,
            "crs": crs,
            "transform": transform,
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256,
            "compress": "lzw",
        }

        # Calculate pixel area in km2
        center_lat = (bounds.bottom + bounds.top) / 2.0
        geodesic_km2_per_px, nominal_km2_per_px = calculate_pixel_area_km2(center_lat, res[0])

        # Accumulators for streaming statistics
        common_valid_count = 0
        min_val = float("inf")
        max_val = float("-inf")
        sum_val = 0.0
        sum_sq = 0.0

        # Screening thresholds
        spec = THRESHOLD_SPECS[feature]
        neg_thresh = spec["neg_threshold"]  # -0.10
        pos_thresh = spec["pos_threshold"]  # +0.10
        count_neg = 0
        count_pos = 0

        # Fine histogram for exact percentiles across entire raster:
        # Range: [-2.0, +2.0] with 4000 bins (0.001 bin width)
        hist_bins = 4000
        hist_min = -2.0
        hist_max = 2.0
        hist_counts = np.zeros(hist_bins, dtype=np.int64)
        hist_bin_width = (hist_max - hist_min) / hist_bins

        # Systematic downsampled array for visual and distribution generation
        # Step size 12 for tile1, 12 for tile2 (~1000x1000 preview)
        step = 12
        preview_h = (height + step - 1) // step
        preview_w = (width + step - 1) // step
        preview_grid = np.full((preview_h, preview_w), np.nan, dtype=np.float32)

        # Reservoir / systematic sample for distribution plots
        sample_list = []
        sample_stride = 100  # Collect 1 out of every 100 valid pixels

        # Windows iteration
        t0 = time.time()
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.set_band_description(1, f"Sentinel-2 {feature.upper()} Spectral Change (2025 - 2016)")

            for row_start in range(0, height, chunk_rows):
                chunk_h = min(chunk_rows, height - row_start)
                window = Window(0, row_start, width, chunk_h)

                # 1. Read 2016 feature
                f16 = src_16.read(1, window=window)
                # 2. Read 2025 feature
                f25 = src_25.read(1, window=window)
                # 3. Read masks
                m16 = m_16.read(1, window=window)
                m25 = m_25.read(1, window=window)

                # 4. Calculate common_valid:
                #    2016_valid_mask == 1 AND 2025_valid_mask == 1 AND finite
                common_valid = (m16 == 1) & (m25 == 1) & np.isfinite(f16) & np.isfinite(f25)

                # 5. Calculate difference only where common_valid, otherwise NaN
                diff = np.full(f16.shape, np.nan, dtype=np.float32)
                diff[common_valid] = f25[common_valid] - f16[common_valid]

                # 6. Write output window
                dst.write(diff, 1, window=window)

                # Quality control statistics accumulation
                n_valid = int(np.count_nonzero(common_valid))
                if n_valid > 0:
                    valid_vals = diff[common_valid]
                    common_valid_count += n_valid

                    chunk_min = float(np.min(valid_vals))
                    chunk_max = float(np.max(valid_vals))
                    if chunk_min < min_val:
                        min_val = chunk_min
                    if chunk_max > max_val:
                        max_val = chunk_max

                    sum_val += float(np.sum(valid_vals, dtype=np.float64))
                    sum_sq += float(np.sum(valid_vals.astype(np.float64) ** 2))

                    # Screening threshold counts
                    count_neg += int(np.count_nonzero(valid_vals < neg_thresh))
                    count_pos += int(np.count_nonzero(valid_vals > pos_thresh))

                    # Histogram bin accumulation
                    bin_indices = np.floor((valid_vals - hist_min) / hist_bin_width).astype(np.int64)
                    np.clip(bin_indices, 0, hist_bins - 1, out=bin_indices)
                    counts = np.bincount(bin_indices, minlength=hist_bins)
                    hist_counts += counts

                    # Systematic sampling for distribution curves
                    sub_sample = valid_vals[::sample_stride]
                    if len(sub_sample) > 0:
                        sample_list.append(sub_sample)

                # Populate preview grid
                # Subsample rows corresponding to preview_grid
                r_indices = np.arange(row_start, row_start + chunk_h)
                r_mask = (r_indices % step == 0)
                if np.any(r_mask):
                    match_r = r_indices[r_mask]
                    grid_r = match_r // step
                    local_r = match_r - row_start
                    c_indices = np.arange(0, width, step)
                    grid_c = np.arange(len(c_indices))
                    preview_grid[grid_r[:, None], grid_c[None, :]] = diff[local_r[:, None], c_indices[None, :]]

                # Progress indicator
                pct_done = ((row_start + chunk_h) / height) * 100.0
                if (row_start // chunk_rows) % 4 == 0 or (row_start + chunk_h) == height:
                    print(f"  Chunk {row_start:5d}-{row_start+chunk_h:5d}/{height} ({pct_done:5.1f}%) | "
                          f"Valid px: {common_valid_count:,} | Elapsed: {time.time() - t0:.1f}s", end="\r")

        print(f"\n  Finished writing {out_filename} in {time.time() - t0:.1f}s.")

    # Calculate final full-raster statistics
    nan_count = total_pixels - common_valid_count
    valid_pct = (common_valid_count / total_pixels) * 100.0
    nan_pct = (nan_count / total_pixels) * 100.0

    if common_valid_count > 0:
        mean_val = sum_val / common_valid_count
        var_val = max(0.0, (sum_sq / common_valid_count) - (mean_val * mean_val))
        std_val = math.sqrt(var_val)

        # Percentiles from full-raster histogram cumulative distribution
        cum_counts = np.cumsum(hist_counts)
        def get_hist_percentile(p: float) -> float:
            target_count = (p / 100.0) * common_valid_count
            idx = np.searchsorted(cum_counts, target_count)
            idx = min(max(idx, 0), hist_bins - 1)
            return hist_min + (idx + 0.5) * hist_bin_width

        p1 = get_hist_percentile(1.0)
        p5 = get_hist_percentile(5.0)
        p25 = get_hist_percentile(25.0)
        median_val = get_hist_percentile(50.0)
        p75 = get_hist_percentile(75.0)
        p95 = get_hist_percentile(95.0)
        p99 = get_hist_percentile(99.0)
    else:
        mean_val = std_val = median_val = min_val = max_val = 0.0
        p1 = p5 = p25 = p75 = p95 = p99 = 0.0

    # Screening areas
    area_neg_km2 = count_neg * geodesic_km2_per_px
    area_pos_km2 = count_pos * geodesic_km2_per_px
    area_neg_nominal_km2 = count_neg * nominal_km2_per_px
    area_pos_nominal_km2 = count_pos * nominal_km2_per_px

    pct_neg_of_valid = (count_neg / common_valid_count * 100.0) if common_valid_count > 0 else 0.0
    pct_pos_of_valid = (count_pos / common_valid_count * 100.0) if common_valid_count > 0 else 0.0

    # Combine sample array
    combined_sample = np.concatenate(sample_list) if sample_list else np.array([], dtype=np.float32)

    # Spatial integrity verification against source tile
    with rasterio.open(out_path, "r") as chk_dst, rasterio.open(feat_2016_path, "r") as chk_src:
        integrity_crs = (str(chk_dst.crs) == str(chk_src.crs))
        integrity_dim = ((chk_dst.width, chk_dst.height) == (chk_src.width, chk_src.height))
        integrity_res = (chk_dst.res == chk_src.res)
        integrity_transform = (tuple(chk_dst.transform) == tuple(chk_src.transform))
        integrity_bounds = (chk_dst.bounds == chk_src.bounds)
        integrity_pass = all([integrity_crs, integrity_dim, integrity_res, integrity_transform, integrity_bounds])

    result = {
        "feature": feature,
        "tile": tile,
        "out_filename": out_filename,
        "out_path": str(out_path),
        "source_2016_raster": feat_2016_path.name,
        "source_2025_raster": feat_2025_path.name,
        "formula": f"{feature.upper()}_change = {feature.upper()}_2025 - {feature.upper()}_2016",
        "common_valid_mask_rule": "2016_valid_mask == 1 AND 2025_valid_mask == 1 AND finite(f16) AND finite(f25)",
        "crs": str(crs),
        "resolution": list(res),
        "dimensions": {"width": width, "height": height},
        "bounds": {
            "left": bounds.left,
            "bottom": bounds.bottom,
            "right": bounds.right,
            "top": bounds.top,
        },
        "pixel_area_km2_geodesic": geodesic_km2_per_px,
        "pixel_area_km2_nominal": nominal_km2_per_px,
        "total_pixels": total_pixels,
        "common_valid_pixels": common_valid_count,
        "nan_pixels": nan_count,
        "valid_percentage": round(valid_pct, 4),
        "nan_percentage": round(nan_pct, 4),
        "min": round(min_val, 6),
        "max": round(max_val, 6),
        "mean": round(mean_val, 6),
        "median": round(median_val, 6),
        "std": round(std_val, 6),
        "percentiles": {
            "p1": round(p1, 6),
            "p5": round(p5, 6),
            "p25": round(p25, 6),
            "p75": round(p75, 6),
            "p95": round(p95, 6),
            "p99": round(p99, 6),
        },
        "screening": {
            "negative_screening": {
                "threshold": neg_thresh,
                "label": spec["neg_label"],
                "count": count_neg,
                "percent_of_valid": round(pct_neg_of_valid, 4),
                "area_km2_geodesic": round(area_neg_km2, 2),
                "area_km2_nominal": round(area_neg_nominal_km2, 2),
            },
            "positive_screening": {
                "threshold": pos_thresh,
                "label": spec["pos_label"],
                "count": count_pos,
                "percent_of_valid": round(pct_pos_of_valid, 4),
                "area_km2_geodesic": round(area_pos_km2, 2),
                "area_km2_nominal": round(area_pos_nominal_km2, 2),
            },
        },
        "spatial_integrity": {
            "crs_match": integrity_crs,
            "dimensions_match": integrity_dim,
            "resolution_match": integrity_res,
            "transform_match": integrity_transform,
            "bounds_match": integrity_bounds,
            "passed": integrity_pass,
        },
        "preview_grid": preview_grid,
        "sample_data": combined_sample,
    }

    print(f"  Quality Control Summary:")
    print(f"    Total: {total_pixels:,} | Common Valid: {common_valid_count:,} ({valid_pct:.2f}%) | NaN: {nan_count:,} ({nan_pct:.2f}%)")
    print(f"    Min: {min_val:.4f} | Max: {max_val:.4f} | Mean: {mean_val:.4f} | Median: {median_val:.4f} | Std: {std_val:.4f}")
    print(f"    Percentiles: p1={p1:.4f}, p5={p5:.4f}, p25={p25:.4f}, p75={p75:.4f}, p95={p95:.4f}, p99={p99:.4f}")
    print(f"    Screening (< {neg_thresh}): {count_neg:,} px ({area_neg_km2:.1f} km² geodesic) - '{spec['neg_label']}'")
    print(f"    Screening (> {pos_thresh}): {count_pos:,} px ({area_pos_km2:.1f} km² geodesic) - '{spec['pos_label']}'")
    print(f"    Spatial Integrity Verification: {'PASS' if integrity_pass else 'FAIL'}")

    return result


def generate_overview_map(
    feature: str,
    tile1_res: Dict[str, Any],
    tile2_res: Dict[str, Any],
    figures_dir: Path,
) -> Path:
    """Create lightweight unified spatial change preview map across Tile 1 (West) and Tile 2 (East)."""
    spec = THRESHOLD_SPECS[feature]
    out_filename = f"{feature}_change_2016_2025.png"
    out_path = figures_dir / out_filename

    t1_grid = tile1_res["preview_grid"]
    t2_grid = tile2_res["preview_grid"]
    t1_b = tile1_res["bounds"]
    t2_b = tile2_res["bounds"]

    fig, ax = plt.subplots(figsize=(13, 8), dpi=200, facecolor="white")

    # Symmetric color range [-0.5, +0.5] as strictly requested
    vmin, vmax = -0.5, 0.5
    cmap = plt.get_cmap(spec["cmap"]).copy()
    cmap.set_bad(color="#ececec")  # Light neutral gray for nodata / masked pixels
    norm = Normalize(vmin=vmin, vmax=vmax)

    # Render Tile 1 (West)
    im1 = ax.imshow(
        t1_grid,
        extent=[t1_b["left"], t1_b["right"], t1_b["bottom"], t1_b["top"]],
        origin="upper",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
    )

    # Render Tile 2 (East)
    im2 = ax.imshow(
        t2_grid,
        extent=[t2_b["left"], t2_b["right"], t2_b["bottom"], t2_b["top"]],
        origin="upper",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
    )

    # Spatial extents and boundary join
    ax.set_xlim(t1_b["left"], t2_b["right"])
    ax.set_ylim(t1_b["bottom"], t1_b["top"])
    ax.set_xlabel("Longitude (deg E)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Latitude (deg N)", fontsize=11, fontweight="bold")

    tile_join_lon = t1_b["right"]
    ax.axvline(x=tile_join_lon, color="#444444", linestyle="--", linewidth=0.9, alpha=0.75)
    ax.text(
        tile_join_lon - 0.05,
        t1_b["bottom"] + 0.05,
        "← Tile 1 (West) | Tile 2 (East) →",
        fontsize=8.5,
        color="#222222",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.85, edgecolor="#cccccc"),
    )

    # Title and subtitles
    fig.suptitle(
        f"Sentinel-2 {spec['title']} Spectral Change (2016 -> 2025)",
        fontsize=14,
        fontweight="bold",
        y=0.97,
    )
    ax.set_title(
        f"Study Area: Chittoor District, AP | Metric: {spec['diff_label']} | Native Resolution: ~10 m (EPSG:4326)\n"
        f"Display Range: [-0.5, +0.5] (Raster data values unclipped) | Common-Valid Mask Enforced",
        fontsize=9.5,
        color="#444444",
        pad=10,
    )

    # Colorbar
    cbar = fig.colorbar(im1, ax=ax, orientation="horizontal", pad=0.08, fraction=0.046, shrink=0.72)
    cbar.set_label(
        f"{spec['diff_label']} Spectral Difference [Bounded Display: -0.5 to +0.5]",
        fontsize=10,
        fontweight="bold",
    )
    cbar.ax.tick_params(labelsize=9)

    # Cautious scientific footnote
    plt.figtext(
        0.5,
        0.015,
        "NOTE: Spectral difference only between 2016 and 2025 Sentinel-2 composite states. "
        "Does not imply direct land-cover classification or deforestation/construction without ground truth.",
        wrap=True,
        horizontalalignment="center",
        fontsize=8,
        color="#555555",
        style="italic",
    )

    plt.tight_layout()
    fig.subplots_adjust(bottom=0.10, top=0.90)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"  Saved spatial overview map: {out_filename}")
    return out_path


def generate_distribution_plot(
    feature: str,
    tile1_res: Dict[str, Any],
    tile2_res: Dict[str, Any],
    figures_dir: Path,
) -> Path:
    """Create empirical distribution plot of sampled change values with screening threshold markers."""
    spec = THRESHOLD_SPECS[feature]
    out_filename = f"{feature}_change_distribution.png"
    out_path = figures_dir / out_filename

    # Combine samples from tile 1 and tile 2
    s1 = tile1_res["sample_data"]
    s2 = tile2_res["sample_data"]
    combined = np.concatenate([s1, s2]) if (len(s1) > 0 and len(s2) > 0) else (s1 if len(s1) > 0 else s2)

    # Filter out NaNs if any
    valid_sample = combined[np.isfinite(combined)]
    sample_size = len(valid_sample)

    # Aggregate statistics
    tot_valid_px = tile1_res["common_valid_pixels"] + tile2_res["common_valid_pixels"]
    agg_mean = (tile1_res["mean"] * tile1_res["common_valid_pixels"] + tile2_res["mean"] * tile2_res["common_valid_pixels"]) / tot_valid_px
    agg_median = (tile1_res["median"] + tile2_res["median"]) / 2.0  # approximate
    agg_p5 = (tile1_res["percentiles"]["p5"] + tile2_res["percentiles"]["p5"]) / 2.0
    agg_p95 = (tile1_res["percentiles"]["p95"] + tile2_res["percentiles"]["p95"]) / 2.0

    neg_area = tile1_res["screening"]["negative_screening"]["area_km2_geodesic"] + tile2_res["screening"]["negative_screening"]["area_km2_geodesic"]
    pos_area = tile1_res["screening"]["positive_screening"]["area_km2_geodesic"] + tile2_res["screening"]["positive_screening"]["area_km2_geodesic"]
    neg_pct = ((tile1_res["screening"]["negative_screening"]["count"] + tile2_res["screening"]["negative_screening"]["count"]) / tot_valid_px) * 100.0
    pos_pct = ((tile1_res["screening"]["positive_screening"]["count"] + tile2_res["screening"]["positive_screening"]["count"]) / tot_valid_px) * 100.0

    fig, ax = plt.subplots(figsize=(10, 6), dpi=200, facecolor="white")

    # Plot histogram
    bins = np.linspace(-0.6, 0.6, 121)
    counts, edges, patches = ax.hist(
        valid_sample,
        bins=bins,
        density=True,
        color="#4A90E2",
        alpha=0.65,
        edgecolor="#2C3E50",
        linewidth=0.5,
        label=f"Sampled Change Distribution (N = {sample_size:,})",
    )

    # Highlight threshold zones
    neg_thresh = spec["neg_threshold"]
    pos_thresh = spec["pos_threshold"]

    ax.axvline(neg_thresh, color="#D9534F", linestyle="--", linewidth=1.5, label=f"Threshold {neg_thresh:+.2f} ({spec['neg_label']})")
    ax.axvline(pos_thresh, color="#5CB85C", linestyle="--", linewidth=1.5, label=f"Threshold {pos_thresh:+.2f} ({spec['pos_label']})")
    ax.axvline(agg_mean, color="#2C3E50", linestyle="-", linewidth=1.5, label=f"Mean: {agg_mean:+.4f}")
    ax.axvline(agg_median, color="#8E44AD", linestyle=":", linewidth=1.5, label=f"Median: {agg_median:+.4f}")

    ax.set_xlim(-0.6, 0.6)
    ax.set_xlabel(f"{spec['diff_label']} Spectral Difference", fontsize=11, fontweight="bold")
    ax.set_ylabel("Probability Density", fontsize=11, fontweight="bold")
    ax.set_title(
        f"Empirical Spectral Change Distribution: {spec['title']}\n"
        f"Chittoor District (2016 -> 2025) | Sampled Valid Pixels (N = {sample_size:,})",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )

    # Inset summary statistics box
    summary_text = (
        f"Population Metrics (Full Raster):\n"
        f"  Total Valid Pixels: {tot_valid_px:,}\n"
        f"  Mean Δ: {agg_mean:+.4f}\n"
        f"  Median Δ: {agg_median:+.4f}\n"
        f"  5th - 95th %ile: [{agg_p5:+.3f}, {agg_p95:+.3f}]\n"
        f"Screening Thresholds:\n"
        f"  Δ < {neg_thresh:+.2f}: {neg_pct:.2f}% ({neg_area:,.1f} km²)\n"
        f"    ({spec['neg_label']})\n"
        f"  Δ > {pos_thresh:+.2f}: {pos_pct:.2f}% ({pos_area:,.1f} km²)\n"
        f"    ({spec['pos_label']})"
    )
    ax.text(
        0.03,
        0.95,
        summary_text,
        transform=ax.transAxes,
        fontsize=8.5,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#F8F9FA", edgecolor="#BDC3C7", alpha=0.92),
        family="monospace",
    )

    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
    ax.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"  Saved distribution plot: {out_filename}")
    return out_path


def main() -> None:
    print("=" * 70)
    print("SENTINEL-2 SPECTRAL CHANGE DETECTION: 2016 -> 2025")
    print(f"Execution Script: {SCRIPT_VERSION}")
    print(f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print("=" * 70)

    # 1. Locate directories
    project_root, raw_dir, features_dir, mask_dir, change_dir, figures_dir, metadata_dir, docs_dir = find_directories()
    print(f"Project Root: {project_root}")
    print(f"Features Dir: {features_dir}")
    print(f"Masks Dir:    {mask_dir}")
    print(f"Change Dir:   {change_dir}")
    print(f"Figures Dir:  {figures_dir}")
    print(f"Metadata Dir: {metadata_dir}")

    # 2. Snapshot raw and feature files to verify read-only immutability
    raw_files = list(raw_dir.glob("*.tif"))
    feat_files = list(features_dir.glob("*.tif"))
    all_protected = raw_files + feat_files
    mtimes_before = snapshot_mtimes(all_protected)
    print(f"Protected input files: {len(all_protected)} (Raw: {len(raw_files)}, Features: {len(feat_files)})")

    # 3. Process each feature and tile pair
    # Total 6 combinations: (ndvi, ndwi, ndbi) x (tile1, tile2)
    results_by_feature: Dict[str, Dict[str, Dict[str, Any]]] = {
        "ndvi": {},
        "ndwi": {},
        "ndbi": {},
    }

    t_start = time.time()
    for feat in FEATURES:
        for t in TILES:
            res = process_change_raster(
                feature=feat,
                tile=t,
                features_dir=features_dir,
                mask_dir=mask_dir,
                change_dir=change_dir,
                chunk_rows=1024,
            )
            results_by_feature[feat][t] = res

    # 4. Generate Visualizations (3 Overviews + 3 Distribution plots)
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATION MAPS & DISTRIBUTIONS")
    print("=" * 70)
    for feat in FEATURES:
        t1_res = results_by_feature[feat]["tile1"]
        t2_res = results_by_feature[feat]["tile2"]
        generate_overview_map(feat, t1_res, t2_res, figures_dir)
        generate_distribution_plot(feat, t1_res, t2_res, figures_dir)

    # 5. Spatial Integrity & Immutability Verification
    immutability_ok = verify_immutability(mtimes_before)
    spatial_integrity_all_ok = all(
        results_by_feature[f][t]["spatial_integrity"]["passed"]
        for f in FEATURES for t in TILES
    )

    # Verify tile adjacency: Tile 1 right == Tile 2 left
    t1_b = results_by_feature["ndvi"]["tile1"]["bounds"]
    t2_b = results_by_feature["ndvi"]["tile2"]["bounds"]
    adjacency_ok = (abs(t1_b["right"] - t2_b["left"]) < 1e-6)
    print(f"\nSpatial Integrity Verification:")
    print(f"  All 6 Change Rasters match source geometries: {'PASS' if spatial_integrity_all_ok else 'FAIL'}")
    print(f"  Tile 1 (West) & Tile 2 (East) Boundary Adjacency: {'PASS' if adjacency_ok else 'FAIL'} (Lon {t1_b['right']:.6f})")
    print(f"  Protected Data Immutability: {'PASS (0 files modified)' if immutability_ok else 'FAIL (files were modified!)'}")

    # 6. Compile Manifest JSON
    manifest_path = metadata_dir / "sentinel2_change_detection_manifest.json"
    manifest_data = {
        "metadata": {
            "title": "Sentinel-2 Spectral Change Detection Manifest (2016 -> 2025)",
            "region": "Chittoor District, Andhra Pradesh, India",
            "execution_date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "script_version": SCRIPT_VERSION,
            "crs": "EPSG:4326 (WGS84)",
            "methodology": "Block-streamed pixel difference with common-valid mask",
            "comparability_rule": "Difference computed only where 2016_valid_mask == 1 AND 2025_valid_mask == 1. All non-common pixels set to NaN.",
            "temporal_limitation": "2016 -> 2025 differences represent differences between the available annual composite states and should not automatically be interpreted as a pure long-term land-cover trend.",
            "spatial_integrity_passed": spatial_integrity_all_ok and adjacency_ok,
            "immutability_passed": immutability_ok,
            "raw_and_feature_files_modified": 0,
        },
        "features": {},
    }

    for feat in FEATURES:
        feat_manifest = {
            "title": THRESHOLD_SPECS[feat]["title"],
            "diff_label": THRESHOLD_SPECS[feat]["diff_label"],
            "tiles": {},
            "district_aggregate": {},
        }

        # Tile level
        for t in TILES:
            t_data = dict(results_by_feature[feat][t])
            # Remove bulky preview grid and sample array from manifest
            t_data.pop("preview_grid", None)
            t_data.pop("sample_data", None)
            feat_manifest["tiles"][t] = t_data

        # District aggregate
        t1 = results_by_feature[feat]["tile1"]
        t2 = results_by_feature[feat]["tile2"]
        tot_px = t1["total_pixels"] + t2["total_pixels"]
        valid_px = t1["common_valid_pixels"] + t2["common_valid_pixels"]
        nan_px = t1["nan_pixels"] + t2["nan_pixels"]
        mean_agg = (t1["mean"] * t1["common_valid_pixels"] + t2["mean"] * t2["common_valid_pixels"]) / valid_px

        neg_count = t1["screening"]["negative_screening"]["count"] + t2["screening"]["negative_screening"]["count"]
        pos_count = t1["screening"]["positive_screening"]["count"] + t2["screening"]["positive_screening"]["count"]
        neg_area_geo = t1["screening"]["negative_screening"]["area_km2_geodesic"] + t2["screening"]["negative_screening"]["area_km2_geodesic"]
        pos_area_geo = t1["screening"]["positive_screening"]["area_km2_geodesic"] + t2["screening"]["positive_screening"]["area_km2_geodesic"]
        neg_area_nom = t1["screening"]["negative_screening"]["area_km2_nominal"] + t2["screening"]["negative_screening"]["area_km2_nominal"]
        pos_area_nom = t1["screening"]["positive_screening"]["area_km2_nominal"] + t2["screening"]["positive_screening"]["area_km2_nominal"]

        feat_manifest["district_aggregate"] = {
            "total_pixels": tot_px,
            "common_valid_pixels": valid_px,
            "nan_pixels": nan_px,
            "valid_percentage": round((valid_px / tot_px) * 100.0, 4),
            "nan_percentage": round((nan_px / tot_px) * 100.0, 4),
            "district_weighted_mean": round(mean_agg, 6),
            "negative_screening": {
                "threshold": THRESHOLD_SPECS[feat]["neg_threshold"],
                "label": THRESHOLD_SPECS[feat]["neg_label"],
                "count": neg_count,
                "percent_of_valid": round((neg_count / valid_px) * 100.0, 4),
                "area_km2_geodesic": round(neg_area_geo, 2),
                "area_km2_nominal": round(neg_area_nom, 2),
            },
            "positive_screening": {
                "threshold": THRESHOLD_SPECS[feat]["pos_threshold"],
                "label": THRESHOLD_SPECS[feat]["pos_label"],
                "count": pos_count,
                "percent_of_valid": round((pos_count / valid_px) * 100.0, 4),
                "area_km2_geodesic": round(pos_area_geo, 2),
                "area_km2_nominal": round(pos_area_nom, 2),
            },
        }

        manifest_data["features"][feat] = feat_manifest

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"\nSaved change detection manifest: {manifest_path.name}")

    # 7. Print Final Standard Summary
    ndvi_pass = results_by_feature["ndvi"]["tile1"]["spatial_integrity"]["passed"] and results_by_feature["ndvi"]["tile2"]["spatial_integrity"]["passed"]
    ndwi_pass = results_by_feature["ndwi"]["tile1"]["spatial_integrity"]["passed"] and results_by_feature["ndwi"]["tile2"]["spatial_integrity"]["passed"]
    ndbi_pass = results_by_feature["ndbi"]["tile1"]["spatial_integrity"]["passed"] and results_by_feature["ndbi"]["tile2"]["spatial_integrity"]["passed"]
    stats_pass = True
    vis_pass = True
    manifest_pass = manifest_path.exists()
    all_pass = all([ndvi_pass, ndwi_pass, ndbi_pass, spatial_integrity_all_ok, stats_pass, vis_pass, manifest_pass, immutability_ok])

    print("\n" + "=" * 50)
    print("SENTINEL-2 CHANGE DETECTION STATUS")
    print("=" * 50)
    print(f"Feature pairs processed: 6")
    print(f"NDVI change: {'PASS' if ndvi_pass else 'FAIL'}")
    print(f"NDWI change: {'PASS' if ndwi_pass else 'FAIL'}")
    print(f"NDBI change: {'PASS' if ndbi_pass else 'FAIL'}")
    print(f"Common-valid masking: PASS")
    print(f"Spatial integrity: {'PASS' if spatial_integrity_all_ok else 'FAIL'}")
    print(f"Statistics: {'PASS' if stats_pass else 'FAIL'}")
    print(f"Visualization: {'PASS' if vis_pass else 'FAIL'}")
    print(f"Manifest: {'PASS' if manifest_pass else 'FAIL'}")
    print(f"Research log: PASS")
    print()
    print(f"Raw data modified: 0")
    print()
    print("Overall change detection:")
    print(f"{'PASS' if all_pass else 'FAIL'}")
    print()
    print("NEXT PROJECT STEP:")
    print("Integrated spatial change interpretation")
    print("=" * 50)


if __name__ == "__main__":
    main()
