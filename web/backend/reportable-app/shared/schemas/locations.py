import uuid
from pydantic import BaseModel, Field
from .base import TimestampMixin

class LocationBaseSchema(BaseModel):
    name: str = Field(..., max_length=128, description="Name of the location")
    slug: str = Field(..., max_length=128, description="Unique slug for the location")

class LocationReadSchema(LocationBaseSchema, TimestampMixin):
    id: uuid.UUID = Field(..., description="Unique identifier of the location")
