from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost/caterstock"
    DATABASE_URL_SQLITE: str = "sqlite:///./caterstock.db"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CaterStock"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # LINE OAuth
    LINE_CHANNEL_ID: Optional[str] = None
    LINE_CHANNEL_SECRET: Optional[str] = None
    LINE_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    
    # LINE Notify
    LINE_NOTIFY_TOKEN: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS origins for production
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001, https://caterstock-frontend.vercel.app/"]
    
    # Database URL selection based on environment
    @property
    def db_url(self) -> str:
        if self.ENVIRONMENT == "production":
            return self.DATABASE_URL
        return self.DATABASE_URL_SQLITE
    
    class Config:
        env_file = ".env"


settings = Settings() 