"""
detector.py — Grounding DINO photo detection service.
Core service that detects individual photos in scanned album pages.
"""
import os
import re
import random
import logging
import warnings
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

import numpy as np
import torch
from PIL import Image

warnings.filterwarnings("ignore", category=FutureWarning,
    module="transformers.models.grounding_dino.processing_grounding_dino")
warnings.filterwarnings("ignore",
    message=".*Image size.*exceeds limit.*could be decompression bomb DOS attack.*")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
Image.MAX_IMAGE_PIXELS = None

log = logging.getLogger("albumai.detector")
CURRENT_YEAR = datetime.now().year


class PhotoDetector:
    """Detects photos in scanned album pages using Grounding DINO."""

    def __init__(self, model_id: str = "IDEA-Research/grounding-dino-base",
                 device: str = None, seed: int = 42):
        self._set_seed(seed)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        log.info(f"Using device: {self.device}")

        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(self.device)
        log.info("Grounding DINO model loaded")

    def _set_seed(self, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def detect(self, image: Image.Image, text_prompt: str = "an old photo.",
               box_threshold: float = 0.2, text_threshold: float = 0.2,
               confidence_threshold: float = 0.15):
        """Run detection on a PIL image. Returns (boxes, scores, labels)."""
        image = image.convert("RGB")
        text_prompt = text_prompt.lower().strip()
        if not text_prompt.endswith("."):
            text_prompt += "."

        inputs = self.processor(images=image, text=text_prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        results = self.processor.post_process_grounded_object_detection(
            outputs, inputs.input_ids,
            box_threshold=box_threshold, text_threshold=text_threshold,
            target_sizes=[image.size[::-1]]
        )

        if not results:
            return [], [], []

        r = results[0]
        boxes = r["boxes"].cpu().numpy().tolist()
        scores = r["scores"].cpu().numpy().tolist()
        raw_labels = r.get("labels", r.get("text", ["photo"] * len(scores)))
        if isinstance(raw_labels, torch.Tensor):
            labels = [f"photo_{i}" for i in range(len(scores))]
        else:
            labels = list(raw_labels)

        # Filter by confidence
        filtered = [(b, s, l) for b, s, l in zip(boxes, scores, labels) if s >= confidence_threshold]
        if not filtered:
            return [], [], []

        boxes, scores, labels = zip(*filtered)
        return list(boxes), list(scores), list(labels)

    @staticmethod
    def overlap_pct(box1, box2) -> float:
        """Overlap percentage based on smaller area."""
        x1, y1 = max(box1[0], box2[0]), max(box1[1], box2[1])
        x2, y2 = min(box1[2], box2[2]), min(box1[3], box2[3])
        if x2 <= x1 or y2 <= y1:
            return 0.0
        inter = (x2 - x1) * (y2 - y1)
        a1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        a2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        return (inter / max(min(a1, a2), 1)) * 100.0

    def remove_overlaps(self, boxes, scores, labels, threshold=0.05):
        """Remove overlapping boxes keeping highest confidence."""
        if len(boxes) <= 1:
            return boxes, scores, labels
        order = list(np.argsort(scores)[::-1])
        keep = []
        while order:
            cur = order.pop(0)
            keep.append(cur)
            remove = []
            for idx in order:
                if self.overlap_pct(boxes[cur], boxes[idx]) >= threshold * 100:
                    remove.append(idx)
            order = [i for i in order if i not in remove]
        return ([boxes[i] for i in keep], [scores[i] for i in keep],
                [labels[i] for i in keep])

    def crop_photos(self, image: Image.Image, boxes, min_size: int = 100):
        """Crop detected regions from image."""
        crops = []
        for box in boxes:
            x1, y1, x2, y2 = [int(round(v)) for v in box]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image.width, x2), min(image.height, y2)
            if (x2 - x1) < min_size or (y2 - y1) < min_size:
                continue
            crops.append(image.crop((x1, y1, x2, y2)))
        return crops

    @staticmethod
    def detect_year(folder_name: str) -> Optional[int]:
        """Detect year from folder name (4-digit, 1801-current)."""
        if re.match(r"^\d{4}$", folder_name):
            y = int(folder_name)
            if 1801 <= y <= CURRENT_YEAR:
                return y
        return None


# Singleton lazy-loaded
_detector: Optional[PhotoDetector] = None


def get_detector() -> PhotoDetector:
    """Get or create the global detector instance."""
    global _detector
    if _detector is None:
        from app.core.config import DETECTOR_MODEL, DEVICE
        _detector = PhotoDetector(model_id=DETECTOR_MODEL, device=DEVICE)
    return _detector
