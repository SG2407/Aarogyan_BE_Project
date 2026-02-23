
from pydantic_settings import BaseSettings
from typing import Optional
import os
print('ENVIRONMENT VARIABLES:', dict(os.environ))



class Settings(BaseSettings):
        # For compatibility with code expecting settings.ALGORITHM
        @property
        def ALGORITHM(self) -> str:
            return self.JWT_ALGORITHM
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # OpenRouter LLM
    OPENROUTER_MODEL: str
    OPENROUTER_API_KEY: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Aarogyan API"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
