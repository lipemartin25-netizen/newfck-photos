"""
rotation.py — Smart auto-rotation endpoints.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io
from app.core.state import _images

router = APIRouter(prefix="/api/rotate", tags=["rotation"])


class AutoRotateRequest(BaseModel):
    image_id: str


class ManualRotateRequest(BaseModel):
    image_id: str
    angle: int = Field(90, ge=0, le=270)  # 0, 90, 180, 270


@router.post("/auto")
async def auto_rotate_endpoint(req: AutoRotateRequest):
    if req.image_id not in _images:
        raise HTTPException(404, "Image not found.")
        
    from app.services.rotator import PhotoRotator
    rotator = PhotoRotator()
    
    img = _images[req.image_id]["image"]
    corrected, angle = rotator.auto_rotate(img)
    
    buf = io.BytesIO()
    corrected.save(buf, "JPEG", quality=95)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/jpeg", headers={"X-Rotated-Angle": str(angle)})


@router.post("/manual")
async def manual_rotate_endpoint(req: ManualRotateRequest):
    if req.image_id not in _images:
        raise HTTPException(404, "Image not found.")
        
    from app.services.rotator import PhotoRotator
    rotator = PhotoRotator()
    
    img = _images[req.image_id]["image"]
    rotated = rotator.rotate_angle(img, req.angle)
    
    buf = io.BytesIO()
    rotated.save(buf, "JPEG", quality=95)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/jpeg")
