from fastapi import Depends
from ...settings import Settings, get_settings
from .services.analyzer import AnalyzerServiceProtocol, AnalyzerService

def get_analyzer_service(settings: Settings = Depends(get_settings)) -> AnalyzerServiceProtocol:
    return AnalyzerService(
        api_key=settings.llm.api_key,
        model_url=settings.llm.model_url,
        prompts_path=settings.llm.prompts_path,
        schema_path=settings.llm.schema_path   
    )
