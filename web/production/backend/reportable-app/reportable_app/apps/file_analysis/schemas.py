import uuid
from pydantic import BaseModel, Field
from shared.schemas.base import TimestampMixin, CreateBaseModel, UpdateBaseModel

class FileProcessingResultBaseSchema(BaseModel):
    input_file_id: uuid.UUID = Field(..., description="ID of the input file")
    result_table: dict = Field(..., description="Resulting data table from file processing")

class FileProcessingResultCreateSchema(FileProcessingResultBaseSchema, CreateBaseModel):
    pass

class FileProcessingResultUpdateSchema(FileProcessingResultBaseSchema, UpdateBaseModel):
    pass

class FileProcessingResultReadSchema(FileProcessingResultBaseSchema, TimestampMixin):
    id: uuid.UUID = Field(..., description="Unique identifier of the file processing result")