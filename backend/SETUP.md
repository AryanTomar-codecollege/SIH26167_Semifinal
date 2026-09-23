# SatQuery AI Backend — Local Setup

## Requirements
- Windows/macOS/Linux
- Python 3.11
- Git

The project intentionally does **not** ship a virtual environment. A venv contains machine-specific binaries and should be created locally from the pinned `requirements.txt`.

## Windows PowerShell

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## Test
Use a `.tif` or `.tiff` GeoTIFF. The API accepts one or two files.

For a first test:
- upload `sample.tif`
- query: `What does this image show?`
- task_hint: `auto`

The current project deliberately leaves EarthDial disconnected. The API proves file validation, GeoTIFF metadata extraction, overlap checks, and deterministic LangChain-compatible routing first.

## Git safety
`.env`, `.venv`, `test_data`, and LoRA adapter files are ignored. Do not commit model weights or private keys.
