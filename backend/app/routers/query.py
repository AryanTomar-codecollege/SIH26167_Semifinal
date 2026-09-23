"""
POST /api/query — main SatQuery AI analysis endpoint.

Accepts 1–3 GeoTIFF files + a text query, validates inputs,
runs the agentic pipeline (orchestrator → tools → EarthDial),
and returns a structured JSON response.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.services.orchestrator import execute

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {".tif", ".tiff"}


def _error(status: int, message: str, code: str) -> JSONResponse:
    """Return a contract-compliant error response."""
    return JSONResponse(
        status_code=status,
        content={"success": False, "error": message, "error_code": code},
    )


@router.post("/query")
def query(
    files: List[UploadFile] = File(...),
    query: str = Form(...),
    task_hint: Optional[str] = Form("auto"),
):
    """
    Main SatQuery AI query endpoint.

    Accepts:
        - 1 to 3 GeoTIFF files
        - A text query
        - Optional task_hint: auto | vqa | grounding | change | caption | metadata | ndvi | flood

    Returns the locked API contract:
        success, answer, geojson, confidence, execution_trace, metadata
    """

    # -----------------------------------------------------------------
    # 1. Validate query
    # -----------------------------------------------------------------
    if not query or not query.strip():
        return _error(400, "Query cannot be empty.", "EMPTY_QUERY")

    clean_query = query.strip()

    # -----------------------------------------------------------------
    # 2. Validate file count
    # -----------------------------------------------------------------
    if not files:
        return _error(400, "At least one GeoTIFF file is required.", "NO_FILES")

    if len(files) > 3:
        return _error(400, "A maximum of 3 files can be uploaded.", "TOO_MANY_FILES")

    # -----------------------------------------------------------------
    # 3. Validate extensions and read file bytes
    # -----------------------------------------------------------------
    prepared = []

    for uploaded_file in files:
        filename = uploaded_file.filename or ""
        if not filename:
            return _error(400, "One of the uploaded files has no filename.", "INVALID_FORMAT")

        ext = ""
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return _error(
                400,
                f"Invalid file '{filename}'. Only .tif and .tiff files are supported.",
                "INVALID_FORMAT",
            )

        # Read the entire file into memory for the orchestrator
        content_bytes = uploaded_file.file.read()
        if not content_bytes:
            return _error(400, f"File '{filename}' is empty.", "INVALID_FORMAT")

        prepared.append((filename, content_bytes, uploaded_file.content_type))

    logger.info(
        "Query received: %d file(s), hint=%s, query=%s",
        len(prepared),
        task_hint,
        clean_query[:120],
    )

    # -----------------------------------------------------------------
    # 4. Run the orchestrator pipeline
    # -----------------------------------------------------------------
    try:
        result = execute(clean_query, prepared, task_hint=task_hint)
    except Exception as exc:
        logger.exception("Pipeline failed for query: %s", clean_query[:200])
        error_msg = str(exc)

        # Map exception to a meaningful error code
        error_code = "INFERENCE_FAILED"
        lower = error_msg.lower()
        if "not configured" in lower or "kaggle_ngrok_url" in lower:
            error_code = "EARTHDIAL_UNAVAILABLE"
        elif "health" in lower or "unreachable" in lower:
            error_code = "EARTHDIAL_UNAVAILABLE"
        elif "timeout" in lower or "timed out" in lower:
            error_code = "INFERENCE_TIMEOUT"
        elif "multi_endpoint_not_available" in lower:
            error_code = "MULTI_ENDPOINT_UNAVAILABLE"

        return _error(
            502,
            f"Analysis failed: {error_msg[:500]}",
            error_code,
        )

    # -----------------------------------------------------------------
    # 5. Normalize response to match the API contract
    # -----------------------------------------------------------------
    geojson = result.get("geojson")
    if not geojson or not isinstance(geojson, dict):
        geojson = {"type": "FeatureCollection", "features": []}

    # Extract confidence from raw EarthDial response if available
    raw = result.get("raw", {})
    confidence = None
    if isinstance(raw, dict):
        earthdial_data = raw.get("earthdial")
        if isinstance(earthdial_data, dict):
            confidence = earthdial_data.get("confidence")

    # Detect whether EarthDial was actually invoked
    tool_name = result.get("tool", "unknown")
    model_used = None
    if isinstance(raw, dict) and raw.get("earthdial"):
        model_used = "EarthDial_4B_MS"

    response = {
        "success": True,
        "answer": result.get("answer", "Analysis completed."),
        "geojson": geojson,
        "confidence": confidence,
        "execution_trace": result.get("execution_trace", []),
        "metadata": result.get("metadata", {}),
        "tool": tool_name,
        "model_used": model_used,
    }

    logger.info("Query completed: tool=%s, model=%s", tool_name, model_used)
    return response