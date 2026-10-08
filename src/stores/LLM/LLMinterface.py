from abc import ABC,abstractmethod # instead of abstractclassmethod we use both @classmethod and @abstractmethod below it

class LLMInterface(ABC):
    @classmethod
    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass
    @classmethod
    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        pass

    @classmethod
    @abstractmethod
    def embed_text(self, text: str, document_type: str = None):
        pass
        
    @classmethod
    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list, max_output_tokens: int, temperature: float = None):
        pass

    @classmethod
    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass