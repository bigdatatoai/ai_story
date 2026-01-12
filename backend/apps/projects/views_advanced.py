"""
高级服务 API 视图
提供 TTS、STT、音乐、去重、发布等高级功能的 API 端点
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.projects.models import Project
from core.services.tts_service import TTSService
from core.services.stt_service import STTService
from core.services.music_service import AudioMixer
from core.services.video_dedup_service import VideoDeduplicationService, VideoRemixService
from core.services.platform_publish_service import PlatformPublishService
from core.services.batch_processing_service import BatchProcessingService

logger = logging.getLogger(__name__)


class AdvancedServiceViewSet(viewsets.ViewSet):
    """高级服务视图集"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'], url_path='generate-voiceover')
    def generate_voiceover(self, request, pk=None):
        """
        生成AI配音
        POST /api/v1/projects/advanced/{project_id}/generate-voiceover/
        Body: {
            "text": "要转换的文本",
            "voice": "xiaoyun",  // 可选
            "provider": "aliyun"  // 可选: aliyun, azure, xunfei
        }
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        text = request.data.get('text')
        voice = request.data.get('voice', 'xiaoyun')
        provider = request.data.get('provider', 'aliyun')
        
        if not text:
            return Response(
                {'error': '缺少 text 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tts_service = TTSService()
            audio_path = tts_service.text_to_speech(
                text=text,
                voice=voice,
                provider=provider
            )
            
            return Response({
                'success': True,
                'audio_path': audio_path,
                'message': 'AI配音生成成功'
            })
        except Exception as e:
            logger.error(f"AI配音生成失败: {str(e)}")
            return Response(
                {'error': f'AI配音生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='generate-subtitles')
    def generate_subtitles(self, request, pk=None):
        """
        生成字幕（语音识别）
        POST /api/v1/projects/advanced/{project_id}/generate-subtitles/
        Body: {
            "video_path": "/path/to/video.mp4",
            "language": "zh"  // 可选
        }
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        video_path = request.data.get('video_path')
        language = request.data.get('language', 'zh')
        
        if not video_path:
            return Response(
                {'error': '缺少 video_path 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stt_service = STTService()
            subtitles = stt_service.generate_subtitles(
                video_path=video_path,
                language=language
            )
            
            return Response({
                'success': True,
                'subtitles': subtitles,
                'message': '字幕生成成功'
            })
        except Exception as e:
            logger.error(f"字幕生成失败: {str(e)}")
            return Response(
                {'error': f'字幕生成失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='add-background-music')
    def add_background_music(self, request, pk=None):
        """
        添加背景音乐
        POST /api/v1/projects/advanced/{project_id}/add-background-music/
        Body: {
            "video_path": "/path/to/video.mp4",
            "music_path": "/path/to/music.mp3",
            "volume": 0.3  // 可选，音乐音量 0-1
        }
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        video_path = request.data.get('video_path')
        music_path = request.data.get('music_path')
        volume = request.data.get('volume', 0.3)
        
        if not video_path or not music_path:
            return Response(
                {'error': '缺少 video_path 或 music_path 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            mixer = AudioMixer()
            output_path = mixer.add_background_music(
                video_path=video_path,
                music_path=music_path,
                music_volume=volume
            )
            
            return Response({
                'success': True,
                'output_path': output_path,
                'message': '背景音乐添加成功'
            })
        except Exception as e:
            logger.error(f"背景音乐添加失败: {str(e)}")
            return Response(
                {'error': f'背景音乐添加失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='deduplicate-video')
    def deduplicate_video(self, request, pk=None):
        """
        视频去重
        POST /api/v1/projects/advanced/{project_id}/deduplicate-video/
        Body: {
            "video_path": "/path/to/video.mp4",
            "method": "mirror"  // mirror, speed, crop, filter
        }
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        video_path = request.data.get('video_path')
        method = request.data.get('method', 'mirror')
        
        if not video_path:
            return Response(
                {'error': '缺少 video_path 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dedup_service = VideoDeduplicationService()
            output_path = dedup_service.apply_deduplication(
                video_path=video_path,
                methods=[method] if method else None,
                intensity='medium'
            )
            
            return Response({
                'success': True,
                'output_path': output_path,
                'method': method,
                'message': '视频去重成功'
            })
        except Exception as e:
            logger.error(f"视频去重失败: {str(e)}")
            return Response(
                {'error': f'视频去重失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='publish-to-platform')
    def publish_to_platform(self, request, pk=None):
        """
        发布到平台
        POST /api/v1/projects/advanced/{project_id}/publish-to-platform/
        Body: {
            "video_path": "/path/to/video.mp4",
            "platform": "douyin",  // douyin, kuaishou, bilibili
            "title": "视频标题",
            "description": "视频描述",
            "tags": ["标签1", "标签2"]
        }
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        video_path = request.data.get('video_path')
        platform = request.data.get('platform')
        title = request.data.get('title')
        description = request.data.get('description', '')
        tags = request.data.get('tags', [])
        
        if not video_path or not platform or not title:
            return Response(
                {'error': '缺少必需参数: video_path, platform, title'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            publisher = PlatformPublishService()
            result = publisher.publish_to_platform(
                platform=platform,
                video_path=video_path,
                title=title,
                description=description,
                tags=tags
            )
            
            return Response({
                'success': True,
                'platform': platform,
                'result': result,
                'message': f'已发布到 {platform}'
            })
        except Exception as e:
            logger.error(f"平台发布失败: {str(e)}")
            return Response(
                {'error': f'平台发布失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='batch-process')
    def batch_process(self, request):
        """
        批量处理
        POST /api/v1/projects/advanced/batch-process/
        Body: {
            "project_ids": ["id1", "id2", "id3"],
            "operation": "export",  // export, publish, etc.
            "params": {}  // 操作参数
        }
        """
        project_ids = request.data.get('project_ids', [])
        operation = request.data.get('operation')
        params = request.data.get('params', {})
        
        if not project_ids or not operation:
            return Response(
                {'error': '缺少必需参数: project_ids, operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证用户权限
        projects = Project.objects.filter(
            id__in=project_ids,
            user=request.user
        )
        
        if projects.count() != len(project_ids):
            return Response(
                {'error': '部分项目不存在或无权限'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            batch_processor = BatchProcessingService()
            task_id = batch_processor.start_batch_processing(
                project_ids=project_ids,
                operation=operation,
                params=params,
                user_id=request.user.id
            )
            
            return Response({
                'success': True,
                'task_id': task_id,
                'total_projects': len(project_ids),
                'message': '批量处理任务已启动'
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"批量处理失败: {str(e)}")
            return Response(
                {'error': f'批量处理失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
