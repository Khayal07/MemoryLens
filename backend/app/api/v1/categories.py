"""Category listing — drives the category-select screen."""

from fastapi import APIRouter

from app.domain.categories import CATEGORIES

router = APIRouter()


@router.get("/categories")
def list_categories() -> list[dict]:
    return [
        {
            "key": c["key"],
            "display_name": c["display_name"],
            "icon": c["config"].get("icon"),
        }
        for c in CATEGORIES
    ]
