"""
event_clusterer.py — CLIP-based event/scene clustering and semantic search.
"""
import logging
from PIL import Image

log = logging.getLogger("albumai.events")

try:
    import numpy as np
    import torch
    import open_clip
    _HAS_CLIP = True
except ImportError:
    _HAS_CLIP = False

SCENE_LABELS = [
    "birthday party", "wedding", "vacation", "christmas", "graduation",
    "beach", "family dinner", "outdoor picnic", "school event", "road trip",
    "holiday celebration", "portrait session", "landscape", "city street",
    "religious ceremony", "baby shower", "sports game", "concert",
]


class EventClusterer:
    """Cluster photos by visual event using CLIP embeddings."""

    def __init__(self, model_name="ViT-B-32", pretrained="laion2b_s34b_b79k"):
        if not _HAS_CLIP:
            raise ImportError("open-clip-torch required: pip install open-clip-torch")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.model.eval()

    def embed_image(self, image: Image.Image) -> np.ndarray:
        """Get 512-dim CLIP embedding for an image."""
        img_t = self.preprocess(image).unsqueeze(0)
        with torch.no_grad():
            feat = self.model.encode_image(img_t)
            feat /= feat.norm(dim=-1, keepdim=True)
        return feat.cpu().numpy()[0]

    def embed_images(self, images: list[Image.Image]) -> np.ndarray:
        """Batch embed multiple images."""
        return np.array([self.embed_image(img) for img in images])

    def classify_scene(self, image: Image.Image, candidates=None, top_k=3) -> list[dict]:
        """Zero-shot scene classification."""
        if candidates is None:
            candidates = SCENE_LABELS
        prompts = [f"a photo of {c}" for c in candidates]
        text = self.tokenizer(prompts)
        img_t = self.preprocess(image).unsqueeze(0)

        with torch.no_grad():
            img_feat = self.model.encode_image(img_t)
            txt_feat = self.model.encode_text(text)
            img_feat /= img_feat.norm(dim=-1, keepdim=True)
            txt_feat /= txt_feat.norm(dim=-1, keepdim=True)
            probs = (100.0 * img_feat @ txt_feat.T).softmax(dim=-1)

        probs_np = probs.cpu().numpy()[0]
        top = probs_np.argsort()[-top_k:][::-1]
        return [{"label": candidates[i], "score": float(probs_np[i])} for i in top]

    def semantic_search(self, query: str, embeddings: np.ndarray, top_k=10) -> list[tuple[int, float]]:
        """Search images by text query."""
        text = self.tokenizer([query])
        with torch.no_grad():
            txt_feat = self.model.encode_text(text)
            txt_feat /= txt_feat.norm(dim=-1, keepdim=True)
        txt_np = txt_feat.cpu().numpy()[0]
        sims = embeddings @ txt_np
        top_idx = sims.argsort()[-top_k:][::-1]
        return [(int(i), float(sims[i])) for i in top_idx]

    def cluster_events(self, embeddings: np.ndarray, min_cluster=3) -> dict:
        """Cluster images into events using HDBSCAN on CLIP embeddings."""
        try:
            import hdbscan
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster, metric="euclidean")
            labels = clusterer.fit_predict(embeddings)
            clusters = {}
            for idx, label in enumerate(labels):
                if label >= 0:
                    clusters.setdefault(int(label), []).append(idx)
            return clusters
        except ImportError:
            return {}
