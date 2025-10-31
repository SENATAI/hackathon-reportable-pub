import uuid
from typing import Optional
from shared.schemas.base import CreateBaseModel, UpdateBaseModel, TimestampMixin
from shared.schemas.files import FileBaseSchema


class FileCreateDBSchema(FileBaseSchema, CreateBaseModel):
    path: str
    creator_user_id: Optional[uuid.UUID] = None
    size: int
    content_type: str
    filename: str


class FileUpdateSchema(FileBaseSchema, UpdateBaseModel):
    pass


class FileUpdateDBSchema(FileUpdateSchema):
    path: str


class FileReadDBSchema(FileBaseSchema, TimestampMixin):
    id: uuid.UUID
    path: str
    creator_user_id: Optional[uuid.UUID] = None
    size: int
    content_type: str
    filename: str

