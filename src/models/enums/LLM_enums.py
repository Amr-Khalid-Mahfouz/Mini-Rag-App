from enum import Enum

class LLMEnum(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAIEnUm(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"