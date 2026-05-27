"""
state.py — Global in-memory shared state with TTL-based cleanup.
Images are stored with a timestamp and automatically evicted after CLEANUP_HOURS.
Max 100 images in cache to prevent unbounded memory growth.
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta, timezone

log = logging.getLogger("albumai.state")

_images: Dict[str, Dict[str, Any]] = {}

MAX_IMAGES = 100
TTL_HOURS = 24


def _evict_expired():
    """Remove images older than TTL_HOURS. Use timezone-aware UTC datetimes."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=TTL_HOURS)
    expired = [k for k, v in _images.items() if v.get("created_at", now) < cutoff]
    for k in expired:
        _images.pop(k, None)
        log.info(f"Evicted expired image: {k}")


def _evict_oldest_if_full():
    """If at capacity, remove the oldest entry."""
    if len(_images) >= MAX_IMAGES:
        now = datetime.now(timezone.utc)
        oldest_key = min(_images, key=lambda k: _images[k].get("created_at", now))
        _images.pop(oldest_key, None)
        log.warning(f"Cache full — evicted oldest image: {oldest_key}")


def store_image(image_id: str, data: Dict[str, Any]):
    """Store an image with a creation timestamp."""
    _evict_expired()
    _evict_oldest_if_full()
    data["created_at"] = datetime.now(timezone.utc)
    _images[image_id] = data


def get_image(image_id: str) -> Dict[str, Any] | None:
    """Retrieve an image from cache."""
    return _images.get(image_id)


def delete_image(image_id: str):
    """Explicitly remove an image from cache (e.g., after crop export)."""
    removed = _images.pop(image_id, None)
    if removed:
        log.info(f"Deleted image from cache: {image_id}")


async def periodic_cleanup(interval_seconds: int = 3600):
    """Background task that runs every hour to clean expired images."""
    while True:
        await asyncio.sleep(interval_seconds)
        before = len(_images)
        _evict_expired()
        after = len(_images)
        if before != after:
            log.info(f"Cleanup: removed {before - after} expired images. Cache size: {after}")
