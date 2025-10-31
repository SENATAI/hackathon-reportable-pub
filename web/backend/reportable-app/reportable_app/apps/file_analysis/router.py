import uuid
from fastapi import APIRouter, Depends, Request, HTTPException, Path
from .schemas import FileProcessingResultReadSchema
from .use_case.create import CreateFileAnalysisUseCaseProtocol
from .use_case.get import GetFileAnalysisUseCaseProtocol
from .depends import (
    get_create_file_analysis_use_case,
    get_get_file_analysis_use_case
)
router = APIRouter(prefix='/api/analyzer', tags=['Analyzer'])


@router.post('/analyze/', response_model=FileProcessingResultReadSchema, status_code=201)
async def analyze_file(
    request: Request,
    use_case: CreateFileAnalysisUseCaseProtocol = Depends(get_create_file_analysis_use_case)
) -> FileProcessingResultReadSchema:
    form = await request.form()
    file = form.get("file") 

    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    return await use_case(file)


@router.get('/{task_id}', response_model=FileProcessingResultReadSchema)
async def get_analysis_result(
    task_id: uuid.UUID = Path(..., description="The ID of the analysis task"),
    use_case: GetFileAnalysisUseCaseProtocol = Depends(get_get_file_analysis_use_case)
) -> FileProcessingResultReadSchema:
    return await use_case(task_id)