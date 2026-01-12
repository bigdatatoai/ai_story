"""
工作流 API 视图
提供工作流的创建、编辑、执行等功能
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.projects.models import Project
from apps.projects.models_workflow import (
    WorkflowTemplate, ProjectWorkflow, WorkflowNode, WorkflowExecution
)
from core.workflow.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)


class WorkflowViewSet(viewsets.ViewSet):
    """工作流视图集"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'], url_path='save-workflow')
    def save_workflow(self, request, pk=None):
        """
        保存项目工作流
        POST /api/v1/projects/{id}/save-workflow/
        Body: {
            "workflow_data": {
                "nodes": [...],
                "edges": [...]
            }
        }
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        workflow_data = request.data.get('workflow_data')
        
        if not workflow_data:
            return Response(
                {'error': '缺少 workflow_data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建或更新工作流
        workflow, created = ProjectWorkflow.objects.update_or_create(
            project=project,
            defaults={'workflow_data': workflow_data}
        )
        
        return Response({
            'message': '工作流已保存',
            'workflow_id': str(workflow.id),
            'created': created
        })
    
    @action(detail=True, methods=['get'], url_path='get-workflow')
    def get_workflow(self, request, pk=None):
        """
        获取项目工作流
        GET /api/v1/projects/{id}/get-workflow/
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        
        try:
            workflow = project.workflow
            return Response({
                'workflow_id': str(workflow.id),
                'workflow_data': workflow.workflow_data,
                'status': workflow.status,
                'execution_results': workflow.execution_results
            })
        except ProjectWorkflow.DoesNotExist:
            return Response({
                'workflow_data': {'nodes': [], 'edges': []},
                'status': 'draft'
            })
    
    @action(detail=True, methods=['post'], url_path='execute-workflow')
    def execute_workflow(self, request, pk=None):
        """
        执行工作流
        POST /api/v1/projects/{id}/execute-workflow/
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        
        try:
            workflow = project.workflow
        except ProjectWorkflow.DoesNotExist:
            return Response(
                {'error': '项目没有工作流'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建执行记录
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='pending'
        )
        
        # 异步执行工作流
        from apps.projects.tasks import execute_workflow_task
        task = execute_workflow_task.delay(
            workflow_id=str(workflow.id),
            execution_id=str(execution.id)
        )
        
        # 更新工作流状态
        workflow.status = 'running'
        workflow.save()
        
        return Response({
            'message': '工作流已启动',
            'execution_id': str(execution.id),
            'task_id': task.id,
            'channel': f'workflow:{workflow.id}:execution'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'], url_path='pause-workflow')
    def pause_workflow(self, request, pk=None):
        """
        暂停工作流执行
        POST /api/v1/projects/{id}/pause-workflow/
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        
        try:
            workflow = project.workflow
            workflow.status = 'paused'
            workflow.save()
            
            return Response({'message': '工作流已暂停'})
        except ProjectWorkflow.DoesNotExist:
            return Response(
                {'error': '项目没有工作流'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='resume-workflow')
    def resume_workflow(self, request, pk=None):
        """
        恢复工作流执行
        POST /api/v1/projects/{id}/resume-workflow/
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        
        try:
            workflow = project.workflow
            
            if workflow.status != 'paused':
                return Response(
                    {'error': '工作流未暂停'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 从当前节点继续执行
            from apps.projects.tasks import resume_workflow_task
            task = resume_workflow_task.delay(workflow_id=str(workflow.id))
            
            workflow.status = 'running'
            workflow.save()
            
            return Response({
                'message': '工作流已恢复',
                'task_id': task.id
            })
        except ProjectWorkflow.DoesNotExist:
            return Response(
                {'error': '项目没有工作流'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='node-library')
    def get_node_library(self, request):
        """
        获取节点库
        GET /api/v1/workflows/node-library/
        """
        nodes = WorkflowNode.objects.filter(is_active=True)
        
        node_data = []
        for node in nodes:
            node_data.append({
                'id': str(node.id),
                'type': node.node_type,
                'name': node.name,
                'category': node.category,
                'description': node.description,
                'icon': node.icon,
                'color': node.color,
                'input_ports': node.input_ports,
                'output_ports': node.output_ports,
                'config_schema': node.config_schema
            })
        
        return Response({'nodes': node_data})
    
    @action(detail=False, methods=['get'], url_path='templates')
    def list_templates(self, request):
        """
        获取工作流模板列表
        GET /api/v1/workflows/templates/
        """
        from django.db.models import Q
        
        # 获取公开模板和用户自己的模板
        templates = WorkflowTemplate.objects.filter(
            Q(is_public=True) | Q(created_by=request.user)
        )
        
        template_data = []
        for template in templates:
            template_data.append({
                'id': str(template.id),
                'name': template.name,
                'description': template.description,
                'preview_image': template.preview_image,
                'usage_count': template.usage_count,
                'is_public': template.is_public,
                'created_by': template.created_by.username,
                'created_at': template.created_at.isoformat()
            })
        
        return Response({'templates': template_data})
    
    @action(detail=False, methods=['post'], url_path='create-template')
    def create_template(self, request):
        """
        创建工作流模板
        POST /api/v1/workflows/create-template/
        Body: {
            "name": "模板名称",
            "description": "描述",
            "workflow_data": {...},
            "is_public": false
        }
        """
        name = request.data.get('name')
        description = request.data.get('description', '')
        workflow_data = request.data.get('workflow_data')
        is_public = request.data.get('is_public', False)
        
        if not name or not workflow_data:
            return Response(
                {'error': '缺少必要参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template = WorkflowTemplate.objects.create(
            name=name,
            description=description,
            workflow_data=workflow_data,
            is_public=is_public,
            created_by=request.user
        )
        
        return Response({
            'message': '模板已创建',
            'template_id': str(template.id)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='apply-template')
    def apply_template(self, request, pk=None):
        """
        应用模板到项目
        POST /api/v1/projects/{id}/apply-template/
        Body: {"template_id": "xxx"}
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        template_id = request.data.get('template_id')
        
        if not template_id:
            return Response(
                {'error': '缺少 template_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            template = WorkflowTemplate.objects.get(id=template_id)
            
            # 创建或更新工作流
            workflow, created = ProjectWorkflow.objects.update_or_create(
                project=project,
                defaults={
                    'workflow_data': template.workflow_data,
                    'template': template
                }
            )
            
            # 增加模板使用次数
            template.usage_count += 1
            template.save()
            
            return Response({
                'message': '模板已应用',
                'workflow_id': str(workflow.id)
            })
            
        except WorkflowTemplate.DoesNotExist:
            return Response(
                {'error': '模板不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], url_path='execution-history')
    def get_execution_history(self, request, pk=None):
        """
        获取工作流执行历史
        GET /api/v1/projects/{id}/execution-history/
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        
        try:
            workflow = project.workflow
            executions = workflow.executions.all()[:20]  # 最近20次
            
            history = []
            for execution in executions:
                history.append({
                    'id': str(execution.id),
                    'status': execution.status,
                    'created_at': execution.created_at.isoformat(),
                    'started_at': execution.started_at.isoformat() if execution.started_at else None,
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                    'error_message': execution.error_message,
                    'logs': execution.logs[-10:] if execution.logs else []  # 最后10条日志
                })
            
            return Response({'executions': history})
            
        except ProjectWorkflow.DoesNotExist:
            return Response({'executions': []})
    
    @action(detail=True, methods=['post'], url_path='validate-workflow')
    def validate_workflow(self, request, pk=None):
        """
        验证工作流配置
        POST /api/v1/projects/{id}/validate-workflow/
        """
        project = get_object_or_404(Project, id=pk, user=request.user)
        
        try:
            workflow = project.workflow
            workflow_data = workflow.workflow_data
            
            # 验证工作流
            engine = WorkflowEngine()
            engine.load_workflow(workflow_data)
            
            # 检查是否有循环依赖
            try:
                execution_order = engine._topological_sort()
                
                return Response({
                    'valid': True,
                    'message': '工作流配置有效',
                    'execution_order': execution_order,
                    'node_count': len(workflow_data.get('nodes', [])),
                    'edge_count': len(workflow_data.get('edges', []))
                })
            except ValueError as e:
                return Response({
                    'valid': False,
                    'error': str(e)
                })
                
        except ProjectWorkflow.DoesNotExist:
            return Response(
                {'error': '项目没有工作流'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({
                'valid': False,
                'error': str(e)
            })
