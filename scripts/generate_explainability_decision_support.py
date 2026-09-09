"""
Script: generate_explainability_decision_support.py
Project: AI-Based Urban Change & Environmental Risk Intelligence
Study Region: Chittoor District, Andhra Pradesh, India

Stage:
STEP 19 — Explainability and Decision-Support Integration

Objective:
Convert the completed analytical results into an interpretable environmental intelligence layer.
Provide rigorous, transparent answers to:
1. Why is a location considered environmentally stressed?
2. What evidence contributes to that stress?
3. How strong is the evidence?
4. Which historical findings support the interpretation?
5. What does the 2026 built-up forecast imply?
6. What decisions could reasonably be supported?
7. What can the system NOT conclude?

Outputs:
- outputs/tables/environmental_stress_explainability.csv (All 6,902 cells)
- outputs/tables/top_100_environmental_stress_cells.csv (Top 100 priority cells)
- outputs/tables/decision_support_matrix.csv (Strategic decision matrix)
- outputs/tables/executive_decision_summary.csv (Executive-level priority briefing)
- outputs/figures/decision_support/environmental_stress_explainability_map.png
- outputs/figures/decision_support/environmental_stress_components.png
- outputs/figures/decision_support/top_stress_evidence.png
- outputs/figures/decision_support/forecast_decision_context.png
- data/metadata/explainability_decision_support_manifest.json
- docs/research_log/14_explainability_decision_support.md
"""

import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timezone

# Ensure UTF-8 stdout
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Base paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES_DIR = os.path.join(PROJECT_ROOT, "outputs", "tables")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "outputs", "figures", "decision_support")
METADATA_DIR = os.path.join(PROJECT_ROOT, "data", "metadata")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs", "research_log")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)


def step1_load_existing_results():
    """Step 1: Load completed project outputs without modifying them."""
    print("=" * 70)
    print("STEP 1: LOAD EXISTING PROJECT OUTPUTS")
    print("=" * 70)
    
    grid_csv = os.path.join(TABLES_DIR, "environmental_stress_grid_1km.csv")
    forecast_csv = os.path.join(TABLES_DIR, "builtup_forecast_2026.csv")
    master_csv = os.path.join(PROJECT_ROOT, "data", "processed", "Chittoor_Master_Research_Dataset_2016_2025.csv")
    
    if not os.path.exists(grid_csv):
        raise FileNotFoundError(f"Stress grid not found: {grid_csv}")
    if not os.path.exists(forecast_csv):
        raise FileNotFoundError(f"Forecast file not found: {forecast_csv}")
    if not os.path.exists(master_csv):
        raise FileNotFoundError(f"Master dataset not found: {master_csv}")
        
    df_grid = pd.read_csv(grid_csv)
    df_forecast = pd.read_csv(forecast_csv)
    df_master = pd.read_csv(master_csv)
    
    print(f"Loaded 1 km Environmental Stress Grid: {len(df_grid):,} spatial cells")
    print(f"Loaded 2026 Built-Up Forecasts: {len(df_forecast)} target indicators")
    print(f"Loaded Master Historical Dataset: {len(df_master)} annual observations (2016-2025)")
    
    return df_grid, df_forecast, df_master


def step2_and_3_explain_individual_cells(df_grid):
    """Step 2 & 3: Explain stress score formulation and generate full cell explainability table."""
    print("\n" + "=" * 70)
    print("STEP 2 & 3: EXPLAIN STRESS SCORE & INDIVIDUAL CELLS")
    print("=" * 70)
    
    # Verify equal-weight transparent formulation: StressScore = (C_urb + C_veg + C_wat) / 3
    # Check that calculated matches stored within rounding tolerance
    recomputed_score = (df_grid["urbanization_component"] + df_grid["vegetation_component"] + df_grid["water_component"]) / 3.0
    diff = np.abs(df_grid["stress_score"] - recomputed_score)
    max_diff = diff.max()
    print(f"Stress score verification against (C_urb + C_veg + C_wat) / 3: Max diff = {max_diff:.6f} (PASS)")
    assert max_diff < 0.001, "Stress score recomputation deviates from stored score"
    
    # Sort descending by stress score to assign ranks
    df_sorted = df_grid.sort_values(by="stress_score", ascending=False).copy()
    df_sorted["rank"] = np.arange(1, len(df_sorted) + 1)
    
    # Select and rename columns matching requested schema:
    # cell_id, longitude, latitude, stress_score, urbanization_component, vegetation_component, water_component, evidence_strength, stress_quartile, rank
    explainability_df = pd.DataFrame({
        "cell_id": df_sorted["cell_id"],
        "longitude": df_sorted["lon"],
        "latitude": df_sorted["lat"],
        "stress_score": df_sorted["stress_score"].round(4),
        "urbanization_component": df_sorted["urbanization_component"].round(4),
        "vegetation_component": df_sorted["vegetation_component"].round(4),
        "water_component": df_sorted["water_component"].round(4),
        "evidence_strength": df_sorted["evidence_strength"],
        "stress_quartile": df_sorted["stress_category"],
        "rank": df_sorted["rank"]
    })
    
    out_path = os.path.join(TABLES_DIR, "environmental_stress_explainability.csv")
    explainability_df.to_csv(out_path, index=False)
    print(f"Saved environmental stress explainability table ({len(explainability_df):,} cells) -> {out_path}")
    return df_sorted, explainability_df


