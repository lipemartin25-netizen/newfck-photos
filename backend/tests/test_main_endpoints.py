import io
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def create_jpeg_bytes():
    img = Image.new("RGB", (80, 60), (10, 20, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_upload_and_detect(monkeypatch):
    # Mock detect_photos to avoid loading heavy ML models
    def fake_detect(image, text_prompt=None, box_threshold=None, text_threshold=None, confidence_threshold=None):
        # Return one box covering center
        return [[10, 10, 50, 40]], [0.9], ["photo"]

    monkeypatch.setattr("app.main.detect_photos", fake_detect)

    img_bytes = create_jpeg_bytes()
    files = [("files", ("scan.jpg", img_bytes, "image/jpeg"))]
    res = client.post("/api/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) and len(data) == 1
    image_id = data[0]["id"]

    # Call detect
    res2 = client.post("/api/detect", json={"image_id": image_id})
    assert res2.status_code == 200
    det = res2.json()
    assert det["count"] == 1
    assert len(det["boxes"]) == 1
