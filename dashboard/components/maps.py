"""Interactive Map Components for Environmental Stress Grid and Hotspots."""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


QUARTILE_COLORS = {
    "Q1: Lower Relative Stress": "#16a34a",
    "Q2: Moderate-Low Relative Stress": "#ca8a04",
    "Q3: Moderate-High Relative Stress": "#ea580c",
    "Q4: Higher Relative Stress": "#dc2626",
}


def render_stress_grid_map(
    df_grid: pd.DataFrame,
    df_explain: Optional[pd.DataFrame] = None,
    show_top_100_only: bool = False,
    selected_quartiles: Optional[List[str]] = None,
    selected_cell_id: Optional[str] = None,
) -> None:
    """Render interactive spatial map of the 1 km Environmental Stress Grid."""
    # Merge explainability quartile if not present in grid
    df_plot = df_grid.copy()
    if "stress_quartile" not in df_plot.columns and df_explain is not None:
        merge_cols = ["cell_id", "stress_quartile", "rank"]
        if "mandal" in df_explain.columns and "mandal" not in df_plot.columns:
            merge_cols.append("mandal")
        df_plot = df_plot.merge(
            df_explain[merge_cols],
            on="cell_id",
            how="left"
        )
    elif "stress_quartile" not in df_plot.columns:
        # Compute quartiles on the fly if needed
        labels = [
            "Q1: Lower Relative Stress",
            "Q2: Moderate-Low Relative Stress",
            "Q3: Moderate-High Relative Stress",
            "Q4: Higher Relative Stress",
        ]
        df_plot["stress_quartile"] = pd.qcut(df_plot["stress_score"], q=4, labels=labels)

    # Filter by quartiles if requested
    if selected_quartiles:
        df_plot = df_plot[df_plot["stress_quartile"].isin(selected_quartiles)]

    # Filter top 100 if requested
    if show_top_100_only:
        df_plot = df_plot.sort_values(by=["stress_score", "cell_id"], ascending=[False, True]).head(100)

    # Determine coordinate columns
    lat_col = "latitude" if "latitude" in df_plot.columns else "lat"
    lon_col = "longitude" if "longitude" in df_plot.columns else "lon"

    # Hover data setup
    hover_dict = {
        lat_col: ":.4f",
        lon_col: ":.4f",
        "stress_score": ":.4f",
        "urbanization_component": ":.3f",
        "vegetation_component": ":.3f",
        "water_component": ":.3f",
        "stress_quartile": True,
    }
    if "mandal" in df_plot.columns:
        hover_dict["mandal"] = True
    elif "mandal_name" in df_plot.columns:
        hover_dict["mandal_name"] = True

    # Create Plotly map scatter using modern px.scatter_map API
    fig = px.scatter_map(
        df_plot,
        lat=lat_col,
        lon=lon_col,
        color="stress_quartile",
        color_discrete_map=QUARTILE_COLORS,
        size=df_plot["stress_score"].clip(lower=0.1) * 8 if show_top_100_only else [5] * len(df_plot),
        hover_name="cell_id",
        hover_data=hover_dict,
        category_orders={"stress_quartile": list(QUARTILE_COLORS.keys())},
        zoom=8.5,
        center=dict(lat=13.25, lon=79.05),
        map_style="carto-positron",
        title="Decadal Relative Environmental Stress Indicator (1 km Grid, N = 6,902)",
    )

    # Highlight selected cell if provided
    if selected_cell_id:
        target_rows = df_grid[df_grid["cell_id"] == selected_cell_id]
        if not target_rows.empty:
            t_row = target_rows.iloc[0]
            t_lat = float(t_row.get("latitude", t_row.get("lat", 13.25)))
            t_lon = float(t_row.get("longitude", t_row.get("lon", 79.05)))
            t_mandal = str(t_row.get("mandal", t_row.get("mandal_name", "Unknown Mandal")))
            t_score = float(t_row.get("stress_score", 0.0))

            fig.add_trace(
                go.Scattermap(
                    lat=[t_lat],
                    lon=[t_lon],
                    mode="markers+text",
                    marker=dict(
                        size=18,
                        color="#0891b2",
                        symbol="circle",
                    ),
                    text=[f"📍 {selected_cell_id}"],
                    textposition="top right",
                    textfont=dict(size=12, color="#0f172a"),
                    name=f"Focused: {selected_cell_id}",
                    hoverinfo="text",
                    hovertext=[
                        f"<b>1-km stress cell {selected_cell_id}</b><br>"
                        f"Mandal: {t_mandal}<br>"
                        f"Stress Score: {t_score:.4f}<br>"
                        f"Centroid: {t_lat:.5f}°N, {t_lon:.5f}°E"
                    ],
                    showlegend=True,
                )
            )

    fig.update_layout(
        height=580,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(
            title=dict(text="Stress Quartile (Relative)"),
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#e2e8f0",
            borderwidth=1,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "🗺️ **Geographic Context:** Grid resolution is 1 km x 1 km (aggregated from 100 x 100 native Sentinel-2 pixels). "
        "Coordinates represent cell centroids. **Relative Environmental Stress** is an observational screening indicator, "
        "not an absolute structural risk or regulatory hazard rating."
    )


def render_cell_inspector(
    cell_id: str,
    df_explain: pd.DataFrame,
    df_top100: Optional[pd.DataFrame] = None
) -> None:
    """Render detailed explainability and location breakdown for a selected 1 km grid cell."""
    cell_row = df_explain[df_explain["cell_id"] == cell_id]
    if cell_row.empty:
        st.warning(f"Cell ID '{cell_id}' not found in the explainability dataset.")
        return

    row = cell_row.iloc[0]

    st.markdown(f"### 🔍 Cell Inspector: `1-km stress cell {row['cell_id']}`")

    # Extract location fields
    lat = float(row.get("latitude", row.get("lat", 0.0)))
    lon = float(row.get("longitude", row.get("lon", 0.0)))
    mandal = row.get("mandal", row.get("mandal_name", "N/A"))
    nearest_place = row.get("nearest_place", "N/A (Requires Authoritative Settlement Gazetteer)")
    nearest_dist = row.get("nearest_place_distance_km", np.nan)
    dist_str = f"{nearest_dist:.2f} km" if pd.notnull(nearest_dist) else "N/A"

    # Geographic and Administrative Location Information Box
    st.markdown(
        f"""
        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-left:4px solid #0284c7; border-radius:6px; padding:0.75rem 1rem; margin-bottom:1rem;">
            <div style="font-weight:600; font-size:0.95rem; color:#0f172a; margin-bottom:0.4rem;">
                📍 Geographic & Administrative Location Context
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; font-size:0.875rem; color:#334155;">
                <div>🏛️ <b>Mandal:</b> {mandal} Mandal</div>
                <div>🌐 <b>Cell Centroid:</b> {lat:.5f}°N, {lon:.5f}°E</div>
                <div>🏘️ <b>Nearest Mapped Settlement:</b> {nearest_place}</div>
                <div>📏 <b>Distance to Settlement:</b> {dist_str}</div>
            </div>
            <div style="font-size:0.78rem; color:#64748b; margin-top:0.4rem; font-style:italic;">
                Stress scores are calculated for approximately 1-km spatial analysis cells. Administrative and settlement names are provided only as geographic context; they are not stress classifications for those places.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Scientific Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Stress Score", f"{row['stress_score']:.4f}")
    with c2:
        st.metric("Quartile", f"{row.get('stress_quartile', 'N/A')}")
    with c3:
        st.metric("District Rank", f"#{int(row.get('rank', 0))}" if pd.notnull(row.get('rank')) else "N/A")
    with c4:
        st.metric("Evidence Strength", f"{row.get('evidence_strength', 'Standard')}")

    # Additive Component Decomposition Chart
    c_urb = float(row.get("urbanization_component", 0.0))
    c_veg = float(row.get("vegetation_component", 0.0))
    c_wat = float(row.get("water_component", 0.0))

    comp_df = pd.DataFrame({
        "Component": ["Urbanization (C_urb)", "Vegetation Loss (C_veg)", "Water/Moisture Loss (C_wat)"],
        "Normalized Score": [c_urb, c_veg, c_wat],
        "Weight": ["1/3 (0.333)", "1/3 (0.333)", "1/3 (0.333)"],
    })

    fig = px.bar(
        comp_df,
        x="Component",
        y="Normalized Score",
        text="Normalized Score",
        color="Component",
        color_discrete_sequence=["#e11d48", "#16a34a", "#0284c7"],
        title="Additive Stress Component Decomposition (Equal 1/3 Weighting)",
        range_y=[0, 1.1],
        template="plotly_white",
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    # Main Evidence Driver
    dom = "Multi-Source Spectral Shift"
    sec = "None"
    act = "Priority Monitoring"
    if df_top100 is not None:
        t_row = df_top100[df_top100["cell_id"] == cell_id]
        if not t_row.empty:
            dom = t_row.iloc[0].get("dominant_evidence", dom)
            sec = t_row.iloc[0].get("secondary_evidence", sec)
            act = t_row.iloc[0].get("decision_support_label", act)

    st.info(f"**Main Evidence Driver:** {dom}  \n**Secondary Evidence:** {sec}  \n**Decision Support Protocol:** {act}")
