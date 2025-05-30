from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.api_v1 import api_router
from app.core.config import settings
from app.database.base import engine
from app.models.models import Base

# データベーステーブルを作成
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# APIルーターを登録
app.include_router(api_router, prefix=settings.API_V1_STR)

# カスタムエラーハンドラー
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": f"The requested URL {request.url} was not found on this server.",
            "available_endpoints": [
                "/",
                "/health",
                "/docs",
                "/redoc",
                f"{settings.API_V1_STR}/auth/line/auth-url",
                f"{settings.API_V1_STR}/inventory/status",
                f"{settings.API_V1_STR}/inventory/items",
                # 他のエンドポイントも必要に応じて追加
            ],
            "environment": settings.ENVIRONMENT,
            "api_version": settings.API_V1_STR,
            "cors_origins": settings.CORS_ORIGINS,
        }
    )

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "message": "CaterStock API is running!",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "api_version": settings.API_V1_STR,
        "available_endpoints": [
            "/",
            "/health",
            "/docs",
            "/redoc",
            f"{settings.API_V1_STR}/auth/line/auth-url",
            f"{settings.API_V1_STR}/inventory/status",
            f"{settings.API_V1_STR}/inventory/items",
        ]
    }

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "api_version": settings.API_V1_STR,
        "database_url": settings.db_url if settings.ENVIRONMENT == "production" else "sqlite:///./caterstock.db"
    }