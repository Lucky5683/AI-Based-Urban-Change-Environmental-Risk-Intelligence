"""Chittoor Environmental Intelligence Dashboard.

AI-Based Urban Change & Environmental Risk Intelligence for Chittoor District, AP.
Interactive presentation and decision-support layer consuming validated project outputs.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.utils.data_loader import (
    get_headline_metrics,
    load_data_contract,
    load_decision_matrix,
    load_executive_summary,
    load_feasibility_matrix,
    load_forecast_2026,
    load_forecast_validation,
    load_headline_audit,
    load_master_timeseries,
    load_model_comparison,
    load_spatial_validation,
    load_spectral_screening_summary,
    load_stress_explainability,
    load_stress_grid,
    load_stress_sensitivity,
    load_top_100_hotspots,
    load_units_dictionary,
    PROJECT_ROOT,
)
from dashboard.utils.raster_helpers import (
    get_figure_path,
    PRESET_ROIS,
    read_feature_window,
    read_raster_window_rgb,
)
from dashboard.components.kpi_cards import (
    render_forecast_kpi_banner,
    render_overview_kpis,
)
from dashboard.components.charts import (
    INDICATOR_META,
    render_anomalies_chart,
    render_backtesting_chart,
    render_distribution_chart,
    render_forecast_chart,
    render_historical_trend_chart,
    render_model_comparison_bar,
    render_statistical_association_chart,
    render_urban_acceleration_chart,
)
from dashboard.components.maps import (
    render_cell_inspector,
    render_stress_grid_map,
)
from dashboard.components.tables_view import (
    render_decision_support_accordions,
    render_top_100_table,
    render_traceability_table,
)


# Set page layout and metadata
st.set_page_config(
    page_title="Chittoor Environmental Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.is_file():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Global Research Disclaimer
DISCLAIMER_TEXT = (
    "This dashboard presents research-oriented environmental screening indicators and model-based estimates. "
    "Spectral change is not automatically confirmed land-use conversion. Relative stress scores are screening indicators, "
    "not regulatory risk classifications. Forecasts represent uncertain estimates and do not predict exact future construction "
    "locations or structural disasters."
)


def render_sidebar():
    """Render sidebar navigation and project metadata."""
    st.sidebar.markdown(
        """
        <div style="padding:0.5rem 0; border-bottom:1px solid #e2e8f0; margin-bottom:1rem;">
            <h2 style="font-size:1.25rem; font-weight:700; color:#0f172a; margin:0;">Chittoor Environmental Intelligence</h2>
            <p style="font-size:0.8rem; color:#64748b; margin:0.25rem 0 0 0;">AI-Based Urban Change & Environmental Risk Intelligence</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "Navigation",
        options=[
            "1. Executive Overview",
            "2. Data Explorer",
            "3. Urban Change Analytics",
            "4. Environmental Analytics",
            "5. Spatial Stress & Hotspots",
            "6. Forecasting & Model Performance",
            "7. Decision Support",
            "8. Methodology & Data Quality",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Study Scope")
    st.sidebar.markdown(
        """
- **Region:** Chittoor District, Andhra Pradesh
- **Valid Footprint:** 6,702.08 km² (Common Clear-Sky)
- **1 km Grid:** 6,902 cells
- **Observation Period:** 2016–2025 (10 Years)
- **Forecast Horizon:** 2026 Built-Up Extent
        """
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size:0.75rem; color:#64748b; line-height:1.4;">
            <b>Scientific Governance:</b><br>
            Strictly enforces <code>outputs/tables/dashboard_data_contract.csv</code>. Non-causal observational wording preserved.
        </div>
        """,
        unsafe_allow_html=True,
    )

    return page


def render_header(title: str, subtitle: str):
    """Render standardized page header banner."""
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div class="badges">
                <span class="badge-pill">Region: Chittoor District, AP</span>
                <span class="badge-pill">Observation Window: 2016–2025</span>
                <span class="badge-pill">Forecast Target: 2026 Built-Up</span>
                <span class="badge-pill">Resolution: 10 m (S2) / 1 km (Grid)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------------------------------------------
def page_overview(metrics: dict, df_master: pd.DataFrame):
    render_header(
        "Chittoor Environmental Intelligence",
        "AI-Based Urban Change & Environmental Risk Intelligence — Executive Overview"
    )

    st.markdown("### 📊 Validated Headline Indicators")
    render_overview_kpis(metrics)
    render_forecast_kpi_banner(metrics)

    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 📈 Historical Multi-Decadal Trajectory")
        indicator_options = {
            "built_up_km2": "Total Built-Up Area (km²)",
            "strong_built_up_km2": "Strong Built-Up Core (km²)",
            "NDVI": "Vegetation Index (NDVI)",
            "LST_C": "Daytime Surface Temperature (°C)",
            "rainfall_mm": "Annual Precipitation (mm)",
            "rainfall_anomaly_mm": "Rainfall Anomaly vs Normal (mm)",
            "environmental_stress": "Annual Compound Stress Index",
        }
        selected_ind = st.selectbox(
            "Select Longitudinal Indicator (2016–2025):",
            options=list(indicator_options.keys()),
            format_func=lambda k: indicator_options[k],
            index=0,
            key="overview_ind_select",
        )
        render_historical_trend_chart(df_master, selected_ind)

    with col_right:
        st.markdown("### 🔬 Validated Statistical Associations")
        pair = st.selectbox(
            "Select Validated Statistical Association:",
            options=["Built-Up vs LST", "NDVI vs LST", "Rainfall vs NDVI"],
            index=0,
            key="overview_pair_select",
        )
        render_statistical_association_chart(df_master, pair)

    st.markdown(
        f"""
        <div class="disclaimer-box">
            <div class="disclaimer-title">⚖️ Research & Policy Disclaimer</div>
            {DISCLAIMER_TEXT}
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------------------------------
# PAGE 2: DATA EXPLORER (NEW)
# -------------------------------------------------------------------------------------------------
def page_data_explorer(df_master: pd.DataFrame):
    render_header(
        "Interactive Data Explorer",
        "Multi-Dimensional Querying, Period Comparison, Distribution Diagnostics & Data Export"
    )

    st.markdown(
        "Perform ad-hoc slice-and-dice queries across the validated 10-year master research dataset (2016–2025). "
        "Compare baseline and evaluation periods, inspect parameter distributions, and download filtered analytical extracts."
    )

    exp_tab1, exp_tab2, exp_tab3 = st.tabs([
        "1. Longitudinal Filter & Distribution",
        "2. Two-Period Comparative Delta",
        "3. Raw Dataset & CSV Export",
    ])

    with exp_tab1:
        c_filt1, c_filt2 = st.columns([1, 2])
        with c_filt1:
            ind_choice = st.selectbox(
                "Select Indicator to Inspect:",
                options=[
                    "built_up_km2",
                    "strong_built_up_km2",
                    "NDVI",
                    "LST_C",
                    "rainfall_mm",
                    "rainfall_anomaly_mm",
                    "environmental_stress",
                ],
                format_func=lambda k: INDICATOR_META.get(k, {}).get("label", k),
                index=0,
            )
            year_range = st.slider(
                "Filter Year Range:",
                min_value=2016,
                max_value=2025,
                value=(2016, 2025),
                step=1,
            )

        df_filtered = df_master[
            (df_master["year"] >= year_range[0]) & (df_master["year"] <= year_range[1])
        ]

        with c_filt2:
            render_historical_trend_chart(df_filtered, ind_choice)

        st.markdown("#### Statistical Distribution Metrics")
        col_dist, col_tbl = st.columns([1, 1])
        with col_dist:
            render_distribution_chart(df_filtered, ind_choice)
        with col_tbl:
            st.markdown(f"**Descriptive Statistics for `{ind_choice}` ({year_range[0]}–{year_range[1]})**")
            stats_s = df_filtered[ind_choice].describe()
            df_stats = pd.DataFrame({
                "Statistic": ["Count", "Mean", "Std Dev", "Min", "25th Pct", "Median (50th)", "75th Pct", "Max", "IQR"],
                "Value": [
                    f"{stats_s['count']:.0f}",
                    f"{stats_s['mean']:.4f}",
                    f"{stats_s['std']:.4f}",
                    f"{stats_s['min']:.4f}",
                    f"{stats_s['25%']:.4f}",
                    f"{stats_s['50%']:.4f}",
                    f"{stats_s['75%']:.4f}",
                    f"{stats_s['max']:.4f}",
                    f"{stats_s['75%'] - stats_s['25%']:.4f}",
                ]
            })
            st.dataframe(df_stats, use_container_width=True, hide_index=True)

    with exp_tab2:
        st.markdown("#### ⚖️ Baseline vs. Comparison Period Analysis")
        p_c1, p_c2 = st.columns(2)
        with p_c1:
            base_year = st.selectbox("Select Baseline Year:", options=df_master["year"].tolist(), index=0)
        with p_c2:
            comp_year = st.selectbox("Select Comparison Year:", options=df_master["year"].tolist(), index=len(df_master)-1)

        row_base = df_master[df_master["year"] == base_year].iloc[0]
        row_comp = df_master[df_master["year"] == comp_year].iloc[0]

        comp_records = []
        for col_name, meta in INDICATOR_META.items():
            if col_name in df_master.columns:
                v_base = float(row_base[col_name])
                v_comp = float(row_comp[col_name])
                delta = v_comp - v_base
                pct_delta = (delta / abs(v_base) * 100.0) if v_base != 0 else np.nan
                comp_records.append({
                    "Indicator": meta["label"],
                    f"Baseline ({base_year})": f"{v_base:.3f} {meta['unit']}",
                    f"Comparison ({comp_year})": f"{v_comp:.3f} {meta['unit']}",
                    "Absolute Delta": f"{delta:+.3f} {meta['unit']}",
                    "Percentage Change": f"{pct_delta:+.2f}%" if pd.notnull(pct_delta) else "N/A",
                })

        st.dataframe(pd.DataFrame(comp_records), use_container_width=True, hide_index=True)
        st.caption(f"Comparing temporal delta from {base_year} to {comp_year} across all authoritative indicators.")

    with exp_tab3:
        st.markdown("#### 📋 Audited Master Dataset Inspection & Export")
        display_cols = [c for c in df_master.columns if c != ".geo"]
        st.dataframe(df_master[display_cols], use_container_width=True)

        csv_data = df_master[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Master Research Dataset (CSV)",
            data=csv_data,
            file_name="Chittoor_Master_Research_Dataset_2016_2025_Export.csv",
            mime="text/csv",
        )


# -------------------------------------------------------------------------------------------------
# PAGE 3: URBAN CHANGE ANALYTICS
# -------------------------------------------------------------------------------------------------
def page_urban_change(df_master: pd.DataFrame, spectral_screening: Optional[Dict[str, Any]] = None):
    render_header(
        "Urban Change Analytics",
        "Decadal Footprint Expansion, Consolidated Core Infill & Spectral Built-Up Screening"
    )

    if spectral_screening is None:
        spectral_screening = load_spectral_screening_summary()

    tab_u1, tab_u2, tab_u3 = st.tabs([
        "1. Urban Expansion Trajectory",
        "2. Spectral Built-Up Screening (Sentinel-2)",
        "3. High-Resolution Optical Inspection (10 m)",
    ])

    with tab_u1:
        st.markdown("### 🏙️ Urban Expansion Dynamics (2016–2025)")
        c1, c2 = st.columns(2)
        with c1:
            fig_bu = go.Figure()
            fig_bu.add_trace(go.Scatter(
                x=df_master["year"],
                y=df_master["built_up_km2"],
                name="Total Built-Up Area (p >= 0.50)",
                line=dict(color="#e11d48", width=3),
                marker=dict(size=8),
            ))
            fig_bu.add_trace(go.Scatter(
                x=df_master["year"],
                y=df_master["strong_built_up_km2"],
                name="Strong Built-Up Core",
                line=dict(color="#be123c", width=2.5, dash="dash"),
                marker=dict(size=7),
            ))
            fig_bu.update_layout(
                title="Decadal Growth: Total Built-Up vs Strong Core (km²)",
                xaxis=dict(title="Year", tickmode="linear", dtick=1),
                yaxis=dict(title="Area (km²)"),
                template="plotly_white",
                height=360,
                legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
            )
            st.plotly_chart(fig_bu, use_container_width=True)

        with c2:
            render_urban_acceleration_chart(df_master)

        st.markdown("#### 📊 Decadal Anthropogenic Expansion Summary")
        row_16 = df_master[df_master["year"] == 2016].iloc[0]
        row_25 = df_master[df_master["year"] == 2025].iloc[0]
        bu_growth = row_25["built_up_km2"] - row_16["built_up_km2"]
        bu_pct = (bu_growth / row_16["built_up_km2"]) * 100
        core_growth = row_25["strong_built_up_km2"] - row_16["strong_built_up_km2"]
        core_pct = (core_growth / row_16["strong_built_up_km2"]) * 100

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("2016 Built-Up Extent", f"{row_16['built_up_km2']:.2f} km²")
        with col_m2:
            st.metric("2025 Built-Up Extent", f"{row_25['built_up_km2']:.2f} km²", delta=f"+{bu_growth:.2f} km² (+{bu_pct:.1f}%)")
        with col_m3:
            st.metric("2016 Core Extent", f"{row_16['strong_built_up_km2']:.2f} km²")
        with col_m4:
            st.metric("2025 Core Extent", f"{row_25['strong_built_up_km2']:.2f} km²", delta=f"+{core_growth:.2f} km² (+{core_pct:.1f}%)")

    with tab_u2:
        st.markdown("### 🛰️ Normalized Difference Built-Up Index (NDBI) Screening")
        st.markdown(
            f"**Formulation:** `NDBI = (B11 - B8) / (B11 + B8)`. Highlights impervious infrastructure and exposed bare surfaces. "
            f"**Authoritative Screening Footprint:** Across the {spectral_screening['footprint_km2']:,.2f} km² valid clear-sky footprint, "
            f"**{spectral_screening['ndbi_increase_km2']:.2f} km² ({spectral_screening['ndbi_increase_pct']:.2f}%)** exhibited decadal NDBI increases $> +0.10$ (screening candidates for urban expansion and quarrying)."
        )
        c_ndbi1, c_ndbi2, c_ndbi3 = st.columns(3)
        with c_ndbi1:
            p16 = get_figure_path("ndbi_2016")
            if p16:
                st.image(str(p16), caption="2016 Baseline NDBI", use_container_width=True)
        with c_ndbi2:
            p25 = get_figure_path("ndbi_2025")
            if p25:
                st.image(str(p25), caption="2025 Current NDBI", use_container_width=True)
        with c_ndbi3:
            pch = get_figure_path("ndbi_change")
            if pch:
                st.image(str(pch), caption="Decadal NDBI Change Screening (2025 - 2016)", use_container_width=True)

        st.markdown(f"##### 📊 Validated District Spectral Screening Areas (Common Valid Footprint: {spectral_screening['footprint_km2']:,.2f} km²)")
        st.dataframe(spectral_screening["df_screening"], use_container_width=True, hide_index=True)

    with tab_u3:
        st.markdown("### 🔬 High-Resolution Native 10 m Optical Window Inspection")
        st.info("Uses memory-safe windowed raster reading to inspect 800 x 800 pixel regions of interest without loading multi-gigabyte files.")

        roi_name = st.selectbox(
            "Select Region of Interest (ROI):",
            options=list(PRESET_ROIS.keys()),
            index=0,
            key="urban_roi_select",
        )
        roi_info = PRESET_ROIS[roi_name]
        st.caption(f"**Selected:** {roi_name} — *{roi_info['description']}*")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.markdown("**2016 True Color Composite (B4/B3/B2):**")
            img16 = read_raster_window_rgb(2016, roi_name, false_color=False)
            if img16 is not None:
                st.image(img16, caption=f"2016 True Color ({roi_name})", use_container_width=True)
            else:
                st.warning("2016 scene window unavailable; check raw raster files.")
        with col_w2:
            st.markdown("**2025 True Color Composite (B4/B3/B2):**")
            img25 = read_raster_window_rgb(2025, roi_name, false_color=False)
            if img25 is not None:
                st.image(img25, caption=f"2025 True Color ({roi_name})", use_container_width=True)
            else:
                st.warning("2025 scene window unavailable.")


# -------------------------------------------------------------------------------------------------
# PAGE 4: ENVIRONMENTAL ANALYTICS
# -------------------------------------------------------------------------------------------------
def page_environmental_analytics(df_master: pd.DataFrame, spectral_screening: Optional[Dict[str, Any]] = None):
    render_header(
        "Environmental Analytics",
        "Multi-Decadal Profiles of Vegetation Vigor, Surface Moisture, Thermal Regimes & Precipitation"
    )

    if spectral_screening is None:
        spectral_screening = load_spectral_screening_summary()

    tab_e1, tab_e2, tab_e3, tab_e4 = st.tabs([
        "1. Compound Anomalies & Z-Scores",
        "2. Vegetation Dynamics (NDVI)",
        "3. Surface Moisture & Water (NDWI)",
        "4. Thermal Regimes & Precipitation",
    ])

    with tab_e1:
        st.markdown("### 🔬 Standardized Temporal Anomalies across Indicators")
        st.markdown(
            "Standardized Z-scores ($Z = (X - \\mu)/\\sigma$) uncover multi-factor compound stress. "
            "Notice the **2019 severe drought shock**: NDVI dropped to its decadal minimum ($Z = -2.14$), "
            "concurrent with peak Land Surface Temperature ($Z = +1.68$) and below-normal rainfall."
        )
        render_anomalies_chart(df_master)

        st.markdown("#### District Bivariate Correlation Heatmap (N = 10)")
        corr_cols = ["built_up_km2", "strong_built_up_km2", "NDVI", "LST_C", "rainfall_mm", "environmental_stress"]
        corr_mat = df_master[corr_cols].corr()
        fig_c = px.imshow(
            corr_mat,
            text_auto=".3f",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            title="Pearson Correlation Matrix (Observational Associations Only, Non-Causal)",
            template="plotly_white",
        )
        fig_c.update_layout(height=420)
        st.plotly_chart(fig_c, use_container_width=True)

    with tab_e2:
        st.markdown("### 🌿 Vegetation Condition & Canopy Screening (NDVI)")
        st.markdown(
            f"**Formulation:** `NDVI = (B8 - B4) / (B8 + B4)`. "
            f"Decadal screening across the {spectral_screening['footprint_km2']:,.2f} km² valid footprint identified "
            f"**{spectral_screening['ndvi_decrease_km2']:.2f} km² ({spectral_screening['ndvi_decrease_pct']:.2f}%)** with NDVI decrease $> 0.10$ "
            f"(candidate zones for canopy thinning and drought stress) and **{spectral_screening['ndvi_increase_km2']:.2f} km² ({spectral_screening['ndvi_increase_pct']:.2f}%)** with NDVI increase $> 0.10$."
        )
        c_v1, c_v2, c_v3 = st.columns(3)
        with c_v1:
            p16 = get_figure_path("ndvi_2016")
            if p16:
                st.image(str(p16), caption="2016 Baseline NDVI Overview", use_container_width=True)
        with c_v2:
            p25 = get_figure_path("ndvi_2025")
            if p25:
                st.image(str(p25), caption="2025 Current NDVI Overview", use_container_width=True)
        with c_v3:
            pch = get_figure_path("ndvi_change")
            if pch:
                st.image(str(pch), caption="Decadal NDVI Change Screening", use_container_width=True)

    with tab_e3:
        st.markdown("### 💧 Surface Moisture Dynamics (NDWI)")
        st.markdown(
            f"**Formulation:** `NDWI = (B3 - B8) / (B3 + B8)`. "
            f"Highlights open reservoirs, irrigation tanks, and high canopy water content. "
            f"Decadal screening identified **{spectral_screening['ndwi_decrease_km2']:.2f} km² ({spectral_screening['ndwi_decrease_pct']:.2f}%)** of moisture loss $> 0.10$ "
            f"and **{spectral_screening['ndwi_increase_km2']:.2f} km² ({spectral_screening['ndwi_increase_pct']:.2f}%)** of moisture gain."
        )
        c_w1, c_w2, c_w3 = st.columns(3)
        with c_w1:
            p16 = get_figure_path("ndwi_2016")
            if p16:
                st.image(str(p16), caption="2016 NDWI Overview", use_container_width=True)
        with c_w2:
            p25 = get_figure_path("ndwi_2025")
            if p25:
                st.image(str(p25), caption="2025 NDWI Overview", use_container_width=True)
        with c_w3:
            pch = get_figure_path("ndwi_change")
            if pch:
                st.image(str(pch), caption="Decadal NDWI Change Screening", use_container_width=True)

    with tab_e4:
        st.markdown("### 🌡️ Thermal Regimes & Precipitation Trends")
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            render_historical_trend_chart(df_master, "LST_C")
        with c_t2:
            render_historical_trend_chart(df_master, "rainfall_mm")


# -------------------------------------------------------------------------------------------------
# PAGE 5: SPATIAL STRESS & HOTSPOTS
# -------------------------------------------------------------------------------------------------
def page_stress_map(df_grid: pd.DataFrame, df_explain: pd.DataFrame, df_top100: pd.DataFrame, df_spatial_val: pd.DataFrame, df_sens: pd.DataFrame):
    render_header(
        "Environmental Stress Intelligence & Hotspots",
        "1 km Spatial Screening Grid (N = 6,902), Cell Inspector, Geostatistics & Sensitivity Analysis"
    )

    st.markdown(
        "The **Environmental Stress Indicator** synthesizes decadal urbanization ($C_{urb}$), "
        "vegetation loss ($C_{veg}$), and surface moisture loss ($C_{wat}$) into an additive screening score "
        "bounded in $[0, 1]$ across 6,902 one-kilometer grid cells. "
        "**Strict Rule:** This is a **relative screening indicator**, not an absolute physical disaster forecast."
    )

    tab_m1, tab_m2, tab_m3 = st.tabs([
        "1. Interactive Spatial Map & Cell Inspector",
        "2. Priority Hotspots Table (Top 100)",
        "3. Geostatistical Validation & Sensitivity",
    ])

    with tab_m1:
        map_ctrl1, map_ctrl2 = st.columns([1, 1])
        with map_ctrl1:
            show_top_only = st.checkbox("Focus Map on Top 100 Hotspots Only", value=False)
            selected_quartiles = st.multiselect(
                "Filter by Stress Quartile:",
                options=[
                    "Q1: Lower Relative Stress",
                    "Q2: Moderate-Low Relative Stress",
                    "Q3: Moderate-High Relative Stress",
                    "Q4: Higher Relative Stress",
                ],
                default=[
                    "Q1: Lower Relative Stress",
                    "Q2: Moderate-Low Relative Stress",
                    "Q3: Moderate-High Relative Stress",
                    "Q4: Higher Relative Stress",
                ],
            )

        with map_ctrl2:
            cell_options = df_top100["cell_id"].tolist() if df_top100 is not None and "cell_id" in df_top100.columns else []
            for extra_c in ["C_052_166", "C_047_043", "C_042_068"]:
                if extra_c not in cell_options and extra_c in df_grid["cell_id"].values:
                    cell_options.append(extra_c)

            chosen_cell = st.selectbox(
                "📍 Highlight & Deconstruct Specific 1-km Cell:",
                options=cell_options,
                index=0,
                help="Select a 1 km cell ID to highlight its centroid location on the map and inspect its geographic, administrative, and component breakdown."
            )

        render_stress_grid_map(
            df_grid,
            df_explain=df_explain,
            show_top_100_only=show_top_only,
            selected_quartiles=selected_quartiles,
            selected_cell_id=chosen_cell,
        )

        st.markdown("---")
        st.markdown("#### 🔬 Detailed Cell Decomposition")
        render_cell_inspector(chosen_cell, df_explain, df_top100)

    with tab_m2:
        st.markdown("### 🎯 Priority Hotspots Table (Top 100 Cells)")
        t_c1, t_c2 = st.columns(2)
        with t_c1:
            rank_slider = st.slider("Rank Range:", min_value=1, max_value=100, value=(1, 50))
        with t_c2:
            min_score = st.slider("Minimum Stress Score Cutoff:", min_value=0.50, max_value=0.68, value=0.52, step=0.01)

        evidence_opts = df_top100["evidence_strength"].unique().tolist() if "evidence_strength" in df_top100.columns else []
        evidence_filter = st.multiselect("Evidence Strength Filter:", options=evidence_opts, default=evidence_opts)

        render_top_100_table(
            df_top100,
            rank_range=rank_slider,
            min_stress=min_score,
            selected_evidence=evidence_filter,
        )

    with tab_m3:
        st.markdown("### 📐 Geostatistical Validation & Sensitivity Analysis")
        st.markdown("#### 1. Spatial Autocorrelation (Global Moran's I)")
        st.dataframe(
            df_spatial_val[df_spatial_val["spatial_autocorrelation"].str.contains("Moran", case=False, na=False)][
                ["research_question", "analysis_scale", "spatial_autocorrelation", "p_value", "interpretation"]
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Moran's I = +0.7131 confirms strong, statistically significant spatial clustering (p < 0.0001) rather than random noise.")

        st.markdown("#### 2. Indicator Formulation Sensitivity (Equal vs. PCA Weights & Spatial Resolution)")
        st.dataframe(
            df_sens[
                ["sensitivity_test", "parameter", "n_cells", "mean_score", "median_score", "p90_score", "correlation_with_primary", "interpretation"]
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Weighting sensitivity: Equal-weight and PCA-weight stress rankings show high concordance (Pearson r = 0.9279; Spearman rho = 0.9385), indicating that the broad spatial ranking is reasonably stable under alternative weighting schemes.")


# -------------------------------------------------------------------------------------------------
# PAGE 6: FORECASTING & MODEL PERFORMANCE
# -------------------------------------------------------------------------------------------------
def page_forecast(df_master: pd.DataFrame, df_forecast: pd.DataFrame, df_val: pd.DataFrame, df_comp: pd.DataFrame, df_feas: pd.DataFrame):
    render_header(
        "Forecasting & Model Performance",
        "Chronological Walk-Forward Validation, Model Benchmarking, 2026 Prediction Intervals & ML Claim Audit"
    )

    st.markdown(
        """
        <div class="scientific-notice">
            <b>Mandatory Scientific Governance:</b><br>
            • <b>Macro-Level Aggregate Extrapolation:</b> Forecasts estimate district-wide built-up area; <b>NO 2026 pixel-level construction map</b> is generated.<br>
            • <b>Strict Chronological Validation:</b> Models are evaluated using walk-forward rolling-origin backtesting (2022–2025 out-of-sample points); NO random train/test splits.<br>
            • <b>Prediction Uncertainty:</b> Forecasts communicate uncertainty via analytical 95% prediction intervals (Student's t, df=8).
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_f1, tab_f2, tab_f3, tab_f4 = st.tabs([
        "1. 2026 Built-Up Forecast",
        "2. Walk-Forward Backtesting",
        "3. Model Comparison Benchmark",
        "4. ML Claim & Feasibility Audit",
    ])

    with tab_f1:
        st.markdown("### 🔮 2026 1-Year-Ahead Built-Up Extent Extrapolation")
        total_row = df_forecast[df_forecast["target"].str.contains("Total Built-Up", case=False)].iloc[0]
        core_row = df_forecast[df_forecast["target"].str.contains("Strong Built-Up", case=False)].iloc[0]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                label="2025 Baseline (Observed)",
                value=f"{total_row['historical_last_value']:.2f} km²",
                delta=f"Core: {core_row['historical_last_value']:.2f} km²",
            )
        with c2:
            st.metric(
                label="2026 Point Forecast (Total Built-Up)",
                value=f"{total_row['point_forecast']:.2f} km²",
                delta=f"+{total_row['point_forecast'] - total_row['historical_last_value']:.2f} km² (+4.3%)",
            )
        with c3:
            st.metric(
                label="95% Analytical Prediction Interval",
                value=f"[{total_row['lower_95']:.2f}, {total_row['upper_95']:.2f}] km²",
                delta=f"Margin: ±{total_row['upper_95'] - total_row['point_forecast']:.2f} km²",
                delta_color="off",
            )

        render_forecast_chart(df_master, df_forecast)

        st.markdown("#### 📋 Authoritative Forecast Verification Table")
        st.dataframe(
            df_forecast[[
                "target", "forecast_year", "point_forecast", "lower_95", "upper_95",
                "historical_last_value", "model", "validation_mae", "baseline_mae", "improvement_percent"
            ]].style.format({
                "point_forecast": "{:.2f}",
                "lower_95": "{:.2f}",
                "upper_95": "{:.2f}",
                "historical_last_value": "{:.2f}",
                "validation_mae": "{:.2f} km²",
                "baseline_mae": "{:.2f} km²",
                "improvement_percent": "+{:.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tab_f2:
        st.markdown("### 🔬 Out-of-Sample Walk-Forward Backtesting (2022–2025)")
        st.markdown(
            "To prevent look-ahead bias and data leakage, models were trained on expanding historical windows (e.g. 2016–2021) "
            "and evaluated strictly on the succeeding out-of-sample year (e.g. 2022). "
            "This procedure was repeated across 4 independent test folds (2022, 2023, 2024, 2025)."
        )
        target_choice = st.radio(
            "Select Validation Target:",
            options=["Total Built-Up Area (km²)", "Strong Built-Up Core (km²)"],
            horizontal=True,
        )
        render_backtesting_chart(df_val, target_choice)

        st.markdown("#### Backtesting Fold-by-Fold Error Records")
        df_val_sub = df_val[df_val["target"].str.contains(target_choice[:10], case=False, na=False)]
        st.dataframe(
            df_val_sub[[
                "prediction_year", "actual", "forecast", "error", "absolute_error",
                "baseline_forecast", "baseline_absolute_error"
            ]].style.format({
                "actual": "{:.2f} km²",
                "forecast": "{:.2f} km²",
                "error": "{:+.2f} km²",
                "absolute_error": "{:.2f} km²",
                "baseline_forecast": "{:.2f} km²",
                "baseline_absolute_error": "{:.2f} km²",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tab_f3:
        st.markdown("### 🏆 Candidate Model Benchmarking")
        st.markdown(
            "All candidate time-series models were benchmarked objectively against the **Naive Persistence Baseline** ($y_{t-1}$). "
            "For Built-Up Area, **OLS Linear Trend Extrapolation** achieved the lowest Mean Absolute Error (**8.07 km²**, a **+44.1% improvement** over baseline)."
        )
        b_target = st.selectbox(
            "Select Indicator Target for Model Comparison:",
            options=["Built-Up Area (km²)", "Strong Built-Up Core (km²)", "Annual NDVI"],
            index=0,
        )
        render_model_comparison_bar(df_comp, b_target[:10])

        st.dataframe(
            df_comp[df_comp["target"].str.contains(b_target[:10], case=False, na=False)][[
                "model", "mae", "rmse", "mape_pct", "baseline_mae", "improvement_mae_pct", "status", "limitations"
            ]].style.format({
                "mae": "{:.4f}",
                "rmse": "{:.4f}",
                "mape_pct": "{:.2f}%",
                "baseline_mae": "{:.4f}",
                "improvement_mae_pct": "{:+.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tab_f4:
        st.markdown("### 🛡️ Machine Learning Claim & Feasibility Audit")
        st.markdown(
            "**Scientific Integrity Rule:** A credible Data Scientist chooses models based on sample size and physics, NOT buzzwords. "
            "With $N = 10$ annual points, training deep neural networks (LSTM/CNN) or complex decision tree ensembles (Random Forest/XGBoost) "
            "guarantees severe overfitting and noise memorization."
        )
        st.dataframe(
            df_feas[[
                "target", "temporal_frequency", "observation_count", "ML_possible",
                "deep_learning_possible", "recommended_method", "confidence_level", "justification"
            ]],
            use_container_width=True,
            hide_index=True,
        )


# -------------------------------------------------------------------------------------------------
# PAGE 7: DECISION SUPPORT
# -------------------------------------------------------------------------------------------------
def page_decision_support(df_matrix: pd.DataFrame, df_exec: pd.DataFrame):
    render_header(
        "Decision Support & Action Prioritization",
        "Operational Guidance for Field Inspection, Resource Monitoring & Planning Review"
    )

    st.markdown(
        """
        <div class="scientific-notice">
            <b>Operational Framing Rule:</b> Recommendations are strictly framed around 
            <b>monitoring, field verification, planning review, environmental assessment, infrastructure planning, and targeted data collection</b>. 
            The system does <i>NOT</i> issue punitive mandates, building collapse warnings, or definitive legal determinations.
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_decision_support_accordions(df_matrix, df_exec)


# -------------------------------------------------------------------------------------------------
# PAGE 8: METHODOLOGY & DATA QUALITY
# -------------------------------------------------------------------------------------------------
def page_methodology(df_contract: pd.DataFrame, df_audit: pd.DataFrame, df_units: pd.DataFrame):
    render_header(
        "Methodology, Datasets & Data Quality",
        "End-to-End Scientific Architecture, Remote Sensing Provenance & Governance Audit"
    )

    st.markdown("### 🔄 End-to-End Scientific Architecture")
    st.markdown(
        """
        ```
        1. Multi-Sensor Data Ingestion (Sentinel-2, Dynamic World, MODIS, CHIRPS)
              ↓
        2. Technical & Scientific Quality Audit (CRS, Band Structure, Immutability)
              ↓
        3. Cloud Screening & Common Clear-Sky Masking (Valid Footprint: 6,702.08 km²)
              ↓
        4. High-Resolution Feature Engineering (NDVI, NDWI, NDBI at Native 10 m)
              ↓
        5. Statistical Validation (Bivariate Association Tests & Moran's I = +0.7131)
              ↓
        6. Decadal Spectral Screening (|Δ| > 0.10 Candidate Zones across 6,702 km²)
              ↓
        7. 1 km Spatial Stress Grid & Hotspot Stratification (N = 6,902 Cells)
              ↓
        8. Predictive Feasibility & Walk-Forward Validation (OLS 2026 Forecast)
              ↓
        9. Explainability & Action Framing (Additive Decomposition & Monitoring Protocols)
              ↓
        10. Analytical Intelligence Dashboard (Presentation Layer)
        ```
        """
    )

    st.markdown("### 📡 Authoritative Remote Sensing Datasets")
    sources_data = [
        {
            "Dataset": "Sentinel-2 MSI",
            "Spatial Resolution": "10 m / 20 m",
            "Temporal Coverage": "2016 & 2025 (Decadal Composites)",
            "Role in Project": "High-resolution multispectral baseline, spectral feature computation (NDVI, NDWI, NDBI), and decadal spectral change screening.",
        },
        {
            "Dataset": "Dynamic World",
            "Spatial Resolution": "10 m",
            "Temporal Coverage": "2016–2025 (Annual Extent)",
            "Role in Project": "Authoritative historical built-up and core urban area time-series extraction based on deep learning FCN.",
        },
        {
            "Dataset": "MODIS Terra (MOD11A2)",
            "Spatial Resolution": "1 km",
            "Temporal Coverage": "2016–2025 (Annual Mean)",
            "Role in Project": "Daytime Land Surface Temperature (LST) and regional thermal dynamics.",
        },
        {
            "Dataset": "CHIRPS Pentad",
            "Spatial Resolution": "0.05° (~5.5 km)",
            "Temporal Coverage": "2016–2025 (Annual Totals)",
            "Role in Project": "Precipitation time series and rainfall anomalies relative to the 1981–2010 climate normal.",
        },
    ]
    st.dataframe(pd.DataFrame(sources_data), use_container_width=True, hide_index=True)

    render_traceability_table(df_contract, df_audit)

    st.markdown("### 📏 Permitted Project Units Dictionary")
    st.dataframe(
        df_units[["variable", "unit", "type", "description", "permitted_symbols"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        f"""
        <div class="disclaimer-box">
            <div class="disclaimer-title">⚖️ Full Legal & Scientific Disclaimer</div>
            {DISCLAIMER_TEXT}
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------------------------------------
# MAIN APP DISPATCHER
# -------------------------------------------------------------------------------------------------
def main():
    # Load all validated datasets
    try:
        metrics = get_headline_metrics()
        df_master = load_master_timeseries()
        df_grid = load_stress_grid()
        df_explain = load_stress_explainability()
        df_top100 = load_top_100_hotspots()
        df_forecast = load_forecast_2026()
        df_val = load_forecast_validation()
        df_comp = load_model_comparison()
        df_feas = load_feasibility_matrix()
        df_spatial_val = load_spatial_validation()
        df_sens = load_stress_sensitivity()
        df_matrix = load_decision_matrix()
        df_exec = load_executive_summary()
        df_contract = load_data_contract()
        df_audit = load_headline_audit()
        df_units = load_units_dictionary()
        spectral_screening = load_spectral_screening_summary()
    except Exception as e:
        st.error(f"Critical error loading validated analytical assets: {e}")
        st.stop()

    # Sidebar navigation
    selected_page = render_sidebar()

    # Dispatch to active page
    if selected_page == "1. Executive Overview":
        page_overview(metrics, df_master)
    elif selected_page == "2. Data Explorer":
        page_data_explorer(df_master)
    elif selected_page == "3. Urban Change Analytics":
        page_urban_change(df_master, spectral_screening)
    elif selected_page == "4. Environmental Analytics":
        page_environmental_analytics(df_master, spectral_screening)
    elif selected_page == "5. Spatial Stress & Hotspots":
        page_stress_map(df_grid, df_explain, df_top100, df_spatial_val, df_sens)
    elif selected_page == "6. Forecasting & Model Performance":
        page_forecast(df_master, df_forecast, df_val, df_comp, df_feas)
    elif selected_page == "7. Decision Support":
        page_decision_support(df_matrix, df_exec)
    elif selected_page == "8. Methodology & Data Quality":
        page_methodology(df_contract, df_audit, df_units)


if __name__ == "__main__":
    main()
