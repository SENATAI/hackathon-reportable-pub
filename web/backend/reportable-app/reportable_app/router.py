"""
Основной модуль для роутов приложения.
"""

from fastapi import FastAPI

from .apps.files.router import router as files_router
from .apps.file_analysis.router import router as analyzer_router


def apply_routes(app: FastAPI) -> FastAPI:
    """
    Применяем роуты приложения.
    """

    app.include_router(files_router)
    app.include_router(analyzer_router)
    return app