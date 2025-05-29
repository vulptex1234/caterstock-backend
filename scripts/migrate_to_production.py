#!/usr/bin/env python3
"""
本番環境へのデータ移行スクリプト
SQLiteの開発データをPostgreSQLに移行
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, User, Item, InventoryLog
from app.core.config import settings

def migrate_data():
    """開発環境のデータを本番環境に移行"""
    
    # 開発環境（SQLite）への接続
    dev_engine = create_engine(settings.DATABASE_URL_SQLITE, connect_args={"check_same_thread": False})
    DevSession = sessionmaker(bind=dev_engine)
    
    # 本番環境（PostgreSQL）への接続
    prod_engine = create_engine(settings.DATABASE_URL)
    ProdSession = sessionmaker(bind=prod_engine)
    
    # 本番環境のテーブル作成
    Base.metadata.create_all(bind=prod_engine)
    
    dev_db = DevSession()
    prod_db = ProdSession()
    
    try:
        print("🚀 データ移行を開始します...")
        
        # ユーザーデータの移行
        print("👥 ユーザーデータを移行中...")
        users = dev_db.query(User).all()
        for user in users:
            # 既存チェック
            existing = prod_db.query(User).filter(User.line_id == user.line_id).first()
            if not existing:
                new_user = User(
                    name=user.name,
                    role=user.role,
                    line_id=user.line_id,
                    last_login=user.last_login
                )
                prod_db.add(new_user)
        prod_db.commit()
        print(f"✅ {len(users)}件のユーザーを移行しました")
        
        # アイテムデータの移行
        print("📦 アイテムデータを移行中...")
        items = dev_db.query(Item).all()
        for item in items:
            # 既存チェック
            existing = prod_db.query(Item).filter(Item.name == item.name).first()
            if not existing:
                new_item = Item(
                    name=item.name,
                    unit=item.unit,
                    category=item.category,
                    inventory_type=item.inventory_type,
                    threshold_low=item.threshold_low,
                    threshold_high=item.threshold_high
                )
                prod_db.add(new_item)
        prod_db.commit()
        print(f"✅ {len(items)}件のアイテムを移行しました")
        
        # 在庫ログの移行（最新のみ）
        print("📊 在庫ログを移行中...")
        
        # 各アイテムの最新ログのみ移行
        migrated_logs = 0
        for item in items:
            latest_log = (dev_db.query(InventoryLog)
                         .filter(InventoryLog.item_id == item.id)
                         .order_by(InventoryLog.updated_at.desc())
                         .first())
            
            if latest_log:
                # 対応するユーザーとアイテムを本番環境で取得
                prod_user = prod_db.query(User).filter(User.line_id == latest_log.user.line_id).first()
                prod_item = prod_db.query(Item).filter(Item.name == latest_log.item.name).first()
                
                if prod_user and prod_item:
                    new_log = InventoryLog(
                        item_id=prod_item.id,
                        quantity=latest_log.quantity,
                        status_level=latest_log.status_level,
                        updated_by=prod_user.id,
                        updated_at=latest_log.updated_at
                    )
                    prod_db.add(new_log)
                    migrated_logs += 1
        
        prod_db.commit()
        print(f"✅ {migrated_logs}件の在庫ログを移行しました")
        
        print("🎉 データ移行が完了しました！")
        
    except Exception as e:
        print(f"❌ データ移行中にエラーが発生しました: {e}")
        prod_db.rollback()
        raise
    finally:
        dev_db.close()
        prod_db.close()

if __name__ == "__main__":
    migrate_data() 