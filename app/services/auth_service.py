from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import User
import httpx


class AuthService:
    """認証関連のサービスクラス"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """JWTアクセストークンを生成"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        """JWTトークンを検証"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id: int = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None
    
    @staticmethod
    async def get_line_auth_url(state: str = "random_state"):
        """LINE OAuth認証URLを生成"""
        if not settings.LINE_CHANNEL_ID:
            raise ValueError("LINE_CHANNEL_ID is not set")
        
        base_url = "https://access.line.me/oauth2/v2.1/authorize"
        params = {
            "response_type": "code",
            "client_id": settings.LINE_CHANNEL_ID,
            "redirect_uri": settings.LINE_REDIRECT_URI,
            "state": state,
            "scope": "profile openid"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    @staticmethod
    async def exchange_line_code_for_token(code: str):
        """LINE認証コードをアクセストークンに交換"""
        if not settings.LINE_CHANNEL_ID or not settings.LINE_CHANNEL_SECRET:
            raise ValueError("LINE credentials are not set")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.line.me/oauth2/v2.1/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.LINE_REDIRECT_URI,
                    "client_id": settings.LINE_CHANNEL_ID,
                    "client_secret": settings.LINE_CHANNEL_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise ValueError("Failed to exchange code for token")
            
            return response.json()
    
    @staticmethod
    async def get_line_profile(access_token: str):
        """LINEプロフィール情報を取得"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.line.me/v2/profile",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise ValueError("Failed to get LINE profile")
            
            return response.json()
    
    @staticmethod
    def find_or_create_user(db: Session, line_id: str, name: str) -> User:
        """LINEユーザーを検索または作成"""
        user = db.query(User).filter(User.line_id == line_id).first()
        
        if not user:
            user = User(
                name=name,
                line_id=line_id,
                role="worker"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # 最終ログイン時刻を更新
            user.last_login = datetime.utcnow()
            db.commit()
        
        return user 