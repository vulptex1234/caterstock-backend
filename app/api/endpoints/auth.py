from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.schemas.schemas import Token, LineAuthURL, LineCallback
from app.services.auth_service import AuthService
import secrets
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/line/auth-url", response_model=LineAuthURL)
async def get_line_auth_url():
    """LINE OAuth認証URLを取得"""
    try:
        state = secrets.token_urlsafe(32)
        auth_url = await AuthService.get_line_auth_url(state)
        return LineAuthURL(auth_url=auth_url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/line/callback")
async def line_oauth_callback_get(code: str, state: str = None, db: Session = Depends(get_db)):
    """
    LINE OAuth認証コールバック (GET)
    """
    try:
        # フロントエンドのコールバックページにリダイレクト
        frontend_callback_url = f"https://caterstock-frontend.vercel.app/auth/callback?code={code}&state={state}"
        return RedirectResponse(url=frontend_callback_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/line/callback", response_model=Token)
async def line_oauth_callback(
    callback_data: LineCallback,
    db: Session = Depends(get_db)
):
    """LINE OAuth認証コールバック (POST)"""
    try:
        # 認証コードをアクセストークンに交換
        token_data = await AuthService.exchange_line_code_for_token(callback_data.code)
        
        # LINEプロフィール情報を取得
        profile = await AuthService.get_line_profile(token_data["access_token"])
        
        # ユーザーを検索または作成
        user = AuthService.find_or_create_user(
            db=db,
            line_id=profile["userId"],
            name=profile["displayName"]
        )
        
        # JWTトークンを生成
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)}
        )
        
        return Token(access_token=access_token, token_type="bearer")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        ) 