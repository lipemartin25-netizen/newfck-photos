"""
Upload validation middleware.
Header-only validation (Content-Length, Content-Type) without consuming request body.
Body validation is delegated to upload_utils.py and endpoint dependencies.
"""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.errors import ErrorResponse, ERROR_CODES

logger = logging.getLogger("albumai.middleware")

# Allowed Content-Type headers
ALLOWED_CONTENT_TYPES = {
    "multipart/form-data",
    "application/octet-stream",
}

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


class UploadValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate uploads via headers only (Content-Length, Content-Type).
    Does NOT consume request body (prevents issues in FastAPI).
    Actual file validation happens in upload_utils.py.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Intercept and validate upload requests."""
        # Only validate upload endpoints
        if request.url.path == "/api/upload" and request.method == "POST":
            # Check Content-Length header
            content_length_header = request.headers.get("content-length")
            if content_length_header:
                try:
                    content_length = int(content_length_header)
                    if content_length > MAX_UPLOAD_SIZE:
                        error_info = ERROR_CODES["FILE_TOO_LARGE"]
                        response = ErrorResponse(
                            error="FILE_TOO_LARGE",
                            message=error_info["message"],
                            detail={"max_size": MAX_UPLOAD_SIZE, "received": content_length}
                        )
                        logger.warning(f"Upload rejected: file too large ({content_length} bytes)")
                        return JSONResponse(
                            status_code=error_info["status"],
                            content=response.model_dump()
                        )
                except ValueError:
                    logger.warning(f"Invalid Content-Length header: {content_length_header}")
            
            # Check Content-Type header
            content_type = request.headers.get("content-type", "").split(";")[0]
            if content_type and content_type not in ALLOWED_CONTENT_TYPES:
                error_info = ERROR_CODES["UNSUPPORTED_MEDIA_TYPE"]
                response = ErrorResponse(
                    error="UNSUPPORTED_MEDIA_TYPE",
                    message=error_info["message"],
                    detail={"received": content_type, "allowed": list(ALLOWED_CONTENT_TYPES)}
                )
                logger.warning(f"Upload rejected: unsupported content-type ({content_type})")
                return JSONResponse(
                    status_code=error_info["status"],
                    content=response.model_dump()
                )
        
        # Pass to next handler
        response = await call_next(request)
        return response

