"""LCI provider backed by soda4LCA (e.g., OEKOBAUDAT)."""
from __future__ import annotations

import logging
from typing import Optional

import httpx
from xml.etree import ElementTree as ET

from ..core.config import get_settings
from .lci_provider_base import LCIProcessCandidate, LCIProvider

LOGGER = logging.getLogger(__name__)


class Soda4LCAProvider:
    """Fetches process datasets from a soda4LCA node."""

    name = "soda4lca"

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.soda4lca_base_url or "https://www.oekobaudat.de/OEKOBAU.DAT/resource"
        configured_user = getattr(settings, "soda4lca_user", None) or settings.soda4lca_username
        configured_password = getattr(settings, "soda4lca_password", None)
        configured_token = getattr(settings, "soda4lca_token", None)
        self.username = username or configured_user
        self.password = password or configured_password
        self.token = token or configured_token
        self._client = client or httpx.Client(timeout=30)

    # -- LCIProvider implementation --------------------------------------------------
    def find_candidates(self, item) -> list[LCIProcessCandidate]:  # pragma: no cover - placeholder
        """Placeholder search implementation.

        TODO: implement name/classification search once the soda4LCA search API is
        documented. For now this provider is only used via get_process_by_uuid.
        """

        return []

    # -- Public helpers --------------------------------------------------------------
    def get_process_by_uuid(self, uuid: str, version: str | None = None) -> Optional[LCIProcessCandidate]:
        """Fetch a process dataset by UUID and map it to an LCIProcessCandidate."""

        if not uuid:
            return None
        try:
            xml_text = self._fetch_process(uuid, version)
        except httpx.HTTPError as exc:
            LOGGER.error("soda4LCA request failed for %s: %s", uuid, exc)
            return None
        except ValueError as exc:
            LOGGER.error("soda4LCA URL misconfigured: %s", exc)
            return None
        if not xml_text:
            return None
        try:
            candidate = self._parse_process(uuid, version, xml_text)
        except ET.ParseError as exc:
            LOGGER.error("Unable to parse soda4LCA ILCD dataset %s: %s", uuid, exc)
            return None
        return candidate

    # -- Internal helpers ------------------------------------------------------------
    def _fetch_process(self, uuid: str, version: str | None) -> str:
        url = self._process_url(uuid, version)
        headers = {"Accept": "application/xml"}
        auth = None
        if self.username and self.password:
            auth = (self.username, self.password)
        request_headers = headers
        if self.token and not auth:
            request_headers = {**headers, "Authorization": f"Bearer {self.token}"}
        response = self._client.get(url, auth=auth, headers=request_headers)
        response.raise_for_status()
        return response.text

    def _process_url(self, uuid: str, version: str | None) -> str:
        if not self.base_url:
            raise ValueError("Missing soda4LCA base URL")
        base = self.base_url.rstrip("/")
        url = f"{base}/processes/{uuid}"
        if version:
            url = f"{url}?version={version}"
        return url

    def _parse_process(self, uuid: str, version: str | None, xml_text: str) -> LCIProcessCandidate:
        root = ET.fromstring(xml_text)
        name = self._find_text(root, "baseName") or self._find_text(root, "name") or "soda4LCA process"
        description = self._find_text(root, "generalComment") or "ILCD dataset fetched from soda4LCA"
        reference_flow = self._find_text(root, "referenceFlow") or name
        location = self._find_text(root, "location")
        classification = self._find_text(root, "classification") or self._find_text(root, "class")
        metadata = {
            "reference_flow": reference_flow,
            "location": location or "",
            "classification": classification or "",
            "uuid": uuid,
        }
        brightway_ref = {
            "database": "soda4lca",
            "code": uuid if not version else f"{uuid}:{version}",
        }
        dataset_identifier = f"soda4lca:{uuid}" + (f"?version={version}" if version else "")
        return LCIProcessCandidate(
            provider=self.name,
            dataset_id=dataset_identifier,
            name=name,
            description=description,
            confidence_score=0.85,
            mapping_rule_id="soda4lca-direct",
            metadata=metadata,
            life_cycle_stage=None,
            brightway_reference=brightway_ref,
        )

    def _find_text(self, root: ET.Element, tag_suffix: str) -> str | None:
        for elem in root.iter():
            if elem.tag.endswith(tag_suffix):
                text = (elem.text or "").strip()
                if text:
                    return text
        return None
