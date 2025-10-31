import uuid
from fastapi import UploadFile
from typing_extensions import Self
from ....core.use_cases import UseCaseProtocol
from ..services.file_analizator import FileAnalizatorServiceProtocol
from ..schemas import FileProcessingResultReadSchema


class GetFileAnalysisUseCaseProtocol(UseCaseProtocol[FileProcessingResultReadSchema]):
    async def __call__(self: Self, task_id: uuid.UUID) -> FileProcessingResultReadSchema:
        ...


class GetFileAnalysisUseCase(GetFileAnalysisUseCaseProtocol):
    def __init__(self: Self, file_service: FileAnalizatorServiceProtocol):
        self.file_service = file_service

    async def __call__(self: Self, task_id: uuid.UUID) -> FileProcessingResultReadSchema:
        return await self.file_service.get_analyzes_result(task_id)