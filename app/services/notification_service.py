import httpx
import asyncio
from datetime import datetime
from typing import Optional
from app.core.config import settings
from app.models.models import Item, StatusLevel


class NotificationService:
    """通知関連のサービスクラス"""
    
    @staticmethod
    def send_inventory_alert(
        item: Item, 
        user_name: str, 
        status: str,
        current_quantity: Optional[int] = None,
        current_status: Optional[StatusLevel] = None
    ):
        """在庫アラートをLINE Notifyで送信（非同期実行）"""
        if not settings.LINE_NOTIFY_TOKEN:
            print("LINE_NOTIFY_TOKEN is not set. Skipping notification.")
            return
        
        # 非同期で実行
        asyncio.create_task(
            NotificationService._send_line_notify_async(
                item, user_name, status, current_quantity, current_status
            )
        )
    
    @staticmethod
    async def _send_line_notify_async(
        item: Item, 
        user_name: str, 
        status: str,
        current_quantity: Optional[int] = None,
        current_status: Optional[StatusLevel] = None
    ):
        """LINE Notify APIで通知を送信（非同期）"""
        try:
            message = NotificationService._create_alert_message(
                item, user_name, status, current_quantity, current_status
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://notify-api.line.me/api/notify",
                    headers={
                        "Authorization": f"Bearer {settings.LINE_NOTIFY_TOKEN}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={"message": message}
                )
                
                if response.status_code == 200:
                    print(f"Alert sent successfully: {message}")
                else:
                    print(f"Failed to send alert: {response.status_code}")
                    
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    @staticmethod
    def _create_alert_message(
        item: Item, 
        user_name: str, 
        status: str,
        current_quantity: Optional[int] = None,
        current_status: Optional[StatusLevel] = None
    ) -> str:
        """アラートメッセージを作成"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if status == "low":
            status_text = "少ない"
            emoji = "⚠️"
        elif status == "high":
            status_text = "過剰"
            emoji = "🔴"
        else:
            return ""  # 正常な場合は通知しない
        
        # カテゴリ情報を追加
        category_text = ""
        if item.category.value == "supplies":
            category_text = "量管理の備品"
        elif item.category.value == "food":
            category_text = "量管理の食品"
        else:
            category_text = "個数管理"
        
        # 現在の状況を表示
        if current_quantity is not None:
            # 個数管理の場合
            current_info = f"{current_quantity}{item.unit}"
            threshold_info = f"下限：{item.threshold_low}{item.unit}、上限：{item.threshold_high}{item.unit}"
        else:
            # 量管理の場合
            status_map = {
                StatusLevel.LOW: "少ない",
                StatusLevel.SUFFICIENT: "十分",
                StatusLevel.HIGH: "多い"
            }
            current_info = status_map.get(current_status, "不明")
            threshold_info = "（3択での管理）"
        
        message = f"""【在庫アラート】
・{item.name}（{category_text}）の状況：{current_info}
・ステータス：{emoji} {status_text}
・管理方法：{threshold_info}
・前回更新：{user_name}（{current_time}）"""
        
        return message
    
    @staticmethod
    async def send_custom_notification(message: str):
        """カスタムメッセージをLINE Notifyで送信"""
        if not settings.LINE_NOTIFY_TOKEN:
            print("LINE_NOTIFY_TOKEN is not set. Skipping notification.")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://notify-api.line.me/api/notify",
                    headers={
                        "Authorization": f"Bearer {settings.LINE_NOTIFY_TOKEN}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={"message": message}
                )
                
                return response.status_code == 200
        except Exception as e:
            print(f"Error sending custom notification: {e}")
            return False 