from stores.vectordb import DistanceMethodEnum, VectordbInterface
from typing import List
from qdrant_client import QdrantClient, models
import logging
import json

class QdrantDBProvider(VectordbInterface):
    def __init__(self, db_path: str,
                distance_method: str
                ):
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        if distance_method == DistanceMethodEnum.DOT.value:
            self.distance_method = models.Distance.DOT
        
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def create_collection(self, 
                        collection_name: str,
                        embedding_size: int,
                        do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        if not self.is_collection(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method),
                )
            return True
        return True
    
    def delete_collection(self, collection_name: str):
        if self.is_collection(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        info = self.client.get_collection(collection_name=collection_name)

        return json.loads(
            json.dumps(info, default=lambda x: x.__dict__)
        )

    def insert_one(self, 
                collection_name: str,
                text: str, vector: list,
                metadata: dict = None,
                record_id: dict = None):
        if not self.is_collection(collection_name=collection_name):
            self.logger.error(f"insertion failed, collection {collection_name}, does not exist yet.")
            return False

        try:
            _ = self.client.upload_points(
                collection_name=collection_name,
                points= models.PointStruct(
                    id=record_id,
                    vector=vector,
                    payload={
                        "metadata":metadata,
                        "text":text}
                )
            )
        except Exception as e:
            self.logger.error(f"error while inserting record: {e}.")
            return False

        return True

    def insert_many(self, 
                collection_name: str,
                text: list, vector: list,
                metadata: list = None,
                record_ids: list = None,
                batch_size: int = 50):
        if not metadata:
            metadata = [None] * len(text)
        if not record_ids:
            record_ids = list(range(0, len(text)))

        for i in range(0, len(text), batch_size):
            batch_end = i + batch_size
            
            batch_texts = text[i:batch_end]
            batch_vectors = vector[i:batch_end]
            batch_metadatas = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_points = [
                models.PointStruct(
                    id=batch_record_ids[x],
                    vector = batch_vectors[x],
                    payload = {
                        "text": batch_texts[x],
                        "metadata": batch_metadatas[x]
                    }
                )
                for x in range(len(batch_texts))
            ]
            try:
                self.client.upload_points(
                    collection_name=collection_name,
                    points=batch_points,
                ) 
                
            except Exception as e:
                self.logger.error(f"error while inserting batch: {e}.")
                return False

        return True

    def search_by_vector(self, 
                        collection_name: str,
                        vector: list,
                        limit: int):

        query_res = self.client.query_points(
                    collection_name=collection_name,
                    query=vector,
                    limit=limit,
                    with_payload=True
                )
        
        return query_res