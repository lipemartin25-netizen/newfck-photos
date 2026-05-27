"""
faces.py — InsightFace clustering endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.state import _images

router = APIRouter(prefix="/api/faces", tags=["faces"])


class FaceClusterRequest(BaseModel):
    image_ids: list[str]
    min_cluster_size: int = 3


@router.post("/cluster")
async def cluster_faces(req: FaceClusterRequest):
    from app.services.face_clustering import FaceClusterer
    try:
        clusterer = FaceClusterer()
    except (ImportError, Exception) as e:
        # Fallback graceful
        return {"ok": False, "error": str(e), "clusters": {}}
        
    embeddings = []
    mapped_keys = []
    
    for img_id in req.image_ids:
        if img_id in _images:
            img = _images[img_id]["image"]
            res = clusterer.extract_from_image(img)
            for face in res:
                embeddings.append(face["embedding"])
                mapped_keys.append({"image_id": img_id, "bbox": face["bbox"]})
                
    if not embeddings:
        return {"ok": True, "clusters": {}}
        
    clusters = clusterer.cluster(embeddings, min_cluster_size=req.min_cluster_size)
    
    formatted_clusters = {}
    for cluster_id, indices in clusters.items():
        formatted_clusters[str(cluster_id)] = [mapped_keys[i] for i in indices]
        
    return {"ok": True, "clusters": formatted_clusters}
