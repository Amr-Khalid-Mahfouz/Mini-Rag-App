from .BaseDataModel import BaseDataModel
from models.db_schemas import Project
from models import DBEnum

class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client: object):

        super().__init__(db_client=db_client)
        self.collection = db_client[DBEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        """function to create an instance of this class instead of __init__, since we need to use async"""
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    # applies indexing to the database 
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        
        if DBEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DBEnum.COLLECTION_PROJECT_NAME.value]
            indices = Project.get_indices()

            for index in indices:
                await self.collection.create_index(
                    index['key'],
                    name=index['name'],
                    unique=index['unique']
                )

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True)) # model_dump = to_dict in pydantic 
        project.id = result.inserted_id
        return project

    async def get_project_or_create(self, project_id: str):
        record = await self.collection.find_one(
            {"project_id":project_id}
            )
        
        # create a new project with said id
        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)

            return project
        
        # ** creates a Project object with the dict values of record
        return Project(**record) 

    # a "get_all" function needs pagination, since the more projects we have the slower the function gets
    # so we need to tell the function to get the data in chunks/pages
    async def get_all_projects(self, page:int=1, page_size: int=10):
        
        # count how many documents we have
        total_documents = await self.collection.count_documents({}) # {} is a filter

        # calculate number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        skip_count = (page-1) * page_size
        cursor = self.collection.find({}).skip(skip_count).limit(page_size)

        projects = []
        async for doc in cursor:
            projects.append(
                Project(**doc)
            )

        return projects, total_pages