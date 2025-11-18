"""FastAPI entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_bom, routes_circularity, routes_mapping, routes_pcf, routes_products, routes_scenarios
from .core.config import get_settings
from .core.logging import configure_logging
from .db.init_db import init_db

configure_logging()
settings = get_settings()
init_db()
app = FastAPI(title="procafocia", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_products.router)
app.include_router(routes_bom.router)
app.include_router(routes_scenarios.router)
app.include_router(routes_pcf.router)
app.include_router(routes_circularity.router)
app.include_router(routes_mapping.router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
