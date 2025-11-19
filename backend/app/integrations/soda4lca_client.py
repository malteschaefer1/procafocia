"""Client for interacting with soda4LCA to fetch LCI datasets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx

from ..core.config import get_settings


class Soda4LCAError(RuntimeError):
    """Raised when soda4LCA interactions fail."""


class Soda4LCAClient:
    """Fetches and caches datasets from soda4LCA.

    soda4LCA generally exposes ILCD-formatted datasets through a REST-like API.
    This client downloads a dataset once, stores it on disk, and returns a
    reference that Brightway (or other importers) can consume later.
    """

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        cache_dir: str | Path | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.soda4lca_base_url or None
        self.username = username or settings.soda4lca_username
        self.password = password or settings.soda4lca_password
        self.cache_dir = Path(cache_dir or settings.soda4lca_cache_dir).resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._client = httpx.Client(timeout=30)

    def ensure_dataset_cached(self, provider: str, dataset_id: str) -> Path:
        """Return path to cached dataset, downloading it if necessary."""

        cache_path = self._cache_path(provider, dataset_id)
        if cache_path.exists():
            return cache_path
        if not self.base_url:
            raise Soda4LCAError("soda4LCA base URL not configured; cannot fetch datasets")
        response_body = self._request_dataset(dataset_id)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(response_body)
        return cache_path

    def build_brightway_reference(self, provider: str, dataset_id: str) -> dict:
        cache_path = self.ensure_dataset_cached(provider, dataset_id)
        return {
            "database": f"soda4lca:{provider.lower()}",
            "code": dataset_id,
            "source": "soda4lca",
            "cache_path": str(cache_path),
        }

    # Internal helpers
    def _cache_path(self, provider: str, dataset_id: str) -> Path:
        safe_provider = provider.replace("/", "_")
        safe_dataset = dataset_id.replace("/", "_")
        return self.cache_dir / safe_provider / f"{safe_dataset}.ilcd.json"

    def _request_dataset(self, dataset_id: str) -> str:
        url = self._dataset_url(dataset_id)
        headers = {"Accept": "application/json"}
        auth = None
        if self.username and self.password:
            auth = (self.username, self.password)
        try:
            response = self._client.get(url, headers=headers, auth=auth)
            response.raise_for_status()
        except Exception as exc:  # broad to wrap httpx errors
            raise Soda4LCAError(f"Failed to download dataset {dataset_id} from soda4LCA: {exc}") from exc
        content_type = response.headers.get("content-type", "")
        if "json" in content_type.lower():
            return response.text
        return json.dumps({"dataset_id": dataset_id, "raw": response.text})

    def _dataset_url(self, dataset_id: str) -> str:
        # soda4LCA often exposes datasets under /rest/datasets/{id}?format=ILCD
        return f"{self.base_url.rstrip('/')}/rest/datasets/{dataset_id}"


def get_soda_client() -> Soda4LCAClient | None:
    settings = get_settings()
    if not settings.soda4lca_base_url:
        return None
    return Soda4LCAClient()
