from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.models import Item, InventoryLog, User, InventoryType, StatusLevel, ItemCategory, Drink
from app.schemas.schemas import (
    InventoryStatus, InventoryLogCreate, InventoryLogUpdate, InventoryLogCountUpdate
)
from app.services.notification_service import NotificationService


class InventoryService:
    """在庫管理関連のサービスクラス"""
    
    @staticmethod
    def get_current_inventory_status(db: Session) -> List[InventoryStatus]:
        """現在の在庫状況を取得"""
        inventory_statuses = []

        # アイテムの最新の在庫ログを取得
        item_subquery = (
            db.query(
                InventoryLog.item_id,
                func.max(InventoryLog.updated_at).label("max_updated_at")
            )
            .filter(InventoryLog.item_id.isnot(None))
            .group_by(InventoryLog.item_id)
            .subquery()
        )
        
        item_results = (
            db.query(Item, InventoryLog, User)
            .join(InventoryLog, Item.id == InventoryLog.item_id)
            .join(User, InventoryLog.updated_by == User.id)
            .join(
                item_subquery, 
                (InventoryLog.item_id == item_subquery.c.item_id) & 
                (InventoryLog.updated_at == item_subquery.c.max_updated_at)
            )
            .all()
        )

        # ドリンクの最新の在庫ログを取得
        drink_subquery = (
            db.query(
                InventoryLog.drink_id,
                func.max(InventoryLog.updated_at).label("max_updated_at")
            )
            .filter(InventoryLog.drink_id.isnot(None))
            .group_by(InventoryLog.drink_id)
            .subquery()
        )
        
        drink_results = (
            db.query(Drink, InventoryLog, User)
            .join(InventoryLog, Drink.id == InventoryLog.drink_id)
            .join(User, InventoryLog.updated_by == User.id)
            .join(
                drink_subquery, 
                (InventoryLog.drink_id == drink_subquery.c.drink_id) & 
                (InventoryLog.updated_at == drink_subquery.c.max_updated_at)
            )
            .all()
        )
        
        # アイテムの在庫状況を処理
        for item, log, user in item_results:
            if item.inventory_type == InventoryType.QUANTITY_MANAGEMENT:
                # 量管理の場合
                status = InventoryService._determine_status_for_quantity_management(log.status_level)
                inventory_statuses.append(InventoryStatus(
                    item=item,
                    current_quantity=None,
                    current_status=log.status_level,
                    last_updated=log.updated_at,
                    updated_by_name=user.name,
                    status=status
                ))
            else:
                # 個数管理の場合
                status = InventoryService._determine_status_for_count_management(log.quantity, item)
                inventory_statuses.append(InventoryStatus(
                    item=item,
                    current_quantity=log.quantity,
                    current_status=None,
                    last_updated=log.updated_at,
                    updated_by_name=user.name,
                    status=status
                ))

        # ドリンクの在庫状況を処理
        for drink, log, user in drink_results:
            if drink.inventory_type == InventoryType.QUANTITY_MANAGEMENT:
                # 量管理の場合
                status = InventoryService._determine_status_for_quantity_management(log.status_level)
                inventory_statuses.append(InventoryStatus(
                    drink=drink,
                    current_quantity=None,
                    current_status=log.status_level,
                    last_updated=log.updated_at,
                    updated_by_name=user.name,
                    status=status
                ))
            else:
                # 個数管理の場合
                status = InventoryService._determine_status_for_count_management(log.quantity, drink)
                inventory_statuses.append(InventoryStatus(
                    drink=drink,
                    current_quantity=log.quantity,
                    current_status=None,
                    last_updated=log.updated_at,
                    updated_by_name=user.name,
                    status=status
                ))
        
        return inventory_statuses
    
    @staticmethod
    def update_inventory_quantity_management(
        db: Session, 
        inventory_data: InventoryLogUpdate, 
        user_id: int
    ) -> InventoryLog:
        """量管理の在庫を更新（3択）"""
        # 新しい在庫ログを作成
        inventory_log = InventoryLog(
            item_id=inventory_data.item_id,
            status_level=inventory_data.status_level,
            updated_by=user_id
        )
        
        db.add(inventory_log)
        db.commit()
        db.refresh(inventory_log)
        
        # アイテム情報を取得
        item = db.query(Item).filter(Item.id == inventory_data.item_id).first()
        
        # 通知チェック
        if item and inventory_data.status_level in [StatusLevel.LOW, StatusLevel.HIGH]:
            status = InventoryService._determine_status_for_quantity_management(inventory_data.status_level)
            NotificationService.send_inventory_alert(
                item=item,
                current_quantity=None,
                current_status=inventory_data.status_level,
                user_name=db.query(User).filter(User.id == user_id).first().name,
                status=status
            )
        
        return inventory_log
    
    @staticmethod
    def update_inventory_count_management(
        db: Session, 
        inventory_data: InventoryLogCountUpdate, 
        user_id: int
    ) -> InventoryLog:
        """個数管理の在庫を更新（数値）"""
        # 新しい在庫ログを作成
        inventory_log = InventoryLog(
            item_id=inventory_data.item_id,
            quantity=inventory_data.quantity,
            updated_by=user_id
        )
        
        db.add(inventory_log)
        db.commit()
        db.refresh(inventory_log)
        
        # アイテム情報を取得
        item = db.query(Item).filter(Item.id == inventory_data.item_id).first()
        
        # しきい値チェックと通知
        if item:
            status = InventoryService._determine_status_for_count_management(inventory_data.quantity, item)
            if status in ["low", "high"]:
                NotificationService.send_inventory_alert(
                    item=item,
                    current_quantity=inventory_data.quantity,
                    current_status=None,
                    user_name=db.query(User).filter(User.id == user_id).first().name,
                    status=status
                )
        
        return inventory_log
    
    @staticmethod
    def get_inventory_history(
        db: Session, 
        item_id: Optional[int] = None,
        limit: int = 100
    ) -> List[InventoryLog]:
        """在庫履歴を取得"""
        query = (
            db.query(InventoryLog)
            .join(Item)
            .join(User)
            .order_by(desc(InventoryLog.updated_at))
        )
        
        if item_id:
            query = query.filter(InventoryLog.item_id == item_id)
        
        return query.limit(limit).all()
    
    @staticmethod
    def _determine_status_for_quantity_management(status_level: StatusLevel) -> str:
        """量管理のステータスレベルから統一ステータスを判定"""
        if status_level == StatusLevel.LOW:
            return "low"
        elif status_level == StatusLevel.HIGH:
            return "high"
        else:  # StatusLevel.SUFFICIENT
            return "normal"
    
    @staticmethod
    def _determine_status_for_count_management(quantity: int, item: Item) -> str:
        """個数管理の在庫数に基づいてステータスを判定"""
        if quantity < item.threshold_low:
            return "low"
        elif quantity > item.threshold_high:
            return "high"
        else:
            return "normal"
    
    @staticmethod
    def get_items(db: Session) -> List[Item]:
        """全アイテムを取得"""
        return db.query(Item).all()
    
    @staticmethod
    def get_items_by_category(db: Session, category: ItemCategory) -> List[Item]:
        """カテゴリ別アイテムを取得"""
        return db.query(Item).filter(Item.category == category).all()
    
    @staticmethod
    def create_item(
        db: Session, 
        name: str, 
        unit: str, 
        category: ItemCategory,
        inventory_type: InventoryType,
        threshold_low: Optional[int] = None, 
        threshold_high: Optional[int] = None
    ) -> Item:
        """新しいアイテムを作成"""
        item = Item(
            name=name,
            unit=unit,
            category=category,
            inventory_type=inventory_type,
            threshold_low=threshold_low,
            threshold_high=threshold_high
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def get_drinks(db: Session) -> List[Drink]:
        """全ドリンクを取得"""
        return db.query(Drink).all()
    
    @staticmethod
    def get_drinks_by_category(db: Session, category: ItemCategory) -> List[Drink]:
        """カテゴリ別ドリンクを取得"""
        return db.query(Drink).filter(Drink.category == category).all()
    
    @staticmethod
    def create_drink(
        db: Session, 
        name: str, 
        unit: str, 
        category: ItemCategory,
        inventory_type: InventoryType,
        threshold_low: Optional[int] = None, 
        threshold_high: Optional[int] = None
    ) -> Drink:
        """新しいドリンクを作成"""
        drink = Drink(
            name=name,
            unit=unit,
            category=category,
            inventory_type=inventory_type,
            threshold_low=threshold_low,
            threshold_high=threshold_high
        )
        db.add(drink)
        db.commit()
        db.refresh(drink)
        return drink 