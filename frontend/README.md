# SatQuery AI Frontend

This frontend uses the supplied SatQuery UI as the visual reference and is integrated with the local FastAPI backend contract.

## Run

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The backend should be running at `http://127.0.0.1:8000`.

EarthDial is intentionally not connected in this stage.
