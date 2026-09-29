from routes import data, base
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings, Settings

# instead of app.on_event('startup')
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    yield
    app.mongo_conn.close()

app = FastAPI(lifespan=life)

app.include_router(base.base_router)
app.include_router(data.data_router)