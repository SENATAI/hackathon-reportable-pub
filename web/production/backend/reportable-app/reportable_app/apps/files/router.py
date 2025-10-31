import uuid
from fastapi import APIRouter, Depends, Path, Request
from shared.schemas.files import FileReadSchema, FileIdsSchema, FilesListReadSchema
from shared.schemas.auth import UserTokenDataReadSchema
from ...core.depends import get_user_token_payload
from .use_cases.create import CreateFileUseCaseProtocol
from .use_cases.delete import DeleteFileUseCaseProtocol
from .use_cases.get import GetFileUseCaseProtocol
from .use_cases.get_by_template import GetByTemplateFileUseCaseProtocol
from .use_cases.create_batch import CreateBatchFileUseCaseProtocol
from .use_cases.get_by_ids import GetIdsFileUseCaseProtocol
from .depends import (
    get_file_create_use_case,
    get_file_delete_use_case,
    get_file_get_by_template_use_case,
    get_file_get_use_case,
    get_file_create_batch_use_case,
    get_file_get_by_ids_use_case
)

router = APIRouter(prefix='/api/files', tags=['Files'])

# @router.post('/ids', response_model=FilesListReadSchema)
# async def get_by_ids(ids: FileIdsSchema, 
#                            use_case: GetIdsFileUseCaseProtocol = Depends(get_file_get_by_ids_use_case)
#                            ) -> FilesListReadSchema:
#     return await use_case(ids)

# @router.post('/', response_model=FileReadSchema, status_code=201)
# async def create(request: Request,
#                     token: UserTokenDataReadSchema = Depends(get_user_token_payload),
#                     use_case: CreateFileUseCaseProtocol = Depends(get_file_create_use_case), 
#                     ) -> FileReadSchema:
#     form = await request.form()
#     data = form["data"]
#     file = form["file"]
#     result = await use_case(data, file, token)

#     return result


# @router.post('/batch/', response_model=FilesListReadSchema, status_code=201)
# async def create_batch(request: Request,
#                        token: UserTokenDataReadSchema = Depends(get_user_token_payload),
#                        use_case: CreateBatchFileUseCaseProtocol = Depends(get_file_create_batch_use_case)
#                        ) -> FilesListReadSchema:
#     form = await request.form()
#     data = form["data"]
#     files = form.getlist("files")
#     result = await use_case(data, files, token)

#     return result


# @router.delete('/{file_id}', response_model=None, status_code=204)
# async def delete(file_id: uuid.UUID = Path(...), 
#                 token: UserTokenDataReadSchema = Depends(get_user_token_payload),
#                            use_case: DeleteFileUseCaseProtocol = Depends(get_file_delete_use_case)
#                            ) -> None:
    
#     await use_case(file_id, token)
#     return None


@router.get('/{file_id}', response_model=FileReadSchema)
async def get(file_id: uuid.UUID = Path(...), 
                           use_case: GetFileUseCaseProtocol = Depends(get_file_get_use_case)
                           ) -> FileReadSchema:
    return await use_case(file_id)


# @router.get('/template_name/{name}', response_model=FileReadSchema)
# async def get_by_template_name(name: str = Path(..., title="File Template Name", description="The template name of the file to retrieve"),
#                            use_case: GetByTemplateFileUseCaseProtocol = Depends(get_file_get_by_template_use_case)
#                            ) -> FileReadSchema:
#     return await use_case(name)

