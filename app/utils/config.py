import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    # OpenAI API configuration
    openai_api_key: str = os.getenv("API_KEY", "")
    openai_default_model: str = os.getenv("MODEL_ID", "gpt-3.5-turbo")
    openai_api_base: str = os.getenv("BASE_URL", "")
    
    # Service configuration
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    log_level: str = os.getenv("LOG_LEVEL", "info")

# Create settings instance
settings = Settings()

# Validate required configuration
if not settings.openai_api_key:
    raise ValueError("API_KEY must be set in .env file or environment variables") 