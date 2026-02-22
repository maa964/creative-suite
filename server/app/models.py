# server/app/models.py
"""Pydantic models for Plugin Store API."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PluginManifest(BaseModel):
    """Plugin manifest schema."""
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+")
    description: Optional[str] = None
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    dependencies: Optional[List[str]] = None
    commands: Optional[List[str]] = None
    hash: Optional[str] = None
    signature: Optional[str] = None


class PluginInfo(BaseModel):
    """Plugin information for listing."""
    name: str
    version: str
    approved: bool = False
    hash: Optional[str] = None
    uploaded_by: Optional[str] = None
    approved_by: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None


class PluginUploadResponse(BaseModel):
    """Response for plugin upload."""
    ok: bool
    name: str
    version: str
    hash: str


class PluginApproveResponse(BaseModel):
    """Response for plugin approval."""
    ok: bool
    signature: Optional[str] = None
    reason: Optional[str] = None


class StoreStats(BaseModel):
    """Plugin store statistics."""
    total_plugins: int
    approved_plugins: int
    pending_plugins: int
    storage_bytes: int
    storage_mb: float


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    storage_path: str
    storage_exists: bool
