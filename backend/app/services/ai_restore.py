import io
import logging
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Optional, Tuple
import torch

logger = logging.getLogger(__name__)

class AIRestorationPipeline:
    """
    AI Restoration pipeline including Real-ESRGAN for upscaling, 
    GFPGAN for face restoration, and a custom Color Revitalizer.
    """
    def __init__(self, use_gfpgan: bool = True, use_realesrgan: bool = True):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_gfpgan = use_gfpgan
        self.use_realesrgan = use_realesrgan
        
        self.upsampler = None
        self.face_enhancer = None
        
        self._initialize_models()

    def _initialize_models(self):
        try:
            if self.use_realesrgan:
                from basicsr.archs.rrdbnet_arch import RRDBNet
                from realesrgan import RealESRGANer
                
                # Model initialization (assuming weights are downloaded in 'weights' dir)
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                self.upsampler = RealESRGANer(
                    scale=4,
                    model_path='weights/RealESRGAN_x4plus.pth',
                    model=model,
                    tile=400,
                    tile_pad=10,
                    pre_pad=0,
                    half=self.device.type == 'cuda',
                    device=self.device
                )
                logger.info("RealESRGANer initialized.")

            if self.use_gfpgan:
                from gfpgan import GFPGANer
                self.face_enhancer = GFPGANer(
                    model_path='weights/GFPGANv1.4.pth',
                    upscale=2,
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=self.upsampler
                )
                logger.info("GFPGANer initialized.")
        except ImportError as e:
            logger.warning(f"Restoration dependencies missing, running in degraded mode: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize restoration models: {e}")

    def revitalize_color(self, img_np: np.ndarray) -> np.ndarray:
        """
        Custom color revitalizer using CLAHE (Contrast Limited Adaptive Histogram Equalization) 
        and Gray-World color constancy to remove color casts (e.g. orange fading).
        """
        # Convert to LAB for CLAHE
        lab = cv2.cvtColor(img_np, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        
        limg = cv2.merge((cl, a, b))
        clahe_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # Gray-World Assumption for color cast removal
        result = clahe_img.astype(np.float32)
        avg_b = np.mean(result[:, :, 0])
        avg_g = np.mean(result[:, :, 1])
        avg_r = np.mean(result[:, :, 2])
        avg_gray = (avg_b + avg_g + avg_r) / 3
        
        if avg_b > 0 and avg_g > 0 and avg_r > 0:
            result[:, :, 0] *= (avg_gray / avg_b)
            result[:, :, 1] *= (avg_gray / avg_g)
            result[:, :, 2] *= (avg_gray / avg_r)
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Boost saturation slightly using PIL
        pil_img = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        enhancer = ImageEnhance.Color(pil_img)
        enhanced_pil = enhancer.enhance(1.15)
        
        return cv2.cvtColor(np.array(enhanced_pil), cv2.COLOR_RGB2BGR)

    def restore_image(self, image_bytes: bytes, enhance_faces: bool = True, revitalize: bool = True) -> bytes:
        """
        Complete restoration pipeline.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image bytes")

        # 1. Color Revitalization
        if revitalize:
            img = self.revitalize_color(img)

        # 2. Upscaling & Face Restoration
        output = img
        if self.face_enhancer and enhance_faces:
            _, _, output = self.face_enhancer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
        elif self.upsampler:
            output, _ = self.upsampler.enhance(img, outscale=2)

        is_success, buffer = cv2.imencode(".jpg", output, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not is_success:
            raise ValueError("Failed to encode restored image")
            
        return buffer.tobytes()

# Singleton
restoration_pipeline = None

def get_restoration_pipeline() -> AIRestorationPipeline:
    global restoration_pipeline
    if restoration_pipeline is None:
        restoration_pipeline = AIRestorationPipeline()
    return restoration_pipeline
