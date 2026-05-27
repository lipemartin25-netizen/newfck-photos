from datetime import datetime, timedelta, timezone
import pytest

from app.core import state


def test_store_and_get_image():
    state._images.clear()
    state.store_image("id1", {"value": 1})
    info = state.get_image("id1")
    assert info is not None
    assert info["value"] == 1


def test_evict_expired():
    state._images.clear()
    old = {
        "created_at": datetime.now(timezone.utc) - timedelta(hours=state.TTL_HOURS + 1)
    }
    state._images["old"] = old
    state._evict_expired()
    assert "old" not in state._images


def test_evict_oldest_if_full():
    state._images.clear()
    # Populate with MAX_IMAGES entries
    for i in range(state.MAX_IMAGES):
        state._images[f"id{i}"] = {"created_at": datetime.now(timezone.utc) - timedelta(seconds=i)}
    # Add new image via store_image - should evict one to keep size <= MAX_IMAGES
    state.store_image("new", {"value": 42})
    assert len(state._images) <= state.MAX_IMAGES
    assert "new" in state._images
