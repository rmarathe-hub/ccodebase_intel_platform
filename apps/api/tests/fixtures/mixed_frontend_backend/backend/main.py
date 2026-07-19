"""FastAPI backend for the mixed frontend/backend fixture."""

from fastapi import APIRouter

from .models import Item
from .services import compute_score, format_label

router = APIRouter()


@router.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    label = format_label(f"item-{item_id}")
    score = compute_score(item_id)
    return Item(id=score, name=label)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
