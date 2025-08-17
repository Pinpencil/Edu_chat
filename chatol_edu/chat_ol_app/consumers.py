from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
from django.urls import re_path
from chat_ol_app import consumers
# WebSocket 路由配置
class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 将连接加入广播组
        print("WebSocket connection established")
        await self.channel_layer.group_add(
            "broadcast_group",
            self.channel_name
        )
        await self.accept()  # 接受 WebSocket 连接

    async def disconnect(self, close_code):
        # 断开连接时离开广播组
        await self.channel_layer.group_discard(
            "broadcast_group",
            self.channel_name
        )

    async def receive(self, text_data):
        # 接收消息时处理
        data = json.loads(text_data)
        print(f"Received message: {data}")
        
        # 可以在这里处理接收到的消息并广播
        await self.channel_layer.group_send(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": data
            }
        )

    # 处理广播消息
    async def broadcast_message(self, event):
        # 发送消息到 WebSocket
        await self.send(text_data=json.dumps(event["message"]))

class ThemeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 获取主题 ID
        self.theme_id = self.scope['url_route']['kwargs']['theme_id']
        self.theme_group_name = f"theme_{self.theme_id}"

        # 将连接加入主题组
        await self.channel_layer.group_add(
            self.theme_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 从主题组移除连接
        await self.channel_layer.group_discard(
            self.theme_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # 接收消息并广播到主题组
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.theme_group_name,
            {
                "type": "theme_message",
                "message": data
            }
        )

    async def theme_message(self, event):
        # 将消息发送到 WebSocket
        await self.send(text_data=json.dumps(event["message"]))