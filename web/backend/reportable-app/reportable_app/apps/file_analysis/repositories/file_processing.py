from ....core.repositories.base_repository import BaseRepositoryImpl
from ..models import FileProcessingResult
from ..schemas import FileProcessingResultCreateSchema, FileProcessingResultReadSchema, FileProcessingResultUpdateSchema

class FileProcessingRepositoryProtocol(
    BaseRepositoryImpl[
        FileProcessingResult,
        FileProcessingResultReadSchema,
        FileProcessingResultCreateSchema,
        FileProcessingResultUpdateSchema
    ]
    ):
    pass

class FileProcessingRepository(FileProcessingRepositoryProtocol):
    pass