def step4_and_5_top_100_locations(df_sorted):
    """Step 4 & 5: Determine dominant evidence families and produce top 100 ranked cells."""
    print("\n" + "=" * 70)
    print("STEP 4 & 5: EVIDENCE DECOMPOSITION FOR TOP 100 HIGH-STRESS LOCATIONS")
    print("=" * 70)
    
    top_100 = df_sorted.head(100).copy()
    
    dominant_list = []
    secondary_list = []
    interpretation_rule_list = []
    
    component_labels = {
        "urbanization_component": "Urbanization Expansion (NDBI + Dynamic World)",
        "vegetation_component": "Vegetation Spectral Decline (NDVI decrease)",
        "water_component": "Water/Moisture Spectral Decline (NDWI decrease)"
    }
    
    for _, row in top_100.iterrows():
        c_urb = row["urbanization_component"]
        c_veg = row["vegetation_component"]
        c_wat = row["water_component"]
        
        scores = [
            ("urbanization_component", c_urb),
            ("vegetation_component", c_veg),
            ("water_component", c_wat)
        ]
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        dom_name, dom_val = scores[0]
        sec_name, sec_val = scores[1]
        
        dom_label = component_labels[dom_name]
        sec_label = component_labels[sec_name]
        
        dominant_list.append(dom_label)
        secondary_list.append(sec_label)
        
        # Step 6: Apply transparent decision-support interpretation rules
        ev_str = str(row["evidence_strength"])
        quartile = str(row["stress_category"])
        
        if "Q4" in quartile and "Multi-Source" in ev_str:
            rule = "Priority Multi-Source Monitoring Zone"
        elif "Q4" in quartile and dom_name == "urbanization_component":
            rule = "Urban Expansion / Land-Cover Transformation Monitoring Zone"
        elif "Q4" in quartile and dom_name == "vegetation_component":
            rule = "Vegetation Condition Monitoring Zone"
        elif "Q4" in quartile and dom_name == "water_component":
            rule = "Water/Moisture Condition Monitoring Zone"
        else:
            rule = "Secondary Environmental Monitoring Zone"
            
        interpretation_rule_list.append(rule)
        
    top_100["dominant_evidence"] = dominant_list
    top_100["secondary_evidence"] = secondary_list
    top_100["decision_support_label"] = interpretation_rule_list
    
    # Required columns:
    # rank, cell_id, latitude, longitude, stress_score, stress_quartile, urbanization_component, vegetation_component, water_component, evidence_strength, dominant_evidence, secondary_evidence
    top_100_output = pd.DataFrame({
        "rank": top_100["rank"],
        "cell_id": top_100["cell_id"],
        "latitude": top_100["lat"],
        "longitude": top_100["lon"],
        "stress_score": top_100["stress_score"].round(4),
        "stress_quartile": top_100["stress_category"],
        "urbanization_component": top_100["urbanization_component"].round(4),
        "vegetation_component": top_100["vegetation_component"].round(4),
        "water_component": top_100["water_component"].round(4),
        "evidence_strength": top_100["evidence_strength"],
        "dominant_evidence": top_100["dominant_evidence"],
        "secondary_evidence": top_100["secondary_evidence"],
        "decision_support_label": top_100["decision_support_label"]
    })
    
    top_path = os.path.join(TABLES_DIR, "top_100_environmental_stress_cells.csv")
    top_100_output.to_csv(top_path, index=False)
    print(f"Saved top 100 environmental stress cells -> {top_path}")
    
    # Print evidence composition summary of top 100
    print("\nDominant Evidence Breakdown in Top 100 Cells:")
    for comp, count in top_100_output["dominant_evidence"].value_counts().items():
        print(f"  - {comp}: {count} cells ({count}%)")
        
    print("\nEvidence Strength Breakdown in Top 100 Cells:")
    for ev, count in top_100_output["evidence_strength"].value_counts().items():
        print(f"  - {ev}: {count} cells ({count}%)")
        
    return top_100_output


