# SatQuery AI — Backend

SIH 26167 backend foundation for an interactive remote-sensing assistant.

## Current scope
- FastAPI API contract
- GeoTIFF validation
- Rasterio metadata extraction
- EPSG:4326 bounds conversion
- Two-image geographic overlap check
- LangChain tool registry + deterministic router
- Fixed success/error response shapes
- EarthDial/Kaggle client scaffold (disabled until the model server exists)

## Not connected yet
EarthDial inference and LoRA are intentionally left out of the local run. The architecture keeps `kaggle_client.py` and `USE_LORA` ready for the later Phase 4 integration.
