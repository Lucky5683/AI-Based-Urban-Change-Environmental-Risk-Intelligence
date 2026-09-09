"""Interactive Table and Matrix Viewers for Chittoor Environmental Intelligence."""

from __future__ import annotations

from typing import List, Optional
import pandas as pd
import streamlit as st


def render_top_100_table(
    df_top100: pd.DataFrame,
    rank_range: tuple[int, int] = (1, 100),
    min_stress: float = 0.50,
    selected_evidence: Optional[List[str]] = None
) -> pd.DataFrame:
    """Render the filtered Top 100 Environmental Stress Hotspots table with deterministic ordering."""
    df_filtered = df_top100.copy()

    # Apply contract deterministic sorting: stress_score DESC, cell_id ASC
    df_filtered = df_filtered.sort_values(
        by=["stress_score", "cell_id"],
        ascending=[False, True]
    ).reset_index(drop=True)
    df_filtered["rank"] = range(1, len(df_filtered) + 1)

    # Rank filter
    df_filtered = df_filtered[
        (df_filtered["rank"] >= rank_range[0]) & (df_filtered["rank"] <= rank_range[1])
    ]

    # Stress score cutoff
    df_filtered = df_filtered[df_filtered["stress_score"] >= min_stress]

    # Evidence strength filter
    if selected_evidence:
        df_filtered = df_filtered[df_filtered["evidence_strength"].isin(selected_evidence)]

    # Ensure coordinate and location columns exist
    if "latitude" not in df_filtered.columns and "lat" in df_filtered.columns:
        df_filtered["latitude"] = df_filtered["lat"]
    if "longitude" not in df_filtered.columns and "lon" in df_filtered.columns:
        df_filtered["longitude"] = df_filtered["lon"]
    if "mandal" not in df_filtered.columns and "mandal_name" in df_filtered.columns:
        df_filtered["mandal"] = df_filtered["mandal_name"]
    if "nearest_place" not in df_filtered.columns:
        df_filtered["nearest_place"] = "N/A"

    # Display columns ordered per specification:
    # Rank, Cell ID, Stress Score, Stress Quartile, Latitude, Longitude, Mandal, Nearest Place, Evidence Strength, Main Evidence Driver, Decision Support
    col_map = {
        "rank": "Rank",
        "cell_id": "Cell ID",
        "stress_score": "Stress Score",
        "stress_quartile": "Stress Quartile",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "mandal": "Mandal",
        "nearest_place": "Nearest Place (if available)",
        "evidence_strength": "Evidence Strength",
        "dominant_evidence": "Main Evidence Driver",
        "decision_support_label": "Decision Support",
    }
    cols_present = [c for c in col_map.keys() if c in df_filtered.columns]
    df_display = df_filtered[cols_present].rename(columns=col_map)

    format_dict = {}
    if "Stress Score" in df_display.columns:
        format_dict["Stress Score"] = "{:.4f}"
    if "Latitude" in df_display.columns:
        format_dict["Latitude"] = "{:.5f}"
    if "Longitude" in df_display.columns:
        format_dict["Longitude"] = "{:.5f}"

    st.dataframe(
        df_display.style.format(format_dict),
        use_container_width=True,
        height=420,
    )

    st.caption(
        f"Displaying **{len(df_filtered)}** priority cells (deterministic ordering by `stress_score DESC, cell_id ASC`). "
        "ℹ️ *Geographic Context Note:* Stress scores are calculated for approximately 1-km spatial analysis cells. "
        "Administrative and settlement names are provided only as geographic context; they are not stress classifications for those places."
    )

    return df_filtered


def render_decision_support_accordions(
    df_matrix: pd.DataFrame,
    df_exec: Optional[pd.DataFrame] = None
) -> None:
    """Render decision support matrix and executive priorities in structured cards/accordions."""
    if df_exec is not None:
        st.markdown("### 🏛️ Executive Priority Summary")
        for _, row in df_exec.iterrows():
            with st.container():
                st.markdown(
                    f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:5px solid #2563eb; border-radius:8px; padding:1rem 1.25rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-weight:700; font-size:1.05rem; color:#1e293b; margin-bottom:0.3rem;">
                            {row.get('priority', 'Priority')}
                        </div>
                        <div style="font-size:0.9rem; color:#334155; margin-bottom:0.5rem;">
                            <b>Finding:</b> {row.get('finding', '')}
                        </div>
                        <div style="font-size:0.85rem; color:#64748b; margin-bottom:0.5rem;">
                            <b>Empirical Evidence:</b> {row.get('evidence', '')} &nbsp;|&nbsp; <b>Confidence:</b> <span style="color:#0284c7; font-weight:600;">{row.get('confidence', '')}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#0f766e; background:#f0fdfa; padding:0.5rem 0.75rem; border-radius:6px; border:1px solid #ccfbf1;">
                            <b>Recommended Operational Next Step:</b> {row.get('recommended_next_step', '')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("### 📋 Thematic Decision Support Matrix")
    for _, row in df_matrix.iterrows():
        with st.expander(f"📌 {row.get('issue', 'Thematic Area')} (Confidence: {row.get('confidence', 'Moderate')})"):
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Observed Empirical Evidence:**")
                st.write(row.get("evidence", "N/A"))
                st.write("**Spatial Indicator:**")
                st.write(row.get("spatial_indicator", "N/A"))
                st.write("**Temporal Indicator:**")
                st.write(row.get("temporal_indicator", "N/A"))
            with c2:
                st.write("**Forecast Indicator:**")
                st.write(row.get("forecast_indicator", "N/A"))
                st.write("**Recommended Monitoring Action:**")
                st.info(row.get("recommended_monitoring_action", "Field inspection and monitoring."))
                st.write("**Scientific Limitation:**")
                st.warning(row.get("limitation", "Observational screening indicator."))


def render_traceability_table(df_contract: pd.DataFrame, df_audit: pd.DataFrame) -> None:
    """Render the authoritative data provenance and audit contract table."""
    st.markdown("### 🛡️ Dashboard Data Contract & Governance")
    st.dataframe(
        df_contract[[
            "dashboard_section", "metric", "source", "unit",
            "spatial_level", "allowed_interpretation", "forbidden_interpretation"
        ]],
        use_container_width=True,
        height=320,
    )

    st.markdown("### 🔍 Headline Results Audit Traceability")
    st.dataframe(
        df_audit[[
            "result", "value", "unit", "source_file", "source_variable", "status", "interpretation"
        ]],
        use_container_width=True,
        height=340,
    )
