from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.base import get_db
from app.schemas.schemas import (
    InventoryStatus, InventoryLogCreate, InventoryLog,
    Item, ItemCreate, User, InventoryLogUpdate, InventoryLogCountUpdate,
    Drink, DrinkCreate
)
from app.services.inventory_service import InventoryService
from app.services.auth_service import AuthService
from app.models.models import User as UserModel, InventoryType, ItemCategory
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserModel:
    """現在のユーザーを取得"""
    user_id = AuthService.verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# 開発用：認証なしエンドポイント
@router.get("/status/test", response_model=List[InventoryStatus])
async def get_inventory_status_test(db: Session = Depends(get_db)):
    """現在の在庫状況を取得（開発用・認証なし）"""
    return InventoryService.get_current_inventory_status(db)


@router.get("/items/test", response_model=List[Item])
async def get_items_test(db: Session = Depends(get_db)):
    """全アイテムを取得（開発用・認証なし）"""
    return InventoryService.get_items(db)


@router.post("/update/quantity/test", response_model=InventoryLog)
async def update_inventory_quantity_management_test(
    inventory_data: InventoryLogUpdate,
    db: Session = Depends(get_db)
):
    """量管理の在庫を更新（開発用・認証なし）"""
    # デフォルトユーザー（管理者）を使用
    return InventoryService.update_inventory_quantity_management(db, inventory_data, 1)


@router.post("/update/count/test", response_model=InventoryLog)
async def update_inventory_count_management_test(
    inventory_data: InventoryLogCountUpdate,
    db: Session = Depends(get_db)
):
    """個数管理の在庫を更新（開発用・認証なし）"""
    # デフォルトユーザー（管理者）を使用
    return InventoryService.update_inventory_count_management(db, inventory_data, 1)


# 認証ありエンドポイント
@router.get("/status", response_model=List[InventoryStatus])
async def get_inventory_status(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """現在の在庫状況を取得"""
    return InventoryService.get_current_inventory_status(db)


@router.post("/update/quantity", response_model=InventoryLog)
async def update_inventory_quantity_management(
    inventory_data: InventoryLogUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """量管理の在庫を更新（3択）"""
    return InventoryService.update_inventory_quantity_management(db, inventory_data, current_user.id)


@router.post("/update/count", response_model=InventoryLog)
async def update_inventory_count_management(
    inventory_data: InventoryLogCountUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """個数管理の在庫を更新（数値）"""
    return InventoryService.update_inventory_count_management(db, inventory_data, current_user.id)


@router.get("/history", response_model=List[InventoryLog])
async def get_inventory_history(
    item_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """在庫履歴を取得"""
    return InventoryService.get_inventory_history(db, item_id, limit)


@router.get("/items", response_model=List[Item])
async def get_items(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """全アイテムを取得"""
    return InventoryService.get_items(db)


@router.get("/items/category/{category}", response_model=List[Item])
async def get_items_by_category(
    category: ItemCategory,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """カテゴリ別アイテムを取得"""
    return InventoryService.get_items_by_category(db, category)


@router.post("/items", response_model=Item)
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """新しいアイテムを作成（管理者のみ）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create items"
        )
    
    return InventoryService.create_item(
        db=db,
        name=item_data.name,
        unit=item_data.unit,
        category=item_data.category,
        inventory_type=item_data.inventory_type,
        threshold_low=item_data.threshold_low,
        threshold_high=item_data.threshold_high
    )


@router.get("/drinks", response_model=List[Drink])
async def get_drinks(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """全ドリンクを取得"""
    return InventoryService.get_drinks(db)


@router.get("/drinks/category/{category}", response_model=List[Drink])
async def get_drinks_by_category(
    category: ItemCategory,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """カテゴリ別ドリンクを取得"""
    return InventoryService.get_drinks_by_category(db, category)


@router.post("/drinks", response_model=Drink)
async def create_drink(
    drink_data: DrinkCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """新しいドリンクを作成（管理者のみ）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create drinks"
        )
    
    return InventoryService.create_drink(
        db=db,
        name=drink_data.name,
        unit=drink_data.unit,
        category=drink_data.category,
        inventory_type=drink_data.inventory_type,
        threshold_low=drink_data.threshold_low,
        threshold_high=drink_data.threshold_high
    ) 