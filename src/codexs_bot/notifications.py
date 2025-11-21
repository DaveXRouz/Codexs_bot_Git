from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx


class WebhookNotifier:
    """Sends application/contact payloads to an external HTTP endpoint."""

    def __init__(self, url: Optional[str], token: Optional[str], label: str) -> None:
        self._url = url
        self._token = token
        self._label = label

    async def post(self, payload: Dict[str, Any]) -> None:
        if not self._url:
            return
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(self._url, json=payload, headers=headers)
        except Exception as exc:  # pylint: disable=broad-except
            logging.warning("Failed to send %s webhook: %s", self._label, exc)

