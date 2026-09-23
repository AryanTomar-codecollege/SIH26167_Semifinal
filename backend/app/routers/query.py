from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.models.schemas import ErrorResponse, SuccessResponse
from app.services.agent import agent
from app.services.geospatial import extract_metadata, images_overlap, validate_geotiff_path
from app.tools import change_tool, grounding_tool, metadata_tool, optical_sar_tool, vqa_tool

router = APIRouter()


@router.post(
    "/api/query",
    response_model=SuccessResponse | ErrorResponse,
)
async def query_endpoint(
    files: List[UploadFile] = File(...),
    query: str = Form(...),
    task_hint: Optional[str] = Form("auto"),
):
    if len(files) not in (1, 2):
        return ErrorResponse(
            error="Exactly 1 or 2 GeoTIFF files are required.",
            error_code="INVALID_FILE_COUNT",
        )

    temp_paths: list[Path] = []
    try:
        for upload in files:
            suffix = Path(upload.filename or "").suffix.lower()
            if suffix not in {".tif", ".tiff"}:
                return ErrorResponse(
                    error="Only GeoTIFF files (.tif or .tiff) are supported.",
                    error_code="INVALID_FILE_TYPE",
                )

            data = await upload.read()
            if not data:
                return ErrorResponse(
                    error="An uploaded file is empty.",
                    error_code="EMPTY_FILE",
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(data)
                temp_paths.append(Path(tmp.name))

        for path in temp_paths:
            validate_geotiff_path(str(path))

        metadata = [extract_metadata(str(path)) for path in temp_paths]

        if len(temp_paths) == 2 and not images_overlap(str(temp_paths[0]), str(temp_paths[1])):
            return ErrorResponse(
                error="The two images do not cover the same geographic area",
                error_code="GEOGRAPHIC_MISMATCH",
            )

        modalities = ["optical"] * len(temp_paths)
        if (task_hint or "auto") == "optical_sar" and len(temp_paths) == 2:
            modalities = ["optical", "sar"]
        decision = agent.route(query, len(temp_paths), modalities, task_hint or "auto")

        if decision.task == "metadata":
            md = metadata_tool.run(str(temp_paths[0]))
            result = {
                "answer": f"The image is {md['width']} x {md['height']} pixels with {md['band_count']} band(s) in {md['crs']}.",
                "confidence": 1.0,
                "pixel_boxes": [],
                "model_used": "local_metadata",
            }
        elif decision.task == "grounding":
            result = grounding_tool.run(query)
        elif decision.task == "change_detection":
            result = change_tool.run(query)
        elif decision.task == "optical_sar":
            result = optical_sar_tool.run(query)
        else:
            result = vqa_tool.run(query)

        return SuccessResponse(
            answer=result["answer"],
            geojson={"type": "FeatureCollection", "features": []},
            confidence=result["confidence"],
            execution_trace={
                "selected_task": decision.task,
                "tools_used": [decision.tool_name],
                "model_used": result["model_used"],
                "parameters": {
                    "task_hint": task_hint or "auto",
                    "image_metadata": metadata,
                },
            },
            metadata={
                "num_images": len(temp_paths),
                "modalities": modalities,
                "crs": metadata[0]["crs"],
            },
        )
    except ValueError as exc:
        return ErrorResponse(error=str(exc), error_code="INVALID_GEOTIFF")
    except Exception as exc:
        return ErrorResponse(error=f"Unexpected backend error: {exc}", error_code="INTERNAL_ERROR")
    finally:
        for path in temp_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
