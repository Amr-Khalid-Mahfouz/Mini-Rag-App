from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from models import DBEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = db_client[DBEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_unset=True))
        chunk._id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one(
            {"_id": ObjectId(chunk_id)}
            )

        if result is None:
            return None

        return DataChunk(**result)

    # batch written 
    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        # we will insert the chunks in batches of "batch_size"
        for x in range(0, len(chunks), batch_size):
            curr_batch = chunks[x:x+batch_size]

            # turn each chunk into a dict and wrap it in an InsertOne operation
            # which describes the insert without performing it yet == a list of 100 pending ops.
            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in curr_batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id":project_id})
        return result.deleted_count