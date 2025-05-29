#!/usr/bin/env python3
"""
データベースをリセットして新しい項目で初期化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.base import SessionLocal, engine
from app.models.models import Base, User, Item, InventoryLog, ItemCategory, InventoryType, StatusLevel
from datetime import datetime

def reset_and_create_new_data():
    """データベースをリセットして新しいデータで初期化"""
    db = SessionLocal()
    
    try:
        # 全てのテーブルを削除して再作成
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # ユーザーを作成
        admin_user = User(
            name="管理者",
            role="admin",
            line_id=None
        )
        db.add(admin_user)
        
        worker_user = User(
            name="作業者",
            role="worker",
            line_id=None
        )
        db.add(worker_user)
        db.commit()
        db.refresh(admin_user)
        
        # 新しい在庫項目データ（3つのカテゴリに分類）
        items_data = [
            # 量管理の備品
            {"name": "箸", "unit": "束", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "おしぼり", "unit": "枚", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "コースター", "unit": "枚", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "和紙", "unit": "枚", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.LOW},
            {"name": "天紙", "unit": "枚", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "ゴミ袋", "unit": "枚", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.HIGH},
            {"name": "手袋", "unit": "枚", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "紙コップ", "unit": "個", "category": ItemCategory.SUPPLIES, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            
            # 量管理の食品
            {"name": "緑茶", "unit": "g", "category": ItemCategory.FOOD, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "紅茶", "unit": "g", "category": ItemCategory.FOOD, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.LOW},
            {"name": "醤油", "unit": "ml", "category": ItemCategory.FOOD, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "おろしソース", "unit": "ml", "category": ItemCategory.FOOD, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.SUFFICIENT},
            {"name": "ゆかり", "unit": "g", "category": ItemCategory.FOOD, "inventory_type": InventoryType.QUANTITY_MANAGEMENT, "initial_status": StatusLevel.HIGH},
            
            # 個数管理
            {"name": "飯器", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 10, "threshold_high": 100, "initial_quantity": 45},
            {"name": "飯器蓋", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 10, "threshold_high": 100, "initial_quantity": 45},
            {"name": "黒皿", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 20, "threshold_high": 200, "initial_quantity": 120},
            {"name": "豆腐 蓋", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 10, "threshold_high": 100, "initial_quantity": 30},
            {"name": "豆腐 白器", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 10, "threshold_high": 100, "initial_quantity": 35},
            {"name": "豆腐 黒器", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 10, "threshold_high": 100, "initial_quantity": 25},
            {"name": "とんすい", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 15, "threshold_high": 150, "initial_quantity": 80},
            {"name": "れんげ", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 20, "threshold_high": 200, "initial_quantity": 110},
            {"name": "れんげ受け", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 20, "threshold_high": 200, "initial_quantity": 90},
            {"name": "五徳", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 5, "threshold_high": 50, "initial_quantity": 25},
            {"name": "竹皿", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 10, "threshold_high": 100, "initial_quantity": 60},
            {"name": "茶碗蒸し下皿", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 10, "threshold_high": 100, "initial_quantity": 40},
            {"name": "天ぷら皿", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 15, "threshold_high": 150, "initial_quantity": 75},
            {"name": "塩皿", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 20, "threshold_high": 200, "initial_quantity": 100},
            {"name": "醤油皿", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 20, "threshold_high": 200, "initial_quantity": 120},
            {"name": "子供什器", "unit": "個", "category": ItemCategory.EQUIPMENT, "inventory_type": InventoryType.COUNT_MANAGEMENT, "threshold_low": 5, "threshold_high": 50, "initial_quantity": 15},
        ]
        
        # アイテムを作成
        items = []
        for item_data in items_data:
            item = Item(
                name=item_data["name"],
                unit=item_data["unit"],
                category=item_data["category"],
                inventory_type=item_data["inventory_type"],
                threshold_low=item_data.get("threshold_low"),
                threshold_high=item_data.get("threshold_high")
            )
            db.add(item)
            items.append((item, item_data))
        
        db.commit()
        
        # 初期在庫ログを作成
        for item, item_data in items:
            db.refresh(item)
            
            if item.inventory_type == InventoryType.QUANTITY_MANAGEMENT:
                # 量管理の場合はstatus_levelを設定
                inventory_log = InventoryLog(
                    item_id=item.id,
                    status_level=item_data["initial_status"],
                    updated_by=admin_user.id
                )
            else:
                # 個数管理の場合はquantityを設定
                inventory_log = InventoryLog(
                    item_id=item.id,
                    quantity=item_data["initial_quantity"],
                    updated_by=admin_user.id
                )
            
            db.add(inventory_log)
        
        db.commit()
        
        print("データベースをリセットして新しいデータで初期化しました。")
        print(f"- ユーザー: 2名")
        print(f"- 在庫項目: {len(items)}件")
        print("- 初期在庫データを投入しました")
        
        # カテゴリ別集計
        categories = {}
        for item, _ in items:
            if item.category == ItemCategory.SUPPLIES:
                cat = "量管理の備品"
            elif item.category == ItemCategory.FOOD:
                cat = "量管理の食品"
            else:
                cat = "個数管理"
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            print(f"- {cat}: {count}件")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_create_new_data()