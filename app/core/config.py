from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres.ipgqwiqyomvxdfpawgvl:o.kyohei.0524@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
    DATABASE_URL_SQLITE: str = "sqlite:///./caterstock.db"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CaterStock"
    
    # Security
    SECRET_KEY: str = "4622f31693a8c3be9ae437877c0c0117b8ece7c291d3375bc4a80fcfa24d1c87"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # LINE OAuth
    LINE_CHANNEL_ID: Optional[str] = "2007495287"
    LINE_CHANNEL_SECRET: Optional[str] = "0d1a85852441bb77ee5993eeee60636d"
    LINE_REDIRECT_URI: str = "https://caterstock-backend.vercel.app/auth/callback"
    
    # LINE Notify
    LINE_NOTIFY_TOKEN: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS origins for production
    CORS_ORIGINS: list[str] = ["https://caterstock-frontend.vercel.app"]
    
    # Database URL selection based on environment
    @property
    def db_url(self) -> str:
        if self.ENVIRONMENT == "production":
            return self.DATABASE_URL
        return self.DATABASE_URL_SQLITE
    
    class Config:
        env_file = ".env"


settings = Settings() 