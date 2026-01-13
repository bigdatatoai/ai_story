"""
内容管理REST API视图
职责: 提供运镜、图片、视频等内容的CRUD接口
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Prefetch, Q
from django.core.cache import cache
import logging

from core.utils.response_wrapper import APIResponse
from .models import (
    CameraMovement, GeneratedImage, GeneratedVideo,
    Storyboard, ContentRewrite
)
from .serializers import (
    CameraMovementSerializer, CameraMovementListSerializer,
    GeneratedImageSerializer, GeneratedVideoSerializer,
    StoryboardSerializer, StoryboardListSerializer,
    ContentRewriteSerializer, BulkCameraMovementSerializer
)
from .tasks import generate_image_task, generate_video_task, generate_camera_movement_task

logger = logging.getLogger(__name__)


class CameraMovementViewSet(viewsets.ModelViewSet):
    """运镜管理ViewSet"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CameraMovementListSerializer
        return CameraMovementSerializer
    
    def get_queryset(self):
        """优化查询，避免N+1问题"""
        queryset = CameraMovement.objects.filter(is_deleted=False).select_related(
            'storyboard', 'model_provider', 'created_by'
        )
        
        # 过滤参数
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        storyboard_id = self.request.query_params.get('storyboard_id')
        if storyboard_id:
            queryset = queryset.filter(storyboard_id=storyboard_id)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """列表查询"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # 分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(serializer.data, message="查询成功")
            
        except Exception as e:
            logger.error(f"查询运镜列表失败: {str(e)}", exc_info=True)
            return APIResponse.server_error(message=f"查询失败: {str(e)}")
    
    def retrieve(self, request, *args, **kwargs):
        """详情查询"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(serializer.data, message="查询成功")
        except Exception as e:
            logger.error(f"查询运镜详情失败: {str(e)}", exc_info=True)
            return APIResponse.not_found(message="运镜数据不存在")
    
    def create(self, request, *args, **kwargs):
        """创建运镜"""
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            # 清除相关缓存
            self._clear_cache(serializer.instance)
            
            return APIResponse.created(serializer.data, message="创建成功")
            
        except Exception as e:
            logger.error(f"创建运镜失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"创建失败: {str(e)}")
    
    def update(self, request, *args, **kwargs):
        """更新运镜"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # 清除相关缓存
            self._clear_cache(serializer.instance)
            
            return APIResponse.success(serializer.data, message="更新成功")
            
        except Exception as e:
            logger.error(f"更新运镜失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"更新失败: {str(e)}")
    
    def destroy(self, request, *args, **kwargs):
        """软删除运镜"""
        try:
            instance = self.get_object()
            instance.delete()  # 调用模型的软删除方法
            
            # 清除相关缓存
            self._clear_cache(instance)
            
            return APIResponse.no_content(message="删除成功")
            
        except Exception as e:
            logger.error(f"删除运镜失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"删除失败: {str(e)}")
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_create(self, request):
        """批量创建运镜"""
        try:
            serializer = BulkCameraMovementSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            result = serializer.save()
            
            return APIResponse.created(result, message=f"批量创建成功，共创建{result['created_count']}条数据")
            
        except Exception as e:
            logger.error(f"批量创建运镜失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"批量创建失败: {str(e)}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_params(self, request, pk=None):
        """异步生成运镜参数"""
        try:
            instance = self.get_object()
            
            # 调用异步任务
            task = generate_camera_movement_task.delay(str(instance.id))
            
            return APIResponse.success({
                'task_id': task.id,
                'camera_movement_id': str(instance.id)
            }, message="运镜参数生成任务已提交")
            
        except Exception as e:
            logger.error(f"提交运镜参数生成任务失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"提交任务失败: {str(e)}")
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def movement_types(self, request):
        """获取运镜类型列表（带缓存）"""
        cache_key = 'camera_movement_types'
        types = cache.get(cache_key)
        
        if types is None:
            types = [{'value': t[0], 'label': t[1]} for t in CameraMovement.MOVEMENT_TYPES]
            cache.set(cache_key, types, 86400)  # 缓存24小时
        
        return APIResponse.success(types, message="查询成功")
    
    def _clear_cache(self, instance):
        """清除相关缓存"""
        if instance.storyboard_id:
            cache.delete(f'storyboard_videos_count_{instance.storyboard_id}')


class GeneratedImageViewSet(viewsets.ModelViewSet):
    """生成图片管理ViewSet"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratedImageSerializer
    
    def get_queryset(self):
        """优化查询"""
        queryset = GeneratedImage.objects.filter(is_deleted=False).select_related(
            'storyboard', 'model_provider', 'created_by'
        )
        
        # 过滤参数
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        storyboard_id = self.request.query_params.get('storyboard_id')
        if storyboard_id:
            queryset = queryset.filter(storyboard_id=storyboard_id)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """列表查询"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(serializer.data, message="查询成功")
            
        except Exception as e:
            logger.error(f"查询图片列表失败: {str(e)}", exc_info=True)
            return APIResponse.server_error(message=f"查询失败: {str(e)}")
    
    def create(self, request, *args, **kwargs):
        """创建图片生成任务"""
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            
            # 异步生成图片
            task = generate_image_task.delay(str(instance.id))
            
            return APIResponse.created({
                'image': serializer.data,
                'task_id': task.id
            }, message="图片生成任务已创建")
            
        except Exception as e:
            logger.error(f"创建图片生成任务失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"创建失败: {str(e)}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def retry(self, request, pk=None):
        """重试失败的图片生成"""
        try:
            instance = self.get_object()
            
            if instance.status not in ['failed', 'pending']:
                return APIResponse.bad_request(message="只能重试失败或待处理的任务")
            
            # 重置状态
            instance.status = 'pending'
            instance.error_message = ''
            instance.save(update_fields=['status', 'error_message', 'updated_at'])
            
            # 重新提交任务
            task = generate_image_task.delay(str(instance.id))
            
            return APIResponse.success({
                'task_id': task.id,
                'image_id': str(instance.id)
            }, message="重试任务已提交")
            
        except Exception as e:
            logger.error(f"重试图片生成失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"重试失败: {str(e)}")


class GeneratedVideoViewSet(viewsets.ModelViewSet):
    """生成视频管理ViewSet"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = GeneratedVideoSerializer
    
    def get_queryset(self):
        """优化查询"""
        queryset = GeneratedVideo.objects.filter(is_deleted=False).select_related(
            'storyboard', 'image', 'camera_movement', 'model_provider', 'created_by'
        )
        
        # 过滤参数
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        storyboard_id = self.request.query_params.get('storyboard_id')
        if storyboard_id:
            queryset = queryset.filter(storyboard_id=storyboard_id)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """列表查询"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(serializer.data, message="查询成功")
            
        except Exception as e:
            logger.error(f"查询视频列表失败: {str(e)}", exc_info=True)
            return APIResponse.server_error(message=f"查询失败: {str(e)}")
    
    def create(self, request, *args, **kwargs):
        """创建视频生成任务"""
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            
            # 异步生成视频
            task = generate_video_task.delay(str(instance.id))
            
            return APIResponse.created({
                'video': serializer.data,
                'task_id': task.id
            }, message="视频生成任务已创建")
            
        except Exception as e:
            logger.error(f"创建视频生成任务失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"创建失败: {str(e)}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def retry(self, request, pk=None):
        """重试失败的视频生成"""
        try:
            instance = self.get_object()
            
            if instance.status not in ['failed', 'pending']:
                return APIResponse.bad_request(message="只能重试失败或待处理的任务")
            
            # 重置状态
            instance.status = 'pending'
            instance.error_message = ''
            instance.save(update_fields=['status', 'error_message', 'updated_at'])
            
            # 重新提交任务
            task = generate_video_task.delay(str(instance.id))
            
            return APIResponse.success({
                'task_id': task.id,
                'video_id': str(instance.id)
            }, message="重试任务已提交")
            
        except Exception as e:
            logger.error(f"重试视频生成失败: {str(e)}", exc_info=True)
            return APIResponse.bad_request(message=f"重试失败: {str(e)}")


class StoryboardViewSet(viewsets.ModelViewSet):
    """分镜管理ViewSet"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StoryboardListSerializer
        return StoryboardSerializer
    
    def get_queryset(self):
        """优化查询"""
        queryset = Storyboard.objects.select_related('project')
        
        # 详情查询时预加载关联数据
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                Prefetch('images', queryset=GeneratedImage.objects.filter(is_deleted=False)),
                Prefetch('videos', queryset=GeneratedVideo.objects.filter(is_deleted=False)),
                'camera_movement'
            )
        
        # 过滤参数
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.order_by('sequence_number')
    
    def list(self, request, *args, **kwargs):
        """列表查询"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(serializer.data, message="查询成功")
            
        except Exception as e:
            logger.error(f"查询分镜列表失败: {str(e)}", exc_info=True)
            return APIResponse.server_error(message=f"查询失败: {str(e)}")
    
    def retrieve(self, request, *args, **kwargs):
        """详情查询"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(serializer.data, message="查询成功")
        except Exception as e:
            logger.error(f"查询分镜详情失败: {str(e)}", exc_info=True)
            return APIResponse.not_found(message="分镜不存在")


class ContentRewriteViewSet(viewsets.ModelViewSet):
    """文案改写管理ViewSet"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ContentRewriteSerializer
    
    def get_queryset(self):
        """优化查询"""
        queryset = ContentRewrite.objects.filter(is_deleted=False).select_related(
            'project', 'model_provider', 'created_by'
        )
        
        # 过滤参数
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """列表查询"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(serializer.data, message="查询成功")
            
        except Exception as e:
            logger.error(f"查询文案改写列表失败: {str(e)}", exc_info=True)
            return APIResponse.server_error(message=f"查询失败: {str(e)}")
