"""Satellite GeoTIFF Data Validation Script.

Discovers and validates all GeoTIFF (.tif / .tiff) files in data/raw/satellite/
using rasterio without modifying, merging, resizing, or processing images.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import rasterio
from rasterio.windows import Window


def find_satellite_directory(specified_dir: str | None = None) -> Path:
    """Locate the data/raw/satellite directory from various relative positions."""
    if specified_dir:
        cand = Path(specified_dir).resolve()
        if cand.is_dir():
            return cand
        raise FileNotFoundError(f"Specified satellite directory does not exist: {specified_dir}")

    # Check common relative candidate locations
    candidates = [
        Path.cwd() / "data" / "raw" / "satellite",
        Path(__file__).resolve().parent.parent / "data" / "raw" / "satellite",
        Path.cwd() / "AI-Based-Urban-Change-Environmental-Risk-Intelligence" / "data" / "raw" / "satellite",
    ]

    for cand in candidates:
        if cand.is_dir():
            return cand.resolve()

    raise FileNotFoundError(
        "Could not automatically locate 'data/raw/satellite/'. "
        "Please provide the path via the --data-dir argument."
    )


def discover_tiff_files(directory: Path) -> List[Path]:
    """Discover all .tif and .tiff files strictly inside the specified directory."""
    tiff_extensions = {".tif", ".tiff"}
    discovered = [
        item for item in directory.iterdir()
        if item.is_file() and item.suffix.lower() in tiff_extensions
    ]
    return sorted(discovered, key=lambda p: p.name.lower())


def format_bytes(num_bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def validate_geotiff(file_path: Path) -> Dict[str, Any]:
    """Validate a single GeoTIFF file using rasterio and extract metadata."""
    file_size = file_path.stat().st_size
    info: Dict[str, Any] = {
        "filename": file_path.name,
        "path": str(file_path),
        "size_bytes": file_size,
        "size_formatted": format_bytes(file_size),
        "driver": None,
        "width": None,
        "height": None,
        "band_count": None,
        "crs": None,
        "bounds": None,
        "transform": None,
        "resolution": None,
        "dtypes": None,
        "nodata": None,
        "is_tiled": None,
        "block_shapes": None,
        "readable": False,
        "validation_status": "FAILED",
        "errors": [],
        "warnings": [],
    }

    try:
        with rasterio.open(file_path) as src:
            info["driver"] = src.driver
            info["width"] = src.width
            info["height"] = src.height
            info["band_count"] = src.count
            info["crs"] = str(src.crs) if src.crs else None
            info["bounds"] = src.bounds
            info["transform"] = tuple(src.transform)
            info["resolution"] = src.res
            info["dtypes"] = list(src.dtypes)
            info["nodata"] = src.nodata
            info["is_tiled"] = src.is_tiled
            info["block_shapes"] = list(src.block_shapes)

            # Checks
            if not src.width or src.width <= 0 or not src.height or src.height <= 0:
                info["errors"].append("Invalid raster dimensions (width or height <= 0).")

            if not src.count or src.count <= 0:
                info["errors"].append("No raster bands found.")

            if not src.crs:
                info["warnings"].append("Missing Coordinate Reference System (CRS).")

            if src.transform is None or src.transform.is_identity:
                info["warnings"].append("Affine transform is missing or default identity.")

            # Test sample window read (top-left 16x16 window) without loading full image into RAM
            test_w = min(16, src.width)
            test_h = min(16, src.height)
            if test_w > 0 and test_h > 0:
                sample_data = src.read(window=Window(0, 0, test_w, test_h))
                if sample_data is not None and sample_data.size > 0:
                    info["readable"] = True
                else:
                    info["errors"].append("Rasterio window read returned empty array.")
            else:
                info["readable"] = True

            if not info["errors"]:
                info["validation_status"] = "PASSED"
            else:
                info["validation_status"] = "FAILED"

    except Exception as exc:
        info["errors"].append(f"Failed to open or read GeoTIFF: {exc}")
        info["validation_status"] = "FAILED"

    return info


def print_validation_results(results: List[Dict[str, Any]], satellite_dir: Path) -> None:
    """Print structured metadata and validation summary for all discovered files."""
    separator = "=" * 80
    sub_sep = "-" * 80

    print("\n" + separator)
    print("      SATELLITE GEOTIFF VALIDATION REPORT (RASTERIO)")
    print(separator)
    print(f"Target Directory : {satellite_dir}")
    print(f"Files Discovered : {len(results)} GeoTIFF file(s)\n")

    if not results:
        print("[WARNING] No .tif / .tiff files found in target directory!")
        print(separator)
        return

    for idx, meta in enumerate(results, start=1):
        print(sub_sep)
        print(f"[{idx}/{len(results)}] File: {meta['filename']}")
        print(sub_sep)
        print(f"  - File Size        : {meta['size_formatted']} ({meta['size_bytes']:,} bytes)")
        print(f"  - Driver           : {meta['driver']}")
        print(f"  - Dimensions       : {meta['width']} (W) x {meta['height']} (H) pixels")
        print(f"  - Band Count       : {meta['band_count']}")
        print(f"  - Band Data Types  : {', '.join(meta['dtypes']) if meta['dtypes'] else 'N/A'}")
        print(f"  - CRS              : {meta['crs']}")
        print(f"  - Resolution (GSD) : {meta['resolution']}")
        print(f"  - NoData Value     : {meta['nodata']}")
        print(f"  - Tiled            : {meta['is_tiled']} (Block shapes: {meta['block_shapes']})")
        if meta["bounds"]:
            b = meta["bounds"]
            print(f"  - Spatial Bounds   : Left={b.left:.6f}, Bottom={b.bottom:.6f}, Right={b.right:.6f}, Top={b.top:.6f}")
        if meta["transform"]:
            print(f"  - Transform Matrix : {meta['transform']}")
        print(f"  - Stream Readable  : {meta['readable']}")
        if meta["warnings"]:
            for w in meta["warnings"]:
                print(f"  - Warning          : {w}")
        if meta["errors"]:
            for e in meta["errors"]:
                print(f"  - Error            : {e}")
        print(f"  - Validation Status: {meta['validation_status']}")

    # Summary Table
    print("\n" + separator)
    print("                     VALIDATION SUMMARY TABLE")
    print(separator)
    header = f"{'Index':<6}{'Filename':<50}{'Bands':<7}{'Dimensions':<16}{'CRS':<12}{'Status':<8}"
    print(header)
    print("-" * len(header))

    passed_count = 0
    for idx, meta in enumerate(results, start=1):
        dims = f"{meta['width']}x{meta['height']}" if meta['width'] else "N/A"
        crs_str = meta['crs'] if meta['crs'] else "None"
        status = meta['validation_status']
        if status == "PASSED":
            passed_count += 1
        name_truncated = (meta['filename'][:47] + "...") if len(meta['filename']) > 50 else meta['filename']
        print(f"{idx:<6}{name_truncated:<50}{str(meta['band_count']):<7}{dims:<16}{crs_str:<12}{status:<8}")

    print(separator)
    print(f"Total Discovered : {len(results)}")
    print(f"Passed Validation: {passed_count}/{len(results)}")
    print(f"Failed Validation: {len(results) - passed_count}/{len(results)}")
    print(separator + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate satellite GeoTIFF files using rasterio.")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Path to data/raw/satellite directory (optional, discovered automatically by default)",
    )
    args = parser.parse_args()

    try:
        satellite_dir = find_satellite_directory(args.data_dir)
    except FileNotFoundError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    discovered_files = discover_tiff_files(satellite_dir)
    results = [validate_geotiff(f) for f in discovered_files]
    print_validation_results(results, satellite_dir)

    all_passed = bool(results) and all(r["validation_status"] == "PASSED" for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
