"""Pydantic schemas for API request/response validation."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    score: float = 0.0
    label: str = "photo"


class DetectionRequest(BaseModel):
    image_id: str
    text_prompt: str = "an old photo."
    confidence_threshold: float = Field(0.15, ge=0.01, le=1.0)
    box_threshold: float = Field(0.2, ge=0.01, le=1.0)
    text_threshold: float = Field(0.2, ge=0.01, le=1.0)
    remove_overlaps: bool = True
    overlap_threshold: float = Field(0.05, ge=0.0, le=1.0)


class DetectionResult(BaseModel):
    image_id: str
    width: int
    height: int
    boxes: List[BBox]
    count: int


class CropInfo(BaseModel):
    """Information about a single cropped photo."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    width: int
    height: int
    box: BBox


class CropResult(BaseModel):
    """Result of a crop operation."""
    image_id: str
    crops: List[CropInfo]
    total: int


class CropRequest(BaseModel):
    image_id: str
    boxes: List[BBox]
    auto_rotate: bool = False
    color_correct: bool = True
    enhance: bool = False
    enhance_scale: int = Field(2, ge=1, le=4)
    apply_exif_year: Optional[int] = None
    output_quality: int = Field(95, ge=1, le=100)


class EnhanceRequest(BaseModel):
    image_id: str
    scale: int = Field(2, ge=1, le=4)
    face_restore: bool = False


class UploadResult(BaseModel):
    id: str
    filename: str
    width: int
    height: int
    size_bytes: int


class HealthResponse(BaseModel):
    ok: bool = True
    device: str
    gpu: bool
    models_loaded: List[str] = []
    version: str = "1.0.0"


class JobProgress(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float = 0.0  # 0-100
    current_step: str = ""
    total_items: int = 0
    processed_items: int = 0
    errors: List[str] = []


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    code: int
