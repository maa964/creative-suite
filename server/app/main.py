# server/app/main.py
"""Creative Studio Plugin Store API - Main application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .plugins import router as plugin_router
from .dashboard import router as dashboard_router

app = FastAPI(
    title="CreativeStudio Plugin Store API",
    description="API for managing Creative Suite plugins",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
# Set CS_STORE_CORS_ORIGINS env var (comma-separated) for production
# Example: CS_STORE_CORS_ORIGINS=https://example.com,https://app.example.com
_cors_origins_env = os.environ.get("CS_STORE_CORS_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _cors_origins_env.split(",") if o.strip()]
if not ALLOWED_ORIGINS:
    # Default: localhost only for development
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

# Include routers
app.include_router(auth_router)
app.include_router(plugin_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "CreativeStudio Plugin Store API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
