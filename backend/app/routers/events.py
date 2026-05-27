"""
events.py — OpenCLIP event clustering and semantic search.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.state import _images
import numpy as np

router = APIRouter(prefix="/api/events", tags=["events"])


class EventClusterRequest(BaseModel):
    image_ids: list[str]
    min_cluster: int = 3


class SemanticSearchRequest(BaseModel):
    query: str
    image_ids: list[str]


@router.post("/cluster")
async def cluster_events(req: EventClusterRequest):
    from app.services.event_clusterer import EventClusterer
    try:
        clusterer = EventClusterer()
    except (ImportError, Exception) as e:
        return {"ok": False, "error": str(e), "clusters": {}}
        
    embeddings = []
    mapped_keys = []
    
    for img_id in req.image_ids:
        if img_id in _images:
            img = _images[img_id]["image"]
            emb = clusterer.embed_image(img)
            embeddings.append(emb)
            mapped_keys.append(img_id)
            
    if not embeddings:
        return {"ok": True, "clusters": {}}
        
    clusters = clusterer.cluster_events(np.array(embeddings), min_cluster=req.min_cluster)
    
    formatted = {}
    for cid, indices in clusters.items():
        formatted[str(cid)] = [mapped_keys[i] for i in indices]
        
    return {"ok": True, "clusters": formatted}


@router.post("/search")
async def semantic_search(req: SemanticSearchRequest):
    from app.services.event_clusterer import EventClusterer
    try:
        clusterer = EventClusterer()
    except (ImportError, Exception) as e:
        raise HTTPException(501, f"CLIP not loaded: {e}")
        
    embeddings = []
    mapped_keys = []
    
    for img_id in req.image_ids:
        if img_id in _images:
            img = _images[img_id]["image"]
            emb = clusterer.embed_image(img)
            embeddings.append(emb)
            mapped_keys.append(img_id)
            
    if not embeddings:
        return {"results": []}
        
    res = clusterer.semantic_search(req.query, np.array(embeddings), top_k=10)
    
    formatted = [{"image_id": mapped_keys[idx], "score": score} for idx, score in res]
    return {"results": formatted}
