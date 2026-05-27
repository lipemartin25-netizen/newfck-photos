"""
enhancer.py — Real-ESRGAN upscaling + optional GFPGAN face restoration.
Loads models on demand; works without them installed.
"""
from PIL import Image
import logging

log = logging.getLogger("albumai.enhancer")

_esrgan = None


class PhotoEnhancer:
    """AI photo enhancement using Real-ESRGAN."""

    def __init__(self, scale: int = 2, device: str = "auto"):
        self.scale = scale
        if device == "auto":
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self._model = None

    def _load_model(self, scale: int):
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet
        if scale == 4:
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                            num_block=23, num_grow_ch=32, scale=4)
            model_name = "RealESRGAN_x4plus"
        else:
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                            num_block=23, num_grow_ch=32, scale=2)
            model_name = "RealESRGAN_x2plus"

        self._model = RealESRGANer(
            scale=scale, model_path=None, dni_weight=None,
            model=model, tile=400, tile_pad=10, pre_pad=0,
            half=self.device == "cuda",
        )
        log.info(f"Loaded {model_name} on {self.device}")

    def enhance(self, image: Image.Image, scale: int = 2) -> Image.Image:
        """Upscale image by given factor."""
        import cv2
        import numpy as np

        if self._model is None or self.scale != scale:
            self.scale = scale
            self._load_model(scale)

        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        output, _ = self._model.enhance(img_cv, outscale=scale)
        return Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

    def batch_enhance(self, images: list[Image.Image], scale: int = 2,
                      progress_callback=None) -> list[Image.Image]:
        results = []
        for i, img in enumerate(images):
            results.append(self.enhance(img, scale))
            if progress_callback:
                progress_callback(i + 1, len(images))
        return results
