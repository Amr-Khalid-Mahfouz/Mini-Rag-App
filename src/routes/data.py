from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal, AssetType
import aiofiles
import os
from schemas import ProcessRequest
from models import ProjectModel, ChunkModel, AssetModel
from models.db_schemas import DataChunk, Asset

data_router = APIRouter(
    prefix="/api/data",
    tags=["api_v1", "data"]
)

@data_router.post('/upload/{project_id}')
async def upload_data(
    request: Request,
    project_id: str, 
    file: UploadFile,
    app_settings: Settings=Depends(get_settings)):

    # get the project model from the FastAPI app object
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_project_or_create(
        project_id=project_id
        )
    
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
    
    # add Asset to the database
    assets_model = await AssetModel.create_instance(db_client=request.app.db_client)
    asset = Asset(
            asset_project_id=project.id,
            asset_type=AssetType.FILE.value,
            asset_name=file_id,
            asset_size=os.path.getsize(file_path)
        )
    asset_record = await assets_model.create_asset(asset=asset)

    return JSONResponse(
        content={
            "signal":ResponseSignal.FILE_UPLOAD_SUCCEDED.value,
            'file_id': str(asset_record.id),
            'project_id': str(project.id)
            }
        )

@data_router.post('/process/{project_id}')
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest
    ):

    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    do_reset = process_request.do_reset
    overlap_size = process_request.overlap_size

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_project_or_create(
            project_id=project_id
            )

    process_controller = ProcessController(project_id)

    file_content = process_controller.get_file_content(file_id)
    
    chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        chunk_overlap=overlap_size,)

    if chunks is None or len(chunks) == 0: # error
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value,
            }
        )
    
    chunk_records = [
        DataChunk( 
            chunk_text= chunk.page_content,
            meta_data= chunk.metadata, 
            chunk_order=i+1,
            chunk_project_id=project.id
            )
        for i, chunk in enumerate(chunks)
    ]

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    deleted_chunks = 0
    if do_reset:
        deleted_chunks = await chunk_model.delete_chunks_by_project_id(project.id)
    
    no_records = await chunk_model.insert_many_chunks(chunk_records)
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_PROCESSING_SUCCEDED.value,
            "inserted_chunks": no_records,
            "deleted_chunks": deleted_chunks
        }
    )