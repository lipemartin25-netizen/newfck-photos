"""
Image processing pipeline orchestration.
Lazy-loads PhotoDetector, orchestrates detect/crop/enhance operations.
"""
import logging
from functools import lru_cache
from typing import Tuple, List
from PIL import Image
import numpy as np

from app.models.errors import DetectorUnavailableError
from app.core.config import DEFAULT_PROMPT, DEFAULT_CONFIDENCE, DEFAULT_OVERLAP, MIN_CROP_SIZE

logger = logging.getLogger("albumai.pipeline")


def get_detector():
    """
    Get or lazy-load the PhotoDetector singleton.
    Uses lru_cache for thread-safe lazy loading.
    Raises DetectorUnavailableError if model cannot be loaded.
    """
    try:
        # Import here to delay loading until first call
        from app.services.detector import PhotoDetector
        detector = PhotoDetector()
        logger.info("✓ PhotoDetector loaded successfully")
        return detector
    except Exception as e:
        logger.error(f"Failed to load PhotoDetector: {e}")
        raise DetectorUnavailableError(f"Cannot load detector model: {str(e)}")


# Wrap detector loading with lru_cache for single-instance pattern
@lru_cache(maxsize=1)
def _cached_detector():
    """Cached detector instance (maxsize=1 ensures singleton)."""
    return get_detector()


def get_detector_cached():
    """Get cached detector instance."""
    try:
        return _cached_detector()
    except DetectorUnavailableError:
        raise


def detect_photos(
    image: Image.Image,
    text_prompt: str = None,
    box_threshold: float = None,
    text_threshold: float = None,
    confidence_threshold: float = None,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Detect photo regions in image using zero-shot detection.
    
    Args:
        image: PIL Image object
        text_prompt: Detection prompt (default: DEFAULT_PROMPT)
        box_threshold: Box detection threshold (default: DEFAULT_CONFIDENCE)
        text_threshold: Text detection threshold (default: DEFAULT_OVERLAP)
        confidence_threshold: Confidence filter threshold
        
    Returns:
        Tuple of (boxes, scores, labels) from detector
        
    Raises:
        DetectorUnavailableError: If detector cannot be loaded
    """
    # Use defaults
    text_prompt = text_prompt or DEFAULT_PROMPT
    box_threshold = box_threshold or DEFAULT_CONFIDENCE
    text_threshold = text_threshold or DEFAULT_OVERLAP
    
    try:
        detector = get_detector_cached()
        boxes, scores, labels = detector.detect(
            image=image,
            text_prompt=text_prompt,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
            confidence_threshold=confidence_threshold,
        )
        logger.info(f"✓ Detected {len(boxes)} photo regions")
        return boxes, scores, labels
    except DetectorUnavailableError:
        raise
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise DetectorUnavailableError(f"Detection error: {str(e)}")


def crop_photos(
    image: Image.Image,
    boxes: np.ndarray,
    min_size: int = MIN_CROP_SIZE,
) -> List[Image.Image]:
    """
    Crop photo regions from image based on bounding boxes.
    Filters boxes smaller than min_size.
    
    Args:
        image: PIL Image object
        boxes: Numpy array of boxes (N, 4) with [x1, y1, x2, y2]
        min_size: Minimum crop dimension to keep
        
    Returns:
        List of cropped PIL Images
    """
    crops = []
    
    for idx, box in enumerate(boxes):
        x1, y1, x2, y2 = [int(coord) for coord in box]
        
        # Validate and filter
        width = x2 - x1
        height = y2 - y1
        if width < min_size or height < min_size:
            logger.debug(f"Skipping box {idx}: size {width}x{height} < {min_size}")
            continue
        
        # Crop
        try:
            crop = image.crop((x1, y1, x2, y2))
            crops.append(crop)
            logger.debug(f"✓ Cropped region {idx}: {width}x{height}")
        except Exception as e:
            logger.warning(f"Failed to crop region {idx}: {e}")
            continue
    
    logger.info(f"✓ Cropped {len(crops)} photo regions")
    return crops


def enhance_photo(
    image: Image.Image,
    scale: float = 2.0,
) -> Image.Image:
    """
    Enhance photo using upscaling.
    Simple implementation: resize with LANCZOS resampling.
    Future: integrate RealESRGAN or similar for better quality.
    
    Args:
        image: PIL Image object
        scale: Upscaling factor (e.g., 2.0 for 2x)
        
    Returns:
        Enhanced PIL Image
    """
    try:
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        enhanced = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"✓ Enhanced image: {image.size} → {enhanced.size} ({scale}x)")
        return enhanced
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        raise Exception(f"Enhancement error: {str(e)}")
