"""
项目模板视图集
职责: 处理项目模板的CRUD操作
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.projects.models_template import ProjectTemplate
from apps.projects.services.template_service import ProjectTemplateService


class ProjectTemplateViewSet(viewsets.ModelViewSet):
    """
    项目模板ViewSet
    
    提供模板的CRUD操作和从模板创建项目功能
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'usage_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """返回当前用户的模板和公开模板"""
        from django.db.models import Q
        return ProjectTemplate.objects.filter(
            Q(created_by=self.request.user) | Q(is_public=True)
        ).select_related('created_by')
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        # TODO: 创建对应的序列化器
        from rest_framework import serializers
        
        class ProjectTemplateSerializer(serializers.ModelSerializer):
            created_by_username = serializers.CharField(source='created_by.username', read_only=True)
            
            class Meta:
                model = ProjectTemplate
                fields = [
                    'id', 'name', 'description', 'is_public',
                    'template_data', 'usage_count',
                    'created_by', 'created_by_username',
                    'created_at', 'updated_at'
                ]
                read_only_fields = ['id', 'created_by', 'usage_count', 'created_at', 'updated_at']
        
        return ProjectTemplateSerializer
    
    def perform_create(self, serializer):
        """创建模板时自动设置当前用户"""
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        """只允许删除自己创建的模板"""
        if instance.created_by != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("只能删除自己创建的模板")
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def create_project(self, request, pk=None):
        """
        从模板创建项目
        POST /api/v1/templates/{id}/create-project/
        Body: {
            "project_name": "新项目",
            "original_topic": "项目主题"
        }
        """
        template = self.get_object()
        
        project_name = request.data.get('project_name')
        original_topic = request.data.get('original_topic')
        
        if not project_name or not original_topic:
            return Response(
                {'error': '缺少必要参数: project_name 和 original_topic'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 从模板创建项目
        project = ProjectTemplateService.create_from_template(
            template=template,
            user=request.user,
            project_name=project_name,
            original_topic=original_topic
        )
        
        from apps.projects.serializers import ProjectDetailSerializer
        
        return Response(
            {
                'message': f'项目已从模板创建: {project_name}',
                'project': ProjectDetailSerializer(project).data
            },
            status=status.HTTP_201_CREATED
        )
