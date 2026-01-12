"""
视频管理视图
提供完整的视频生成、编辑、导出等功能
"""

import logging
import uuid
from typing import Dict, Any
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.content.models.video_models import Video, VideoScene, VideoExport, VideoTemplate
from apps.content.serializers.video_serializers import (
    VideoSerializer, VideoCreateSerializer, VideoUpdateSerializer
)
from core.services.video_generation_service import video_generation_service
from core.middleware.rate_limiting import rate_limit_decorator

logger = logging.getLogger('ai_story.api')


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class VideoViewSet(viewsets.ModelViewSet):
    """视频管理ViewSet"""
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = VideoSerializer
    
    def get_queryset(self):
        return Video.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return VideoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VideoUpdateSerializer
        return VideoSerializer
    
    def perform_create(self, serializer):
        """创建视频时自动设置用户"""
        serializer.save(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """重写list方法，返回统一格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'success': True,
                'data': {
                    'results': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link()
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """重写create方法，返回统一格式"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': '创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def retrieve(self, request, *args, **kwargs):
        """重写retrieve方法，返回统一格式"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """重写update方法，返回统一格式"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': '更新成功',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """重写destroy方法，返回统一格式"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': '删除成功'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=5, window=60)
    def text_to_video(self, request):
        """
        文本转视频
        
        POST /api/v1/videos/text_to_video/
        
        Request:
        {
            "prompt": "一只可爱的小兔子在森林里跳跃",
            "duration": 4,
            "resolution": "1280x720",
            "style": "cartoon"
        }
        """
        try:
            prompt = request.data.get('prompt')
            if not prompt:
                return Response({
                    'success': False,
                    'error': '请提供视频描述'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建视频记录
            video = Video.objects.create(
                user=request.user,
                title=prompt[:100],
                generation_type='text_to_video',
                prompt=prompt,
                status='processing',
                generation_config=request.data
            )
            
            # 异步生成视频
            try:
                result = video_generation_service.text_to_video(
                    prompt=prompt,
                    duration=request.data.get('duration', 4),
                    resolution=request.data.get('resolution', '1280x720'),
                    style=request.data.get('style', 'realistic')
                )
                
                # 更新视频信息
                video.video_url = result['video_url']
                video.thumbnail_url = result.get('thumbnail_url', '')
                video.duration = result['duration']
                video.resolution = result['resolution']
                video.file_size = result.get('file_size', 0)
                video.status = 'completed'
                video.completed_at = timezone.now()
                video.save()
                
                return Response({
                    'success': True,
                    'message': '视频生成成功',
                    'data': {
                        'video_id': str(video.id),
                        'video_url': video.video_url,
                        'thumbnail_url': video.thumbnail_url,
                        'duration': video.duration
                    }
                })
                
            except Exception as e:
                video.status = 'failed'
                video.error_message = str(e)
                video.save()
                raise
            
        except Exception as e:
            logger.error(f"文本转视频失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'视频生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=5, window=60)
    def image_to_video(self, request):
        """
        图片转视频
        
        POST /api/v1/videos/image_to_video/
        
        Request:
        {
            "image_url": "https://...",
            "motion_prompt": "镜头缓慢推进",
            "duration": 4
        }
        """
        try:
            image_url = request.data.get('image_url')
            if not image_url:
                return Response({
                    'success': False,
                    'error': '请提供图片URL'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建视频记录
            video = Video.objects.create(
                user=request.user,
                title=f"图片转视频_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                generation_type='image_to_video',
                status='processing',
                generation_config=request.data
            )
            
            # 生成视频
            try:
                result = video_generation_service.image_to_video(
                    image_url=image_url,
                    motion_prompt=request.data.get('motion_prompt', ''),
                    duration=request.data.get('duration', 4),
                    motion_strength=request.data.get('motion_strength', 0.5)
                )
                
                video.video_url = result['video_url']
                video.duration = result['duration']
                video.status = 'completed'
                video.completed_at = timezone.now()
                video.save()
                
                return Response({
                    'success': True,
                    'data': {
                        'video_id': str(video.id),
                        'video_url': video.video_url
                    }
                })
                
            except Exception as e:
                video.status = 'failed'
                video.error_message = str(e)
                video.save()
                raise
            
        except Exception as e:
            logger.error(f"图片转视频失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'视频生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=3, window=60)
    def storyboard_to_video(self, request):
        """
        故事板转视频
        
        POST /api/v1/videos/storyboard_to_video/
        
        Request:
        {
            "title": "我的故事视频",
            "storyboard": [
                {
                    "image_url": "https://...",
                    "narration": "很久很久以前...",
                    "duration": 4,
                    "motion": "镜头推进"
                }
            ],
            "transition_style": "fade",
            "background_music_url": "https://..."
        }
        """
        try:
            storyboard = request.data.get('storyboard', [])
            if not storyboard:
                return Response({
                    'success': False,
                    'error': '请提供故事板'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建视频记录
            video = Video.objects.create(
                user=request.user,
                title=request.data.get('title', '故事板视频'),
                generation_type='storyboard_to_video',
                status='processing',
                generation_config=request.data
            )
            
            # 创建场景记录
            for i, scene_data in enumerate(storyboard):
                VideoScene.objects.create(
                    video=video,
                    scene_number=i + 1,
                    image_url=scene_data.get('image_url', ''),
                    narration=scene_data.get('narration', ''),
                    motion_prompt=scene_data.get('motion', ''),
                    duration=scene_data.get('duration', 4)
                )
            
            # 生成视频
            try:
                result = video_generation_service.storyboard_to_video(
                    storyboard=storyboard,
                    transition_style=request.data.get('transition_style', 'fade'),
                    background_music_url=request.data.get('background_music_url')
                )
                
                video.video_url = result['video_url']
                video.duration = result['duration']
                video.resolution = result['resolution']
                video.file_size = result.get('file_size', 0)
                video.status = 'completed'
                video.completed_at = timezone.now()
                video.save()
                
                return Response({
                    'success': True,
                    'message': '视频生成成功',
                    'data': {
                        'video_id': str(video.id),
                        'video_url': video.video_url,
                        'duration': video.duration
                    }
                })
                
            except Exception as e:
                video.status = 'failed'
                video.error_message = str(e)
                video.save()
                raise
            
        except Exception as e:
            logger.error(f"故事板转视频失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'视频生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """
        导出视频
        
        POST /api/v1/videos/{id}/export/
        
        Request:
        {
            "format": "mp4",
            "resolution": "1920x1080",
            "quality": "high"
        }
        """
        video = self.get_object()
        
        try:
            export_record = VideoExport.objects.create(
                video=video,
                user=request.user,
                format=request.data.get('format', 'mp4'),
                resolution=request.data.get('resolution', video.resolution),
                quality=request.data.get('quality', 'high'),
                status='pending'
            )
            
            # TODO: 异步处理导出任务
            
            return Response({
                'success': True,
                'message': '导出任务已创建',
                'data': {
                    'export_id': str(export_record.id),
                    'status': export_record.status
                }
            })
            
        except Exception as e:
            logger.error(f"创建导出任务失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'导出失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """获取视频生成状态"""
        video = self.get_object()
        
        return Response({
            'success': True,
            'data': {
                'video_id': str(video.id),
                'status': video.status,
                'progress': 100 if video.status == 'completed' else 50,
                'video_url': video.video_url if video.status == 'completed' else None,
                'error_message': video.error_message if video.status == 'failed' else None
            }
        })
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=10, window=60)
    def generate_anime_character(self, request):
        """
        生成动漫角色
        
        POST /api/v1/content/videos/generate_anime_character/
        """
        try:
            from core.services.anime_generation_service import anime_generation_service
            
            character_description = request.data.get('character_description', {})
            anime_style = request.data.get('anime_style', 'shounen')
            poses = request.data.get('poses', ['standing', 'side_view'])
            expressions = request.data.get('expressions', ['neutral', 'happy'])
            
            result = anime_generation_service.generate_anime_character(
                character_description=character_description,
                anime_style=anime_style,
                poses=poses,
                expressions=expressions
            )
            
            return Response({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            logger.error(f"生成动漫角色失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=10, window=60)
    def generate_anime_scene(self, request):
        """
        生成动漫场景
        
        POST /api/v1/content/videos/generate_anime_scene/
        """
        try:
            from core.services.anime_generation_service import anime_generation_service
            
            scene_description = request.data.get('scene_description', '')
            characters = request.data.get('characters', [])
            anime_style = request.data.get('anime_style', 'shounen')
            camera_angle = request.data.get('camera_angle', 'medium_shot')
            
            result = anime_generation_service.generate_anime_scene(
                scene_description=scene_description,
                characters=characters,
                anime_style=anime_style,
                camera_angle=camera_angle
            )
            
            return Response({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            logger.error(f"生成动漫场景失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=5, window=60)
    def generate_comic_panels(self, request):
        """
        生成漫画分格
        
        POST /api/v1/content/videos/generate_comic_panels/
        """
        try:
            from core.services.anime_generation_service import anime_generation_service
            
            script = request.data.get('script', {})
            panel_layout = request.data.get('panel_layout', '4_panel')
            
            result = anime_generation_service.generate_comic_panels(
                script=script,
                panel_layout=panel_layout
            )
            
            return Response({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            logger.error(f"生成漫画分格失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=3, window=300)
    def batch_produce(self, request):
        """
        批量生产
        
        POST /api/v1/content/videos/batch_produce/
        """
        try:
            name = request.data.get('name', '批量任务')
            video_type = request.data.get('type', 'short_drama')
            themes = request.data.get('themes', [])
            episode_count = request.data.get('episode_count', 3)
            duration_per_episode = request.data.get('duration_per_episode', 60)
            visual_style = request.data.get('visual_style', 'realistic')
            
            if not themes:
                return Response({
                    'success': False,
                    'error': '请提供主题列表'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建批量任务记录
            batch_task = {
                'id': str(uuid.uuid4()),
                'name': name,
                'type': video_type,
                'total_count': len(themes),
                'completed_count': 0,
                'failed_count': 0,
                'status': 'processing',
                'items': []
            }
            
            # 为每个主题创建视频项目
            for theme in themes:
                video = Video.objects.create(
                    user=request.user,
                    title=f"{theme}",
                    generation_type='drama_production',
                    status='pending',
                    generation_config={
                        'theme': theme,
                        'episode_count': episode_count,
                        'duration_per_episode': duration_per_episode,
                        'visual_style': visual_style
                    }
                )
                batch_task['items'].append({
                    'id': str(video.id),
                    'title': theme,
                    'status': 'pending'
                })
            
            return Response({
                'success': True,
                'data': batch_task
            })
            
        except Exception as e:
            logger.error(f"批量生产失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'批量生产失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        获取生产统计
        
        GET /api/v1/content/videos/stats/
        """
        try:
            user_videos = Video.objects.filter(user=request.user)
            
            stats = {
                'total': user_videos.count(),
                'processing': user_videos.filter(status='processing').count(),
                'completed': user_videos.filter(status='completed').count(),
                'failed': user_videos.filter(status='failed').count(),
                'total_duration': sum(v.duration or 0 for v in user_videos.filter(status='completed')),
                'total_views': sum(v.view_count or 0 for v in user_videos),
            }
            
            return Response({
                'success': True,
                'data': stats
            })
            
        except Exception as e:
            logger.error(f"获取统计失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'获取统计失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
