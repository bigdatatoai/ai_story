"""
WebSocket路由配置
"""

from django.urls import re_path
from core.websocket.collaboration_consumer import StoryCollaborationConsumer

websocket_urlpatterns = [
    re_path(r'ws/story/(?P<story_id>[^/]+)/$', StoryCollaborationConsumer.as_asgi()),
]
