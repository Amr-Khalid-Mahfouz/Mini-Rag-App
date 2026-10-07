from .BaseDataModel import BaseDataModel
from models.db_schemas import Asset
from models import DBEnum
from bson import ObjectId

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

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        
        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        cursor = await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type
            }).to_list(length=None)
        
        assets = []
        for doc in cursor:
            assets.append(
                Asset(**doc)
            )

        return assets

    async def get_asset_by_asset_name(self, asset_name: str, asset_project_id: str):
        result = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name
        })

        if result:
            return Asset(**result)
        return None