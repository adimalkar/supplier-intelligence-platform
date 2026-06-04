from pydantic_settings import BaseSettings
import os

class LLMConfig(BaseSettings):
    provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "bedrock"
    model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))

llm_config = LLMConfig()
