"""
内容生成序列化器
职责: 数据序列化、验证、缓存优化
遵循单一职责原则(SRP)
"""

from rest_framework import serializers
from django.core.cache import cache
from django.db.models import Prefetch
import logging

from ..models import (
    ContentRewrite, Storyboard, GeneratedImage, 
    CameraMovement, GeneratedVideo
)

logger = logging.getLogger(__name__)


class CameraMovementSerializer(serializers.ModelSerializer):
    """运镜序列化器 - 带缓存和嵌套关联"""
    
    storyboard_name = serializers.CharField(source='storyboard.scene_description', read_only=True)
    model_provider_name = serializers.CharField(source='model_provider.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = CameraMovement
        fields = [
            'id', 'storyboard', 'storyboard_name', 'movement_type', 'movement_type_display',
            'movement_params', 'model_provider', 'model_provider_name', 'prompt_used',
            'is_deleted', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate_movement_params(self, value):
        """验证运镜参数"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("运镜参数必须是字典类型")
        
        required_params = ['speed', 'duration']
        for param in required_params:
            if param not in value:
                raise serializers.ValidationError(f"运镜参数缺失：{param}必须存在")
            if not isinstance(value[param], (int, float)):
                raise serializers.ValidationError(f"运镜参数类型错误：{param}必须为数字")
            if value[param] <= 0:
                raise serializers.ValidationError(f"运镜参数值错误：{param}必须大于0")
        
        return value

    def create(self, validated_data):
        """创建运镜数据，记录创建人"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        try:
            return super().create(validated_data)
        except Exception as e:
            logger.error(f"创建运镜数据失败: {str(e)}", exc_info=True)
            raise serializers.ValidationError(f"创建运镜数据失败: {str(e)}")


class CameraMovementListSerializer(serializers.ModelSerializer):
    """运镜列表序列化器 - 轻量级，带缓存"""
    
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    model_provider_name = serializers.SerializerMethodField()

    class Meta:
        model = CameraMovement
        fields = [
            'id', 'movement_type', 'movement_type_display', 
            'model_provider_name', 'created_at'
        ]

    def get_model_provider_name(self, obj):
        """缓存模型提供商名称"""
        if not obj.model_provider_id:
            return None
        
        cache_key = f'model_provider_name_{obj.model_provider_id}'
        name = cache.get(cache_key)
        
        if name is None:
            try:
                name = obj.model_provider.name if obj.model_provider else None
                cache.set(cache_key, name, 3600)
            except Exception as e:
                logger.warning(f"查询模型提供商名称失败: {str(e)}")
                name = None
        
        return name


class GeneratedImageSerializer(serializers.ModelSerializer):
    """生成图片序列化器"""
    
    storyboard_info = serializers.SerializerMethodField()
    model_provider_name = serializers.CharField(source='model_provider.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = GeneratedImage
        fields = [
            'id', 'storyboard', 'storyboard_info', 'image_url', 'thumbnail_url',
            'generation_params', 'model_provider', 'model_provider_name',
            'status', 'status_display', 'retry_count', 'error_message',
            'file_size', 'width', 'height', 'is_deleted',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def get_storyboard_info(self, obj):
        """获取分镜基本信息"""
        try:
            return {
                'id': str(obj.storyboard.id),
                'sequence_number': obj.storyboard.sequence_number,
                'scene_description': obj.storyboard.scene_description[:100]
            }
        except Exception as e:
            logger.warning(f"获取分镜信息失败: {str(e)}")
            return None


class GeneratedVideoSerializer(serializers.ModelSerializer):
    """生成视频序列化器"""
    
    storyboard_info = serializers.SerializerMethodField()
    image_url = serializers.CharField(source='image.image_url', read_only=True)
    camera_movement_type = serializers.CharField(source='camera_movement.movement_type', read_only=True)
    model_provider_name = serializers.CharField(source='model_provider.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = GeneratedVideo
        fields = [
            'id', 'storyboard', 'storyboard_info', 'image', 'image_url',
            'camera_movement', 'camera_movement_type', 'video_url', 'thumbnail_url',
            'duration', 'width', 'height', 'fps', 'file_size',
            'model_provider', 'model_provider_name', 'generation_params',
            'status', 'status_display', 'retry_count', 'error_message',
            'is_deleted', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def get_storyboard_info(self, obj):
        """获取分镜基本信息"""
        try:
            return {
                'id': str(obj.storyboard.id),
                'sequence_number': obj.storyboard.sequence_number,
                'scene_description': obj.storyboard.scene_description[:100]
            }
        except Exception as e:
            logger.warning(f"获取分镜信息失败: {str(e)}")
            return None


class StoryboardSerializer(serializers.ModelSerializer):
    """分镜序列化器 - 包含关联数据"""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    images = GeneratedImageSerializer(many=True, read_only=True)
    camera_movement = CameraMovementSerializer(read_only=True)
    videos = GeneratedVideoSerializer(many=True, read_only=True)
    
    images_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()

    class Meta:
        model = Storyboard
        fields = [
            'id', 'project', 'project_name', 'sequence_number',
            'scene_description', 'narration_text', 'image_prompt', 'duration_seconds',
            'images', 'images_count', 'camera_movement', 'videos', 'videos_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_images_count(self, obj):
        """缓存图片数量"""
        cache_key = f'storyboard_images_count_{obj.id}'
        count = cache.get(cache_key)
        
        if count is None:
            try:
                count = obj.images.filter(is_deleted=False).count()
                cache.set(cache_key, count, 300)
            except Exception as e:
                logger.warning(f"查询图片数量失败: {str(e)}")
                count = 0
        
        return count

    def get_videos_count(self, obj):
        """缓存视频数量"""
        cache_key = f'storyboard_videos_count_{obj.id}'
        count = cache.get(cache_key)
        
        if count is None:
            try:
                count = obj.videos.filter(is_deleted=False).count()
                cache.set(cache_key, count, 300)
            except Exception as e:
                logger.warning(f"查询视频数量失败: {str(e)}")
                count = 0
        
        return count


class StoryboardListSerializer(serializers.ModelSerializer):
    """分镜列表序列化器 - 轻量级"""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    has_camera_movement = serializers.SerializerMethodField()

    class Meta:
        model = Storyboard
        fields = [
            'id', 'project', 'project_name', 'sequence_number',
            'scene_description', 'duration_seconds', 'has_camera_movement',
            'created_at', 'updated_at'
        ]

    def get_has_camera_movement(self, obj):
        """检查是否有运镜数据"""
        try:
            return hasattr(obj, 'camera_movement') and not obj.camera_movement.is_deleted
        except Exception:
            return False


class ContentRewriteSerializer(serializers.ModelSerializer):
    """文案改写序列化器"""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    model_provider_name = serializers.CharField(source='model_provider.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ContentRewrite
        fields = [
            'id', 'project', 'project_name', 'original_text', 'rewritten_text',
            'model_provider', 'model_provider_name', 'prompt_used', 'generation_metadata',
            'is_deleted', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        """创建文案改写，记录创建人"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        try:
            return super().create(validated_data)
        except Exception as e:
            logger.error(f"创建文案改写失败: {str(e)}", exc_info=True)
            raise serializers.ValidationError(f"创建文案改写失败: {str(e)}")


class BulkCameraMovementSerializer(serializers.Serializer):
    """批量创建运镜序列化器"""
    
    camera_movements = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100
    )

    def validate_camera_movements(self, value):
        """验证批量数据"""
        for idx, data in enumerate(value):
            required_fields = ['storyboard', 'movement_type', 'movement_params']
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError(
                        f"第{idx+1}条数据缺少必需字段: {field}"
                    )
            
            if 'movement_params' in data:
                params = data['movement_params']
                if not isinstance(params, dict):
                    raise serializers.ValidationError(
                        f"第{idx+1}条数据的movement_params必须是字典类型"
                    )
                
                required_params = ['speed', 'duration']
                for param in required_params:
                    if param not in params:
                        raise serializers.ValidationError(
                            f"第{idx+1}条数据的运镜参数缺失: {param}"
                        )
        
        return value

    def create(self, validated_data):
        """批量创建运镜数据"""
        camera_movements_data = validated_data['camera_movements']
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None
        
        instances = []
        for data in camera_movements_data:
            if user:
                data['created_by'] = user
            instances.append(CameraMovement(**data))
        
        try:
            created = CameraMovement.objects.bulk_create(instances, batch_size=100)
            return {'created_count': len(created), 'camera_movements': created}
        except Exception as e:
            logger.error(f"批量创建运镜数据失败: {str(e)}", exc_info=True)
            raise serializers.ValidationError(f"批量创建失败: {str(e)}")
