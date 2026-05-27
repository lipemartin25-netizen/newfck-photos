"""
retouch.py — Endpoints for color revitalization and presets.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io
from app.core.state import _images

router = APIRouter(prefix="/api/retouch", tags=["retouch"])


class AutoRevitalizeRequest(BaseModel):
    image_id: str
    strength: float = Field(1.0, ge=0.0, le=2.0)


class ManualAdjustRequest(BaseModel):
    image_id: str
    brightness: float = Field(0.0, ge=-50.0, le=50.0)
    contrast: float = Field(0.0, ge=-50.0, le=50.0)
    saturation: float = Field(0.0, ge=-50.0, le=50.0)
    yellow_cast: float = Field(0.0, ge=0.0, le=100.0)


@router.post("/revitalize")
async def revitalize(req: AutoRevitalizeRequest):
    if req.image_id not in _images:
        raise HTTPException(404, "Image not found.")
        
    from app.services.retoucher import PhotoRetoucher
    retoucher = PhotoRetoucher()
    
    img = _images[req.image_id]["image"]
    revitalized = retoucher.revitalize_colors(img, req.strength)
    
    buf = io.BytesIO()
    revitalized.save(buf, "JPEG", quality=95)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/jpeg")


@router.post("/manual")
async def manual_retouch(req: ManualAdjustRequest):
    if req.image_id not in _images:
        raise HTTPException(404, "Image not found.")
        
    from app.services.retoucher import PhotoRetoucher
    retoucher = PhotoRetoucher()
    
    img = _images[req.image_id]["image"]
    
    # Adjust channels
    adjusted = retoucher.adjust_manual(img, req.brightness, req.contrast, req.saturation)
    if req.yellow_cast > 0:
        adjusted = retoucher.remove_yellow_cast(adjusted, req.yellow_cast / 100.0)
        
    buf = io.BytesIO()
    adjusted.save(buf, "JPEG", quality=95)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/jpeg")
