from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
import enum


class ItemCategory(str, enum.Enum):
    SUPPLIES = "supplies"  # 量管理の備品
    FOOD = "food"  # 量管理の食品
    EQUIPMENT = "equipment"  # 個数管理


class InventoryType(str, enum.Enum):
    QUANTITY_MANAGEMENT = "quantity_management"  # 量管理（3択）
    COUNT_MANAGEMENT = "count_management"  # 個数管理（数値）


class StatusLevel(str, enum.Enum):
    HIGH = "high"  # 多い（過剰）
    SUFFICIENT = "sufficient"  # 十分（正常）
    LOW = "low"  # 少ない（不足）


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="worker")  # "admin" or "worker"
    line_id = Column(String, unique=True, nullable=True)
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    inventory_logs = relationship("InventoryLog", back_populates="user")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)  # 例：個、本、kg
    category = Column(Enum(ItemCategory), nullable=False)
    inventory_type = Column(Enum(InventoryType), nullable=False)
    threshold_low = Column(Integer, nullable=True)  # 個数管理のみ使用
    threshold_high = Column(Integer, nullable=True)  # 個数管理のみ使用
    
    # Relationship
    inventory_logs = relationship("InventoryLog", back_populates="item")


class InventoryLog(Base):
    __tablename__ = "inventory_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=True)  # 個数管理のみ使用
    status_level = Column(Enum(StatusLevel), nullable=True)  # 量管理のみ使用
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    item = relationship("Item", back_populates="inventory_logs")
    user = relationship("User", back_populates="inventory_logs")


class Drink(Base):
    __tablename__ = "drinks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)  # 例：個、本、kg
    category = Column(Enum(ItemCategory), nullable=False)
    inventory_type = Column(Enum(InventoryType), nullable=False)
    threshold_low = Column(Integer, nullable=True)  # 個数管理のみ使用
    threshold_high = Column(Integer, nullable=True)  # 個数管理のみ使用
    
    # Relationship
    inventory_logs = relationship("InventoryLog", back_populates="drink") 