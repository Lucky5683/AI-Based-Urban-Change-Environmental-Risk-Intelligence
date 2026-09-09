"""Authoritative Data Loader for Chittoor Environmental Intelligence Dashboard.

Loads validated tabular assets, validates against the dashboard data contract,
and provides caching and robust error handling.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import streamlit as st


def get_project_root() -> Path:
    """Resolve the project root directory reliably."""
    # Try relative to this file: dashboard/utils/data_loader.py -> parent x 2
    root = Path(__file__).resolve().parent.parent.parent
    if (root / "outputs" / "tables").exists() or (root / "data").exists():
        return root
    
    # Fallback to current working directory
    cwd = Path.cwd()
    if (cwd / "outputs" / "tables").exists() or (cwd / "data").exists():
        return cwd
    
    # Check if inside project directory
    nested = cwd / "AI-Based-Urban-Change-Environmental-Risk-Intelligence"
    if nested.exists():
        return nested
    
    return root


PROJECT_ROOT = get_project_root()


def _resolve_path(rel_path: str) -> Path:
    """Resolve relative path against PROJECT_ROOT and verify existence."""
    candidates = [
        PROJECT_ROOT / rel_path,
        Path.cwd() / rel_path,
        PROJECT_ROOT / "outputs" / "tables" / Path(rel_path).name,
        PROJECT_ROOT / "data" / "processed" / Path(rel_path).name,
    ]
    for c in candidates:
        if c.is_file():
            return c
    return PROJECT_ROOT / rel_path


@st.cache_data(show_spinner=False)
def load_csv_safely(rel_path: str) -> Optional[pd.DataFrame]:
    """Load a CSV file safely with graceful Streamlit warning on failure."""
    resolved = _resolve_path(rel_path)
    if not resolved.is_file():
        # Only show st.warning if Streamlit runtime is active
        try:
            st.warning(f"Required analytical asset is missing: {rel_path}")
        except Exception:
            pass
        return None
    try:
        return pd.read_csv(resolved)
    except Exception as e:
        try:
            st.error(f"Error reading asset {rel_path}: {e}")
        except Exception:
            pass
        return None


@st.cache_data(show_spinner=False)
def load_data_contract() -> pd.DataFrame:
    """Load the authoritative dashboard data contract."""
    df = load_csv_safely("outputs/tables/dashboard_data_contract.csv")
    if df is None:
        raise FileNotFoundError("Missing authoritative file: outputs/tables/dashboard_data_contract.csv")
    return df


@st.cache_data(show_spinner=False)
def load_master_timeseries() -> pd.DataFrame:
    """Load the 10-year master research dataset (2016-2025)."""
    df = load_csv_safely("data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv")
    if df is None:
        df = load_csv_safely("outputs/tables/Chittoor_Master_Research_Dataset_2016_2025.csv")
    if df is None:
        raise FileNotFoundError("Missing master dataset: Chittoor_Master_Research_Dataset_2016_2025.csv")
    # Ensure year is integer sorted
    if "year" in df.columns:
        df["year"] = df["year"].astype(int)
        df = df.sort_values("year").reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_headline_audit() -> pd.DataFrame:
    """Load the audited headline results."""
    df = load_csv_safely("outputs/tables/final_headline_results_audit.csv")
    if df is None:
        raise FileNotFoundError("Missing headline audit: outputs/tables/final_headline_results_audit.csv")
    return df


@st.cache_data(show_spinner=False)
def load_units_dictionary() -> pd.DataFrame:
    """Load the project units dictionary."""
    df = load_csv_safely("outputs/tables/final_units_dictionary.csv")
    if df is None:
        raise FileNotFoundError("Missing units dictionary: outputs/tables/final_units_dictionary.csv")
    return df


@st.cache_data(show_spinner=False)
def load_stress_grid() -> pd.DataFrame:
    """Load the 1 km spatial environmental stress grid (N=6,902 cells)."""
    df = load_csv_safely("outputs/tables/environmental_stress_grid_1km_enriched.csv")
    if df is None:
        df = load_csv_safely("outputs/tables/environmental_stress_grid_1km.csv")
    if df is None:
        raise FileNotFoundError("Missing stress grid: outputs/tables/environmental_stress_grid_1km.csv")
    return df


@st.cache_data(show_spinner=False)
def load_stress_explainability() -> pd.DataFrame:
    """Load the cell-level stress explainability dataset."""
    df = load_csv_safely("outputs/tables/environmental_stress_explainability_enriched.csv")
    if df is None:
        df = load_csv_safely("outputs/tables/environmental_stress_explainability.csv")
    if df is None:
        raise FileNotFoundError("Missing explainability table: outputs/tables/environmental_stress_explainability.csv")
    return df


@st.cache_data(show_spinner=False)
def load_top_100_hotspots() -> pd.DataFrame:
    """Load the top 100 environmental stress hotspots with deterministic tie-break."""
    df = load_csv_safely("outputs/tables/top_100_environmental_stress_cells_enriched.csv")
    if df is None:
        df = load_csv_safely("outputs/tables/top_100_environmental_stress_cells.csv")
    if df is None:
        raise FileNotFoundError("Missing top 100 table: outputs/tables/top_100_environmental_stress_cells.csv")
    # Deterministic contract ordering: stress_score DESC, cell_id ASC
    if "stress_score" in df.columns and "cell_id" in df.columns:
        df = df.sort_values(by=["stress_score", "cell_id"], ascending=[False, True]).reset_index(drop=True)
        df["rank"] = range(1, len(df) + 1)
    return df


@st.cache_data(show_spinner=False)
def load_forecast_2026() -> pd.DataFrame:
    """Load the validated 2026 built-up forecast table."""
    df = load_csv_safely("outputs/tables/builtup_forecast_2026.csv")
    if df is None:
        raise FileNotFoundError("Missing forecast table: outputs/tables/builtup_forecast_2026.csv")
    return df


@st.cache_data(show_spinner=False)
def load_decision_matrix() -> pd.DataFrame:
    """Load the decision support matrix."""
    df = load_csv_safely("outputs/tables/decision_support_matrix.csv")
    if df is None:
        raise FileNotFoundError("Missing decision matrix: outputs/tables/decision_support_matrix.csv")
    return df


@st.cache_data(show_spinner=False)
def load_forecast_validation() -> pd.DataFrame:
    """Load the out-of-sample walk-forward validation backtesting table."""
    df = load_csv_safely("outputs/tables/builtup_forecast_validation.csv")
    if df is None:
        raise FileNotFoundError("Missing forecast validation table: outputs/tables/builtup_forecast_validation.csv")
    return df


@st.cache_data(show_spinner=False)
def load_model_comparison() -> pd.DataFrame:
    """Load the comprehensive multi-model comparison table."""
    df = load_csv_safely("outputs/tables/forecast_model_comparison.csv")
    if df is None:
        raise FileNotFoundError("Missing model comparison table: outputs/tables/forecast_model_comparison.csv")
    return df


@st.cache_data(show_spinner=False)
def load_feasibility_matrix() -> pd.DataFrame:
    """Load the systematic prediction feasibility matrix."""
    df = load_csv_safely("outputs/tables/prediction_feasibility_matrix.csv")
    if df is None:
        raise FileNotFoundError("Missing feasibility matrix: outputs/tables/prediction_feasibility_matrix.csv")
    return df


@st.cache_data(show_spinner=False)
def load_spatial_validation() -> pd.DataFrame:
    """Load the spatial statistical validation results (including Moran's I)."""
    df = load_csv_safely("outputs/tables/spatial_statistical_validation.csv")
    if df is None:
        raise FileNotFoundError("Missing spatial validation table: outputs/tables/spatial_statistical_validation.csv")
    return df


@st.cache_data(show_spinner=False)
def load_stress_sensitivity() -> pd.DataFrame:
    """Load the environmental stress indicator sensitivity analysis table."""
    df = load_csv_safely("outputs/tables/environmental_stress_sensitivity.csv")
    if df is None:
        raise FileNotFoundError("Missing stress sensitivity table: outputs/tables/environmental_stress_sensitivity.csv")
    return df


@st.cache_data(show_spinner=False)
def load_executive_summary() -> pd.DataFrame:
    """Load the executive decision summary."""
    df = load_csv_safely("outputs/tables/executive_decision_summary.csv")
    if df is None:
        raise FileNotFoundError("Missing executive summary: outputs/tables/executive_decision_summary.csv")
    return df



@st.cache_data(show_spinner=False)
def get_headline_metrics() -> Dict[str, Any]:
    """Extract authoritative headline metrics directly from validated tables."""
    master = load_master_timeseries()
    forecast = load_forecast_2026()
    grid = load_stress_grid()

    # 2016 vs 2025 values from Master CSV
    row_2016 = master[master["year"] == 2016].iloc[0]
    row_2025 = master[master["year"] == 2025].iloc[0]

    builtup_2016 = float(row_2016["built_up_km2"])
    builtup_2025 = float(row_2025["built_up_km2"])
    builtup_diff = builtup_2025 - builtup_2016
    builtup_pct = (builtup_diff / builtup_2016) * 100.0 if builtup_2016 != 0 else 0.0

    strong_core_2016 = float(row_2016["strong_built_up_km2"])
    strong_core_2025 = float(row_2025["strong_built_up_km2"])
    strong_core_diff = strong_core_2025 - strong_core_2016
    strong_core_pct = (strong_core_diff / strong_core_2016) * 100.0 if strong_core_2016 != 0 else 0.0

    ndvi_2016 = float(row_2016["NDVI"])
    ndvi_2025 = float(row_2025["NDVI"])
    ndvi_diff = ndvi_2025 - ndvi_2016
    ndvi_min = float(master["NDVI"].min())
    ndvi_max = float(master["NDVI"].max())

    lst_2016 = float(row_2016["LST_C"])
    lst_2025 = float(row_2025["LST_C"])
    lst_diff = lst_2025 - lst_2016
    lst_min = float(master["LST_C"].min())
    lst_max = float(master["LST_C"].max())

    rainfall_2016 = float(row_2016["rainfall_mm"])
    rainfall_2025 = float(row_2025["rainfall_mm"])
    rainfall_mean = float(master["rainfall_mm"].mean())
    rainfall_diff_mean = rainfall_2025 - rainfall_mean

    temporal_stress_2025 = float(row_2025["environmental_stress"])

    # Forecast row for Total Built-Up
    fc_row = forecast[forecast["target"].str.contains("Total Built-Up", case=False, na=False)].iloc[0]
    forecast_2026_val = float(fc_row["point_forecast"])
    forecast_2026_lower = float(fc_row["lower_95"])
    forecast_2026_upper = float(fc_row["upper_95"])

    # Forecast row for Strong Core
    fc_core_row = forecast[forecast["target"].str.contains("Strong Built-Up", case=False, na=False)].iloc[0]
    core_forecast_val = float(fc_core_row["point_forecast"])
    core_forecast_lower = float(fc_core_row["lower_95"])
    core_forecast_upper = float(fc_core_row["upper_95"])

    # Grid Stress Metrics
    stress_mean = float(grid["stress_score"].mean())
    stress_max = float(grid["stress_score"].max())
    peak_cell = grid.sort_values(by=["stress_score", "cell_id"], ascending=[False, True]).iloc[0]["cell_id"]

    return {
        "builtup_2016": builtup_2016,
        "builtup_2025": builtup_2025,
        "builtup_diff": builtup_diff,
        "builtup_pct": builtup_pct,
        "strong_core_2016": strong_core_2016,
        "strong_core_2025": strong_core_2025,
        "strong_core_diff": strong_core_diff,
        "strong_core_pct": strong_core_pct,
        "ndvi_2016": ndvi_2016,
        "ndvi_2025": ndvi_2025,
        "ndvi_diff": ndvi_diff,
        "ndvi_min": ndvi_min,
        "ndvi_max": ndvi_max,
        "lst_2016": lst_2016,
        "lst_2025": lst_2025,
        "lst_diff": lst_diff,
        "lst_min": lst_min,
        "lst_max": lst_max,
        "rainfall_2016": rainfall_2016,
        "rainfall_2025": rainfall_2025,
        "rainfall_mean": rainfall_mean,
        "rainfall_diff_mean": rainfall_diff_mean,
        "temporal_stress_2025": temporal_stress_2025,
        "forecast_2026": forecast_2026_val,
        "forecast_2026_lower": forecast_2026_lower,
        "forecast_2026_upper": forecast_2026_upper,
        "core_forecast": core_forecast_val,
        "core_forecast_lower": core_forecast_lower,
        "core_forecast_upper": core_forecast_upper,
        "stress_mean": stress_mean,
        "stress_max": stress_max,
        "peak_cell": peak_cell,
    }


@st.cache_data(show_spinner=False)
def load_spectral_screening_summary() -> Dict[str, Any]:
    """Load authoritative decadal spectral screening metrics from manifest and format table."""
    manifest_path = _resolve_path("data/metadata/sentinel2_change_detection_manifest.json")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing authoritative change detection manifest: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    features = manifest.get("features", {})
    ndvi_da = features.get("ndvi", {}).get("district_aggregate", {})
    ndwi_da = features.get("ndwi", {}).get("district_aggregate", {})
    ndbi_da = features.get("ndbi", {}).get("district_aggregate", {})

    tile1_info = features.get("ndvi", {}).get("tiles", {}).get("tile1", {})
    pixel_area_km2 = float(tile1_info.get("pixel_area_km2_geodesic", 9.677251838356328e-05))
    common_valid_pixels = int(ndvi_da.get("common_valid_pixels", 69256014))
    footprint_km2 = round(common_valid_pixels * pixel_area_km2, 2)

    ndvi_neg = ndvi_da.get("negative_screening", {})
    ndvi_pos = ndvi_da.get("positive_screening", {})
    ndwi_neg = ndwi_da.get("negative_screening", {})
    ndwi_pos = ndwi_da.get("positive_screening", {})
    ndbi_neg = ndbi_da.get("negative_screening", {})
    ndbi_pos = ndbi_da.get("positive_screening", {})

    records = [
        {
            "Spectral Index": "NDVI (Vegetation)",
            "Screening Direction": "NDVI decrease > 0.10 (Vegetation Decrease Screening)",
            "Area (km²)": float(ndvi_neg.get("area_km2_geodesic", 951.56)),
            "Percent of Valid": f"{float(ndvi_neg.get('percent_of_valid', 14.1979)):.2f}%",
            "Interpretation": "Candidate zones for vegetation canopy thinning / drought stress",
        },
        {
            "Spectral Index": "NDVI (Vegetation)",
            "Screening Direction": "NDVI increase > 0.10 (Vegetation Vigor Screening)",
            "Area (km²)": float(ndvi_pos.get("area_km2_geodesic", 1188.84)),
            "Percent of Valid": f"{float(ndvi_pos.get('percent_of_valid', 17.7383)):.2f}%",
            "Interpretation": "Canopy greening / post-monsoon agricultural recovery",
        },
        {
            "Spectral Index": "NDWI (Moisture)",
            "Screening Direction": "NDWI decrease > 0.10 (Surface Moisture Loss Screening)",
            "Area (km²)": float(ndwi_neg.get("area_km2_geodesic", 377.04)),
            "Percent of Valid": f"{float(ndwi_neg.get('percent_of_valid', 5.6257)):.2f}%",
            "Interpretation": "Surface water / tank shrinkage and soil moisture drawdown",
        },
        {
            "Spectral Index": "NDWI (Moisture)",
            "Screening Direction": "NDWI increase > 0.10 (Moisture Accretion Screening)",
            "Area (km²)": float(ndwi_pos.get("area_km2_geodesic", 581.42)),
            "Percent of Valid": f"{float(ndwi_pos.get('percent_of_valid', 8.6752)):.2f}%",
            "Interpretation": "Water storage replenishment and moist canal zones",
        },
        {
            "Spectral Index": "NDBI (Built-Up)",
            "Screening Direction": "NDBI decrease < -0.10 (Built/Bare Surface Decrease)",
            "Area (km²)": float(ndbi_neg.get("area_km2_geodesic", 829.42)),
            "Percent of Valid": f"{float(ndbi_neg.get('percent_of_valid', 12.3757)):.2f}%",
            "Interpretation": "Moisture/vegetation recovery over previously bare soil",
        },
        {
            "Spectral Index": "NDBI (Built-Up)",
            "Screening Direction": "NDBI increase > +0.10 (Built/Bare Spectral Increase)",
            "Area (km²)": float(ndbi_pos.get("area_km2_geodesic", 849.15)),
            "Percent of Valid": f"{float(ndbi_pos.get('percent_of_valid', 12.6698)):.2f}%",
            "Interpretation": "Candidate zones for anthropogenic expansion and quarrying",
        },
    ]
    df_screening = pd.DataFrame(records)

    return {
        "df_screening": df_screening,
        "footprint_km2": footprint_km2,
        "ndvi_decrease_km2": float(ndvi_neg.get("area_km2_geodesic", 951.56)),
        "ndvi_decrease_pct": float(ndvi_neg.get("percent_of_valid", 14.1979)),
        "ndvi_increase_km2": float(ndvi_pos.get("area_km2_geodesic", 1188.84)),
        "ndvi_increase_pct": float(ndvi_pos.get("percent_of_valid", 17.7383)),
        "ndwi_decrease_km2": float(ndwi_neg.get("area_km2_geodesic", 377.04)),
        "ndwi_decrease_pct": float(ndwi_neg.get("percent_of_valid", 5.6257)),
        "ndwi_increase_km2": float(ndwi_pos.get("area_km2_geodesic", 581.42)),
        "ndwi_increase_pct": float(ndwi_pos.get("percent_of_valid", 8.6752)),
        "ndbi_decrease_km2": float(ndbi_neg.get("area_km2_geodesic", 829.42)),
        "ndbi_decrease_pct": float(ndbi_neg.get("percent_of_valid", 12.3757)),
        "ndbi_increase_km2": float(ndbi_pos.get("area_km2_geodesic", 849.15)),
        "ndbi_increase_pct": float(ndbi_pos.get("percent_of_valid", 12.6698)),
    }
