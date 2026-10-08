from routes import data, base
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings, Settings
from stores.LLM import LLMProviderFactory

# instead of app.on_event('startup')
# @asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # initialize mongoDB
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    # initialize LLM models
    llm_provider_factory = LLMProviderFactory(settings)
    app.generation_client = llm_provider_factory.create(provider_name=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID) 
    
    app.embedding_client = llm_provider_factory.create(provider_name=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBDEDING_MODEL_ID, embedding_size=settings.EMBDEDING_MODEL_SIZE)
    
    yield
    app.mongo_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)