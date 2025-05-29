from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 環境に応じたデータベースURL
engine = create_engine(
    settings.db_url,
    # SQLiteの場合のみcheck_same_threadを無効化
    connect_args={"check_same_thread": False} if "sqlite" in settings.db_url else {},
    # PostgreSQLの場合はpool設定
    pool_pre_ping=True if "postgresql" in settings.db_url else False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """データベースセッションの依存性注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 