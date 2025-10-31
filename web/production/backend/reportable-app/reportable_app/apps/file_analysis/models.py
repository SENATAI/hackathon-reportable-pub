import uuid
from typing import Optional
import sqlalchemy as sa
from shared.models import TimestampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn
from sqlalchemy.dialects.postgresql import UUID, JSON 
from ...core.db import Base


class FileProcessingResult(Base, TimestampMixin):
    __tablename__ = "file_processing_results"

    input_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )
    result_table: MappedColumn[Optional[dict]] = mapped_column(
        JSON,  
        nullable=True
    )