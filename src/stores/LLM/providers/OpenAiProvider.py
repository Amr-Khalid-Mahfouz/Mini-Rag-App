from ..LLMinterface import LLMInterface
from openai import OpenAI
from models.enums import OpenAIEnUm
import logging

class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str,
                api_url: str = None,
                default_input_max_char: int = 1000,
                default_generation_max_char: int = 1000,
                temperature: float = 1.0):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_generation_max_char = default_generation_max_char
        self.default_input_max_char = default_input_max_char
        self.temperature = temperature

        self.generation_model_id = None
        
        self.enmbedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            api_url=self.api_url)

        self.logger = logging.logger(__name__) # file name
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.enmbedding_model_id = model_id
        self.embedding_size = embedding_size

    def embed_text(self, text: str, document_type: str):
        if not self.client:
            self.logger.error("OpenAI was not set")
            return None
        if not self.enmbedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None

        response = self.client.embeddings.create(
            model = self.enmbedding_model_id,
            input = text
        )
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Embedding was not found")
            return None
        
        return response.data[0].embedding
        
    def generate_text(self, prompt: str, chat_history: list, max_output_tokens: int = None, temperature: float = None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        if not self.generation_model_id:
            self.logger.error("generation model for OpenAI was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_char
        temperature =  temperature if temperature else self.temperature

        chat_history.append(self.construct_prompt(prompt, OpenAIEnUm.USER.value))

        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message or not response.choices[0].message.content:
            self.logger.error("generated text was not found")
            return None
        
        return response.choices[0].message.content
        
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
    
    def process_text(self, text: str):
        return text[:self.default_generation_max_char].strip()