# server/app/main.py
"""Creative Studio Plugin Store API - Main application entry point."""

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
