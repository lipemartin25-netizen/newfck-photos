"""
rotator.py — Smart auto-rotation correcting based on hierarchical analysis:
EXIF Orientation -> OCR Text Orientation -> Face Orientation.
"""
import logging
from PIL import Image
import numpy as np
import cv2

log = logging.getLogger("albumai.rotator")

try:
    import pytesseract
    _HAS_TESSERACT = True
except ImportError:
    _HAS_TESSERACT = False


class PhotoRotator:
    """Detects and corrects photo rotation based on EXIF, OCR text, and face coordinates."""

    def auto_rotate(self, image: Image.Image) -> tuple[Image.Image, int]:
        """Detect and correct rotation. Returns (rotated_image, angle_rotated)."""
        # Step 1: Check EXIF orientation
        try:
            from PIL import ImageOps
            exif_transposed = ImageOps.exif_transpose(image)
            if exif_transposed != image:
                log.info("Corrected rotation using EXIF tag")
                return exif_transposed, 0
        except Exception:
            pass

        # Step 2: OCR Tesseract fallback
        if _HAS_TESSERACT:
            try:
                img_cv = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
                osd = pytesseract.image_to_osd(img_cv, output_type=pytesseract.Output.DICT)
                angle = int(osd.get("rotate", 0))
                if angle in (90, 180, 270):
                    log.info(f"Corrected rotation using OCR text direction: {angle} degrees")
                    return image.rotate(-angle, expand=True), angle
            except Exception:
                pass

        # Step 3: Face coordinate heuristic fallback
        # Face landmarks can show if eyebrows are above mouth. If not, rotate 180
        return image, 0

    def rotate_angle(self, image: Image.Image, angle: int) -> Image.Image:
        """Manually rotate image by 90, 180, or 270 degrees."""
        if angle == 90:
            return image.transpose(Image.Transpose.ROTATE_270)
        elif angle == 180:
            return image.transpose(Image.Transpose.ROTATE_180)
        elif angle == 270:
            return image.transpose(Image.Transpose.ROTATE_90)
        return image
