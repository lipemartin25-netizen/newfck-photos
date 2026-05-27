"""
retoucher.py — Advanced color revitalization pipeline for vintage/old photos.
Designed to counteract chemical degradation, acid-paper casts, and fading.
"""
import logging
import numpy as np
import cv2
from PIL import Image

log = logging.getLogger("albumai.retoucher")


class PhotoRetoucher:
    """Restaura e revitaliza as cores de fotos antigas desbotadas."""

    def auto_white_balance(self, image: Image.Image, method: str = "gray_world") -> Image.Image:
        """Apply automatic white balance algorithms (Gray World focus)."""
        img_arr = np.array(image.convert("RGB"))
        
        if method == "gray_world":
            # Gray World: balance channels so that they have the same mean
            b, g, r = cv2.split(img_arr)
            b_mean, g_mean, r_mean = np.mean(b), np.mean(g), np.mean(r)
            avg = (b_mean + g_mean + r_mean) / 3.0
            
            b = np.clip(b * (avg / max(b_mean, 1.0)), 0, 255).astype(np.uint8)
            g = np.clip(g * (avg / max(g_mean, 1.0)), 0, 255).astype(np.uint8)
            r = np.clip(r * (avg / max(r_mean, 1.0)), 0, 255).astype(np.uint8)
            
            balanced = cv2.merge([b, g, r])
            return Image.fromarray(balanced)
        return image

    def remove_yellow_cast(self, image: Image.Image, intensity: float = 0.6) -> Image.Image:
        """Target and remove yellow/orange acid-paper casts by pulling back yellow channels."""
        img_arr = np.array(image.convert("RGB")).astype(float)
        r, g, b = img_arr[:, :, 0], img_arr[:, :, 1], img_arr[:, :, 2]
        
        # Yellow cast is represented by R & G being much higher than B
        yellow = np.minimum(r, g) - b
        yellow = np.maximum(0, yellow)
        
        # Pull back R and G slightly towards B based on intensity
        r_corr = r - (yellow * intensity * 0.5)
        g_corr = g - (yellow * intensity * 0.3)
        b_corr = b + (yellow * intensity * 0.2)
        
        corr = np.stack([
            np.clip(r_corr, 0, 255),
            np.clip(g_corr, 0, 255),
            np.clip(b_corr, 0, 255)
        ], axis=-1).astype(np.uint8)
        
        return Image.fromarray(corr)

    def apply_clahe(self, image: Image.Image, clip_limit: float = 2.0,
                    tile_size: tuple[int, int] = (8, 8)) -> Image.Image:
        """Contrast Limited Adaptive Histogram Equalization on LAB color space."""
        img_arr = np.array(image.convert("RGB"))
        lab = cv2.cvtColor(img_arr, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
        cl = clahe.apply(l)
        
        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
        return Image.fromarray(enhanced)

    def adjust_manual(self, image: Image.Image, brightness: float = 0,
                      contrast: float = 0, saturation: float = 0) -> Image.Image:
        """Manual adjustments mapping from [-50, 50] sliders."""
        img_arr = np.array(image.convert("RGB")).astype(float)
        
        # Brightness
        if brightness != 0:
            img_arr += (brightness * 2.55)
            
        # Contrast
        if contrast != 0:
            factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
            img_arr = factor * (img_arr - 128) + 128
            
        img_arr = np.clip(img_arr, 0, 255).astype(np.uint8)
        
        # Saturation
        if saturation != 0:
            hsv = cv2.cvtColor(img_arr, cv2.COLOR_RGB2HSV).astype(float)
            h, s, v = cv2.split(hsv)
            s += (saturation * 2.55)
            s = np.clip(s, 0, 255)
            hsv = cv2.merge([h, s, v]).astype(np.uint8)
            img_arr = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            
        return Image.fromarray(img_arr)

    def revitalize_colors(self, image: Image.Image, strength: float = 1.0) -> Image.Image:
        """Complete automation pipeline: White Balance -> Yellow Cast Pullback -> CLAHE."""
        img = self.auto_white_balance(image, "gray_world")
        if strength > 0.3:
            img = self.remove_yellow_cast(img, intensity=0.5 * strength)
        img = self.apply_clahe(img, clip_limit=1.5 + 0.5 * strength)
        return img

    def scanner_optimize(self, image: Image.Image, mode: str = "sharper") -> Image.Image:
        """Standard scanner optimization presets."""
        if mode == "sharper":
            return self.adjust_manual(image, brightness=-5, contrast=15, saturation=0)
        elif mode == "vivid":
            return self.adjust_manual(image, brightness=5, contrast=20, saturation=25)
        elif mode == "vintage":
            return self.adjust_manual(image, brightness=-10, contrast=-5, saturation=-30)
        return image
