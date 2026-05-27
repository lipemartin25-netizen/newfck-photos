"""
Response formatters for crop and enhance endpoints.
Handles StreamingResponse creation for zip and image exports.
"""
import io
import logging
from typing import List
from zipfile import ZipFile
from PIL import Image
from fastapi.responses import StreamingResponse

logger = logging.getLogger("albumai.responses")


def create_zip_response(crops: List[Image.Image]) -> StreamingResponse:
    """
    Create a zip file containing cropped images.
    
    Args:
        crops: List of PIL Image objects (cropped photos)
        
    Returns:
        StreamingResponse with zip file download
    """
    # Create zip in memory
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zf:
        for idx, crop in enumerate(crops, 1):
            # Convert image to JPEG bytes
            img_buffer = io.BytesIO()
            crop.save(img_buffer, format="JPEG", quality=95)
            img_buffer.seek(0)
            # Add to zip with numbered filename
            zf.writestr(f"crop_{idx:03d}.jpg", img_buffer.getvalue())
    
    zip_buffer.seek(0)
    logger.info(f"✓ Created zip with {len(crops)} cropped images")
    
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=crops.zip"}
    )


def create_image_response(image: Image.Image, quality: int = 95) -> StreamingResponse:
    """
    Create a StreamingResponse for a single image (enhanced photo).
    
    Args:
        image: PIL Image object
        quality: JPEG quality (1-100, default 95)
        
    Returns:
        StreamingResponse with image download
    """
    # Convert image to JPEG bytes
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="JPEG", quality=quality)
    img_buffer.seek(0)
    
    logger.info(f"✓ Created image response (JPEG, quality={quality})")
    
    return StreamingResponse(
        iter([img_buffer.getvalue()]),
        media_type="image/jpeg",
        headers={"Content-Disposition": "attachment; filename=enhanced.jpg"}
    )


def create_health_response() -> dict:
    """Create health check response."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "api": "ok",
            "detector": "lazy-loaded",  # Will be loaded on first detect request
        }
    }
