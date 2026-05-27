"""EXIF and image utility functions."""
import subprocess
import io
from pathlib import Path
from typing import Optional
from PIL import Image

try:
    import piexif
    _HAS_PIEXIF = True
except ImportError:
    _HAS_PIEXIF = False


def apply_exif_date(path: Path, year: int, day_of_year: int = 1):
    """Apply EXIF date via piexif + exiftool fallback."""
    month = min(12, (day_of_year - 1) // 30 + 1)
    day = min(28, (day_of_year - 1) % 30 + 1)
    date_str = f"{year}:{month:02d}:{day:02d} 12:00:00"

    if _HAS_PIEXIF:
        try:
            try:
                exif_dict = piexif.load(str(path))
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode()
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode()
            exif_dict["0th"][piexif.ImageIFD.Make] = b"AlbumAI"
            exif_dict["0th"][piexif.ImageIFD.Software] = b"AlbumAI Studio v1.0"
            exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode()
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(path))
        except Exception:
            pass

    # Try exiftool
    try:
        iptc_date = f"{year}{month:02d}{day:02d}"
        subprocess.run([
            "exiftool", "-overwrite_original",
            f"-EXIF:DateTimeOriginal={date_str}",
            f"-EXIF:CreateDate={date_str}",
            f"-EXIF:ModifyDate={date_str}",
            f"-XMP:DateCreated={date_str}",
            f"-IPTC:DateCreated={iptc_date}",
            f"-AllDates={date_str}",
            str(path)
        ], capture_output=True, timeout=10)
    except (FileNotFoundError, Exception):
        pass


def auto_rotate_pil(image: Image.Image) -> Image.Image:
    """Auto-rotate based on EXIF orientation tag."""
    try:
        from PIL import ImageOps
        return ImageOps.exif_transpose(image) or image
    except Exception:
        return image


def color_correct_pil(image: Image.Image, strength: float = 1.0) -> Image.Image:
    """Simple color correction via contrast/sharpness enhancement."""
    from PIL import ImageEnhance
    if strength <= 0:
        return image
    image = ImageEnhance.Contrast(image).enhance(1.0 + 0.3 * strength)
    image = ImageEnhance.Sharpness(image).enhance(1.0 + 0.2 * strength)
    return image
