from __future__ import annotations

from typing import Any

from app.services.kaggle_client import KaggleClient


async def run(
    filepath: str,
    query: str,
    modality: str = "optical",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    client = KaggleClient()

    result = await client.infer(
        file_path=filepath,
        query=query,
    )

    return {
        "answer": result.get(
            "answer",
            "EarthDial did not return an answer."
        ),
        "confidence": 0.0,
        "pixel_boxes": [],
        "model_used": result.get(
            "model",
            "EarthDial_4B_MS"
        ),
        "metadata": result,
    }