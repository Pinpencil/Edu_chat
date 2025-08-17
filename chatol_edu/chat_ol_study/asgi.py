"""
ASGI config for chat_ol_study project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from chat_ol_app.consumers import NotifyConsumer, ThemeConsumer  # 引入 WebSocket 消费者

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_ol_study.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/notify/", NotifyConsumer.as_asgi()),  # 配置通知 WebSocket 路由
            path("ws/theme/<int:theme_id>/", ThemeConsumer.as_asgi()),  # 配置主题 WebSocket 路由
        ])
    ),
})