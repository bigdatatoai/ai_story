"""内容生成URL路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StorageImageListView, 
    StorageImageDetailView, 
    StorageVideoDetailView
)
from .api_views import (
    CameraMovementViewSet,
    GeneratedImageViewSet,
    GeneratedVideoViewSet,
    StoryboardViewSet,
    ContentRewriteViewSet
)

try:
    from .views.story_views import StoryViewSet, StoryTemplateViewSet, CharacterViewSet
    from .views.video_views import VideoViewSet
    HAS_STORY_VIEWS = True
except ImportError:
    HAS_STORY_VIEWS = False

# 创建DRF路由器
router = DefaultRouter()

# 新增REST API路由
router.register(r'camera-movements', CameraMovementViewSet, basename='camera-movement')
router.register(r'images', GeneratedImageViewSet, basename='generated-image')
router.register(r'videos-generated', GeneratedVideoViewSet, basename='generated-video')
router.register(r'storyboards', StoryboardViewSet, basename='storyboard')
router.register(r'content-rewrites', ContentRewriteViewSet, basename='content-rewrite')

# 原有路由（如果存在）
if HAS_STORY_VIEWS:
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
