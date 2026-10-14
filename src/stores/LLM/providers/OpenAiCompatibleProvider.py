from ..LLMinterface import LLMInterface
from openai import OpenAI
from models.enums import OpenAIEnum
import logging
from typing import List

# works with both OpenAi models and Qwen models
class OpenAICompatibleProvider(LLMInterface):
    
    def __init__(self, api_key: str,
                api_url: str = None,
                default_input_max_char: int = 1000,
                default_generation_max_char: int = 1000,
                temperature: float = 1.0
                ):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_generation_max_char = default_generation_max_char
        self.default_input_max_char = default_input_max_char
        self.temperature = temperature

        self.generation_model_id = None
        
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url)

        self.enums = OpenAIEnum
        self.logger = logging.getLogger(__name__) # file name
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def embed_text(self, text: List[str], document_type: str = None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None

        try:
            response = self.client.embeddings.create(
                    model = self.embedding_model_id,
                    input = text,
                    dimensions=self.embedding_size,
                    encoding_format= "float"
                )
        except Exception:
            self.logger.exception("Embedding request failed")
            return None
        
        
        if not response or not response.data or len(response.data) == 0:
            self.logger.error("Embedding was not found")
            return None
        
        return [x.embedding for x in response.data]
        
    def generate_text(self, prompt: str, chat_history: list, max_output_tokens: int = None, temperature: float = None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        if not self.generation_model_id:
            self.logger.error("generation model for OpenAI was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_char
        temperature =  temperature if temperature else self.temperature

        chat_history.append(self.construct_prompt(prompt, OpenAIEnum.USER.value))

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