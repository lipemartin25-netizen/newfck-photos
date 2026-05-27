"""AlbumAI Studio — Core configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
for d in (MODELS_DIR, UPLOADS_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Device
try:
    import torch
    DEVICE = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
except ImportError:
    DEVICE = "cpu"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 52428800))  # 50MB
CLEANUP_HOURS = int(os.getenv("CLEANUP_HOURS", 24))

# Model defaults
DETECTOR_MODEL = os.getenv("DETECTOR_MODEL", "IDEA-Research/grounding-dino-base")
DEFAULT_PROMPT = os.getenv("DEFAULT_PROMPT", "an old photo. a picture. a photograph.")
DEFAULT_CONFIDENCE = float(os.getenv("DEFAULT_CONFIDENCE", "0.15"))
DEFAULT_OVERLAP = float(os.getenv("DEFAULT_OVERLAP", "0.05"))
MIN_CROP_SIZE = int(os.getenv("MIN_CROP_SIZE", "100"))

# Feature flags
ENABLE_ADVANCED_ROUTES = os.getenv("ENABLE_ADVANCED_ROUTES", "false").lower() == "true"
