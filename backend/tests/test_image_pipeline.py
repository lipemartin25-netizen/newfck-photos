from PIL import Image
import numpy as np

from app.services.image_pipeline import crop_photos, enhance_photo


def test_crop_photos_filters_small():
    img = Image.new("RGB", (200, 200), (128, 128, 128))
    boxes = np.array([
        [10, 10, 50, 50],   # 40x40 -> keep
        [0, 0, 10, 10],     # 10x10 -> too small
    ])
    crops = crop_photos(img, boxes, min_size=30)
    assert len(crops) == 1
    assert crops[0].size == (40, 40)


def test_enhance_photo_scales():
    img = Image.new("RGB", (64, 32), (255, 0, 0))
    enhanced = enhance_photo(img, scale=2.0)
    assert enhanced.size == (128, 64)
