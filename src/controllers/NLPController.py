from .BaseController import BaseController
from models.db_schemas import Project, DataChunk
from typing import List
from models.enums import DocumentType
from stores.vectordb import VectordbInterface
from stores.LLM import LLMInterface
import asyncio

class NLPController(BaseController):

    def __init__(self, vectodb_client: VectordbInterface, generation_client: LLMInterface, embedding_client: LLMInterface):
        super().__init__()

        self.vectodb_client = vectodb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

    def create_Collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_Collection_name(project.project_id)
        return self.vectodb_client.delete_collection(collection_name)

    def get_vector_collection_info(self, project: Project) -> dict:
        collection_name = self.create_Collection_name(project.project_id)
        return self.vectodb_client.get_collection_info(collection_name)

    def index_into_vectordb(self, project: Project, chunks: List[DataChunk], record_ids : List[int], do_reset: bool = 0):
        collection_name = self.create_Collection_name(project.project_id)

        # manage Items
        texts = [x.chunk_text for x in chunks]
        metadatas = [x.meta_data for x in chunks]
        vectors = self.embedding_client.embed_text(text=texts, document_type=DocumentType.DOCUMENT.value)    

        # create collection if no one exists
        check = self.vectodb_client.create_collection(
            collection_name=collection_name, 
            embedding_size=self.embedding_client.embedding_size,
            do_reset = do_reset,
            )
        
        # insert into vectorDB
        try:
            _ = self.vectodb_client.insert_many(collection_name=collection_name, text=texts, vector=vectors, metadata=metadatas, record_ids=record_ids)
        except Exception as e:
            raise ValueError("Error in insertion")

        return True

    def search_vectordb_collection(self, project: Project, text: str, limit: int  = 10):
        # get collection name
        collection_name = self.create_Collection_name(project_id=project.project_id)
  
        # embed text
        embedding = self.embedding_client.embed_text([text], DocumentType.DOCUMENT)[0]

        # do semantic search
        results = self.vectodb_client.search_by_vector(
            collection_name=collection_name,
            vector=embedding,
            limit=limit
        )

        return [
            {
                "text": result.payload.text,
                "score": result.score
                }
            for result in results
                ]
        