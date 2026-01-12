"""内容生成URL路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StorageImageListView, 
    StorageImageDetailView, 
    StorageVideoDetailView
)
from .views.story_views import StoryViewSet, StoryTemplateViewSet, CharacterViewSet
from .views.video_views import VideoViewSet

# 创建DRF路由器
router = DefaultRouter()
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'story-templates', StoryTemplateViewSet, basename='story-template')
router.register(r'characters', CharacterViewSet, basename='character')
router.register(r'videos', VideoViewSet, basename='video')

urlpatterns = [
    # Storage图片API
    path('storage/image/', StorageImageListView.as_view(), name='storage-image-list'),
    # 支持日期子目录: storage/image/2025-11-30/xx.png
    path('storage/image/<path:filepath>', StorageImageDetailView.as_view(), name='storage-image-detail'),
    # 支持日期子目录: storage/video/2025-11-30/xx.mp4
    path('storage/video/<path:filepath>', StorageVideoDetailView.as_view(), name='storage-video-detail'),
    
    # REST API路由 - 所有ViewSet的路由
    path('', include(router.urls)),
]
