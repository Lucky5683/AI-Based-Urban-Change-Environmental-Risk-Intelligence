"""Interactive Plotly Charts for Chittoor Environmental Intelligence Dashboard."""

from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import streamlit as st


INDICATOR_META = {
    "built_up_km2": {
        "label": "Total Built-Up Area",
        "unit": "km²",
        "color": "#e11d48",
        "description": "Observed district-wide built-up footprint (Dynamic World p >= 0.50).",
    },
    "strong_built_up_km2": {
        "label": "Strong Built-Up Core",
        "unit": "km²",
        "color": "#be123c",
        "description": "High-confidence consolidated urban core footprint.",
    },
    "NDVI": {
        "label": "Normalized Difference Vegetation Index",
        "unit": "dimensionless",
        "color": "#16a34a",
        "description": "Annual composite mean vegetation condition index [-1 to +1].",
    },
    "LST_C": {
        "label": "Daytime Land Surface Temperature",
        "unit": "°C",
        "color": "#ea580c",
        "description": "MODIS Terra (MOD11A2) Daytime LST annual mean.",
    },
    "rainfall_mm": {
        "label": "Annual Precipitation",
        "unit": "mm",
        "color": "#0284c7",
        "description": "CHIRPS pentad cumulative annual rainfall sum.",
    },
    "rainfall_anomaly_mm": {
        "label": "Rainfall Anomaly (vs Normal)",
        "unit": "mm",
        "color": "#6366f1",
        "description": "Annual precipitation departure from 1981-2010 normal.",
    },
    "environmental_stress": {
        "label": "Annual Aggregate Environmental Stress",
        "unit": "dimensionless [0, 1]",
        "color": "#9333ea",
        "description": "Aggregated annual observational multi-factor stress index.",
    },
}


