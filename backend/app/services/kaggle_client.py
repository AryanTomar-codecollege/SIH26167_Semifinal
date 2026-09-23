from __future__ import annotations

from typing import Any

import httpx
from dotenv import load_dotenv
import os

load_dotenv()


class KaggleClient:
    """Small client for the future EarthDial inference server on Kaggle."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("KAGGLE_NGROK_URL", "")).rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self.base_url)

    async def infer(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("KAGGLE_NGROK_URL is not configured yet.")

        headers = {"ngrok-skip-browser-warning": "true"}
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/infer",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
