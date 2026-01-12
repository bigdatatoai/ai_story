"""
工作流序列化器
"""

from rest_framework import serializers
from apps.projects.models_workflow import (
    WorkflowTemplate, ProjectWorkflow, WorkflowNode, WorkflowExecution
)


class WorkflowNodeSerializer(serializers.ModelSerializer):
    """工作流节点序列化器"""
    
    class Meta:
        model = WorkflowNode
        fields = [
            'id', 'node_type', 'name', 'category',
            'config_schema', 'input_ports', 'output_ports',
            'icon', 'color', 'description', 'help_text',
            'is_active'
        ]
        read_only_fields = ['id']


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """工作流模板序列化器"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'workflow_data',
            'preview_image', 'is_public', 'usage_count',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'usage_count', 'created_at', 'updated_at']


class ProjectWorkflowSerializer(serializers.ModelSerializer):
    """项目工作流序列化器"""
    
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ProjectWorkflow
        fields = [
            'id', 'project', 'workflow_data', 'template', 'template_name',
            'status', 'current_node_id', 'execution_results',
            'created_at', 'updated_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """工作流执行记录序列化器"""
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'status', 'logs', 'error_message',
            'results', 'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at']
