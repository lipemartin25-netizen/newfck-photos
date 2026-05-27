"""
Upload validation and image processing utilities.
Handles file validation (extension, size, magic bytes, decodability).
"""
import io
import logging
from typing import Tuple
from PIL import Image

from app.models.errors import InvalidUploadError
from app.core.config import MAX_UPLOAD_SIZE, MIN_CROP_SIZE

logger = logging.getLogger("albumai.upload")

# Allowed extensions and their MIME magic bytes
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"}
MAGIC_BYTES = {
    b"\xff\xd8\xff": "jpeg",      # JPEG: FF D8 FF
    b"\x89PNG": "png",             # PNG: 89 50 4E 47
    b"II*\x00": "tiff",            # TIFF (little-endian): 49 49 2A 00
    b"MM\x00*": "tiff",            # TIFF (big-endian): 4D 4D 00 2A
    b"RIFF": "webp",               # WEBP: 52 49 46 46 (RIFF header)
}


def validate_upload_file(filename: str, file_bytes: bytes) -> None:
    """
    Validate uploaded file (extension, size, magic bytes, decodability).
    Raises InvalidUploadError if validation fails.
    
    Args:
        filename: Original filename
        file_bytes: File content as bytes
        
    Raises:
        InvalidUploadError: If any validation check fails
    """
    # 1. Check extension
    name_lower = filename.lower()
    ext = next((e for e in ALLOWED_EXTENSIONS if name_lower.endswith(e)), None)
    if not ext:
        raise InvalidUploadError(
            f"Unsupported file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 2. Check file size
    file_size = len(file_bytes)
    if file_size == 0:
        raise InvalidUploadError("File is empty.")
    if file_size > MAX_UPLOAD_SIZE:
        raise InvalidUploadError(
            f"File exceeds maximum size ({MAX_UPLOAD_SIZE} bytes)."
        )
    
    # 3. Check magic bytes
    has_valid_magic = any(
        file_bytes.startswith(magic) for magic in MAGIC_BYTES.keys()
    )
    if not has_valid_magic:
        raise InvalidUploadError(
            "File magic bytes do not match allowed image formats."
        )
    
    # 4. Check WEBP: verify WEBP-specific header
    if file_bytes.startswith(b"RIFF"):
        if len(file_bytes) < 12 or file_bytes[8:12] != b"WEBP":
            raise InvalidUploadError(
                "RIFF file does not have WEBP format indicator."
            )
    
    # 5. Verify image can be decoded
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verify integrity without fully loading
        logger.info(f"✓ File validated: {filename} ({file_size} bytes, {image.format})")
    except Exception as e:
        raise InvalidUploadError(
            f"File is corrupted or cannot be decoded: {str(e)}"
        )


def open_image_from_bytes(file_bytes: bytes) -> Image.Image:
    """
    Open and convert image to RGB.
    Raises InvalidUploadError if image cannot be decoded or converted.
    
    Args:
        file_bytes: File content as bytes
        
    Returns:
        PIL Image in RGB mode
        
    Raises:
        InvalidUploadError: If image cannot be decoded or converted
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Convert to RGB (handles RGBA, grayscale, palette, etc.)
        if image.mode != "RGB":
            image = image.convert("RGB")
        logger.info(f"✓ Image opened and converted to RGB: {image.size}")
        return image
    except Exception as e:
        raise InvalidUploadError(
            f"Failed to decode image: {str(e)}"
        )


def get_image_metadata(image: Image.Image) -> dict:
    """
    Extract metadata from PIL Image.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary with image metadata
    """
    return {
        "width": image.width,
        "height": image.height,
        "format": image.format,
        "mode": image.mode,
        "size_kb": (image.tobytes().__sizeof__()) / 1024,
    }
