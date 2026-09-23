# SatQuery AI Backend — EarthDial + OmniRoute

This is the local FastAPI backend for the current working Kaggle EarthDial 4B MS service.

## Put the two keys/URLs in `.env`

```env
OMNIROUTE_BASE_URL=http://127.0.0.1:20128/v1
OMNIROUTE_API_KEY=PUT_YOUR_OMNIROUTE_ENDPOINT_KEY_HERE
OMNIROUTE_MODEL=auto
KAGGLE_NGROK_URL=PUT_CURRENT_KAGGLE_NGROK_URL_HERE
```

- Keep `NGROK_AUTHTOKEN` only in Kaggle Secrets.
- Keep `OMNIROUTE_API_KEY` only in the backend `.env`.
- Do not put either secret in React.

## Install/run

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Backend runs on `http://127.0.0.1:8001`.

## Main endpoint

`POST /api/query` accepts 1–3 GeoTIFF files plus a natural-language query.

The OmniRoute layer chooses one of:

- metadata
- VQA
- caption
- grounding
- compare
- change detection
- NDVI
- flood analysis

Then the selected tool uses EarthDial/Rasterio, and OmniRoute produces the final answer.

Grounding only returns GeoJSON when EarthDial actually emits parseable boxes; the backend never fabricates coordinates.

For 2–3 images, joint EarthDial change detection uses `/infer_multi` if that endpoint exists. With your current Kaggle cell, the backend automatically falls back to independent EarthDial analyses + OmniRoute comparison. See `docs/KAGGLE_CHANGES.md` for the minimal patch; `/infer` is not replaced.

The backend is intentionally LoRA-free.
