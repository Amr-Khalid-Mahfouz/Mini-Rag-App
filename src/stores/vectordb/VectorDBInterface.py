from abc import ABC, abstractmethod
from typing import List
from models.db_schemas import RetrievedDocument

class VectordbInterface(ABC):

    @classmethod
    @abstractmethod
    def connect(self):
        pass

    @classmethod
    @abstractmethod
    def disconnect(self):
        pass

    @classmethod
    @abstractmethod
    def is_collection(self, collection_name: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def create_collection(self, 
                        collection_name: str,
                        embedding_size: int,
                        do_reset: bool = False):
        pass    
    
    @classmethod
    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @classmethod
    @abstractmethod
    def list_all_collections(self) -> List:
        pass

    @classmethod
    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass

    @classmethod
    @abstractmethod
    def insert_one(self, 
                collection_name: str,
                text: str, vector: list,
                metadata: dict = None,
                record_id: dict = None):
        pass

    @classmethod
    @abstractmethod
    def insert_many(self, 
                collection_name: list,
                text: list, vector: list,
                metadata: list = None,
                record_ids: list = None,
                batch_size: int = 50):
        pass

    @classmethod
    @abstractmethod
    def search_by_vector(self, 
                        collection_name: str,
                        vector: list,
                        limit: int) -> List[RetrievedDocument]:
        pass