"""
dedup.py — Perceptual hash near-duplicate detection.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.state import _images

router = APIRouter(prefix="/api/dedup", tags=["dedup"])


class DedupRequest(BaseModel):
    image_ids: list[str]
    threshold: int = 5


@router.post("/find")
async def find_duplicates(req: DedupRequest):
    from app.services.dedup import Deduplicator
    try:
        dedup = Deduplicator(threshold=req.threshold)
    except (ImportError, Exception) as e:
        return {"ok": False, "error": str(e), "duplicates": []}
        
    img_dict = {}
    for img_id in req.image_ids:
        if img_id in _images:
            img_dict[img_id] = _images[img_id]["image"]
            
    if not img_dict:
        return {"ok": True, "duplicates": []}
        
    hashes = dedup.compute_hashes(img_dict)
    dups = dedup.find_duplicates(hashes)
    
    return {"ok": True, "duplicates": dups}
