from fastapi import Depends
from ...core.db import AsyncSession, get_async_session
from ..files.services.file_managment_service import FileManagmentServiceProtocol
from ..files.depends import get_file_managment_service
from ..analyzer.services.analyzer import AnalyzerServiceProtocol
from ..analyzer.depends import get_analyzer_service
from .repositories.file_processing import FileProcessingRepositoryProtocol, FileProcessingRepository
from .services.file_analizator import FileAnalizatorServiceProtocol, FileAnalizatorService
from .use_case.create import CreateFileAnalysisUseCaseProtocol, CreateFileAnalysisUseCase
from .use_case.get import GetFileAnalysisUseCaseProtocol, GetFileAnalysisUseCase

def __get_file_processing_repository(
    session: AsyncSession = Depends(get_async_session),
) -> FileProcessingRepositoryProtocol:
    return FileProcessingRepository(session=session)

def get_file_analizator_service(
    file_processing_repository: FileProcessingRepositoryProtocol = Depends(__get_file_processing_repository),
    file_service: FileManagmentServiceProtocol = Depends(get_file_managment_service),
    analyzer_service: AnalyzerServiceProtocol = Depends(get_analyzer_service),
) -> FileAnalizatorServiceProtocol:
    return FileAnalizatorService(
        file_processing_repository=file_processing_repository,
        file_service=file_service,
        analyzer_service=analyzer_service,
    )

def get_create_file_analysis_use_case(
    file_analizator_service: FileAnalizatorServiceProtocol = Depends(get_file_analizator_service),
) -> CreateFileAnalysisUseCaseProtocol:
    return CreateFileAnalysisUseCase(file_service=file_analizator_service)

def get_get_file_analysis_use_case(
    file_analizator_service: FileAnalizatorServiceProtocol = Depends(get_file_analizator_service),
) -> GetFileAnalysisUseCaseProtocol:
    return GetFileAnalysisUseCase(file_service=file_analizator_service)