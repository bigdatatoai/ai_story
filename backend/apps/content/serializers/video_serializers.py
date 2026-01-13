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
    
    prompt = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(write_only=True, required=False)
    theme = serializers.CharField(write_only=True, required=False)
    episode_count = serializers.IntegerField(write_only=True, required=False)
    duration_per_episode = serializers.IntegerField(write_only=True, required=False)
    visual_style = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'generation_type', 'prompt', 'generation_config',
            'type', 'theme', 'episode_count', 'duration_per_episode', 'visual_style'
        ]
        extra_kwargs = {
            'title': {'required': False},
            'generation_type': {'required': False},
            'description': {'required': False},
        }
    
    def validate(self, attrs):
        """处理前端字段映射"""
        # 处理 type -> generation_type 映射
        if 'type' in attrs:
            attrs['generation_type'] = attrs.pop('type', 'text_to_video')
        
        # 如果没有 generation_type，设置默认值
        if 'generation_type' not in attrs:
            attrs['generation_type'] = 'text_to_video'
        
        # 处理 theme -> title 映射
        if 'theme' in attrs:
            attrs['title'] = attrs.pop('theme', '未命名视频')
            if 'prompt' not in attrs or not attrs.get('prompt'):
                attrs['prompt'] = attrs['title']
        
        # 确保有 title
        if not attrs.get('title'):
            attrs['title'] = '未命名视频'
        
        # 确保有 prompt
        if not attrs.get('prompt'):
            attrs['prompt'] = attrs.get('title', '未命名视频')
        
        # 处理配置字段
        config = attrs.get('generation_config', {})
        if 'episode_count' in attrs:
            config['episode_count'] = attrs.pop('episode_count')
        if 'duration_per_episode' in attrs:
            config['duration_per_episode'] = attrs.pop('duration_per_episode')
        if 'visual_style' in attrs:
            config['visual_style'] = attrs.pop('visual_style')
        
        if config:
            attrs['generation_config'] = config
        
        return attrs
    
    def validate_generation_type(self, value):
        """验证生成类型"""
        valid_types = ['text_to_video', 'image_to_video', 'storyboard_to_video', 'story_to_video', 
                       'drama', 'anime', 'comic']
        if value not in valid_types:
            return 'text_to_video'
        return value


class VideoUpdateSerializer(serializers.ModelSerializer):
    """视频更新序列化器"""
    
    class Meta:
        model = Video
        fields = ['title', 'description']
