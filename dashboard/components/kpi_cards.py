"""KPI Card Renderers for Chittoor Environmental Intelligence Dashboard."""

from __future__ import annotations

from typing import Any, Dict
import streamlit as st


def render_overview_kpis(metrics: Dict[str, Any]) -> None:
    """Render the 6 mandatory headline KPI indicator cards with verified units."""
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        st.metric(
            label="2025 Built-Up Area",
            value=f"{metrics['builtup_2025']:.2f} km²",
            delta=f"+{metrics['builtup_diff']:.2f} km² (+{metrics['builtup_pct']:.1f}%) since 2016",
            help="Authoritative Dynamic World 10 m satellite built-up footprint (threshold p >= 0.50)."
        )

    with col2:
        st.metric(
            label="Built-Up Increase (2016→2025)",
            value=f"+{metrics['builtup_diff']:.2f} km²",
            delta=f"+{metrics['builtup_pct']:.1f}% decadal expansion",
            help="Net anthropogenic land transformation over the 10-year observation period."
        )

    with col3:
        st.metric(
            label="2025 Mean NDVI",
            value=f"{metrics['ndvi_2025']:.4f}",
            delta=f"{metrics['ndvi_diff']:+.4f} vs 2016 (range: {metrics['ndvi_min']:.3f}–{metrics['ndvi_max']:.3f})",
            help="Sentinel-2 / Landsat annual composite normalized vegetation condition indicator."
        )

    with col4:
        st.metric(
            label="2025 Daytime LST",
            value=f"{metrics['lst_2025']:.2f} °C",
            delta=f"{metrics['lst_diff']:+.2f} °C vs 2016 (range: {metrics['lst_min']:.2f}–{metrics['lst_max']:.2f} °C)",
            delta_color="inverse",
            help="MODIS Terra (MOD11A2) Daytime Land Surface Temperature annual mean."
        )

    with col5:
        st.metric(
            label="2025 Annual Rainfall",
            value=f"{metrics['rainfall_2025']:.2f} mm",
            delta=f"{metrics['rainfall_diff_mean']:+.2f} mm vs climate normal ({metrics['rainfall_mean']:,.1f} mm 10-yr mean)",
            help="CHIRPS pentad cumulative annual precipitation."
        )

    with col6:
        st.metric(
            label="Spatial Stress Grid (1 km Summary)",
            value=f"{metrics['stress_mean']:.4f} (Mean)",
            delta=f"Peak: {metrics['stress_max']:.4f} (Cell {metrics['peak_cell']}) | 2025 Temporal: {metrics['temporal_stress_2025']:.4f}",
            delta_color="off",
            help=f"Decadal 1 km Spatial Grid (Mean: {metrics['stress_mean']:.4f}, Peak: {metrics['stress_max']:.4f}). Distinct from annual district-level temporal stress (2025: {metrics['temporal_stress_2025']:.4f}). Relative screening indicator in [0, 1]."
        )


def render_forecast_kpi_banner(metrics: Dict[str, Any]) -> None:
    """Render the secondary forecast and core urban indicators."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(
            f"**2025 Strong Built-Up Core:** `{metrics['strong_core_2025']:.2f} km²`  \n"
            f"*High-confidence consolidated urban core ({metrics['strong_core_pct']:+.1f}% growth since 2016)*"
        )
    with c2:
        st.info(
            f"**2026 Point Forecast:** `{metrics['forecast_2026']:.2f} km²`  \n"
            f"*95% Prediction Interval: [{metrics['forecast_2026_lower']:.2f}, {metrics['forecast_2026_upper']:.2f}] km²*"
        )
    with c3:
        st.info(
            f"**2026 Strong Core Forecast:** `{metrics['core_forecast']:.2f} km²`  \n"
            f"*95% Prediction Interval: [{metrics['core_forecast_lower']:.2f}, {metrics['core_forecast_upper']:.2f}] km²*"
        )
