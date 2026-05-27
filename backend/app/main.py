"""
AlbumAI Studio — FastAPI Backend.
Provides API for photo detection, cropping, enhancement and organization.
"""
import uuid
import io
import asyncio
import zipfile
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image

from app.core.config import (
    CORS_ORIGINS, DEVICE, UPLOADS_DIR, OUTPUT_DIR,
    DEFAULT_PROMPT, DEFAULT_CONFIDENCE, DEFAULT_OVERLAP, MIN_CROP_SIZE,
    LOG_LEVEL, MAX_UPLOAD_SIZE, ENABLE_ADVANCED_ROUTES
)
from app.models.schemas import (
    DetectionRequest, DetectionResult, BBox,
    CropRequest, EnhanceRequest, UploadResult, HealthResponse,
    ErrorResponse
)
from app.core.state import store_image, get_image, delete_image, periodic_cleanup

# New helper modules
from app.core.exceptions import register_exception_handlers
from app.core.upload_utils import validate_upload_file, open_image_from_bytes, get_image_metadata
from app.core.responses import create_zip_response, create_image_response, create_health_response
from app.services.image_pipeline import detect_photos, crop_photos, enhance_photo
from app.core.middleware import UploadValidationMiddleware

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
log = logging.getLogger("albumai")

# Allowed MIME types for upload (magic byte validation)
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/tiff", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"}

_detector = None


def _get_detector():
    global _detector
    if _detector is None:
        from app.services.detector import PhotoDetector
        _detector = PhotoDetector(device=DEVICE)
    return _detector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    log.info("AlbumAI Studio starting up...")
    # Start background cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup(3600))
    yield
    # Shutdown
    cleanup_task.cancel()
    log.info("AlbumAI Studio shutting down.")


app = FastAPI(
    title="AlbumAI Studio API",
    description="AI-powered photo detection, extraction, and enhancement",
    version="1.0.0",
    lifespan=lifespan,
)

# Register centralized exception handlers
register_exception_handlers(app)

# Upload header-only validation middleware (does not consume body)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Header-only upload validation (does not read body)
app.add_middleware(UploadValidationMiddleware)


# legacy validation removed — use app.core.upload_utils.validate_upload_file


# ========== HEALTH ==========

@app.get("/api/health", response_model=HealthResponse)
async def health():
    models = []
    if _detector is not None:
        models.append("grounding-dino")
    return HealthResponse(
        ok=True, device=DEVICE, gpu=DEVICE == "cuda",
        models_loaded=models,
    )


# ========== UPLOAD ==========

@app.post("/api/upload", response_model=list[UploadResult])
async def upload(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "No files provided.")

    results = []
    for f in files:
        data = await f.read()

        # Use centralized upload validation (raises InvalidUploadError)
        validate_upload_file(f.filename or "unknown", data)

        # Decode and normalize image
        img = open_image_from_bytes(data)

        img_id = str(uuid.uuid4())
        save_path = UPLOADS_DIR / f"{img_id}.jpg"
        img.save(str(save_path), "JPEG", quality=95)

        store_image(img_id, {
            "path": save_path,
            "image": img,
            "width": img.width,
            "height": img.height,
            "filename": f.filename or "upload.jpg",
        })

        results.append(UploadResult(
            id=img_id, filename=f.filename or "upload.jpg",
            width=img.width, height=img.height,
            size_bytes=len(data),
        ))

    log.info(f"Uploaded {len(results)} file(s)")
    return results


# ========== DETECTION ==========

@app.post("/api/detect", response_model=DetectionResult)
async def detect(req: DetectionRequest):
    info = get_image(req.image_id)
    if info is None:
        raise HTTPException(404, "Image not found. Upload first.")

    try:
        boxes, scores, labels = detect_photos(
            image=info["image"],
            text_prompt=req.text_prompt,
            box_threshold=req.box_threshold,
            text_threshold=req.text_threshold,
            confidence_threshold=req.confidence_threshold,
        )
    except Exception as e:
        log.error(f"Detection failed: {e}")
        raise HTTPException(500, f"Detection failed: {str(e)}")

    # Optionally remove overlaps using detector implementation if requested
    if req.remove_overlaps and boxes is not None:
        try:
            detector = _get_detector()
            if hasattr(detector, "remove_overlaps"):
                boxes, scores, labels = detector.remove_overlaps(
                    boxes, scores, labels, req.overlap_threshold
                )
        except Exception:
            log.warning("remove_overlaps requested but failed; continuing with raw boxes")

    bboxes = [
        BBox(x1=int(b[0]), y1=int(b[1]), x2=int(b[2]), y2=int(b[3]), score=float(s), label=str(l))
        for b, s, l in zip(boxes, scores, labels)
    ]

    return DetectionResult(
        image_id=req.image_id,
        width=info["width"], height=info["height"],
        boxes=bboxes, count=len(bboxes),
    )


# ========== CROP + EXPORT ==========

@app.post("/api/crop")
async def crop_and_export(req: CropRequest):
    info = get_image(req.image_id)
    if info is None:
        raise HTTPException(404, "Image not found.")

    image = info["image"]

    # Attempt to crop using pipeline helper
    boxes = []
    for b in req.boxes:
        boxes.append([b.x1, b.y1, b.x2, b.y2])

    crops = crop_photos(image=image, boxes=boxes, min_size=MIN_CROP_SIZE)

    if not crops:
        raise HTTPException(422, "No valid crops could be generated. All boxes were too small.")

    return create_zip_response(crops)


# ========== ENHANCE ==========

@app.post("/api/enhance")
async def enhance(req: EnhanceRequest):
    info = get_image(req.image_id)
    if info is None:
        raise HTTPException(404, "Image not found.")

    try:
        enhanced = enhance_photo(info["image"], scale=req.scale)
        return create_image_response(enhanced, quality=95)
    except Exception as e:
        log.error(f"Enhancement failed: {e}")
        raise HTTPException(500, f"Enhancement failed: {str(e)}")


# ========== INCLUDE ROUTERS ==========

def _include_routers():
    """Import and include routers with graceful error handling."""
    router_modules = [
        ("app.routers.retouch", "retouch"),
        ("app.routers.rotation", "rotation"),
        ("app.routers.faces", "faces"),
        ("app.routers.events", "events"),
        ("app.routers.dedup", "dedup"),
    ]
    if not ENABLE_ADVANCED_ROUTES:
        log.info("Advanced routes are disabled by configuration; skipping.")
        return
    for module_path, name in router_modules:
        try:
            import importlib
            mod = importlib.import_module(module_path)
            app.include_router(mod.router)
            log.info(f"Router loaded: {name}")
        except Exception as e:
            log.warning(f"Router '{name}' could not be loaded: {e}")

_include_routers()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
