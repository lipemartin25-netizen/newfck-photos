"""
dedup.py — Perceptual hash deduplication service.
"""
import logging
from pathlib import Path
from PIL import Image

log = logging.getLogger("albumai.dedup")

try:
    import imagehash
    _OK = True
except ImportError:
    _OK = False


class Deduplicator:
    """Find duplicate and near-duplicate photos using perceptual hashing."""

    def __init__(self, hash_size: int = 16, threshold: int = 5):
        if not _OK:
            raise ImportError("imagehash required: pip install imagehash")
        self.hash_size = hash_size
        self.threshold = threshold

    def compute_hashes(self, images: dict[str, Image.Image]) -> dict[str, dict]:
        """Compute pHash, dHash, wHash for each image."""
        results = {}
        for key, img in images.items():
            results[key] = {
                "phash": str(imagehash.phash(img, hash_size=self.hash_size)),
                "dhash": str(imagehash.dhash(img, hash_size=self.hash_size)),
                "whash": str(imagehash.whash(img, hash_size=self.hash_size)),
            }
        return results

    def find_duplicates(self, hashes: dict[str, dict]) -> list[list[str]]:
        """Group images with hamming distance below threshold."""
        keys = list(hashes.keys())
        groups = []
        visited = set()

        for i, k1 in enumerate(keys):
            if k1 in visited:
                continue
            group = [k1]
            h1 = imagehash.hex_to_hash(hashes[k1]["phash"])
            for k2 in keys[i + 1:]:
                if k2 in visited:
                    continue
                h2 = imagehash.hex_to_hash(hashes[k2]["phash"])
                if (h1 - h2) <= self.threshold:
                    group.append(k2)
                    visited.add(k2)
            if len(group) > 1:
                groups.append(group)
                visited.add(k1)

        return groups

    def suggest_best(self, group_images: list[Image.Image]) -> int:
        """Pick best version: highest resolution + sharpness."""
        import numpy as np
        scores = []
        for img in group_images:
            pixels = img.width * img.height
            arr = np.array(img.convert("L")).astype(float)
            # Laplacian variance as sharpness proxy
            lap = np.abs(np.diff(arr, axis=0)).mean() + np.abs(np.diff(arr, axis=1)).mean()
            scores.append(pixels * 0.001 + lap * 10)
        return int(np.argmax(scores))
