import uuid
from fastapi import UploadFile
from typing import Protocol
from typing_extensions import Self
from shared.schemas.files import FileCreateSchema
from ...analyzer.services.analyzer import AnalyzerServiceProtocol
from ...files.services.file_managment_service import FileManagmentServiceProtocol
from ..repositories.file_processing import FileProcessingRepositoryProtocol
from ..schemas import FileProcessingResultCreateSchema, FileProcessingResultReadSchema

class FileAnalizatorServiceProtocol(Protocol):
    file_service: FileManagmentServiceProtocol
    analyzer_service: AnalyzerServiceProtocol

    async def analyze_and_store(self: Self, file: UploadFile) -> FileProcessingResultReadSchema:
        ...

    async def get_analyzes_result(self: Self, task_id: uuid.UUID) -> FileProcessingResultReadSchema:
        ...

class FileAnalizatorService(FileAnalizatorServiceProtocol):
    def __init__(self: Self, 
                 file_processing_repository: FileProcessingRepositoryProtocol,
                 file_service: FileManagmentServiceProtocol, 
                 analyzer_service: AnalyzerServiceProtocol,
                 ):
        self.file_processing_repository = file_processing_repository
        self.file_service = file_service
        self.analyzer_service = analyzer_service

    async def analyze_and_store(self: Self, file: UploadFile) -> FileProcessingResultReadSchema:
        # Сохраняем любой файл, который пришёл к нам с помощью file_service
        content = await file.read()
        created_file = await self.file_service.create_from_content(FileCreateSchema(), content, file.filename)


        # Потом анализируем файл
        analysis_result = await self.analyzer_service.analyze(content)

        
        file_result = FileProcessingResultCreateSchema(
            input_file_id=created_file.id,
            result_table=analysis_result
        )

        return await self.file_processing_repository.create(file_result)
    
    async def get_analyzes_result(self: Self, task_id: uuid.UUID) -> FileProcessingResultReadSchema:
        return await self.file_processing_repository.get(task_id)