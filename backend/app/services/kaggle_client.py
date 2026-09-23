from __future__ import annotations

from typing import Any
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class KaggleClient:
    """Client for the EarthDial inference server running on Kaggle."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (
            base_url or os.getenv("KAGGLE_NGROK_URL", "")
        ).rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self.base_url)

    async def health(self) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError(
                "KAGGLE_NGROK_URL is not configured yet."
            )

        headers = {
            "ngrok-skip-browser-warning": "true"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/health",
                headers=headers,
            )

            response.raise_for_status()
            return response.json()

    async def infer(
        self,
        file_path: str,
        query: str,
    ) -> dict[str, Any]:

        if not self.configured:
            raise RuntimeError(
                "KAGGLE_NGROK_URL is not configured yet."
            )

        headers = {
            "ngrok-skip-browser-warning": "true"
        }

        with open(file_path, "rb") as image_file:

            files = {
                "file": (
                    os.path.basename(file_path),
                    image_file,
                    "image/tiff",
                )
            }

            data = {
                "query": query
            }

            async with httpx.AsyncClient(
                timeout=120.0
            ) as client:

                response = await client.post(
                    f"{self.base_url}/infer",
                    files=files,
                    data=data,
                    headers=headers,
                )

                response.raise_for_status()

                return response.json()