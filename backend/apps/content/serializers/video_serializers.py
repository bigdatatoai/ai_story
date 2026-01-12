"""
视频相关的序列化器
"""

from rest_framework import serializers
from apps.content.models.video_models import Video, VideoScene, VideoExport, VideoTemplate


class VideoSceneSerializer(serializers.ModelSerializer):
    """视频场景序列化器"""
    
    class Meta:
        model = VideoScene
        fields = [
            'id', 'scene_number', 'image_url', 'video_clip_url',
            'narration', 'dialogue', 'duration', 'motion_prompt', 'transition',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VideoExportSerializer(serializers.ModelSerializer):
    """视频导出记录序列化器"""
    
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = VideoExport
        fields = [
            'id', 'format', 'format_display', 'status', 'status_display',
            'file_url', 'file_size', 'export_config', 'error_message',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'file_url', 'file_size', 'created_at', 'completed_at']


class VideoTemplateSerializer(serializers.ModelSerializer):
    """视频模板序列化器"""
    
    class Meta:
        model = VideoTemplate
        fields = [
            'id', 'name', 'description', 'category', 'template_config',
            'preview_url', 'thumbnail_url',
            'is_public', 'use_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'created_at', 'updated_at']


class VideoSerializer(serializers.ModelSerializer):
    """视频序列化器（详细）"""
    
    generation_type_display = serializers.CharField(
        source='get_generation_type_display',
        read_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    scenes = VideoSceneSerializer(many=True, read_only=True)
    exports = VideoExportSerializer(many=True, read_only=True)
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'generation_type', 'generation_type_display',
            'status', 'status_display', 'prompt', 'video_url', 'thumbnail_url',
            'duration', 'resolution', 'file_size', 'generation_config',
            'view_count', 'like_count', 'share_count',
            'scenes', 'exports', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'status', 'video_url', 'thumbnail_url', 'duration',
            'file_size', 'view_count', 'like_count',
            'share_count', 'created_at', 'updated_at', 'completed_at'
        ]


class VideoCreateSerializer(serializers.ModelSerializer):
    """视频创建序列化器"""
    
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'generation_type', 'prompt', 'generation_config'
        ]
    
    def validate_prompt(self, value):
        """验证prompt不能为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("视频描述不能为空")
        return value.strip()


class VideoUpdateSerializer(serializers.ModelSerializer):
    """视频更新序列化器"""
    
    class Meta:
        model = Video
        fields = ['title', 'description']
