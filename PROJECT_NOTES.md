# Project notes

## Deliberate limitations in this build

- No EarthDial weights are bundled.
- No Kaggle runtime is required for the local demo.
- No LLM API key is required for the deterministic router.
- No `venv` is bundled; it is recreated locally from pinned dependencies.
- No `sample.tif` is bundled; keep the test file in `backend/test_data/` locally.

## Backend contract

Success responses use:
- success
- answer
- geojson
- confidence
- execution_trace
- metadata

Errors use:
- success
- error
- error_code

The frontend does not call Kaggle directly.
