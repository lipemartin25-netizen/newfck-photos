import io
import logging
from typing import List, Dict, Any
import torch
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
from PIL import Image

logger = logging.getLogger(__name__)

class DINOProcessor:
    """
    Grounding DINO implementation using Hugging Face Transformers.
    Responsible for identifying individual photos, cards, or documents within a larger flatbed scan.
    """
    def __init__(self, model_id: str = "IDEA-Research/grounding-dino-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Grounding DINO model '{model_id}' on device: {self.device}")
        try:
            self.processor = AutoProcessor.from_pretrained(model_id)
            self.model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(self.device)
            self.model.eval()
        except Exception as e:
            logger.error(f"Failed to load Grounding DINO: {str(e)}")
            raise

    def detect_objects(self, image_bytes: bytes, text_queries: List[str] = ["photograph", "polaroid", "postcard"], box_threshold: float = 0.3, text_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Detect bounding boxes of items in the scanned image based on text queries.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            text = ". ".join(text_queries) + "."
            
            inputs = self.processor(images=image, text=text, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            results = self.processor.post_process_grounded_object_detection(
                outputs,
                inputs.input_ids,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
                target_sizes=[image.size[::-1]] # (height, width)
            )[0]
            
            bboxes = results["boxes"].cpu().numpy().tolist()
            scores = results["scores"].cpu().numpy().tolist()
            labels = results["labels"]
            
            detected = []
            for bbox, score, label in zip(bboxes, scores, labels):
                detected.append({
                    "bbox": [round(c, 2) for c in bbox], # [xmin, ymin, xmax, ymax]
                    "score": round(score, 4),
                    "label": label
                })
                
            logger.info(f"Detected {len(detected)} objects.")
            return detected
            
        except Exception as e:
            logger.error(f"Error during DINO inference: {str(e)}")
            raise

# Singleton instance to be used by FastAPI endpoints
dino_processor = None

def get_dino_processor() -> DINOProcessor:
    global dino_processor
    if dino_processor is None:
        dino_processor = DINOProcessor()
    return dino_processor