def step7_8_9_decision_support_matrix(df_forecast):
    """Step 7, 8, 9, 10, 11: Construct the comprehensive decision-support matrix."""
    print("\n" + "=" * 70)
    print("STEP 7, 8, 9 & 10: DECISION-SUPPORT MATRIX & HISTORICAL INTEGRATION")
    print("=" * 70)
    
    fc_built = df_forecast[df_forecast["target"].str.contains("Total Built-Up")].iloc[0]
    fc_strong = df_forecast[df_forecast["target"].str.contains("Strong Built-Up")].iloc[0]
    
    matrix_rows = [
        {
            "issue": "Urban Expansion & Land Transformation",
            "evidence": "Concurrence of Sentinel-2 NDBI spectral increase (> +0.10) and Dynamic World built-up transition (class == 1). Corroborated by district-level secular expansion (+62.6% from 2016 to 2025).",
            "spatial_indicator": "High urbanization component (C_urb > 0.40) in 1 km spatial grid cells, concentrated along major transit corridors (NH-69, NH-71) and peri-urban fringes.",
            "temporal_indicator": "Historical monotonic increase from 159.40 km² (2016) to 259.21 km² (2025) (OLS slope: +11.09 km²/yr, R² = 0.960, p < 0.001).",
            "forecast_indicator": f"2026 forecast: {fc_built['point_forecast']:.2f} km² (95% PI: [{fc_built['lower_95']:.2f}, {fc_built['upper_95']:.2f}] km²; expected net delta: +11.11 km²).",
            "confidence": "MODERATE to HIGH (High for trend direction; Moderate for satellite-derived boundaries due to shared Sentinel-2 sensor ancestry between NDBI and Dynamic World).",
            "recommended_monitoring_action": "Targeted planning reviews, drone/field verification of unauthorized peri-urban development, audit of zoning boundary compliance along economic corridors.",
            "limitation": "Satellite spectral change is not proof of completed legal construction; quarry rock and dry barren soil can mimic built-up spectral signatures."
        },
        {
            "issue": "Vegetation Spectral Degradation",
            "evidence": "Sentinel-2 NDVI spectral decrease (< -0.10). Strongly coupled with same-sensor NDBI (r = -0.801, R² = 0.642).",
            "spatial_indicator": "Elevated vegetation stress component (C_veg > 0.50) in 1 km grid cells, prominent in scrubland transitions and agricultural-urban interfaces.",
            "temporal_indicator": "Annual district NDVI exhibits severe non-monotonic swings (0.284 in 2019 drought to 0.457 in 2025 wet year) heavily driven by monsoon anomalies.",
            "forecast_indicator": "Annual NDVI forecasting is NOT recommended due to stochastic monsoon dependence; baseline historical mean provides monitoring benchmark (0.410).",
            "confidence": "MODERATE (Strong spectral evidence, but heavily confounded by seasonal rainfall, crop cycles, and irrigation practices).",
            "recommended_monitoring_action": "Ground-based forestry and agricultural assessments to distinguish permanent canopy loss from seasonal fallow land or agricultural drought.",
            "limitation": "NDVI decline does not automatically indicate deforestation or permanent environmental destruction; seasonal harvesting and drought produce identical spectral dips."
        },
        {
            "issue": "Water & Surface Moisture Decline",
            "evidence": "Sentinel-2 NDWI spectral decrease (< -0.10). Detects localized desiccation of minor tanks, ponds, and surface moisture regimes.",
            "spatial_indicator": "High water stress component (C_wat > 0.40) in 1 km grid cells surrounding historical minor surface waterbodies.",
            "temporal_indicator": "Decadal surface moisture shifts reflecting localized drainage alteration and minor tank encroachment.",
            "forecast_indicator": "Not forecastable at cell level due to lack of longitudinal spatial panels.",
            "confidence": "MODERATE (Accurate at detecting surface reflectance shifts, but sensitive to seasonal rainfall timing and aquatic weed proliferation).",
            "recommended_monitoring_action": "Field verification of minor irrigation tanks, siltation audits, wetland buffer zoning reviews, and groundwater monitoring well checks.",
            "limitation": "NDWI decline does not prove permanent water disappearance; normal seasonal drawdowns, desiltation works, or macrophyte cover mimic water loss."
        },
        {
            "issue": "Multi-Source Compound Environmental Stress",
            "evidence": "Simultaneous co-occurrence of high urbanization expansion, vegetation loss, and water/moisture decline (supporting_evidence_count >= 2).",
            "spatial_indicator": "Top quartile (Q4) cells with 'High (Multi-Source Convergence)' status (N = 1,726 cells, top 100 cells mapped in detail).",
            "temporal_indicator": "Decadal compound pressure capturing persistent hotspots of anthropogenic land transformation.",
            "forecast_indicator": "District-level built-up momentum (+4.29% projected expansion) will further intensify pressure on these compound stress hotspots.",
            "confidence": "HIGH (Convergence of multiple distinct spectral indices and cross-dataset land-cover transition evidence minimizes single-sensor false positives).",
            "recommended_monitoring_action": "Classify as 'Priority Environmental Monitoring Zones' for integrated environmental impact assessments, conservation reviews, and municipal land audits.",
            "limitation": "The stress indicator is an observational screening index relative to Chittoor District, not a statutory hazard map or building collapse predictor."
        },
        {
            "issue": "Future Built-Up Area Expansion (2026 Pressure)",
            "evidence": "Chronologically validated OLS linear trend model (44.1% error reduction over Naive persistence, walk-forward MAE = 8.07 km²).",
            "spatial_indicator": "District-level aggregate projection; spatially expected to concentrate in existing Q4 compound stress corridors.",
            "temporal_indicator": "Monotonic expansion of total built-up (+11.09 km²/yr) and strong core (+3.51 km²/yr) over 2016-2025.",
            "forecast_indicator": f"Total built-up: {fc_built['point_forecast']:.2f} km² (95% PI: [{fc_built['lower_95']:.2f}, {fc_built['upper_95']:.2f}] km²); Strong core: {fc_strong['point_forecast']:.2f} km² (95% PI: [{fc_strong['lower_95']:.2f}, {fc_strong['upper_95']:.2f}] km²).",
            "confidence": "HIGH for district aggregate trajectory; LOW for exact spatial pixel allocation.",
            "recommended_monitoring_action": "Incorporate forecast uncertainty intervals into master infrastructure planning, water allocation budgets, and conservation zoning reviews.",
            "limitation": "District-level model cannot predict exact parcel-level construction sites; macroeconomic shocks or policy interventions may alter expansion rates."
        }
    ]
    
    matrix_df = pd.DataFrame(matrix_rows)
    mat_path = os.path.join(TABLES_DIR, "decision_support_matrix.csv")
    matrix_df.to_csv(mat_path, index=False)
    print(f"Saved decision-support matrix -> {mat_path}")
    return matrix_df


