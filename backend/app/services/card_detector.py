"""
card_detector.py — Card Mode photo extraction.
Identifies rectangular cards (trading cards, postcards, business cards)
using computer vision contour detection and aspect ratio fitting.
"""
import logging
import numpy as np
import cv2
from PIL import Image

log = logging.getLogger("albumai.cards")


class CardDetector:
    """Detect rectangular cards using aspect ratios."""

    def __init__(self, target_aspects: dict[str, float] = None):
        self.aspects = target_aspects or {
            "trading_card": 0.714,  # 2.5 : 3.5
            "postcard": 0.667,      # 4 : 6
            "business_card": 1.750,  # 3.5 : 2
            "id_card": 1.585        # 85.6 : 54
        }

    def detect_cards(self, image: Image.Image, threshold: float = 0.15) -> list[dict]:
        """Detect rectangular contours and return bounding boxes matching expected card ratios."""
        img_arr = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY)
        
        # Blur + adaptive thresholding
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cards = []
        img_h, img_w = img_arr.shape[:2]
        
        for c in contours:
            area = cv2.contourArea(c)
            if area < 5000:  # Skip small specs
                continue
                
            # Approximate contour as polygon
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            # Cards should be quadrilaterals
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect = float(w) / float(h)
                
                # Check aspect ratio fitting
                matched = None
                for card_type, target in self.aspects.items():
                    if abs(aspect - target) <= threshold:
                        matched = card_type
                        break
                        
                if matched:
                    cards.append({
                        "bbox": [x, y, x + w, y + h],
                        "type": matched,
                        "aspect": aspect,
                        "corners": approx.reshape(4, 2).tolist()
                    })
                    
        return cards

    def perspective_correct(self, image: Image.Image, corners: list[list[float]]) -> Image.Image:
        """Correct perspective skew if card was scanned crooked."""
        img_arr = np.array(image.convert("RGB"))
        pts = np.array(corners, dtype="float32")
        
        # Order corners: top-left, top-right, bottom-right, bottom-left
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        
        rect = np.zeros((4, 2), dtype="float32")
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        (tl, tr, br, bl) = rect
        
        # Compute width of new image
        wA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        wB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxW = max(int(wA), int(wB))
        
        # Compute height
        hA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        hB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxH = max(int(hA), int(hB))
        
        dst = np.array([
            [0, 0],
            [maxW - 1, 0],
            [maxW - 1, maxH - 1],
            [0, maxH - 1]
        ], dtype="float32")
        
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img_arr, M, (maxW, maxH))
        
        return Image.fromarray(warped)
