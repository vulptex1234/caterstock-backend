#!/usr/bin/env python3
"""
初期データを投入するスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.base import SessionLocal, engine
from app.models.models import Base, User, Item, InventoryLog
from datetime import datetime

def create_initial_data():
    """初期データを作成"""
    db = SessionLocal()
    
    try:
        # テーブルを作成
        Base.metadata.create_all(bind=engine)
        
        # 既存データをチェック
        if db.query(User).first() or db.query(Item).first():
            print("初期データは既に存在します。")
            return
        
        # 管理者ユーザーを作成
        admin_user = User(
            name="管理者",
            role="admin",
            line_id=None
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # 一般ユーザーを作成
        worker_user = User(
            name="作業者",
            role="worker",
            line_id=None
        )
        db.add(worker_user)
        db.commit()
        db.refresh(worker_user)
        
        # 在庫アイテムを作成
        items_data = [
            {"name": "卵", "unit": "個", "threshold_low": 5, "threshold_high": 50},
            {"name": "牛乳", "unit": "本", "threshold_low": 3, "threshold_high": 20},
            {"name": "パン", "unit": "斤", "threshold_low": 2, "threshold_high": 15},
            {"name": "米", "unit": "kg", "threshold_low": 5, "threshold_high": 30},
            {"name": "鶏肉", "unit": "kg", "threshold_low": 2, "threshold_high": 10},
            {"name": "野菜", "unit": "kg", "threshold_low": 3, "threshold_high": 15},
            {"name": "調味料", "unit": "本", "threshold_low": 1, "threshold_high": 10},
        ]
        
        items = []
        for item_data in items_data:
            item = Item(**item_data)
            db.add(item)
            items.append(item)
        
        db.commit()
        
        # 初期在庫ログを作成
        initial_quantities = [3, 15, 8, 20, 5, 10, 7]  # 一部は警告レベル
        
        for item, quantity in zip(items, initial_quantities):
            db.refresh(item)  # IDを取得
            inventory_log = InventoryLog(
                item_id=item.id,
                quantity=quantity,
                updated_by=admin_user.id
            )
            db.add(inventory_log)
        
        db.commit()
        
        print("初期データの作成が完了しました。")
        print(f"- 管理者ユーザー: {admin_user.name} (ID: {admin_user.id})")
        print(f"- 一般ユーザー: {worker_user.name} (ID: {worker_user.id})")
        print(f"- 在庫アイテム: {len(items)}件")
        print("- 初期在庫データを投入しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data() 