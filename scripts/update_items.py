#!/usr/bin/env python3
"""
新しい在庫項目を追加するスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.base import SessionLocal, engine
from app.models.models import Base, User, Item, InventoryLog
from datetime import datetime

def update_inventory_items():
    """新しい在庫項目を追加"""
    db = SessionLocal()
    
    try:
        # 既存の古い項目を削除（オプション）
        # db.query(InventoryLog).delete()
        # db.query(Item).delete()
        # db.commit()
        
        # 新しい在庫項目データ（設計書から）
        new_items_data = [
            # 量管理 - 備品
            {"name": "箸", "unit": "束", "category": "量管理", "item_type": "備品", "threshold_low": 5, "threshold_high": 50},
            {"name": "おしぼり", "unit": "枚", "category": "量管理", "item_type": "備品", "threshold_low": 20, "threshold_high": 200},
            {"name": "コースター", "unit": "枚", "category": "量管理", "item_type": "備品", "threshold_low": 10, "threshold_high": 100},
            {"name": "和紙", "unit": "枚", "category": "量管理", "item_type": "備品", "threshold_low": 10, "threshold_high": 100},
            {"name": "天紙", "unit": "枚", "category": "量管理", "item_type": "備品", "threshold_low": 10, "threshold_high": 100},
            {"name": "ゴミ袋", "unit": "枚", "category": "量管理", "item_type": "備品", "threshold_low": 10, "threshold_high": 100},
            {"name": "手袋", "unit": "枚", "category": "量管理", "item_type": "備品", "threshold_low": 20, "threshold_high": 200},
            {"name": "紙コップ", "unit": "個", "category": "量管理", "item_type": "備品", "threshold_low": 50, "threshold_high": 500},
            
            # 量管理 - 食品
            {"name": "緑茶", "unit": "g", "category": "量管理", "item_type": "食品", "threshold_low": 100, "threshold_high": 1000},
            {"name": "紅茶", "unit": "g", "category": "量管理", "item_type": "食品", "threshold_low": 100, "threshold_high": 1000},
            {"name": "醤油", "unit": "ml", "category": "量管理", "item_type": "食品", "threshold_low": 500, "threshold_high": 2000},
            {"name": "おろしソース", "unit": "ml", "category": "量管理", "item_type": "食品", "threshold_low": 200, "threshold_high": 1000},
            {"name": "ゆかり", "unit": "g", "category": "量管理", "item_type": "食品", "threshold_low": 50, "threshold_high": 500},
            
            # 個数管理 - 什器
            {"name": "飯器", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 10, "threshold_high": 100},
            {"name": "飯器蓋", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 10, "threshold_high": 100},
            {"name": "黒皿", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 20, "threshold_high": 200},
            {"name": "豆腐 蓋", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 10, "threshold_high": 100},
            {"name": "豆腐 白器", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 10, "threshold_high": 100},
            {"name": "豆腐 黒器", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 10, "threshold_high": 100},
            {"name": "とんすい", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 15, "threshold_high": 150},
            {"name": "れんげ", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 20, "threshold_high": 200},
            {"name": "れんげ受け", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 20, "threshold_high": 200},
            {"name": "五徳", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 5, "threshold_high": 50},
            {"name": "竹皿", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 10, "threshold_high": 100},
            {"name": "茶碗蒸し下皿", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 10, "threshold_high": 100},
            {"name": "天ぷら皿", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 15, "threshold_high": 150},
            {"name": "塩皿", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 20, "threshold_high": 200},
            {"name": "醤油皿", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 20, "threshold_high": 200},
            {"name": "子供什器", "unit": "個", "category": "個数管理", "item_type": "什器", "threshold_low": 5, "threshold_high": 50},
        ]
        
        # 管理者ユーザーを取得（在庫ログ用）
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            print("管理者ユーザーが見つかりません。先に初期データを作成してください。")
            return
        
        # 新しいアイテムを追加
        new_items = []
        for item_data in new_items_data:
            # 既存チェック
            existing_item = db.query(Item).filter(Item.name == item_data["name"]).first()
            if existing_item:
                print(f"項目 '{item_data['name']}' は既に存在します。スキップ。")
                continue
            
            # categoryとitem_typeはモデルに追加されていない場合は削除
            item_create_data = {
                "name": item_data["name"],
                "unit": item_data["unit"],
                "threshold_low": item_data["threshold_low"],
                "threshold_high": item_data["threshold_high"]
            }
            
            item = Item(**item_create_data)
            db.add(item)
            new_items.append((item, item_data))
        
        db.commit()
        
        # 初期在庫ログを作成（ランダムな値）
        import random
        for item, item_data in new_items:
            db.refresh(item)
            # しきい値の範囲内でランダムな初期値を設定
            min_qty = item_data["threshold_low"]
            max_qty = item_data["threshold_high"]
            initial_qty = random.randint(min_qty, max_qty)
            
            inventory_log = InventoryLog(
                item_id=item.id,
                quantity=initial_qty,
                updated_by=admin_user.id
            )
            db.add(inventory_log)
        
        db.commit()
        
        print(f"新しい在庫項目 {len(new_items)} 件を追加しました。")
        for item, item_data in new_items:
            print(f"- {item.name} ({item.unit}) [{item_data.get('category', '未分類')} - {item_data.get('item_type', '未分類')}]")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_inventory_items()