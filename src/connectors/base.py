from __future__ import annotations
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class ERPClient:
    """HTTP client base para ambos ERP. Autenticacion por Bearer token por defecto."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get(self, path: str, params: dict | None = None) -> dict:
        r = self._client.get(path, params=params)
        r.raise_for_status()
        return r.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
