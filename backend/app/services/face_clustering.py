"""
face_clustering.py — InsightFace detection + HDBSCAN clustering.
"""
import logging
from pathlib import Path
from typing import Optional
from PIL import Image

log = logging.getLogger("albumai.faces")

try:
    import numpy as np
    import cv2
    from insightface.app import FaceAnalysis
    _HAS_FACE = True
except ImportError:
    _HAS_FACE = False

try:
    import hdbscan
    _HAS_HDBSCAN = True
except ImportError:
    _HAS_HDBSCAN = False


class FaceClusterer:
    """Detect faces and cluster by identity."""

    def __init__(self, det_threshold: float = 0.5):
        if not _HAS_FACE:
            raise ImportError("insightface required: pip install insightface onnxruntime")
        self.app = FaceAnalysis(name="buffalo_l")
        import torch
        ctx = 0 if torch.cuda.is_available() else -1
        self.app.prepare(ctx_id=ctx, det_size=(640, 640))
        self.threshold = det_threshold

    def extract_from_image(self, image: Image.Image) -> list[dict]:
        """Extract face embeddings from a PIL image."""
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        faces = self.app.get(img_cv)
        results = []
        for f in faces:
            if f.det_score < self.threshold:
                continue
            bbox = f.bbox.astype(int)
            results.append({
                "bbox": {"x": int(bbox[0]), "y": int(bbox[1]),
                         "w": int(bbox[2] - bbox[0]), "h": int(bbox[3] - bbox[1])},
                "age": int(f.age),
                "gender": "M" if f.gender == 1 else "F",
                "embedding": f.embedding.tolist(),
                "score": float(f.det_score),
            })
        return results

    def cluster(self, embeddings: list, min_cluster_size: int = 3) -> dict:
        """Cluster face embeddings using HDBSCAN."""
        if not _HAS_HDBSCAN or len(embeddings) < min_cluster_size:
            return {}

        emb_array = np.array(embeddings)
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric="euclidean",
            cluster_selection_method="eom",
        )
        labels = clusterer.fit_predict(emb_array)

        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:
                continue
            clusters.setdefault(int(label), []).append(idx)
        return clusters
