"""Automated Test Suite for Chittoor Environmental Intelligence Dashboard."""

from __future__ import annotations

import os
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

from dashboard.utils.data_loader import (
    get_headline_metrics,
    get_project_root,
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
    load_stress_explainability,
    load_stress_grid,
    load_stress_sensitivity,
    load_top_100_hotspots,
    load_units_dictionary,
    PROJECT_ROOT,
)


class TestDashboardIntegration(unittest.TestCase):
    """Test suite validating data loading, schema integrity, and scientific contracts."""

    def test_01_dashboard_imports(self):
        """Test 1: Verify dashboard modules, utils, and components import cleanly."""
        try:
            import dashboard.app
            import dashboard.components.charts
            import dashboard.components.kpi_cards
            import dashboard.components.maps
            import dashboard.components.tables_view
            import dashboard.utils.data_loader
            import dashboard.utils.raster_helpers
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import dashboard modules: {e}")

    def test_02_master_csv_loads(self):
        """Test 2: Master CSV loads with exactly 10 annual rows (2016-2025)."""
        df = load_master_timeseries()
        self.assertIsNotNone(df, "Master time series DataFrame should not be None")
        self.assertEqual(len(df), 10, f"Expected 10 rows for 2016-2025, got {len(df)}")
        self.assertListEqual(
            sorted(df["year"].tolist()),
            list(range(2016, 2026)),
            "Years must span exactly 2016 to 2025"
        )

    def test_03_stress_grid_loads(self):
        """Test 3: Stress grid loads with exactly 6,902 cells and valid coordinates."""
        df = load_stress_grid()
        self.assertIsNotNone(df, "Stress grid DataFrame should not be None")
        self.assertEqual(len(df), 6902, f"Expected 6,902 cells, got {len(df)}")
        
        # Check coordinate bounds for Chittoor District (~12.6°N to 14.1°N, 78.1°E to 80.0°E)
        lat_col = "lat" if "lat" in df.columns else "latitude"
        lon_col = "lon" if "lon" in df.columns else "longitude"
        self.assertTrue((df[lat_col] >= 12.0).all() and (df[lat_col] <= 14.5).all())
        self.assertTrue((df[lon_col] >= 78.0).all() and (df[lon_col] <= 80.5).all())

    def test_04_forecast_table_loads(self):
        """Test 4: Forecast table loads with required targets."""
        df = load_forecast_2026()
        self.assertIsNotNone(df, "Forecast table should not be None")
        self.assertGreaterEqual(len(df), 2, "Forecast table must have at least 2 target rows")
        targets = " ".join(df["target"].tolist())
        self.assertIn("Total Built-Up", targets)
        self.assertIn("Strong Built-Up", targets)

    def test_05_required_columns_exist(self):
        """Test 5: Verify all required columns exist across core tables."""
        master = load_master_timeseries()
        req_master = ["year", "built_up_km2", "strong_built_up_km2", "NDVI", "LST_C", "rainfall_mm", "environmental_stress"]
        for col in req_master:
            self.assertIn(col, master.columns, f"Missing required column '{col}' in master CSV")

        grid = load_stress_grid()
        req_grid = ["cell_id", "stress_score", "urbanization_component", "vegetation_component", "water_component"]
        for col in req_grid:
            self.assertIn(col, grid.columns, f"Missing required column '{col}' in stress grid")

        contract = load_data_contract()
        req_contract = ["dashboard_section", "metric", "source", "allowed_interpretation", "forbidden_interpretation"]
        for col in req_contract:
            self.assertIn(col, contract.columns, f"Missing required column '{col}' in data contract")

    def test_06_forecast_values_are_valid(self):
        """Test 6: Forecast values match validated project outputs."""
        df = load_forecast_2026()
        total_row = df[df["target"].str.contains("Total Built-Up", case=False)].iloc[0]
        core_row = df[df["target"].str.contains("Strong Built-Up", case=False)].iloc[0]

        # Validated Total Built-Up 2026: ~270.32 km² [250.02, 290.62]
        self.assertAlmostEqual(float(total_row["point_forecast"]), 270.32, places=1)
        self.assertAlmostEqual(float(total_row["lower_95"]), 250.02, places=1)
        self.assertAlmostEqual(float(total_row["upper_95"]), 290.62, places=1)

        # Validated Strong Core 2026: ~70.31 km² [64.75, 75.87]
        self.assertAlmostEqual(float(core_row["point_forecast"]), 70.31, places=1)
        self.assertAlmostEqual(float(core_row["lower_95"]), 64.75, places=1)
        self.assertAlmostEqual(float(core_row["upper_95"]), 75.87, places=1)

    def test_07_stress_score_range_is_valid(self):
        """Test 7: Stress scores and components are bounded within [0.0, 1.0]."""
        grid = load_stress_grid()
        self.assertTrue((grid["stress_score"] >= 0.0).all() and (grid["stress_score"] <= 1.0).all(),
                        "Grid stress scores must be bounded in [0.0, 1.0]")
        self.assertTrue((grid["urbanization_component"] >= 0.0).all() and (grid["urbanization_component"] <= 1.0).all())
        self.assertTrue((grid["vegetation_component"] >= 0.0).all() and (grid["vegetation_component"] <= 1.0).all())
        self.assertTrue((grid["water_component"] >= 0.0).all() and (grid["water_component"] <= 1.0).all())

        # Top 100 Hotspots deterministic tie-break check
        top100 = load_top_100_hotspots()
        self.assertEqual(len(top100), 100)
        # Check Rank 1 is C_052_166 with score 0.6771
        self.assertEqual(top100.iloc[0]["cell_id"], "C_052_166")
        self.assertAlmostEqual(float(top100.iloc[0]["stress_score"]), 0.6771, places=3)
        # Check tie break between C_049_170 and C_051_035 (both 0.5335)
        r77 = top100[top100["cell_id"] == "C_049_170"].iloc[0]["rank"]
        r78 = top100[top100["cell_id"] == "C_051_035"].iloc[0]["rank"]
        self.assertLess(r77, r78, "Deterministic sorting requires C_049_170 before C_051_035")

    def test_08_no_raw_data_modified(self):
        """Test 8: Confirm raw data directory exists and has not been emptied or removed."""
        raw_sat = PROJECT_ROOT / "data" / "raw" / "satellite"
        self.assertTrue(raw_sat.is_dir(), "Raw satellite directory must exist")
        tiffs = list(raw_sat.glob("*.tif"))
        self.assertGreaterEqual(len(tiffs), 4, f"Expected at least 4 raw GeoTIFFs, found {len(tiffs)}")

    def test_09_stress_grid_map_renders(self):
        """Test 9: Confirm 1 km stress grid map figure generates cleanly with installed Plotly."""
        import plotly.express as px
        grid = load_stress_grid()
        explain = load_stress_explainability()
        self.assertEqual(len(grid), 6902)
        
        # Test map generation logic directly without Streamlit UI display
        df_plot = grid.merge(explain[["cell_id", "stress_quartile", "rank"]], on="cell_id", how="left")
        
        common_kwargs = dict(
            lat="lat",
            lon="lon",
            color="stress_quartile",
            zoom=8.5,
            center=dict(lat=13.25, lon=79.05),
            title="Decadal Relative Environmental Stress Indicator (1 km Grid, N = 6,902)",
        )
        
        fig = px.scatter_map(df_plot, map_style="carto-positron", **common_kwargs)
        self.assertIsNotNone(fig)
        self.assertIn("map", fig.layout)


    def test_10_ols_trendlines_render(self):
        """Test 10: Confirm OLS trendlines render for statistical associations using statsmodels."""
        import plotly.express as px
        master = load_master_timeseries()
        for pair in [("built_up_km2", "LST_C"), ("NDVI", "LST_C"), ("rainfall_mm", "NDVI")]:
            fig = px.scatter(
                master,
                x=pair[0],
                y=pair[1],
                trendline="ols",
                title=f"Test {pair[0]} vs {pair[1]}"
            )
            self.assertIsNotNone(fig)
            # Verify trendline trace exists in figure data
            trendline_traces = [t for t in fig.data if "mode" in t and "lines" in t.mode]
            self.assertGreater(len(trendline_traces), 0, f"Expected OLS trendline trace for {pair}")


    def test_11_location_enrichment_integrity(self):
        """Test 11: Confirm location enrichment correctly assigns mandals and coordinates without modifying scientific data."""
        grid = load_stress_grid()
        top100 = load_top_100_hotspots()

        # 1. Row count and coordinates preserved
        self.assertEqual(len(grid), 6902)
        self.assertIn("latitude", grid.columns)
        self.assertIn("longitude", grid.columns)
        self.assertIn("mandal", grid.columns)

        # 2. Zero missing mandals across all 6,902 cells
        self.assertEqual(grid["mandal"].isnull().sum(), 0)

        # 3. Specific user test cases verified
        c_47_43 = grid[grid["cell_id"] == "C_047_043"]
        self.assertFalse(c_47_43.empty)
        self.assertEqual(c_47_43.iloc[0]["mandal"], "Punganur")
        self.assertAlmostEqual(float(c_47_43.iloc[0]["stress_score"]), 0.5967, places=4)

        c_42_68 = grid[grid["cell_id"] == "C_042_068"]
        self.assertFalse(c_42_68.empty)
        self.assertEqual(c_42_68.iloc[0]["mandal"], "Somala")
        self.assertAlmostEqual(float(c_42_68.iloc[0]["stress_score"]), 0.5953, places=4)

        c_52_166 = grid[grid["cell_id"] == "C_052_166"]
        self.assertFalse(c_52_166.empty)
        self.assertEqual(c_52_166.iloc[0]["mandal"], "Vijayapuram")
        self.assertAlmostEqual(float(c_52_166.iloc[0]["stress_score"]), 0.6771, places=4)

        # 4. Top 100 Hotspots location columns
        self.assertEqual(len(top100), 100)
        self.assertIn("mandal", top100.columns)
        self.assertIn("latitude", top100.columns)
        self.assertIn("longitude", top100.columns)
        self.assertEqual(top100["mandal"].isnull().sum(), 0)
        self.assertEqual(top100.iloc[0]["cell_id"], "C_052_166")
        self.assertEqual(top100.iloc[0]["mandal"], "Vijayapuram")

    def test_12_forecast_validation_table_loads(self):
        """Test 12: Walk-forward backtesting table loads with valid out-of-sample error records."""
        df_val = load_forecast_validation()
        self.assertIsNotNone(df_val)
        self.assertGreaterEqual(len(df_val), 8)
        self.assertIn("prediction_year", df_val.columns)
        self.assertIn("actual", df_val.columns)
        self.assertIn("forecast", df_val.columns)
        self.assertIn("error", df_val.columns)
        self.assertIn("baseline_forecast", df_val.columns)

    def test_13_model_comparison_table_loads(self):
        """Test 13: Candidate model comparison table benchmarks models across multiple targets."""
        df_comp = load_model_comparison()
        self.assertIsNotNone(df_comp)
        self.assertGreaterEqual(len(df_comp), 10)
        self.assertIn("target", df_comp.columns)
        self.assertIn("model", df_comp.columns)
        self.assertIn("mae", df_comp.columns)
        self.assertIn("improvement_mae_pct", df_comp.columns)
        
        # Check OLS is superior to baseline for built-up
        bu_ols = df_comp[(df_comp["target"].str.contains("Built-Up Area", case=False)) & (df_comp["model"].str.contains("OLS Linear", case=False))]
        self.assertFalse(bu_ols.empty)
        self.assertGreater(float(bu_ols.iloc[0]["improvement_mae_pct"]), 0.0)

    def test_14_feasibility_matrix_loads(self):
        """Test 14: Systematic prediction feasibility matrix documents scientific claim limits."""
        df_feas = load_feasibility_matrix()
        self.assertIsNotNone(df_feas)
        self.assertGreaterEqual(len(df_feas), 5)
        self.assertIn("target", df_feas.columns)
        self.assertIn("ML_possible", df_feas.columns)
        self.assertIn("deep_learning_possible", df_feas.columns)
        self.assertIn("justification", df_feas.columns)

    def test_15_spatial_validation_and_sensitivity_loads(self):
        """Test 15: Spatial statistical validation (Moran's I) and sensitivity tables load."""
        df_sp = load_spatial_validation()
        self.assertIsNotNone(df_sp)
        moran = df_sp[df_sp["spatial_autocorrelation"].str.contains("Moran", case=False, na=False)]
        self.assertFalse(moran.empty)
        
        df_sens = load_stress_sensitivity()
        self.assertIsNotNone(df_sens)
        self.assertGreaterEqual(len(df_sens), 4)
        self.assertIn("correlation_with_primary", df_sens.columns)


if __name__ == "__main__":
    unittest.main()



