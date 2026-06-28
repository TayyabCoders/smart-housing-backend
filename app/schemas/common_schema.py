from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

T = TypeVar('T')


class BBox(BaseModel):
    """Bounding box for detection results"""
    x: float
    y: float
    width: float
    height: float

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic paginated response wrapper"""
    items: list[T]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)
