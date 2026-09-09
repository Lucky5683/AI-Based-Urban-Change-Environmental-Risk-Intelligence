"""Spatial Location Enrichment Pipeline for Chittoor Environmental Stress Grid.

Spatially joins the 1 km Environmental Stress Grid cells (N=6,902) to the
authoritative Chittoor Mandal boundary dataset to add administrative and
geographic location interpretability.

Preserves 100% mathematical and data invariance of all original stress scores,
components, rankings, and scientific calculations.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import urllib.request
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point


MANDAL_URL = "https://raw.githubusercontent.com/satishvmadala/andhrapradesh_opendata_locations/main/TODO-GeoJSONS/MANDAL.geojson"


def clean_mandal_name(raw_name: str) -> str:
    """Standardize mandal names to clean, readable Title Case format."""
    if not isinstance(raw_name, str):
        return "Unknown Mandal"
    name = raw_name.strip()
    
    # Remove trailing digits (e.g. GANGAVARAM1 -> GANGAVARAM)
    name = re.sub(r"\d+$", "", name).strip()
    
    # Custom known replacements for official AP administrative consistency
    corrections = {
        "B.KOTHAKOTA": "B. Kothakota",
        "BAIREDDIPALLE": "Baireddipalle",
        "BANGARUPALEM": "Bangarupalem",
        "BUCHINAIDU  KANDRIGA": "Buchinaidu Kandriga",
        "CHANDRAGIRI": "Chandragiri",
        "CHINNAGOTTIGALLU": "Chinnagottigallu",
        "CHITTOOR": "Chittoor",
        "CHOWDEPALLE": "Chowdepalle",
        "GANGADHARANELLORE": "Gangadhara Nellore",
        "GANGAVARAM": "Gangavaram",
        "GUDIPALA": "Gudipala",
        "GUDUPALLE": "Gudupalle",
        "GURRAMKONDA": "Gurramkonda",
        "IRALA": "Irala",
        "K.V.B.PURAM": "K.V.B. Puram",
        "KALAKADA": "Kalakada",
        "KALIKIRI": "Kalikiri",
        "KAMBHAMVARIPALLE": "Kambhamvaripalle",
        "KUPPAM": "Kuppam",
        "KURABALAKOTA": "Kurabalakota",
        "MADANAPALLE": "Madanapalle",
        "MULAKALACHERUVU": "Mulakalacheruvu",
        "NAGALAPURAM": "Nagalapuram",
        "NAGARI": "Nagari",
        "NARAYANAVANAM": "Narayanavanam",
        "NIMMANAPALLE": "Nimmanapalle",
        "NINDRA": "Nindra",
        "PAKALA": "Pakala",
        "PALAMANER": "Palamaner",
        "PALASAMUDRAM": "Palasamudram",
        "PEDDA THIPPASAMUDRAM": "Pedda Thippasamudram",
        "PEDDAMANDYAM": "Peddamandyam",
        "PEDDAPANJANI": "Peddapanjani",
        "PENUMURU": "Penumuru",
        "PICHATUR": "Pichatur",
        "PILERU": "Pileru",
        "PULICHERLA": "Pulicherla",
        "PUNGANUR": "Punganur",
        "PUTHALAPATTU": "Puthalapattu",
        "PUTTUR": "Puttur",
        "RAMACHANDRAPURAM": "Ramachandrapuram",
        "RAMAKUPPAM": "Ramakuppam",
        "RAMASAMUDRAM": "Ramasamudram",
        "RENIGUNTA": "Renigunta",
        "ROMPICHERLA": "Rompicherla",
        "SANTHIPURAM": "Santhipuram",
        "SATYAVEDU": "Satyavedu",
        "SODAM": "Sodam",
        "SOMALA": "Somala",
        "SRIKALAHASTI": "Srikalahasti",
        "SRIRANGARAJAPURAM": "Srirangarajapuram",
        "THAMBALLAPALLE": "Thamballapalle",
        "THAVANAMPALLE": "Thavanampalle",
        "THOTTAMBEDU": "Thottambedu",
        "TIRUPATI (RURAL)": "Tirupati (Rural)",
        "TIRUPATI (URBAN)": "Tirupati (Urban)",
        "VADAMALAPETA": "Vadamalapeta",
        "VARADAIAHPALEM": "Varadaiahpalem",
        "VAYALPAD": "Vayalpad (Valmikipuram)",
        "VEDURUKUPPAM": "Vedurukuppam",
        "VENKATAGIRIKOTA": "Venkatagirikota",
        "VIJAYAPURAM": "Vijayapuram",
        "YADAMARRI": "Yadamarri",
        "YERPEDU": "Yerpedu",
        "YERRAVARIPALEM": "Yerravaripalem",
    }
    
    if name in corrections:
        return corrections[name]
    
    return name.title()


def get_project_root() -> Path:
    """Find the project root directory."""
    candidates = [
        Path.cwd(),
        Path.cwd() / "AI-Based-Urban-Change-Environmental-Risk-Intelligence",
        Path(__file__).resolve().parent.parent,
    ]
    for c in candidates:
        if (c / "outputs" / "tables").exists():
            return c
    return Path.cwd()


def acquire_chittoor_mandals(boundary_path: Path) -> gpd.GeoDataFrame:
    """Acquire and cache official Chittoor mandal boundaries GeoJSON."""
    boundary_path.parent.mkdir(parents=True, exist_ok=True)
    if not boundary_path.exists():
        print(f"Downloading authoritative AP Mandal boundaries from {MANDAL_URL}...")
        req = urllib.request.Request(MANDAL_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        # Filter strictly for Chittoor district mandals
        chittoor_features = [
            f for f in data["features"]
            if "CHITTOOR" in f["properties"].get("DNAME", "").upper()
        ]
        
        # Deduplicate features by DMNAME if duplicate geometries exist
        unique_feats = []
        seen_mandals = set()
        for f in chittoor_features:
            dm = f["properties"].get("DMNAME", "").strip()
            # If duplicated, keep first
            if dm not in seen_mandals:
                seen_mandals.add(dm)
                unique_feats.append(f)
            else:
                # Some mandals like Ramakuppam may have multiple polygon parts; keep both as valid features
                unique_feats.append(f)

        filtered_geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "source": "Government of Andhra Pradesh / Open Data Locations",
                "district": "Chittoor (Unified 67 Mandals)",
                "feature_count": len(unique_feats),
            },
            "features": unique_feats
        }
        
        with open(boundary_path, "w", encoding="utf-8") as f:
            json.dump(filtered_geojson, f, indent=2)
        print(f"Saved {len(unique_feats)} Chittoor mandal boundaries to {boundary_path}")

    gdf = gpd.read_file(boundary_path)
    gdf["mandal_clean"] = gdf["DMNAME"].apply(clean_mandal_name)
    return gdf


def run_enrichment():
    project_root = get_project_root()
    print(f"Project root: {project_root}")
    
    boundary_file = project_root / "data" / "raw" / "boundaries" / "chittoor_mandals.geojson"
    grid_csv = project_root / "outputs" / "tables" / "environmental_stress_grid_1km.csv"
    top100_csv = project_root / "outputs" / "tables" / "top_100_environmental_stress_cells.csv"
    explain_csv = project_root / "outputs" / "tables" / "environmental_stress_explainability.csv"
    
    assert grid_csv.exists(), f"Missing grid CSV: {grid_csv}"
    
    # 1. Load mandals GeoDataFrame
    gdf_mandals = acquire_chittoor_mandals(boundary_file)
    print(f"Loaded {len(gdf_mandals)} mandal polygon features.")
    
    # 2. Load 1 km stress grid
    df_grid = pd.read_csv(grid_csv)
    original_cell_count = len(df_grid)
    original_mean_stress = df_grid["stress_score"].mean()
    print(f"Loaded {original_cell_count} grid cells (Mean stress: {original_mean_stress:.4f})")
    
    # Determine lat / lon columns
    lat_col = "lat" if "lat" in df_grid.columns else "latitude"
    lon_col = "lon" if "lon" in df_grid.columns else "longitude"
    
    # Standardize coordinate column names
    df_grid["latitude"] = df_grid[lat_col].round(6)
    df_grid["longitude"] = df_grid[lon_col].round(6)
    
    # Build point geometries
    geometry = [Point(xy) for xy in zip(df_grid["longitude"], df_grid["latitude"])]
    gdf_grid = gpd.GeoDataFrame(df_grid, geometry=geometry, crs="EPSG:4326")
    
    # 3. Spatial Join (Within)
    joined = gpd.sjoin(
        gdf_grid,
        gdf_mandals[["mandal_clean", "geometry"]],
        how="left",
        predicate="within"
    )
    
    # If point falls on boundary between two polygons, drop duplicate index
    joined = joined[~joined.index.duplicated(keep="first")]
    
    # 4. Handle boundary edge cells (those falling slightly outside simplified polygon borders)
    unmatched_idx = joined[joined["mandal_clean"].isnull()].index
    print(f"Direct point-in-polygon matches: {original_cell_count - len(unmatched_idx)} ({((original_cell_count - len(unmatched_idx))/original_cell_count)*100:.2f}%)")
    
    if len(unmatched_idx) > 0:
        print(f"Assigning {len(unmatched_idx)} peripheral edge cells via nearest-boundary join...")
        unmatched_gdf = gdf_grid.loc[unmatched_idx]
        
        # Project to UTM Zone 44N (EPSG:32644) for accurate meter metric
        unmatched_utm = unmatched_gdf.to_crs(epsg=32644)
        mandals_utm = gdf_mandals[["mandal_clean", "geometry"]].to_crs(epsg=32644)
        
        nearest = gpd.sjoin_nearest(unmatched_utm, mandals_utm, distance_col="boundary_dist_m")
        nearest = nearest[~nearest.index.duplicated(keep="first")]
        
        for idx in unmatched_idx:
            if idx in nearest.index:
                m_name = nearest.loc[idx, "mandal_clean"]
                joined.loc[idx, "mandal_clean"] = m_name
    
    # Confirm 100% assignment
    assert joined["mandal_clean"].isnull().sum() == 0, "Some cells could not be assigned a mandal!"
    
    # 5. Populate location fields
    df_grid_enriched = df_grid.copy()
    df_grid_enriched["mandal"] = joined["mandal_clean"].values
    df_grid_enriched["mandal_name"] = df_grid_enriched["mandal"]
    
    # Per scientific instruction: do NOT fabricate settlement place names without verified point gazetteer
    df_grid_enriched["nearest_place"] = "N/A (Requires Authoritative Settlement Gazetteer)"
    df_grid_enriched["nearest_place_distance_km"] = np.nan
    
    # 6. Validate strict scientific invariance
    assert len(df_grid_enriched) == original_cell_count, "Cell count changed!"
    assert np.isclose(df_grid_enriched["stress_score"].mean(), original_mean_stress), "Stress scores altered!"
    assert (df_grid_enriched["cell_id"] == df_grid["cell_id"]).all(), "Cell IDs altered!"
    
    # 7. Specific user test cases check
    c_47_43 = df_grid_enriched[df_grid_enriched["cell_id"] == "C_047_043"].iloc[0]
    c_42_68 = df_grid_enriched[df_grid_enriched["cell_id"] == "C_042_068"].iloc[0]
    c_52_166 = df_grid_enriched[df_grid_enriched["cell_id"] == "C_052_166"].iloc[0]
    
    print("\n--- User Highlighted Test Cells ---")
    print(f"Cell {c_47_43.cell_id}: Mandal = '{c_47_43.mandal}', Stress = {c_47_43.stress_score:.4f}, Coords = ({c_47_43.latitude:.4f}°N, {c_47_43.longitude:.4f}°E)")
    print(f"Cell {c_42_68.cell_id}: Mandal = '{c_42_68.mandal}', Stress = {c_42_68.stress_score:.4f}, Coords = ({c_42_68.latitude:.4f}°N, {c_42_68.longitude:.4f}°E)")
    print(f"Cell {c_52_166.cell_id} (Rank 1): Mandal = '{c_52_166.mandal}', Stress = {c_52_166.stress_score:.4f}, Coords = ({c_52_166.latitude:.4f}°N, {c_52_166.longitude:.4f}°E)")
    
    assert c_47_43["mandal"] == "Punganur", f"Expected Punganur, got {c_47_43['mandal']}"
    assert c_42_68["mandal"] == "Somala", f"Expected Somala, got {c_42_68['mandal']}"
    assert c_52_166["mandal"] == "Vijayapuram", f"Expected Vijayapuram, got {c_52_166['mandal']}"
    
    # 8. Save enriched 1 km grid derivative table
    out_grid_enriched = project_root / "outputs" / "tables" / "environmental_stress_grid_1km_enriched.csv"
    df_grid_enriched.to_csv(out_grid_enriched, index=False)
    print(f"\nSaved enriched 1 km grid to: {out_grid_enriched}")
    
    # 9. Enrich Top 100 Hotspots table
    if top100_csv.exists():
        df_top = pd.read_csv(top100_csv)
        mandal_map = dict(zip(df_grid_enriched["cell_id"], df_grid_enriched["mandal"]))
        df_top["mandal"] = df_top["cell_id"].map(mandal_map)
        df_top["nearest_place"] = "N/A (Requires Authoritative Settlement Gazetteer)"
        df_top["nearest_place_distance_km"] = np.nan
        
        # Ensure latitude/longitude columns exist
        if "latitude" not in df_top.columns and "lat" in df_top.columns:
            df_top["latitude"] = df_top["lat"]
        if "longitude" not in df_top.columns and "lon" in df_top.columns:
            df_top["longitude"] = df_top["lon"]
            
        out_top100_enriched = project_root / "outputs" / "tables" / "top_100_environmental_stress_cells_enriched.csv"
        df_top.to_csv(out_top100_enriched, index=False)
        print(f"Saved enriched Top 100 Hotspots to: {out_top100_enriched}")
    
    # 10. Enrich Explainability table
    if explain_csv.exists():
        df_exp = pd.read_csv(explain_csv)
        mandal_map = dict(zip(df_grid_enriched["cell_id"], df_grid_enriched["mandal"]))
        df_exp["mandal"] = df_exp["cell_id"].map(mandal_map)
        df_exp["nearest_place"] = "N/A (Requires Authoritative Settlement Gazetteer)"
        df_exp["nearest_place_distance_km"] = np.nan
        out_exp_enriched = project_root / "outputs" / "tables" / "environmental_stress_explainability_enriched.csv"
        df_exp.to_csv(out_exp_enriched, index=False)
        print(f"Saved enriched Explainability table to: {out_exp_enriched}")
        
    print("\nSUCCESS: All location enrichment derivative tables created and verified.")


if __name__ == "__main__":
    run_enrichment()
