from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_EXTENSIONS: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    
    # Mongo Config
    MONGODB_URL: str
    MONGODB_DATABASE: str
    
    # LLM Config
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID: str = None
    EMBDEDING_MODEL_ID: str = None
    EMBDEDING_MODEL_SIZE: str = None

    GENERATION_DEFUALT_TEMPERATURE: int = None
    DEFUALT_GENERATION_MAX_CHAR: int = None
    DEFAULT_INPUT_MAX_CHAR: int = None

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
