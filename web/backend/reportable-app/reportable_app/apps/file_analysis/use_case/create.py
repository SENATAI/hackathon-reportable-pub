from fastapi import UploadFile
from typing_extensions import Self
from ....core.use_cases import UseCaseProtocol
from ..services.file_analizator import FileAnalizatorServiceProtocol
from ..schemas import FileProcessingResultReadSchema


class CreateFileAnalysisUseCaseProtocol(UseCaseProtocol[FileProcessingResultReadSchema]):

    async def __call__(self: Self, file: UploadFile) -> FileProcessingResultReadSchema:
        ...


class CreateFileAnalysisUseCase(CreateFileAnalysisUseCaseProtocol):

    def __init__(self: Self, file_service: FileAnalizatorServiceProtocol):
        self.file_service = file_service

    async def __call__(self: Self, file: UploadFile) -> FileProcessingResultReadSchema:
        return await self.file_service.analyze_and_store(file)