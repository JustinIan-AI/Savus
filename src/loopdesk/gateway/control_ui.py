"""Modern LoopDesk WebUI route factory — serves the React SPA from frontend/dist."""

from __future__ import annotations

import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import FileResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from loopdesk.gateway.config import GatewayConfig

_FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"
_DIST_DIR = _FRONTEND_DIR / "dist"
_ASSETS_DIR = _DIST_DIR / "assets"
_INDEX_HTML = _DIST_DIR / "index.html"

_STATIC_CACHE_CONTROL = "public, max-age=2592000"


class _CachedStaticFiles(StaticFiles):
    """StaticFiles subclass that attaches Cache-Control to 200 responses."""

    async def get_response(self, path: str, scope):  # type: ignore[override]
        response = await super().get_response(path, scope)
        if response.status_code == 200 and not os.environ.get(
            "LOOPDESK_STATIC_NO_CACHE"
        ):
            response.headers.setdefault("Cache-Control", _STATIC_CACHE_CONTROL)
        return response


def create_control_ui_routes(config: GatewayConfig) -> list[Route | Mount]:
    """Create routes for the LoopDesk WebUI (React SPA)."""
    if not config.control_ui.enabled:
        return []

    if not _INDEX_HTML.is_file():
        return []

    async def serve_spa_index(request: Request) -> Response:
        return FileResponse(_INDEX_HTML)

    routes: list[Route | Mount] = []

    # Mount assets directory
    if _ASSETS_DIR.is_dir():
        routes.append(
            Mount(
                "/assets",
                app=_CachedStaticFiles(directory=str(_ASSETS_DIR)),
                name="spa_assets",
            )
        )

    # Base path routes for SPA fallback
    base = config.control_ui.base_path.rstrip("/")
    if base and base != "":
        routes.append(Route(f"{base}", serve_spa_index, methods=["GET"]))
        routes.append(Route(f"{base}/", serve_spa_index, methods=["GET"]))
        routes.append(Route(f"{base}/{{path:path}}", serve_spa_index, methods=["GET"]))

    # Also root SPA route
    routes.append(Route("/", serve_spa_index, methods=["GET"]))

    return routes
