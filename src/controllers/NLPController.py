from .BaseController import BaseController
from models.db_schemas import Project, DataChunk
from typing import List
from models.enums import DocumentType
from stores.vectordb import VectordbInterface
from stores.LLM import LLMInterface
from models.db_schemas import RetrievedDocument
from stores.templates.template_parser import TemplateParser

class NLPController(BaseController):

    def __init__(self, vectodb_client: VectordbInterface,
                  generation_client: LLMInterface, 
                  embedding_client: LLMInterface,
                  template_parser: TemplateParser):
        super().__init__()

        self.vectodb_client = vectodb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

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

        if not results:
            return None

        return [
            RetrievedDocument(** {
                "text": result.payload["text"],
                "score": result.score
            })
                for result in results.points
            ]

    def answer_rag_question(self, project: Project, text: str, limit: int = 10):
        
        answer, full_prompt, chat_history = None, None, None 
        retrieved_documents = self.search_vectordb_collection(project, text, limit)

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history

        system_prompt = self.template_parser.get("rag", "system_prompt")
        
        document_prompts = "\n".join(
            [
            self.template_parser.get(group="rag",
                                key="document_prompt",
                                vars={
                                    "doc_num": idx + 1,
                                    "chunk_text": doc.text
                                      })

              for idx, doc in enumerate(retrieved_documents)
            ]
        )

        footer_prompt = self.template_parser.get("rag", "footer_prompt", vars={"user_query": text})

        full_prompt = "\n\n".join([document_prompts, footer_prompt])

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]

        answer = self.generation_client.generate_text(prompt=full_prompt, chat_history=chat_history)
        
        return answer, full_prompt, chat_history