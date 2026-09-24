from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal 
import aiofiles
import os
from schemas import ProcessRequest

data_router = APIRouter(
    prefix="/api/data",
    tags=["api_v1", "data"]
)

@data_router.post('/upload/{project_id}')
async def upload_data(
    project_id: str, 
    file: UploadFile,
    app_settings: Settings=Depends(get_settings)):
    
    # validate the file
    data_conroller = DataController()
    is_valid, message = data_conroller.validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":message
            }
        )

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    random_file_name, file_id = data_conroller.generate_unique_file_path(file.filename, project_id)
    file_path = os.path.join(project_dir_path, random_file_name)

    # asyncronized byte writing of the file to file path 
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk) 
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
        
    return JSONResponse(
        content={
            "signal":ResponseSignal.FILE_UPLOAD_SUCCEDED.value,
            'file_id': file_id
            }
        )

@data_router.post('/process/{project_id}')
async def process_endpoint(
    project_id: str,
    process_request: ProcessRequest):
    
    file_id = process_request.file_id
    process_controller = ProcessController(project_id)

    file_content = process_controller.get_file_content(file_id)
    
    chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=process_request.chunk_size,
        chunk_overlap=process_request.overlap_size,)

    if chunks is None or len(chunks) == 0: # error
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value,
            }
        )
    
    return chunks