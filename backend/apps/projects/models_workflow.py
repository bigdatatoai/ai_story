"""
可视化工作流模型（导演模式）
支持节点式编辑和自定义工作流
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkflowTemplate(models.Model):
    """工作流模板"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="模板名称")
    description = models.TextField(blank=True, verbose_name="描述")
    
    # 工作流数据（节点和连接）
    workflow_data = models.JSONField(verbose_name="工作流数据")
    # 格式: {
    #   "nodes": [
    #     {
    #       "id": "node-1",
    #       "type": "image_input",
    #       "position": {"x": 100, "y": 100},
    #       "data": {"label": "图片输入", "config": {...}}
    #     }
    #   ],
    #   "edges": [
    #     {
    #       "id": "edge-1",
    #       "source": "node-1",
    #       "target": "node-2",
    #       "sourceHandle": "output",
    #       "targetHandle": "input"
    #     }
    #   ]
    # }
    
    # 预览图
    preview_image = models.CharField(max_length=512, blank=True, verbose_name="预览图")
    
    # 创建者
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workflow_templates',
        verbose_name="创建者"
    )
    
    # 是否公开
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'workflow_templates'
        verbose_name = '工作流模板'
        verbose_name_plural = '工作流模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ProjectWorkflow(models.Model):
    """项目工作流实例"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='workflow',
        verbose_name="项目"
    )
    
    # 工作流数据
    workflow_data = models.JSONField(verbose_name="工作流数据")
    
    # 基于的模板
    template = models.ForeignKey(
        WorkflowTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="基于模板"
    )
    
    # 执行状态
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('running', '运行中'),
        ('paused', '已暂停'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="状态"
    )
    
    # 当前执行的节点
    current_node_id = models.CharField(max_length=100, blank=True, verbose_name="当前节点ID")
    
    # 执行结果
    execution_results = models.JSONField(default=dict, blank=True, verbose_name="执行结果")
    # 格式: {
    #   "node-1": {"status": "completed", "output": {...}},
    #   "node-2": {"status": "running", "progress": 0.5}
    # }
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    
    class Meta:
        db_table = 'project_workflows'
        verbose_name = '项目工作流'
        verbose_name_plural = '项目工作流'
    
    def __str__(self):
        return f"Workflow for {self.project.name}"


class WorkflowNode(models.Model):
    """工作流节点定义（节点类型库）"""
    
    NODE_CATEGORY_CHOICES = [
        ('input', '输入'),
        ('processing', '处理'),
        ('ai', 'AI生成'),
        ('output', '输出'),
        ('control', '控制'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_type = models.CharField(max_length=50, unique=True, verbose_name="节点类型")
    name = models.CharField(max_length=255, verbose_name="节点名称")
    category = models.CharField(
        max_length=20,
        choices=NODE_CATEGORY_CHOICES,
        verbose_name="分类"
    )
    
    # 节点配置
    config_schema = models.JSONField(verbose_name="配置模式")
    # 格式: {
    #   "fields": [
    #     {
    #       "name": "image_url",
    #       "type": "string",
    #       "label": "图片URL",
    #       "required": true
    #     }
    #   ]
    # }
    
    # 输入输出端口
    input_ports = models.JSONField(default=list, verbose_name="输入端口")
    # 格式: [{"name": "image", "type": "image", "label": "图片输入"}]
    
    output_ports = models.JSONField(default=list, verbose_name="输出端口")
    # 格式: [{"name": "result", "type": "image", "label": "处理结果"}]
    
    # 处理器类路径
    processor_class = models.CharField(max_length=255, verbose_name="处理器类")
    
    # 图标和样式
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标")
    color = models.CharField(max_length=20, default='#3b82f6', verbose_name="颜色")
    
    # 描述和帮助
    description = models.TextField(blank=True, verbose_name="描述")
    help_text = models.TextField(blank=True, verbose_name="帮助文本")
    
    # 是否启用
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'workflow_nodes'
        verbose_name = '工作流节点'
        verbose_name_plural = '工作流节点'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.node_type})"


class WorkflowExecution(models.Model):
    """工作流执行记录"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        ProjectWorkflow,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name="工作流"
    )
    
    # 执行状态
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="状态"
    )
    
    # 执行日志
    logs = models.JSONField(default=list, blank=True, verbose_name="执行日志")
    # 格式: [
    #   {
    #     "timestamp": "2024-01-01T00:00:00",
    #     "node_id": "node-1",
    #     "level": "info",
    #     "message": "开始处理"
    #   }
    # ]
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    
    # 执行结果
    results = models.JSONField(default=dict, blank=True, verbose_name="执行结果")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    
    class Meta:
        db_table = 'workflow_executions'
        verbose_name = '工作流执行记录'
        verbose_name_plural = '工作流执行记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Execution {self.id} - {self.status}"
