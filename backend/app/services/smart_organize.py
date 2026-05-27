import io
import logging
from typing import List, Dict, Any
import numpy as np
import cv2
from PIL import Image
import torch
import open_clip

logger = logging.getLogger(__name__)

class SmartOrganizeService:
    """
    Smart organization using InsightFace for facial embeddings, 
    OpenCLIP for semantic content, and HDBSCAN for clustering events and people.
    """
    def __init__(self, use_insightface: bool = True, use_clip: bool = True):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.face_app = None
        self.clip_model = None
        self.clip_preprocess = None
        self.clip_tokenizer = None
        
        if use_insightface:
            try:
                from insightface.app import FaceAnalysis
                # Using buffalo_l as it is highly accurate
                self.face_app = FaceAnalysis(name='buffalo_l')
                self.face_app.prepare(ctx_id=0 if torch.cuda.is_available() else -1, det_size=(640, 640))
                logger.info("InsightFace loaded.")
            except Exception as e:
                logger.error(f"Failed to load InsightFace: {e}")
                
        if use_clip:
            try:
                # Load OpenCLIP model (ViT-B-32 trained on LAION)
                self.clip_model, _, self.clip_preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k', device=self.device)
                self.clip_tokenizer = open_clip.get_tokenizer('ViT-B-32')
                logger.info("OpenCLIP loaded.")
            except Exception as e:
                logger.error(f"Failed to load OpenCLIP: {e}")

    def extract_faces(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Detect faces and extract 512-d embeddings.
        """
        if not self.face_app:
            return []
            
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            faces = self.face_app.get(img)
            results = []
            for face in faces:
                results.append({
                    "bbox": face.bbox.tolist(), # [left, top, right, bottom]
                    "kps": face.kps.tolist(), # Keypoints
                    "embedding": face.embedding.tolist(), # 512-d float
                    "det_score": float(face.det_score),
                    "age": int(face.age) if hasattr(face, 'age') else None,
                    "gender": int(face.gender) if hasattr(face, 'gender') else None
                })
            return results
        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            return []

    def extract_semantic_features(self, image_bytes: bytes) -> List[float]:
        """
        Extract OpenCLIP image embedding (512-d vector).
        """
        if not self.clip_model or not self.clip_preprocess:
            return []
            
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            processed_image = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.clip_model.encode_image(processed_image)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                
            return image_features[0].cpu().numpy().tolist()
        except Exception as e:
            logger.error(f"Semantic feature extraction failed: {e}")
            return []

    def cluster_embeddings(self, embeddings: List[List[float]], min_cluster_size: int = 2) -> List[int]:
        """
        Cluster facial or semantic embeddings using HDBSCAN.
        Returns cluster labels for each embedding (-1 means noise/unclustered).
        """
        try:
            import hdbscan
            
            if not embeddings or len(embeddings) < min_cluster_size:
                return [-1] * len(embeddings)
                
            np_embeddings = np.array(embeddings, dtype=np.float32)
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean', cluster_selection_method='eom')
            cluster_labels = clusterer.fit_predict(np_embeddings)
            
            return cluster_labels.tolist()
        except ImportError:
            logger.error("HDBSCAN not installed. Please install hdbscan.")
            return [-1] * len(embeddings)
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return [-1] * len(embeddings)

# Singleton
smart_organize_service = None

def get_smart_organize_service() -> SmartOrganizeService:
    global smart_organize_service
    if smart_organize_service is None:
        smart_organize_service = SmartOrganizeService()
    return smart_organize_service
