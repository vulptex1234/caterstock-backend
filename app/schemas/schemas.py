from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.models import ItemCategory, InventoryType, StatusLevel


# User schemas
class UserBase(BaseModel):
    name: str
    role: str = "worker"


class UserCreate(UserBase):
    line_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    id: int
    line_id: Optional[str] = None
    last_login: datetime
    
    class Config:
        from_attributes = True


# Item schemas
class ItemBase(BaseModel):
    name: str
    unit: str
    category: ItemCategory
    inventory_type: InventoryType
    threshold_low: Optional[int] = None  # 個数管理のみ
    threshold_high: Optional[int] = None  # 個数管理のみ


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[ItemCategory] = None
    inventory_type: Optional[InventoryType] = None
    threshold_low: Optional[int] = None
    threshold_high: Optional[int] = None


class Item(ItemBase):
    id: int
    
    class Config:
        from_attributes = True


# InventoryLog schemas
class InventoryLogBase(BaseModel):
    item_id: int
    quantity: Optional[int] = None  # 個数管理のみ
    status_level: Optional[StatusLevel] = None  # 量管理のみ


class InventoryLogCreate(InventoryLogBase):
    pass


class InventoryLogUpdate(BaseModel):
    """量管理用の3択更新"""
    item_id: int
    status_level: StatusLevel


class InventoryLogCountUpdate(BaseModel):
    """個数管理用の数値更新"""
    item_id: int
    quantity: int


class InventoryLog(InventoryLogBase):
    id: int
    updated_by: int
    updated_at: datetime
    item: Item
    user: User
    
    class Config:
        from_attributes = True


# Current inventory status
class InventoryStatus(BaseModel):
    item: Item
    current_quantity: Optional[int] = None  # 個数管理のみ
    current_status: Optional[StatusLevel] = None  # 量管理のみ
    last_updated: datetime
    updated_by_name: str
    status: str  # "normal", "low", "high" (統一ステータス)


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# LINE OAuth schemas
class LineAuthURL(BaseModel):
    auth_url: str


class LineCallback(BaseModel):
    code: str
    state: Optional[str] = None 