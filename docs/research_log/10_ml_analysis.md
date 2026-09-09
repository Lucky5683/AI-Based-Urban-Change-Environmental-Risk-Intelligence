# Machine Learning & Predictive Modeling Log

**Study Region:** Chittoor District, Andhra Pradesh, India  
**Stage:** Predictive Modeling / Forecasting Feasibility Assessment  
**Status:** COMPLETE / FEASIBILITY ASSESSMENT PASSED  
**Primary Research Log:** See [docs/research_log/12_prediction_feasibility.md](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/docs/research_log/12_prediction_feasibility.md)

## Summary of Feasibility Assessment & Governance Protocol
In strict adherence to the project principle **"DO NOT TRAIN A MODEL JUST TO CLAIM 'AI'"**, a comprehensive feasibility assessment was conducted across all candidate targets.

### Target Classification Summary:
1. **Category A — FORECASTING RECOMMENDED:**
   - Total Built-Up Area (`built_up_km2`) and Strong Built-Up Core (`strong_built_up_km2`): Monotonic secular growth ($R^2 = 0.960, p < 10^{-6}$), high physical inertia, walk-forward out-of-sample MAE $= 8.07\text{ km}^2$ ($+44.1\%$ error reduction over naive baseline). Conservative 1-year ahead forecast (2026) supported with 95% prediction intervals.
2. **Category B — FORECASTING POSSIBLE BUT HIGH UNCERTAINTY:**
   - Annual NDVI (`NDVI`): Non-monotonic climate-driven oscillations; linear trend performs $-24.1\%$ worse than naive persistence; 95% prediction interval covers almost the entire historical dynamic range. Retained as observational monitoring indicator.
3. **Category C — FORECASTING NOT SCIENTIFICALLY DEFENSIBLE / NOT CURRENTLY FEASIBLE:**
   - Daytime LST (`LST_C`): Confounded by synoptic weather, humidity, and cloud masking.
   - Annual Rainfall (`rainfall_mm`): Chaotic atmospheric driver; $N=10$ provides near-zero predictive capacity.
   - Decadal Spatial Environmental Stress (1 km Grid): Effective temporal sample size $N=1$ ($2016 \rightarrow 2025$ delta). Spatial cells are not temporal replicates.
   - Sentinel-2 Image Prediction: Two temporal states ($N=2$) do not permit deep generative model training.

For complete walk-forward validation tables, prediction interval equations, diagnostic figures, and scientific justification, refer to [12_prediction_feasibility.md](file:///c:/DK/Chittoor/AI-Based-Urban-Change-Environmental-Risk-Intelligence/docs/research_log/12_prediction_feasibility.md).

