"""Test modern React WebUI routes serving from frontend/dist."""

from __future__ import annotations

from pathlib import Path
from starlette.testclient import TestClient

from loopdesk.gateway.app import create_gateway_app
from loopdesk.gateway.config import GatewayConfig


def test_control_ui_serves_spa_index() -> None:
    config = GatewayConfig()
    app = create_gateway_app(config=config)
    client = TestClient(app, follow_redirects=False)

    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "<!doctype html>" in resp.text.lower()


def test_control_ui_serves_control_path_index() -> None:
    config = GatewayConfig()
    app = create_gateway_app(config=config)
    client = TestClient(app, follow_redirects=False)

    resp = client.get("/control")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_control_ui_serves_assets_with_cache_control() -> None:
    config = GatewayConfig()
    app = create_gateway_app(config=config)
    client = TestClient(app, follow_redirects=False)

    dist_assets = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "assets"
    asset_files = list(dist_assets.glob("*.js"))
    if asset_files:
        asset_name = asset_files[0].name
        resp = client.get(f"/assets/{asset_name}")
        assert resp.status_code == 200
        assert "max-age" in resp.headers.get("cache-control", "")
