from routes import data, base
from fastapi import FastAPI

app = FastAPI()

app.include_router(base.base_router)
app.include_router(data.data_router)