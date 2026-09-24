from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import urllib.request
import urllib.error

class KnowledgeSourceAdapter(ABC):
    @abstractmethod
    def fetch_doc(self, doc_id: str) -> str:
        pass

class ConfluenceRestAdapter(KnowledgeSourceAdapter):
    def __init__(self, base_url: str, api_token: str = "", email: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.email = email

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = "Bearer " + self.api_token
        return headers

    def fetch_doc(self, doc_id: str) -> str:
        url = self.base_url + "/wiki/rest/api/content/" + doc_id + "?expand=body.storage"
        req = urllib.request.Request(url, headers=self._get_headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    body = data.get("body", {}).get("storage", {}).get("value", "")
                    title = data.get("title", "")
                    return "# " + title + chr(10) + chr(10) + body
        except Exception:
            return ""
        return ""
