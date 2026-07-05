"""Collection (saved-favourites) DTOs."""

from datetime import datetime

from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class CollectionRename(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class AddItemRequest(BaseModel):
    item_id: int


class SavedItem(BaseModel):
    item_id: int
    title: str
    description: str = ""
    image_url: str | None = None
    source_url: str | None = None
    category: str
    metadata: dict = Field(default_factory=dict)


class CollectionOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    items: list[SavedItem] = Field(default_factory=list)
