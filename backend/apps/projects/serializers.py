"""
项目管理序列化器
职责: 数据序列化与验证
遵循单一职责原则(SRP)
"""

from rest_framework import serializers

from apps.projects.utils import parse_storyboard_json
from .models import Project, ProjectStage, ProjectModelConfig
from .constants import ProjectStatus, StageStatus, StageType, ErrorMessage


class ProjectStageSerializer(serializers.ModelSerializer):
    """项目阶段序列化器"""

    stage_type_display = serializers.CharField(source='get_stage_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ProjectStage
        fields = [
            'id', 'project', 'stage_type', 'stage_type_display',
            'status', 'status_display', 'input_data', 'output_data',
            'retry_count', 'max_retries', 'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        stage_type = data.get("stage_type")
        if stage_type == "storyboard":
            try:    
                data["output_data"]["human_text"] = parse_storyboard_json(data["output_data"].get("storyboard_text", ""))
            except Exception:
                pass
        elif stage_type == "image_generation":
            try:
                data["input_data"]["human_text"] = parse_storyboard_json(data["input_data"].get("storyboard_text", ""))
            except Exception:
                pass
        return data


class ProjectModelConfigSerializer(serializers.ModelSerializer):
    """项目模型配置序列化器"""

    load_balance_strategy_display = serializers.CharField(
        source='get_load_balance_strategy_display',
        read_only=True
    )

    # 显示模型提供商名称列表
    rewrite_providers_names = serializers.SerializerMethodField()
    storyboard_providers_names = serializers.SerializerMethodField()
    image_providers_names = serializers.SerializerMethodField()
    camera_providers_names = serializers.SerializerMethodField()
    video_providers_names = serializers.SerializerMethodField()

    class Meta:
        model = ProjectModelConfig
        fields = [
            'id', 'project', 'load_balance_strategy', 'load_balance_strategy_display',
            'rewrite_providers', 'rewrite_providers_names',
            'storyboard_providers', 'storyboard_providers_names',
            'image_providers', 'image_providers_names',
            'camera_providers', 'camera_providers_names',
            'video_providers', 'video_providers_names',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_rewrite_providers_names(self, obj):
        try:
            if obj is None:
                return []
            return [p.name for p in obj.rewrite_providers.all()]
        except Exception:
            return []

    def get_storyboard_providers_names(self, obj):
        try:
            if obj is None:
                return []
            return [p.name for p in obj.storyboard_providers.all()]
        except Exception:
            return []

    def get_image_providers_names(self, obj):
        try:
            if obj is None:
                return []
            return [p.name for p in obj.image_providers.all()]
        except Exception:
            return []

    def get_camera_providers_names(self, obj):
        try:
            if obj is None:
                return []
            return [p.name for p in obj.camera_providers.all()]
        except Exception:
            return []

    def get_video_providers_names(self, obj):
        try:
            if obj is None:
                return []
            return [p.name for p in obj.video_providers.all()]
        except Exception:
            return []


class ProjectListSerializer(serializers.ModelSerializer):
    """项目列表序列化器 - 轻量级"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    prompt_set_name = serializers.CharField(source='prompt_template_set.name', read_only=True)

    # 统计信息
    stages_count = serializers.SerializerMethodField()
    completed_stages_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'original_topic',
            'status', 'status_display', 'user', 'user_name',
            'prompt_template_set', 'prompt_set_name',
            'stages_count', 'completed_stages_count',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at']

    def get_stages_count(self, obj):
        try:
            if obj is None:
                return 0
            return obj.stages.count()
        except Exception:
            return 0

    def get_completed_stages_count(self, obj):
        try:
            if obj is None:
                return 0
            return obj.stages.filter(status=StageStatus.COMPLETED).count()
        except Exception:
            return 0


class ProjectDetailSerializer(serializers.ModelSerializer):
    """项目详情序列化器 - 包含完整信息"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    prompt_set_name = serializers.CharField(source='prompt_template_set.name', read_only=True)

    # 嵌套序列化
    stages = ProjectStageSerializer(many=True, read_only=True)
    model_config = ProjectModelConfigSerializer(read_only=True)

    # 统计信息
    total_stages = serializers.SerializerMethodField()
    completed_stages = serializers.SerializerMethodField()
    failed_stages = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'original_topic',
            'status', 'status_display', 'user', 'user_name',
            'prompt_template_set', 'prompt_set_name',
            'stages', 'model_config',
            'total_stages', 'completed_stages', 'failed_stages', 'progress_percentage',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at']

    def get_total_stages(self, obj):
        try:
            if obj is None:
                return 0
            return obj.stages.count()
        except Exception:
            return 0

    def get_completed_stages(self, obj):
        try:
            if obj is None:
                return 0
            return obj.stages.filter(status=StageStatus.COMPLETED).count()
        except Exception:
            return 0

    def get_failed_stages(self, obj):
        try:
            if obj is None:
                return 0
            return obj.stages.filter(status=StageStatus.FAILED).count()
        except Exception:
            return 0

    def get_progress_percentage(self, obj):
        try:
            if obj is None:
                return 0
            total = obj.stages.count()
            if total == 0:
                return 0
            completed = obj.stages.filter(status=StageStatus.COMPLETED).count()
            return round((completed / total) * 100, 2)
        except Exception:
            return 0


class ProjectCreateSerializer(serializers.ModelSerializer):
    """项目创建序列化器"""

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'original_topic',
            'prompt_template_set'
        ]
        read_only_fields = ['id']

    def validate_original_topic(self, value):
        """验证原始主题不能为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("原始主题不能为空")
        return value.strip()

    def create(self, validated_data):
        """创建项目并初始化阶段"""
        # 从请求中获取用户
        user = self.context['request'].user
        validated_data['user'] = user

        # 创建项目
        project = Project.objects.create(**validated_data)

        # 初始化所有阶段
        for stage_type in [StageType.REWRITE, StageType.STORYBOARD]:
            ProjectStage.objects.create(
                project=project,
                stage_type=stage_type,
                status=StageStatus.PENDING,
                input_data={
                    "raw_text": project.original_topic,
                    "human_text": ""
                },
                output_data={
                    "raw_text": "",
                    "human_text": ""
                }
            )
        
        stage_types = [
            StageType.IMAGE_GENERATION,
            StageType.CAMERA_MOVEMENT,
            StageType.VIDEO_GENERATION
        ]
        for stage_type in stage_types:
            ProjectStage.objects.create(
                project=project,
                stage_type=stage_type,
                status=StageStatus.PENDING,
                input_data={
                    "raw_text": "",
                    "human_text": ""
                },
                output_data={
                    "raw_text": "",
                    "human_text": ""
                }
            )
        
        # 创建默认模型配置
        ProjectModelConfig.objects.create(project=project)

        return project


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """项目更新序列化器"""

    class Meta:
        model = Project
        fields = ['name', 'description', 'original_topic', 'prompt_template_set', 'status']

    def validate_status(self, value):
        """验证状态转换的合法性"""
        instance = self.instance
        if instance:
            # 已完成的项目不能修改为其他状态
            if instance.status == ProjectStatus.COMPLETED and value != ProjectStatus.COMPLETED:
                raise serializers.ValidationError("已完成的项目不能修改状态")

            # 只有暂停和草稿状态可以恢复处理
            if value == ProjectStatus.PROCESSING and instance.status not in [ProjectStatus.PAUSED, ProjectStatus.DRAFT]:
                raise serializers.ValidationError(f"项目状态为 {instance.get_status_display()} 时不能开始处理")

        return value


class StageRetrySerializer(serializers.Serializer):
    """阶段重试序列化器"""

    stage_name = serializers.ChoiceField(
        choices=[
            (StageType.REWRITE, '文案改写'),
            (StageType.STORYBOARD, '分镜生成'),
            (StageType.IMAGE_GENERATION, '文生图'),
            (StageType.CAMERA_MOVEMENT, '运镜生成'),
            (StageType.VIDEO_GENERATION, '图生视频'),
        ]
    )

    def validate_stage_name(self, value):
        """验证阶段是否存在且可重试"""
        project_id = self.context.get('project_id')
        if not project_id:
            raise serializers.ValidationError("缺少项目ID")

        try:
            stage = ProjectStage.objects.get(project_id=project_id, stage_type=value)
        except ProjectStage.DoesNotExist:
            raise serializers.ValidationError(
                ErrorMessage.STAGE_NOT_FOUND.format(stage_name=value)
            )

        # 检查重试次数
        if stage.retry_count >= stage.max_retries:
            raise serializers.ValidationError(
                ErrorMessage.STAGE_MAX_RETRIES.format(
                    stage_name=stage.get_stage_type_display(),
                    max_retries=stage.max_retries
                )
            )

        return value


class StageExecuteSerializer(serializers.Serializer):
    """阶段执行序列化器"""

    stage_name = serializers.ChoiceField(
        choices=[
            (StageType.REWRITE, '文案改写'),
            (StageType.STORYBOARD, '分镜生成'),
            (StageType.IMAGE_GENERATION, '文生图'),
            (StageType.CAMERA_MOVEMENT, '运镜生成'),
            (StageType.VIDEO_GENERATION, '图生视频'),
        ]
    )
    input_data = serializers.JSONField(required=False, default=dict)

    def validate(self, attrs):
        """验证阶段执行的前置条件"""
        project_id = self.context.get('project_id')
        stage_name = attrs['stage_name']

        if not project_id:
            raise serializers.ValidationError("缺少项目ID")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(ErrorMessage.PROJECT_NOT_FOUND)

        # 检查项目状态
        if project.status not in ProjectStatus.EXECUTABLE_STATUSES:
            raise serializers.ValidationError(
                f"项目状态为 {project.get_status_display()} 时不能执行阶段"
            )

        # 检查阶段是否存在
        try:
            stage = ProjectStage.objects.get(project_id=project_id, stage_type=stage_name)
        except ProjectStage.DoesNotExist:
            raise serializers.ValidationError(
                ErrorMessage.STAGE_NOT_FOUND.format(stage_name=stage_name)
            )

        return attrs


class ProjectTemplateSerializer(serializers.Serializer):
    """项目模板序列化器"""

    template_name = serializers.CharField(max_length=255)
    include_model_config = serializers.BooleanField(default=True)

    def validate_template_name(self, value):
        """验证模板名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("模板名称不能为空")
        return value.strip()
