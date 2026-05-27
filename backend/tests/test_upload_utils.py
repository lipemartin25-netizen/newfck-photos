import io
from PIL import Image
import pytest

from app.core.upload_utils import validate_upload_file, open_image_from_bytes
from app.models.errors import InvalidUploadError
from app.core.config import MAX_UPLOAD_SIZE


def create_jpeg_bytes(color=(255, 0, 0), size=(64, 64)):
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_validate_valid_jpeg():
    b = create_jpeg_bytes()
    # Should not raise
    validate_upload_file("photo.jpg", b)


def test_validate_bad_extension():
    b = create_jpeg_bytes()
    with pytest.raises(InvalidUploadError):
        validate_upload_file("photo.txt", b)


def test_validate_large_file():
    big = b"\x00" * (MAX_UPLOAD_SIZE + 1)
    with pytest.raises(InvalidUploadError):
        validate_upload_file("big.jpg", big)


def test_open_image_from_bytes_success():
    b = create_jpeg_bytes()
    img = open_image_from_bytes(b)
    assert img.mode == "RGB"


def test_open_image_from_bytes_corrupt():
    with pytest.raises(InvalidUploadError):
        open_image_from_bytes(b"notanimage")
