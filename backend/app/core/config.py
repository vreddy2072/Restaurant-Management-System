from typing import Optional
from pydantic import BaseSettings
from pydantic.networks import AnyHttpUrl

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Restaurant App"
    
    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5173"  # Vite default port
    ]

    # Database
    SQLITE_DB: str = "restaurant_app.db"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///./{SQLITE_DB}"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