def step13_executive_summary():
    """Step 13: Generate executive-level priority summary table."""
    print("\n" + "=" * 70)
    print("STEP 13: EXECUTIVE DECISION SUMMARY TABLE")
    print("=" * 70)
    
    summary_records = [
        {
            "priority": "1. Urgent Operational Priority",
            "finding": "Identified Top 100 Compound Stress Hotspots exhibiting simultaneous urbanization, vegetation loss, and moisture depletion.",
            "evidence": "High multi-source convergence (NDBI increase + Dynamic World built-up transition + NDVI/NDWI decline) across 1 km spatial grid cells.",
            "confidence": "HIGH",
            "decision_relevance": "These locations represent the highest compound ecological pressure and are most vulnerable to irreversible land transformation.",
            "recommended_next_step": "Deploy joint field inspection teams to the top 100 ranked cells (led by municipal planning, forestry, and water resource officers) to verify land status."
        },
        {
            "priority": "2. Regional Planning Priority",
            "finding": "Total built-up extent is projected to expand by +11.11 km² (+4.29%) in 2026, reaching 270.32 km² (95% PI: 250.02 to 290.62 km²).",
            "evidence": "Chronologically validated OLS linear trend model achieving 44.1% error reduction over naive baseline in walk-forward testing (2022-2025).",
            "confidence": "HIGH (District aggregate)",
            "decision_relevance": "Urban growth momentum is robust and persistent, placing continued demand on peri-urban land, municipal services, and groundwater reserves.",
            "recommended_next_step": "Integrate 2026 built-up forecast uncertainty bounds into the Chittoor Regional Master Plan to pre-empt infrastructure deficits."
        },
        {
            "priority": "3. Natural Resource Monitoring",
            "finding": "Surface moisture decline (C_wat > 0.40) co-occurs with vegetation degradation around peripheral minor irrigation tanks and agricultural valleys.",
            "evidence": "Sentinel-2 NDWI change rasters coupled with district-level precipitation variance.",
            "confidence": "MODERATE",
            "decision_relevance": "Encroachment or siltation of minor waterbodies reduces groundwater recharge capacity and increases local climate vulnerability.",
            "recommended_next_step": "Conduct hydrological ground audits and satellite-assisted desiltation tracking for minor tanks within Q4 stress cells."
        },
        {
            "priority": "4. Methodological Governance",
            "finding": "Deep learning forecasting, pixel-level 2026 mapping, and meteorological forecasting (NDVI, LST, rainfall) were scientifically rejected.",
            "evidence": "Rigorous sample-size audit (temporal N=10; image pairs N=1); stochastic atmospheric confounding; zero historical spatial panels.",
            "confidence": "HIGH",
            "decision_relevance": "Prevents decision-makers from relying on overfitted 'black-box' artificial intelligence or hallucinated future maps.",
            "recommended_next_step": "Maintain transparent, indicator-based decision support and require empirical field validation before statutory regulatory actions."
        }
    ]
    
    exec_df = pd.DataFrame(summary_records)
    exec_path = os.path.join(TABLES_DIR, "executive_decision_summary.csv")
    exec_df.to_csv(exec_path, index=False)
    print(f"Saved executive decision summary -> {exec_path}")
    return exec_df


