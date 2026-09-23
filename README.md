# SatQuery AI — SIH 26167

Student-built prototype for **SatQuery AI: An Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Text Queries**.

## What is included

- `backend/` — FastAPI + Rasterio + Shapely/GeoPandas + LangChain-compatible routing.
- `frontend/` — React + Vite + Leaflet interface.
- EarthDial/Kaggle integration is **scaffolded but intentionally disabled** in this version.
- LoRA is represented by configuration (`USE_LORA`) and an adapter path, but no training or model weights are included.

## Backend plan preserved

The backend follows the locked structure and API contract:

`POST /api/query` → validation → geospatial metadata/overlap → tool routing → structured response.

The current routing is deterministic because the LLM/EarthDial service has not been connected yet. This keeps the local project runnable without a GPU or API key. The router is isolated in `app/services/agent.py` so a real LangChain LLM agent can replace the deterministic decision layer later without changing the frontend contract.

## Important: do not copy a virtual environment

A Windows `.venv` contains machine-specific executables and compiled packages. It is intentionally **not shipped in this archive**. The setup commands create a clean Python 3.11 venv from the pinned `backend/requirements.txt`, which is the reliable way to avoid dependency conflicts.

## Quick start

### 1. Backend — Windows PowerShell

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Backend docs: http://127.0.0.1:8000/docs

### 2. Frontend — new terminal

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the local Vite URL printed in the terminal.

### 3. First test

Use the `sample.tif` file you already downloaded from the `mommermi/geotiff_sample` repository. Keep it under `backend/test_data/` locally. The project ignores `test_data/`, so the satellite file is not pushed to GitHub.

In the frontend:
- choose `sample.tif`
- ask: `What does this image show?`
- leave Task Hint as `Auto`
- click **Run analysis**

The request will reach FastAPI, validate the GeoTIFF, read its spatial metadata, route the query, and return a structured response. Because EarthDial is not connected, the answer will explicitly say that the model service is not connected yet.

## Later EarthDial integration

When the model work is ready:

1. Run `EarthDial_4B_MS` on Kaggle T4.
2. Expose the inference server through Ngrok.
3. Put the current Ngrok URL in `backend/.env` as `KAGGLE_NGROK_URL`.
4. Connect the relevant tools to `KaggleClient`.
5. Enable LoRA only after the adapter has been trained and tested.

The public EarthDial project provides the `EarthDial_4B_MS` checkpoint and documents its multimodal EO capabilities. The model repository is separate from this student project.

## Team architecture

```text
React + Leaflet
      |
      | POST /api/query
      v
FastAPI
  |-- validation
  |-- Rasterio / geospatial
  |-- LangChain tool router
  |-- VQA / grounding / change / optical-SAR tools
  `-- Kaggle client (future)
             |
             v
       EarthDial + LoRA (future)
```
