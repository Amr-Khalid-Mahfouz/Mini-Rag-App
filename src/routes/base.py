from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]    
)

@base_router.get("/") # default route
async def welcome(app_settings: Settings=Depends(get_settings)): # run this function only if this dependency is valid/usable
    app_name = Settings.APP_NAME
    app_ver = Settings.APP_VERSION
    
    return {
        'app_name' : app_name,
        'app_version': app_ver
    }
