from ..LLM.providers import QdrantDBProvider
from ...helpers.config import Settings
from vectordb import VectorDBEnum
from controllers import BaseController

class VectorDBProviderFactory:
    def __init__(self, config: Settings):
        self.config = config
        self.base_controller = BaseController()
    
    def create(self, provider: str):
        if provider == VectorDBEnum.QDRANT.value:
            return QdrantDBProvider(
                db_path= self.base_controller.get_db_path(db_path = self.config.VECTOR_DB_PATH),
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )
        return None
            