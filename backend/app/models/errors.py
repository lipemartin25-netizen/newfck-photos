"""
Error models and custom exceptions for AlbumAI Studio.
Centralizes all error handling, codes and responses.
"""
from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Standard error response sent to client."""
    error: str          # error code: "INVALID_FILE", "FILE_TOO_LARGE", etc.
    message: str        # human-readable message
    detail: Optional[dict] = None  # optional context


class DetectorUnavailableError(Exception):
    """Raised when PhotoDetector cannot be loaded or initialized."""
    pass


class InvalidUploadError(Exception):
    """Raised when upload validation fails."""
    pass


# Error codes and default messages
ERROR_CODES = {
    "INVALID_FILE": {"status": 400, "message": "File is invalid or corrupted."},
    "UNSUPPORTED_MEDIA_TYPE": {"status": 415, "message": "File type not supported."},
    "FILE_TOO_LARGE": {"status": 413, "message": "File exceeds maximum size."},
    "IMAGE_NOT_FOUND": {"status": 404, "message": "Image not found in cache."},
    "DETECTOR_UNAVAILABLE": {"status": 501, "message": "Photo detector unavailable."},
    "INTERNAL_ERROR": {"status": 500, "message": "Internal server error."},
}
