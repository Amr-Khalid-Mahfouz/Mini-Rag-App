from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from models import ProjectModel, ChunkModel
import logging
from helpers.config import get_settings, Settings
from controllers import NLPController
from models import ResponseSignal, AssetType
from schemas import PushRequest, SearchRequest
from models.db_schemas import DataChunk, Asset, Project

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=['nlp', 'api_v1']
)

@nlp_router.post('/index/push/{project_id}')
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    
    do_reset = push_request.do_reset
    # get the project model from the FastAPI app object
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_project_or_create(
        project_id=project_id
        )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PORJECT_NOT_FOUND.value
            }
        )

    nlp_controller = NLPController(
        vectodb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    has_records = True
    page_number = 1
    insertion_count = 0
    idx = 0

    while has_records:
        # get a page of chunks
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_number=page_number, page_size=10)

        # we should reset the collection the first time we insert only
        if page_number > 1:
            do_reset  = 0

        if len(page_chunks):
            page_number += 1
        
        # nothing returned
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(idx, idx+len(page_chunks)))
        idx += len(page_chunks)
         
        # Push the current Page
        inserted = nlp_controller.index_into_vectordb(project=project, chunks=page_chunks, do_reset=do_reset, record_ids=chunk_ids)

        if not inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content= {
                "signal": ResponseSignal.INSERTION_INTO_VECTORDB_ERROR.value
                }        
            )

        insertion_count += len(page_chunks)

    return JSONResponse(
        content= {
            "signal": ResponseSignal.INSERTION_INTO_VECTORDB_SUCCEEDED.value,
            "insertion_count": insertion_count
        }
    )

@nlp_router.get('/index/info/{project_id}')
async def get_project_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(request.app.db_client)

    project =  await project_model.get_project_or_create(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PORJECT_NOT_FOUND.value
            }
        )

    nlp_controller = NLPController(
        vectodb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)

    info = nlp_controller.get_vector_collection_info(project)

    return JSONResponse(
        content= {
            "signal": ResponseSignal.COLLECTION_SEARCH_SUCCEEDED.value,
            "collection_info": info
        }
    )

@nlp_router.post('/index/search/{project_id}')
async def search(request: Request, project_id: str, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create(project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PORJECT_NOT_FOUND.value
            }
        )

    nlp_controller = NLPController(
        vectodb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client)

    res = nlp_controller.search_vectordb_collection(project, search_request.text, search_request.limit)

    if not res or len(res) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content= {
                "signal": ResponseSignal.COLLECTION_SEARCH_FAILED.value
            }
        )        

    return JSONResponse(
        content= {
            "signal": ResponseSignal.COLLECTION_SEARCH_SUCCEEDED.value,
            "most_similar_texts": res
        }
    )