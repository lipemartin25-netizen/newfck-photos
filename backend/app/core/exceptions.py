"""
Exception handlers for FastAPI app.
Centralizes error response formatting.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.models.errors import ErrorResponse, ERROR_CODES, DetectorUnavailableError, InvalidUploadError

logger = logging.getLogger("albumai.exceptions")


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(DetectorUnavailableError)
    async def detector_unavailable_handler(request: Request, exc: DetectorUnavailableError):
        """Handle detector unavailable."""
        error_info = ERROR_CODES["DETECTOR_UNAVAILABLE"]
        response = ErrorResponse(
            error="DETECTOR_UNAVAILABLE",
            message=error_info["message"],
            detail={"reason": str(exc)}
        )
        logger.warning(f"Detector unavailable: {exc}")
        return JSONResponse(
            status_code=error_info["status"],
            content=response.model_dump()
        )

    @app.exception_handler(InvalidUploadError)
    async def invalid_upload_handler(request: Request, exc: InvalidUploadError):
        """Handle invalid upload."""
        error_info = ERROR_CODES["INVALID_FILE"]
        response = ErrorResponse(
            error="INVALID_FILE",
            message=error_info["message"],
            detail={"reason": str(exc)}
        )
        logger.warning(f"Invalid upload: {exc}")
        return JSONResponse(
            status_code=error_info["status"],
            content=response.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        error_info = ERROR_CODES["INVALID_FILE"]
        response = ErrorResponse(
            error="INVALID_FILE",
            message="Request validation failed.",
            detail={"errors": exc.errors()}
        )
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=error_info["status"],
            content=response.model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors — no stacktrace to client."""
        error_info = ERROR_CODES["INTERNAL_ERROR"]
        response = ErrorResponse(
            error="INTERNAL_ERROR",
            message=error_info["message"]
        )
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=error_info["status"],
            content=response.model_dump()
        )