def render_historical_trend_chart(df_master: pd.DataFrame, selected_col: str) -> None:
    """Render interactive Plotly line chart for historical master indicators (2016-2025)."""
    meta = INDICATOR_META.get(selected_col, {
        "label": selected_col,
        "unit": "",
        "color": "#2563eb",
        "description": "",
    })

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_master["year"],
            y=df_master[selected_col],
            mode="lines+markers",
            name=meta["label"],
            line=dict(color=meta["color"], width=3),
            marker=dict(size=8, color=meta["color"], symbol="circle"),
            hovertemplate=(
                f"<b>Year:</b> %{{x}}<br>"
                f"<b>{meta['label']}:</b> %{{y:.2f}} {meta['unit']}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text=f"Historical Trajectory: {meta['label']} (2016–2025)",
            font=dict(size=16, color="#0f172a"),
        ),
        xaxis=dict(
            title="Observation Year",
            tickmode="linear",
            tick0=2016,
            dtick=1,
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        yaxis=dict(
            title=f"{meta['label']} ({meta['unit']})",
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        template="plotly_white",
        height=420,
        margin=dict(l=40, r=30, t=50, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"ℹ️ **Indicator Context:** {meta['description']} *(Historical observational data; does not imply isolated causality)*")


def render_statistical_association_chart(
    df_master: pd.DataFrame,
    pair_name: str
) -> None:
    """Render scatter plot with trend line for validated bivariate statistical relationships."""
    if pair_name == "Built-Up vs LST":
        x_col, y_col = "built_up_km2", "LST_C"
        x_lab, y_lab = "Total Built-Up Area (km²)", "Daytime LST (°C)"
        note_template = "Statistically significant negative district-level association (r = {r:.3f}, p = {p:.3f}). NON-CAUSAL: Confounded by decadal rainfall trends and cloud screening; does NOT indicate urban cooling."
    elif pair_name == "NDVI vs LST":
        x_col, y_col = "NDVI", "LST_C"
        x_lab, y_lab = "Mean NDVI (dimensionless)", "Daytime LST (°C)"
        note_template = "Weak negative district-level association (r = {r:.3f}, p = {p:.3f}). Non-significant at alpha = 0.05 level."
    elif pair_name == "Rainfall vs NDVI":
        x_col, y_col = "rainfall_mm", "NDVI"
        x_lab, y_lab = "Annual Rainfall (mm)", "Mean NDVI (dimensionless)"
        note_template = "Negligible annual correlation (r = {r:.3f}, p = {p:.3f}). Non-significant; NDVI is driven by seasonal timing rather than annual total sum."
    else:
        return

    # Check columns exist
    if x_col not in df_master.columns or y_col not in df_master.columns:
        st.warning(f"Insufficient data: Columns '{x_col}' or '{y_col}' missing from dataset.")
        return

    # Filter valid finite numeric observations
    req_cols = [x_col, y_col]
    if "year" in df_master.columns:
        req_cols.append("year")
    valid = df_master[req_cols].dropna()
    valid = valid[np.isfinite(valid[x_col]) & np.isfinite(valid[y_col])]
    n_obs = len(valid)

    if n_obs < 3:
        st.warning(f"Insufficient data observations for Pearson correlation ({pair_name}: N = {n_obs}). Minimum 3 valid observations required.")
        return

    # Dynamically compute Pearson r and p-value via scipy.stats
    res = stats.pearsonr(valid[x_col], valid[y_col])
    pearson_r = float(res.statistic if hasattr(res, "statistic") else res[0])
    p_val = float(res.pvalue if hasattr(res, "pvalue") else res[1])
    note = note_template.format(r=pearson_r, p=p_val)

    fig = px.scatter(
        valid,
        x=x_col,
        y=y_col,
        text="year" if "year" in valid.columns else None,
        trendline="ols",
        title=f"District-Level Association: {pair_name}",
        labels={x_col: x_lab, y_col: y_lab},
        template="plotly_white",
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(size=10, color="#1e293b", opacity=0.85),
    )
    fig.update_layout(
        height=400,
        margin=dict(l=40, r=30, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div class="scientific-notice">
            <b>Statistical Metric:</b> Pearson <i>r</i> = <b>{pearson_r:.4f}</b> | <i>p</i>-value = <b>{p_val:.4f}</b><br>
            <b>Classification:</b> District-level association (N = {n_obs} annual observations)<br>
            <b>Scientific Interpretation:</b> {note}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_forecast_chart(df_master: pd.DataFrame, df_forecast: pd.DataFrame) -> None:
    """Render the 2026 Built-Up forecast chart with analytical 95% prediction interval."""
    # Historical data
    hist_years = df_master["year"].tolist()
    hist_vals = df_master["built_up_km2"].tolist()

    # Forecast row
    fc_row = df_forecast[df_forecast["target"].str.contains("Total Built-Up", case=False, na=False)].iloc[0]
    fc_year = int(fc_row["forecast_year"])
    fc_val = float(fc_row["point_forecast"])
    fc_lower = float(fc_row["lower_95"])
    fc_upper = float(fc_row["upper_95"])

    fig = go.Figure()

    # 1. Historical line
    fig.add_trace(
        go.Scatter(
            x=hist_years,
            y=hist_vals,
            mode="lines+markers",
            name="Observed Built-Up (2016–2025)",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=8, color="#1d4ed8"),
            hovertemplate="Observed %{x}: %{y:.2f} km²<extra></extra>",
        )
    )

    # 2. Prediction interval band connecting from 2025 to 2026
    pi_x = [2025, fc_year, fc_year, 2025]
    pi_y = [hist_vals[-1], fc_upper, fc_lower, hist_vals[-1]]

    fig.add_trace(
        go.Scatter(
            x=pi_x,
            y=pi_y,
            fill="toself",
            fillcolor="rgba(244, 63, 94, 0.18)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="95% Analytical Prediction Interval",
        )
    )

    # 3. Forecast point & connector line
    fig.add_trace(
        go.Scatter(
            x=[2025, fc_year],
            y=[hist_vals[-1], fc_val],
            mode="lines",
            line=dict(color="#e11d48", width=3, dash="dot"),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[fc_year],
            y=[fc_val],
            mode="markers+text",
            name=f"2026 Forecast ({fc_val:.2f} km²)",
            text=[f"2026 Forecast:<br>{fc_val:.2f} km²<br>[{fc_lower:.1f}, {fc_upper:.1f}]"],
            textposition="top center",
            marker=dict(size=12, color="#e11d48", symbol="diamond"),
            hovertemplate=(
                f"<b>Target Year:</b> {fc_year}<br>"
                f"<b>Point Forecast:</b> {fc_val:.2f} km²<br>"
                f"<b>95% Prediction Interval:</b> [{fc_lower:.2f}, {fc_upper:.2f}] km²<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="1-Year-Ahead Built-Up Extent Forecast (OLS Linear Trend)",
        xaxis=dict(
            title="Year",
            tickmode="linear",
            tick0=2016,
            dtick=1,
            range=[2015.5, 2026.8],
            showgrid=True,
            gridcolor="#f1f5f9",
        ),
        yaxis=dict(
            title="Total Built-Up Extent (km²)",
            showgrid=True,
            gridcolor="#f1f5f9",
            range=[140, 310],
        ),
        template="plotly_white",
        height=480,
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_anomalies_chart(df_master: pd.DataFrame) -> None:
    """Render standardized Z-score anomalies across indicators to show temporal deviations."""
    z_df = pd.DataFrame({"year": df_master["year"]})
    indicators = ["built_up_km2", "NDVI", "LST_C", "rainfall_mm"]
    labels = {
        "built_up_km2": "Built-Up (Z-Score)",
        "NDVI": "NDVI (Z-Score)",
        "LST_C": "LST (Z-Score)",
        "rainfall_mm": "Rainfall (Z-Score)",
    }

    for ind in indicators:
        vals = df_master[ind]
        z_df[labels[ind]] = (vals - vals.mean()) / vals.std()

    fig = go.Figure()
    colors = {"Built-Up (Z-Score)": "#e11d48", "NDVI (Z-Score)": "#16a34a", "LST (Z-Score)": "#ea580c", "Rainfall (Z-Score)": "#0284c7"}

    for name, col in colors.items():
        fig.add_trace(
            go.Scatter(
                x=z_df["year"],
                y=z_df[name],
                mode="lines+markers",
                name=name,
                line=dict(color=col, width=2),
                marker=dict(size=6),
            )
        )

    fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
    fig.update_layout(
        title="Standardized Temporal Anomalies (Z-Scores, 2016–2025)",
        xaxis=dict(title="Year", tickmode="linear", dtick=1),
        yaxis=dict(title="Standard Deviations from Decadal Mean (σ)"),
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=30, t=50, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_backtesting_chart(df_val: pd.DataFrame, target_keyword: str = "Total Built-Up") -> None:
    """Render walk-forward rolling-origin backtesting actual vs forecast curves."""
    df_sub = df_val[df_val["target"].str.contains(target_keyword, case=False, na=False)].copy()
    if df_sub.empty:
        df_sub = df_val.iloc[:4].copy()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_sub["prediction_year"],
            y=df_sub["actual"],
            mode="lines+markers",
            name="Actual Observation",
            line=dict(color="#0f172a", width=3),
            marker=dict(size=9, symbol="circle"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_sub["prediction_year"],
            y=df_sub["forecast"],
            mode="lines+markers",
            name="OLS Linear Walk-Forward Forecast",
            line=dict(color="#2563eb", width=2.5, dash="dash"),
            marker=dict(size=8, symbol="diamond"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_sub["prediction_year"],
            y=df_sub["baseline_forecast"],
            mode="lines+markers",
            name="Naive Persistence Baseline (y_{t-1})",
            line=dict(color="#94a3b8", width=2, dash="dot"),
            marker=dict(size=6, symbol="x"),
        )
    )

    fig.update_layout(
        title=f"Walk-Forward Backtesting (2022–2025 Out-of-Sample): {target_keyword}",
        xaxis=dict(title="Prediction Fold Year", tickmode="linear", dtick=1),
        yaxis=dict(title="Extent (km²)", showgrid=True, gridcolor="#f1f5f9"),
        template="plotly_white",
        height=360,
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_model_comparison_bar(df_comp: pd.DataFrame, target_keyword: str = "Built-Up Area") -> None:
    """Render comparative bar chart of model MAE against baseline."""
    df_sub = df_comp[df_comp["target"].str.contains(target_keyword, case=False, na=False)].copy()
    if df_sub.empty:
        return

    df_sub = df_sub.sort_values("mae", ascending=True)
    colors = ["#16a34a" if imp > 0 else ("#94a3b8" if imp == 0 else "#dc2626") for imp in df_sub["improvement_mae_pct"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=df_sub["model"],
            x=df_sub["mae"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.2f} km² ({imp:+.1f}%)" if imp != 0 else f"{v:.2f} km² (Baseline)" for v, imp in zip(df_sub["mae"], df_sub["improvement_mae_pct"])],
            textposition="auto",
        )
    )

    baseline_val = float(df_sub["baseline_mae"].iloc[0])
    fig.add_vline(x=baseline_val, line_dash="dash", line_color="#0f172a", annotation_text=f"Baseline MAE: {baseline_val:.2f} km²")

    fig.update_layout(
        title=f"Candidate Model Evaluation (Walk-Forward MAE): {target_keyword}",
        xaxis=dict(title="Mean Absolute Error (km², lower is better)"),
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        height=320,
        margin=dict(l=30, r=30, t=50, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_urban_acceleration_chart(df_master: pd.DataFrame) -> None:
    """Render YoY net additions (km²/year) and growth acceleration."""
    df_plot = df_master.sort_values("year").copy()
    df_plot["bu_net_annual"] = df_plot["built_up_km2"].diff()
    df_plot["core_net_annual"] = df_plot["strong_built_up_km2"].diff()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_plot["year"].iloc[1:],
            y=df_plot["bu_net_annual"].iloc[1:],
            name="Total Built-Up Annual Additions (km²/yr)",
            marker_color="#e11d48",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_plot["year"].iloc[1:],
            y=df_plot["core_net_annual"].iloc[1:],
            name="Strong Core Annual Additions (km²/yr)",
            marker_color="#be123c",
        )
    )

    fig.update_layout(
        title="Annual Net Built-Up Land Additions (2017–2025)",
        xaxis=dict(title="Year", tickmode="linear", dtick=1),
        yaxis=dict(title="Annual Net Expansion (km²/year)"),
        barmode="group",
        template="plotly_white",
        height=340,
        margin=dict(l=30, r=30, t=40, b=30),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_distribution_chart(df_master: pd.DataFrame, indicator: str) -> None:
    """Render boxplot and distribution summary for an indicator."""
    meta = INDICATOR_META.get(indicator, {"label": indicator, "unit": "", "color": "#2563eb"})
    vals = df_master[indicator].dropna()

    fig = go.Figure()
    fig.add_trace(
        go.Box(
            y=vals,
            name=meta["label"],
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8,
            marker_color=meta["color"],
            line_color=meta["color"],
        )
    )
    fig.update_layout(
        title=f"Decadal Distribution (2016–2025): {meta['label']}",
        yaxis=dict(title=f"{meta['label']} ({meta['unit']})"),
        template="plotly_white",
        height=320,
        margin=dict(l=30, r=30, t=40, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

