from models import LLMEnum
from providers import OpenAIProvider, CohereProvider
from helpers import Settings, get_settings

class LLMProviderFactory():

    def __init__(self, config: Settings):
        self.config = config

    def create(self, provider_name: str):
        if provider_name == LLMEnum.OPENAI.value:
            provider = OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_generation_max_char=self.config.DEFUALT_GENERATION_MAX_CHAR,
                default_input_max_char=self.config.DEFAULT_INPUT_MAX_CHAR,
                temperature=self.config.GENERATION_DEFUALT_TEMPERATURE
            )
            
        if provider_name == LLMEnum.COHERE.value:
            provider = CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                
                default_generation_max_char=self.config.DEFUALT_GENERATION_MAX_CHAR,
                default_input_max_char=self.config.DEFAULT_INPUT_MAX_CHAR,
                temperature=self.config.GENERATION_DEFUALT_TEMPERATURE
            )
        
        return provider