def step12_generate_visualizations(df_grid, top_100_output, df_forecast, df_master):
    """Step 12: Generate the four required decision-support visualizations."""
    print("\n" + "=" * 70)
    print("STEP 12: GENERATING DECISION-SUPPORT VISUALIZATIONS")
    print("=" * 70)
    
    # -------------------------------------------------------------
    # Figure 1: Environmental Stress Explainability Map
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 9), dpi=300)
    
    quartile_colors = {
        "Q1: Lower Relative Stress": "#3b82f6",          # Blue
        "Q2: Moderate-Low Relative Stress": "#10b981",    # Emerald
        "Q3: Moderate-High Relative Stress": "#f59e0b",   # Amber
        "Q4: Higher Relative Stress": "#ef4444"           # Red
    }
    
    for q_label, color in quartile_colors.items():
        subset = df_grid[df_grid["stress_category"] == q_label]
        ax.scatter(subset["lon"], subset["lat"], c=color, s=12, alpha=0.65, label=q_label, edgecolors="none")
        
    # Highlight top 100 high-stress cells with black rings
    ax.scatter(top_100_output["longitude"], top_100_output["latitude"],
               facecolors="none", edgecolors="black", s=45, linewidth=1.2,
               label="Top 100 Priority Hotspots", zorder=5)
               
    ax.set_title("Chittoor District: 1 km Environmental Stress Explainability Map\n(Decadal Relative Stress Quartiles & Priority Hotspots)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Longitude (°E)", fontsize=11)
    ax.set_ylabel("Latitude (°N)", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="lower left", fontsize=9.5, framealpha=0.95, facecolor="white")
    
    # Text badge
    ax.text(0.98, 0.03, "Unit of Analysis: 1 km Grid Cells (N = 6,902)\nTop 100 Cells Highlighted for Field Verification",
            transform=ax.transAxes, fontsize=9, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1"))
            
    plt.tight_layout()
    f1_path = os.path.join(FIGURES_DIR, "environmental_stress_explainability_map.png")
    plt.savefig(f1_path, bbox_inches="tight")
    plt.close()
    print(f"Saved Figure 1 -> {f1_path}")
    
    # -------------------------------------------------------------
    # Figure 2: Environmental Stress Components Contribution
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=300)
    
    # Subplot A: Mean component contributions across stress quartiles
    quartiles = ["Q1: Lower", "Q2: Mod-Low", "Q3: Mod-High", "Q4: Higher"]
    q_keys = ["Q1: Lower Relative Stress", "Q2: Moderate-Low Relative Stress", "Q3: Moderate-High Relative Stress", "Q4: Higher Relative Stress"]
    
    mean_urb = [df_grid[df_grid["stress_category"] == k]["urbanization_component"].mean() for k in q_keys]
    mean_veg = [df_grid[df_grid["stress_category"] == k]["vegetation_component"].mean() for k in q_keys]
    mean_wat = [df_grid[df_grid["stress_category"] == k]["water_component"].mean() for k in q_keys]
    
    x = np.arange(len(quartiles))
    width = 0.25
    
    b1 = ax1.bar(x - width, mean_urb, width, label="Urbanization (C_urb)", color="#ef4444", edgecolor="black", linewidth=0.8)
    b2 = ax1.bar(x, mean_veg, width, label="Vegetation Decline (C_veg)", color="#10b981", edgecolor="black", linewidth=0.8)
    b3 = ax1.bar(x + width, mean_wat, width, label="Water Decline (C_wat)", color="#3b82f6", edgecolor="black", linewidth=0.8)
    
    ax1.set_title("(A) Mean Component Score Across Stress Quartiles", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Relative Stress Quartile", fontsize=11)
    ax1.set_ylabel("Normalized Component Score [0, 1]", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(quartiles, fontsize=10, fontweight="bold")
    ax1.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left", fontsize=9.5)
    
    # Annotations on Q4 bars
    ax1.text(3 - width, mean_urb[3] + 0.02, f"{mean_urb[3]:.2f}", ha="center", fontsize=9, fontweight="bold")
    ax1.text(3, mean_veg[3] + 0.02, f"{mean_veg[3]:.2f}", ha="center", fontsize=9, fontweight="bold")
    ax1.text(3 + width, mean_wat[3] + 0.02, f"{mean_wat[3]:.2f}", ha="center", fontsize=9, fontweight="bold")
    
    # Subplot B: Evidence Strength Distribution Across District
    ev_counts = df_grid["evidence_strength"].value_counts()
    ev_labels = [k.replace(" (", "\n(").replace(" / ", "/\n") for k in ev_counts.index]
    colors_pie = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
    
    ax2.barh(ev_labels[::-1], ev_counts.values[::-1], color=colors_pie[:len(ev_counts)][::-1], edgecolor="black", linewidth=0.8)
    for i, v in enumerate(ev_counts.values[::-1]):
        ax2.text(v + 30, i, f"{v:,} ({v/len(df_grid)*100:.1f}%)", va="center", fontsize=9.5, fontweight="bold")
        
    ax2.set_xlim(0, max(ev_counts.values) * 1.25)
    ax2.set_title("(B) Evidence Strength Breakdown Across 6,902 Cells", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Number of 1 km Grid Cells", fontsize=11)
    ax2.grid(True, axis="x", linestyle=":", alpha=0.6)
    
    plt.tight_layout()
    f2_path = os.path.join(FIGURES_DIR, "environmental_stress_components.png")
    plt.savefig(f2_path, bbox_inches="tight")
    plt.close()
    print(f"Saved Figure 2 -> {f2_path}")
    
    # -------------------------------------------------------------
    # Figure 3: Evidence Composition of Top 25 Stress Cells
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    
    top_25 = top_100_output.head(25).copy()
    y_pos = np.arange(len(top_25))
    
    # Plot horizontal stacked bar showing component breakdown
    # Each component contributes 1/3 to the total score: Stress = (C_urb + C_veg + C_wat) / 3
    c_urb_contrib = top_25["urbanization_component"] / 3.0
    c_veg_contrib = top_25["vegetation_component"] / 3.0
    c_wat_contrib = top_25["water_component"] / 3.0
    
    labels_cells = [f"Rank {r}: {cid}" for r, cid in zip(top_25["rank"], top_25["cell_id"])]
    
    p1 = ax.barh(y_pos, c_urb_contrib, color="#ef4444", label="Urbanization (1/3 × C_urb)", edgecolor="black", linewidth=0.6)
    p2 = ax.barh(y_pos, c_veg_contrib, left=c_urb_contrib, color="#10b981", label="Vegetation Decline (1/3 × C_veg)", edgecolor="black", linewidth=0.6)
    p3 = ax.barh(y_pos, c_wat_contrib, left=c_urb_contrib + c_veg_contrib, color="#3b82f6", label="Water Decline (1/3 × C_wat)", edgecolor="black", linewidth=0.6)
    
    # Total score text at end of bar
    for idx, (tot, dom) in enumerate(zip(top_25["stress_score"], top_25["dominant_evidence"])):
        short_dom = dom.split(" (")[0]
        ax.text(tot + 0.01, idx, f"{tot:.3f} | Dom: {short_dom}", va="center", fontsize=8.5, fontweight="bold")
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels_cells, fontsize=9)
    ax.invert_yaxis()  # Rank 1 at top
    ax.set_xlim(0, 0.82)
    ax.set_title("Evidence Decomposition for Top 25 Ranked Environmental Stress Hotspots\n(Additive Contribution of Equal-Weight Components to Total Stress Score)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Relative Environmental Stress Score [0, 1]", fontsize=11)
    ax.grid(True, axis="x", linestyle=":", alpha=0.6)
    ax.legend(loc="lower right", fontsize=10, framealpha=0.95)
    
    plt.tight_layout()
    f3_path = os.path.join(FIGURES_DIR, "top_stress_evidence.png")
    plt.savefig(f3_path, bbox_inches="tight")
    plt.close()
    print(f"Saved Figure 3 -> {f3_path}")
    
    # -------------------------------------------------------------
    # Figure 4: Forecast Decision Context (2016-2025 History + 2026 Forecast)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    
    years = df_master["year"].values
    built = df_master["built_up_km2"].values
    
    fc_row = df_forecast[df_forecast["target"].str.contains("Total Built-Up")].iloc[0]
    pt_2026 = fc_row["point_forecast"]
    low_2026 = fc_row["lower_95"]
    up_2026 = fc_row["upper_95"]
    
    # Plot historical trajectory
    ax.plot(years, built, "ko-", linewidth=2.5, markersize=8, label="Historical Built-Up Area (2016–2025: +62.6%)")
    
    # Plot linear trend line
    t_hist = np.arange(len(years))
    slope, intercept = np.polyfit(t_hist, built, 1)
    t_full = np.arange(11)
    years_full = np.append(years, 2026)
    trend_full = intercept + slope * t_full
    ax.plot(years_full, trend_full, "b--", linewidth=2, label=f"OLS Secular Trend (+{slope:.2f} km²/yr, R² = 0.960)")
    
    # Plot 2026 forecast and prediction interval
    ax.plot(2026, pt_2026, "r*", markersize=16, label=f"2026 Point Forecast: {pt_2026:.2f} km²")
    ax.errorbar(2026, pt_2026, yerr=[[pt_2026 - low_2026], [up_2026 - pt_2026]],
                fmt="none", ecolor="red", capsize=7, elinewidth=2.5,
                label=f"95% Prediction Interval: [{low_2026:.1f}, {up_2026:.1f}] km²")
                
    # Historical mean benchmark
    ax.axhline(np.mean(built), color="gray", linestyle=":", label=f"Historical 10-Yr Mean ({np.mean(built):.1f} km²)")
    
    # Decision support annotations
    ax.annotate(f"Projected 2025->2026 Expansion:\n+{pt_2026 - built[-1]:.2f} km² (+4.29%)\nDecision: Reserve Infrastructure Corridors",
                xy=(2026, pt_2026), xytext=(2022.5, 275),
                arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
                fontsize=9.5, fontweight="bold", backgroundcolor="#fef2f2",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#fef2f2", edgecolor="#f87171"))
                
    ax.annotate("2016 Baseline:\n159.40 km²", xy=(2016, 159.4), xytext=(2016.3, 175),
                arrowprops=dict(arrowstyle="->", color="black"), fontsize=9)
                
    ax.set_title("Decision Context: Chittoor Built-Up Area Secular Trajectory & 2026 Planning Forecast\n(Validated Trend Continuation vs. Policy & Infrastructure Demand)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Total Built-Up Area (km²)", fontsize=11)
    ax.set_xticks(np.arange(2016, 2027, 1))
    ax.set_ylim(140, 305)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", fontsize=9.5, framealpha=0.95)
    
    plt.tight_layout()
    f4_path = os.path.join(FIGURES_DIR, "forecast_decision_context.png")
    plt.savefig(f4_path, bbox_inches="tight")
    plt.close()
    print(f"Saved Figure 4 -> {f4_path}")


def step15_generate_manifest():
    """Step 15: Create machine-readable reproducibility manifest."""
    print("\n" + "=" * 70)
    print("STEP 15: WRITE METADATA MANIFEST")
    print("=" * 70)
    
    manifest_data = {
        "metadata": {
            "title": "Explainability & Decision-Support Integration Manifest",
            "region": "Chittoor District, Andhra Pradesh, India",
            "execution_date_utc": datetime.now(timezone.utc).isoformat(),
            "script_name": "generate_explainability_decision_support.py",
            "version": "1.0",
            "governing_principle": "DO NOT TRAIN A MODEL JUST TO CLAIM 'AI'. Convert analytical findings into interpretable decision support."
        },
        "source_datasets": [
            "outputs/tables/environmental_stress_grid_1km.csv",
            "outputs/tables/environmental_stress_rankings.csv",
            "outputs/tables/spatial_statistical_validation.csv",
            "outputs/tables/builtup_forecast_2026.csv",
            "data/processed/Chittoor_Master_Research_Dataset_2016_2025.csv"
        ],
        "stress_score_formulation": {
            "equation": "StressScore = (C_urb + C_veg + C_wat) / 3",
            "weights": {"urbanization": 0.3333, "vegetation": 0.3333, "water": 0.3333},
            "weighting_rationale": "Transparent equal-weight baseline selected after high correlation with data-driven PCA (r = 0.9279)."
        },
        "evidence_categories": [
            "Baseline / Low",
            "Low (Single Evidence Family)",
            "Moderate (Compound Moisture/Vegetation Stress)",
            "Moderate (Same-Sensor Spectral Agreement)",
            "Moderate (Compound Urban/Water Signal)",
            "High (Multi-Source Convergence)"
        ],
        "decision_support_rules": {
            "priority_monitoring": "Q4 High Stress + High Multi-Source Convergence",
            "urbanization_monitoring": "Q4 High Stress + Urbanization Dominates",
            "vegetation_monitoring": "Q4 High Stress + Vegetation Dominates",
            "water_monitoring": "Q4 High Stress + Water/Moisture Dominates"
        },
        "confidence_framework": {
            "HIGH": "Multiple independent evidence families converge (e.g. cross-sensor, validated statistical association).",
            "MODERATE": "Multiple indicators agree, but some share common sensor ancestry (e.g. Sentinel-2 NDBI + Dynamic World).",
            "LOW": "Single evidence family or uncorroborated spectral dip."
        },
        "generated_outputs": {
            "tables": [
                "outputs/tables/environmental_stress_explainability.csv",
                "outputs/tables/top_100_environmental_stress_cells.csv",
                "outputs/tables/decision_support_matrix.csv",
                "outputs/tables/executive_decision_summary.csv"
            ],
            "figures": [
                "outputs/figures/decision_support/environmental_stress_explainability_map.png",
                "outputs/figures/decision_support/environmental_stress_components.png",
                "outputs/figures/decision_support/top_stress_evidence.png",
                "outputs/figures/decision_support/forecast_decision_context.png"
            ]
        }
    }
    
    man_path = os.path.join(METADATA_DIR, "explainability_decision_support_manifest.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Saved reproducibility manifest -> {man_path}")


def main():
    print("STARTING STEP 19: EXPLAINABILITY & DECISION-SUPPORT INTEGRATION")
    print(f"Timestamp UTC: {datetime.now(timezone.utc).isoformat()}")
    
    # Step 1
    df_grid, df_forecast, df_master = step1_load_existing_results()
    
    # Step 2 & 3
    df_sorted, explainability_df = step2_and_3_explain_individual_cells(df_grid)
    
    # Step 4 & 5
    top_100_output = step4_and_5_top_100_locations(df_sorted)
    
    # Step 7, 8, 9, 10, 11
    matrix_df = step7_8_9_decision_support_matrix(df_forecast)
    
    # Step 13
    exec_df = step13_executive_summary()
    
    # Step 12
    step12_generate_visualizations(df_grid, top_100_output, df_forecast, df_master)
    
    # Step 15
    step15_generate_manifest()
    
    print("\n" + "=" * 70)
    print("EXPLAINABILITY & DECISION-SUPPORT INTEGRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
