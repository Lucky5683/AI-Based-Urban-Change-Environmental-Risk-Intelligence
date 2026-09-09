"""Scientific Band Validation for Sentinel-2 Multispectral GeoTIFFs.

Validates band order, metadata descriptions, tags, dtypes, and sample window
statistics for 2016 and 2025 Sentinel-2 imagery of Chittoor District without
modifying, merging, resizing, or loading entire rasters into memory.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import rasterio
from rasterio.windows import Window

EXPECTED_BANDS = ("B2", "B3", "B4", "B8", "B11", "B12")


def find_satellite_dir(specified_dir: str | None = None) -> Path:
    if specified_dir:
        p = Path(specified_dir).resolve()
        if p.is_dir():
            return p
        raise FileNotFoundError(f"Directory not found: {specified_dir}")

    candidates = [
        Path.cwd() / "data" / "raw" / "satellite",
        Path(__file__).resolve().parent.parent / "data" / "raw" / "satellite",
        Path.cwd() / "AI-Based-Urban-Change-Environmental-Risk-Intelligence" / "data" / "raw" / "satellite",
    ]
    for c in candidates:
        if c.is_dir():
            return c.resolve()
    raise FileNotFoundError("Could not find 'data/raw/satellite/'.")


def discover_sentinel2_tiffs(satellite_dir: Path) -> List[Path]:
    """Discover exclusively the 4 Sentinel-2 multispectral GeoTIFFs."""
    tiffs = []
    for p in satellite_dir.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".tif", ".tiff"):
            continue
        # Exclude land cover / built-up masks or other non-Sentinel-2 products
        if "Sentinel2" in p.name and "Multispectral" in p.name:
            tiffs.append(p)
    return sorted(tiffs, key=lambda x: x.name)


def compute_sample_window_stats(src: rasterio.io.DatasetReader, window: Window) -> List[Dict[str, Any]]:
    """Read a small sample window and compute band-level statistics."""
    data = src.read(window=window)
    stats_list = []

    for b_idx in range(src.count):
        band_arr = data[b_idx]
        finite_mask = np.isfinite(band_arr)
        pct_finite = float(np.mean(finite_mask) * 100.0)
        valid_vals = band_arr[finite_mask]

        if len(valid_vals) > 0:
            stats_list.append({
                "band_num": b_idx + 1,
                "min": float(np.min(valid_vals)),
                "max": float(np.max(valid_vals)),
                "mean": float(np.mean(valid_vals)),
                "median": float(np.median(valid_vals)),
                "pct_finite": pct_finite,
            })
        else:
            stats_list.append({
                "band_num": b_idx + 1,
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "pct_finite": 0.0,
            })
    return stats_list


def inspect_sentinel2_tiff(path: Path) -> Dict[str, Any]:
    """Inspect metadata, band tags/descriptions, and sample statistics of a Sentinel-2 GeoTIFF."""
    result: Dict[str, Any] = {
        "filename": path.name,
        "path": str(path),
        "band_count": None,
        "band_descriptions": None,
        "band_tags": [],
        "global_tags": {},
        "dtypes": [],
        "crs": None,
        "resolution": None,
        "width": None,
        "height": None,
        "bounds": None,
        "sample_window": None,
        "band_stats": [],
    }

    with rasterio.open(path) as src:
        result["band_count"] = src.count
        result["band_descriptions"] = tuple(src.descriptions) if src.descriptions else ()
        result["global_tags"] = dict(src.tags())
        result["band_tags"] = [dict(src.tags(b)) for b in range(1, src.count + 1)]
        result["dtypes"] = list(src.dtypes)
        result["crs"] = str(src.crs) if src.crs else None
        result["resolution"] = src.res
        result["width"] = src.width
        result["height"] = src.height
        result["bounds"] = src.bounds

        # Pick a 100x100 sample window that lies within valid data area of the district
        # Western tile (x=6700, y=6400); Eastern tile (x=200, y=3200)
        if "0000013568" in path.name:
            col_off, row_off = 200, 3200
        else:
            col_off, row_off = 6700, 6400

        window = Window(col_off, row_off, 100, 100)
        result["sample_window"] = {"col_off": col_off, "row_off": row_off, "width": 100, "height": 100}
        result["band_stats"] = compute_sample_window_stats(src, window)

    return result


def parse_tile_id(filename: str) -> str:
    """Extract the tile coordinate string e.g. 0000000000-0000000000 or 0000000000-0000013568."""
    parts = filename.replace(".tif", "").replace(".tiff", "").split("-")
    if len(parts) >= 3:
        return f"{parts[-2]}-{parts[-1]}"
    return filename


def run_scientific_validation(satellite_dir: Path | None = None) -> int:
    sat_dir = find_satellite_dir(satellite_dir)
    tiffs = discover_sentinel2_tiffs(sat_dir)

    print("=" * 80)
    print("      SCIENTIFIC BAND VALIDATION: SENTINEL-2 MULTISPECTRAL GEOTIFFS")
    print("=" * 80)
    print(f"Directory: {sat_dir}")
    print(f"Discovered Sentinel-2 multispectral files ({len(tiffs)}):")
    for t in tiffs:
        print(f"  - {t.name}")
    print()

    if len(tiffs) != 4:
        print(f"[ERROR] Expected exactly 4 Sentinel-2 multispectral tiles, found {len(tiffs)}.")
        return 1

    inspections = [inspect_sentinel2_tiff(t) for t in tiffs]

    # Print individual file inspection
    for idx, info in enumerate(inspections, start=1):
        print("-" * 80)
        print(f"[{idx}/4] FILE: {info['filename']}")
        print("-" * 80)
        print(f"1. Filename                 : {info['filename']}")
        print(f"2. Band Count               : {info['band_count']}")
        print(f"3. Band Descriptions        : {info['band_descriptions']}")
        print(f"4. Band-Level Metadata/Tags : {info['band_tags']}")
        print(f"   Global Tags              : {info['global_tags']}")
        print(f"5. Raster Dtype             : {info['dtypes']}")
        print(f"6. Sample Window Evaluated  : {info['sample_window']} (100x100 pixels, inside district)")
        print("7. Band Statistics (Sample Window):")
        desc_labels = info["band_descriptions"] if info["band_descriptions"] else [f"Band_{i+1}" for i in range(info["band_count"])]
        for s in info["band_stats"]:
            b_label = desc_labels[s["band_num"] - 1] if s["band_num"] - 1 < len(desc_labels) else f"Band {s['band_num']}"
            if s["min"] is not None:
                print(f"   - Band {s['band_num']} [{b_label}]: min={s['min']:.4f}, max={s['max']:.4f}, mean={s['mean']:.4f}, median={s['median']:.4f}, finite={s['pct_finite']:.1f}%")
            else:
                print(f"   - Band {s['band_num']} [{b_label}]: min=N/A, max=N/A, mean=N/A, median=N/A, finite={s['pct_finite']:.1f}%")

    # Pair files between 2016 and 2025
    files_2016 = {parse_tile_id(i["filename"]): i for i in inspections if "2016" in i["filename"]}
    files_2025 = {parse_tile_id(i["filename"]): i for i in inspections if "2025" in i["filename"]}

    print("\n" + "=" * 80)
    print("           TEMPORAL PAIRING & CONSISTENCY COMPARISON (2016 vs 2025)")
    print("=" * 80)

    checks = []

    # Check 1: Pair matching
    common_tiles = sorted(set(files_2016.keys()).intersection(set(files_2025.keys())))
    pairing_ok = len(common_tiles) == 2 and len(files_2016) == 2 and len(files_2025) == 2
    checks.append(("Four Sentinel-2 tiles paired correctly between 2016 and 2025", pairing_ok))
    print(f"- Temporal Tile Pairs Formed: {len(common_tiles)} pairs")
    for tile_id in common_tiles:
        print(f"  * Tile ID [{tile_id}]:\n      2016 -> {files_2016[tile_id]['filename']}\n      2025 -> {files_2025[tile_id]['filename']}")

    # Check 2: Same number of bands
    all_band_counts = [i["band_count"] for i in inspections]
    same_band_count = all(bc == 6 for bc in all_band_counts)
    checks.append(("Both years have the same number of bands (6 bands)", same_band_count))

    # Check 3: Band ordering
    descriptions_match = all(i["band_descriptions"] == EXPECTED_BANDS for i in inspections)
    checks.append((f"Band ordering matches expected {EXPECTED_BANDS}", descriptions_match))

    # Check 4: CRS identical
    all_crs = [i["crs"] for i in inspections]
    crs_identical = len(set(all_crs)) == 1 and all_crs[0] == "EPSG:4326"
    checks.append(("CRS is identical across all files (EPSG:4326)", crs_identical))

    # Check 5: Resolution identical
    all_res = [i["resolution"] for i in inspections]
    res_identical = len(set(all_res)) == 1
    checks.append(("Pixel resolution (GSD) is identical across all files", res_identical))

    # Check 6 & 7: Dimensions and Bounds of corresponding tiles identical
    dims_bounds_ok = True
    for tile_id in common_tiles:
        t16 = files_2016[tile_id]
        t25 = files_2025[tile_id]
        if (t16["width"], t16["height"]) != (t25["width"], t25["height"]):
            dims_bounds_ok = False
        if t16["bounds"] != t25["bounds"]:
            dims_bounds_ok = False

    checks.append(("Pixel dimensions of corresponding tiles are identical", dims_bounds_ok))
    checks.append(("Corresponding tile spatial bounds are identical", dims_bounds_ok))

    print("\nVerification Checklist:")
    all_checks_passed = True
    for name, passed in checks:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_checks_passed = False
        print(f"  [{status_str}] {name}")

    print("\n" + "=" * 80)
    print("SCIENTIFIC BAND IDENTITY CONFIRMATION IN GEOTIFF METADATA:")
    print("=" * 80)
    if descriptions_match:
        print("CONFIRMED VIA GDAL BAND DESCRIPTIONS:")
        print("The GeoTIFF files explicitly encode the band names in the GDAL Band Descriptions metadata:")
        print(f"  Band Descriptions: {EXPECTED_BANDS}")
        print("  - Band 1: B2  (Blue, ~490 nm)")
        print("  - Band 2: B3  (Green, ~560 nm)")
        print("  - Band 3: B4  (Red, ~665 nm)")
        print("  - Band 4: B8  (NIR Broad, ~842 nm)")
        print("  - Band 5: B11 (SWIR-1, ~1610 nm)")
        print("  - Band 6: B12 (SWIR-2, ~2190 nm)")
        print("Note: Band-level key-value tag dictionaries (src.tags(b)) are empty ({}), but the standard")
        print("GDAL band description field within the GeoTIFF header explicitly specifies the band names.")
    else:
        print("UNCONFIRMED IN METADATA:")
        print("The TIFF metadata itself does not independently encode the Sentinel-2 band names.")
        print("The band order is known from the original Google Earth Engine export definition.")

    print("\n" + "=" * 80)
    print("SCIENTIFIC BAND VALIDATION STATUS:")
    if all_checks_passed:
        print("PASS")
    else:
        print("REVIEW REQUIRED")
    print("=" * 80)

    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    sys.exit(run_scientific_validation())
