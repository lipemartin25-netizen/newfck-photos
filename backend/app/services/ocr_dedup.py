import io
import logging
from PIL import Image
import pytesseract
import imagehash

logger = logging.getLogger(__name__)

class OCRDedupService:
    """
    OCR and Deduplication service using Tesseract and ImageHash.
    """
    def __init__(self):
        # Optional: Set custom tesseract cmd path here if needed in production
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass

    def extract_text(self, image_bytes: bytes, lang: str = 'por+eng') -> str:
        """
        Extract text from image using Tesseract OCR.
        Useful for reading dates or notes scribbled on the back of photos.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Basic preprocessing could be added here (grayscale, thresholding)
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    def compute_phash(self, image_bytes: bytes, hash_size: int = 8) -> str:
        """
        Compute perceptual hash (pHash) for deduplication.
        pHash is resilient to minor scaling, cropping, and color adjustments.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # perceptual hash
            hash_obj = imagehash.phash(image, hash_size=hash_size)
            return str(hash_obj)
        except Exception as e:
            logger.error(f"pHash computation failed: {e}")
            return ""
            
    def compute_ahash(self, image_bytes: bytes, hash_size: int = 8) -> str:
        """
        Compute average hash (aHash) for deduplication.
        Faster, but slightly less robust than pHash.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            hash_obj = imagehash.average_hash(image, hash_size=hash_size)
            return str(hash_obj)
        except Exception as e:
            logger.error(f"aHash computation failed: {e}")
            return ""

    def is_duplicate(self, hash1: str, hash2: str, threshold: int = 5) -> bool:
        """
        Compare two hex hash strings. If the Hamming distance is <= threshold, 
        they are considered duplicates or near-duplicates.
        """
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            distance = h1 - h2
            return distance <= threshold
        except Exception as e:
            logger.error(f"Hash comparison failed: {e}")
            return False

# Singleton
ocr_dedup_service = None

def get_ocr_dedup_service() -> OCRDedupService:
    global ocr_dedup_service
    if ocr_dedup_service is None:
        ocr_dedup_service = OCRDedupService()
    return ocr_dedup_service
