"""内容管理视图包"""
from .base_views import StorageImageListView, StorageImageDetailView, StorageVideoDetailView
from .story_views import StoryViewSet, StoryTemplateViewSet, CharacterViewSet
from .video_views import VideoViewSet

__all__ = [
    'StorageImageListView',
    'StorageImageDetailView', 
    'StorageVideoDetailView',
    'StoryViewSet',
    'StoryTemplateViewSet',
    'CharacterViewSet',
    'VideoViewSet',
]
