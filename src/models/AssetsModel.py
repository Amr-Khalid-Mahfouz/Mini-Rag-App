from .BaseDataModel import BaseDataModel
from models.db_schemas import Asset
from models import DBEnum

class AssetModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = db_client[DBEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        """function to create an instance of this class instead of __init__, since we need to use async"""
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    # applies indexing to the database 
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        
        if DBEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DBEnum.COLLECTION_ASSET_NAME.value]
            indices = Asset.get_indices()

            for index in indices:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )

    async def create_asset(self, Asset):
        pass