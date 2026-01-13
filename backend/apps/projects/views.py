"""
项目管理视图集
职责: 处理HTTP请求和业务逻辑编排
遵循单一职责原则(SRP)
"""

import json
import logging

from celery.result import AsyncResult
from django.conf import settings
from django.db import transaction, DatabaseError
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .constants import ProjectStatus, StageStatus, StageType, ErrorCode, ErrorMessage
from .exceptions import (
    ProjectNotResumableException,
    ProjectNotPausableException,
    StageNotFoundException,
    TaskStartFailedException,
    DatabaseException,
)

logger = logging.getLogger(__name__)

from .models import Project, ProjectModelConfig, ProjectStage
from .serializers import (
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectModelConfigSerializer,
    ProjectStageSerializer,
    ProjectTemplateSerializer,
    ProjectUpdateSerializer,
    StageExecuteSerializer,
    StageRetrySerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目管理ViewSet

    提供项目的CRUD操作和工作流控制
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "prompt_template_set"]
    search_fields = ["name", "description", "original_topic"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """只返回当前用户的项目"""
        return (
            Project.objects.filter(user=self.request.user)
            .select_related("user", "prompt_template_set")
            .prefetch_related("stages")
        )

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == "list":
            return ProjectListSerializer
        elif self.action == "retrieve":
            return ProjectDetailSerializer
        elif self.action == "create":
            return ProjectCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ProjectUpdateSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        """创建项目时自动设置当前用户"""
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """删除项目前检查状态"""
        instance.delete()

    @action(detail=True, methods=["get"])
    def stages(self, request, pk=None):
        """
        获取项目的所有阶段
        GET /api/v1/projects/{id}/stages/

        智能数据传递逻辑:
        - 当分镜生成阶段有输出数据时,自动传递给文生图阶段的输入
        """
        project = self.get_object()
        stages = project.stages.all()
        serializer = ProjectStageSerializer(stages, many=True)

        # 获取序列化后的数据
        data = serializer.data

        # 构建阶段索引字典
        stage_index_map = {}
        for index, stage_data in enumerate(data):
            stage_type = stage_data["stage_type"]
            stage_index_map[stage_type] = index

        return Response(data)

    @action(detail=True, methods=["post"])
    def execute_stage(self, request, pk=None):
        """
        执行指定阶段
        POST /api/v1/projects/projects/{id}/execute_stage/
        Body: {
            "stage_name": "rewrite",
            "input_data": {...},
            "use_streaming": false  // 可选，true=SSE流式(旧方式), false=Celery异步(默认)
        }

        模式1 (默认): Celery异步任务
        返回:
        {
            "task_id": "celery-task-id",
            "channel": "ai_story:project:xxx:stage:rewrite",
            "message": "任务已启动"
        }
        前端需要:
        1. 通过WebSocket订阅返回的channel
        2. 或通过轮询 /api/v1/projects/{id}/task-status/?task_id=xxx 获取状态

        模式2: SSE流式输出 (use_streaming=true)
        返回: text/event-stream 流式响应
        前端使用EventSource接收
        ⚠️ 需要ASGI服务器支持
        """
        project = self.get_object()
        serializer = StageExecuteSerializer(
            data=request.data, context={"project_id": str(project.id)}
        )
        serializer.is_valid(raise_exception=True)

        stage_name = serializer.validated_data["stage_name"]
        input_data = serializer.validated_data.get("input_data", {})
        use_streaming = request.data.get("use_streaming", False)

        # 获取阶段
        stage = get_object_or_404(ProjectStage, project=project, stage_type=stage_name)

        # 更新项目状态为处理中
        if project.status != ProjectStatus.PROCESSING:
            project.status = ProjectStatus.PROCESSING
            project.save(update_fields=['status', 'updated_at'])

        # 模式1: SSE流式输出 (旧方式，作为fallback)
        if use_streaming:
            return self._execute_stage_streaming(project, stage_name, input_data)

        # 模式2: Celery异步任务 (默认，推荐)
        return self._execute_stage_async(project, stage_name, input_data)

    def _execute_stage_async(self, project, stage_name, input_data):
        """
        使用Celery异步执行阶段 (推荐方式)
        """
        from apps.projects.tasks import (
            execute_image2video_stage,
            execute_llm_stage,
            execute_text2image_stage,
        )

        # 获取阶段对象
        stage = get_object_or_404(ProjectStage, project=project, stage_type=stage_name)

        # 使用统一的任务启动方法
        try:
            task = self._start_stage_task(
                stage_name=stage_name,
                project_id=str(project.id),
                input_data=input_data,
                user_id=self.request.user.id
            )
        except TaskStartFailedException as e:
            return Response(
                {"error": str(e.detail.get('error', '任务启动失败')), "code": e.detail.get('code')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 保存task_id到阶段记录，用于后续追踪和取消
        stage.task_id = task.id
        stage.save(update_fields=['task_id'])

        # 构建Redis频道名称
        channel = f"ai_story:project:{project.id}:stage:{stage_name}"

        logger.info(f"阶段 {stage_name} 任务已启动，task_id: {task.id}")

        return Response(
            {
                "task_id": task.id,
                "channel": channel,
                "stage": stage_name,
                "message": f"阶段 {stage_name} 任务已启动",
                "project_id": str(project.id),
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def _execute_stage_streaming(self, project, stage_name, input_data):
        """
        使用SSE流式执行阶段 (旧方式，作为fallback)
        ⚠️ 需要ASGI服务器支持
        """
        import asyncio
        import queue
        import threading

        from apps.content.processors.image2video_stage import (
            Image2VideoStageProcessor,
        )
        from apps.content.processors.llm_stage import LLMStageProcessor
        from apps.content.processors.text2image_stage import (
            Text2ImageStageProcessor,
        )

        # 使用队列在异步和同步之间传递数据
        data_queue = queue.Queue()

        # 根据阶段类型选择处理器
        if stage_name in ["rewrite", "storyboard", "camera_movement"]:
            processor_class = LLMStageProcessor
            processor_kwargs = {"stage_type": stage_name}
            timeout = 300  # 5分钟
        elif stage_name == "image_generation":
            processor_class = Text2ImageStageProcessor
            processor_kwargs = {}
            timeout = 300
        elif stage_name == "video_generation":
            processor_class = Image2VideoStageProcessor
            processor_kwargs = {}
            timeout = 600  # 10分钟
        else:
            return Response(
                {"error": f"未知阶段类型: {stage_name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 异步任务:在后台线程中运行
        async def async_producer():
            """异步生成器 - 在独立线程的事件循环中运行"""
            processor = processor_class(**processor_kwargs)

            try:
                # 根据阶段类型调用不同的处理方法
                if stage_name in ["rewrite", "storyboard", "camera_movement"]:
                    async for chunk in processor.process_stream(
                        project_id=str(project.id), input_data=input_data
                    ):
                        event_data = json.dumps(chunk, ensure_ascii=False)
                        data_queue.put(f"data: {event_data}\n\n".encode("utf-8"))
                else:
                    # 文生图和图生视频
                    storyboard_ids = input_data.get("storyboard_ids", None)
                    async for chunk in processor.process_stream(
                        project_id=str(project.id), storyboard_ids=storyboard_ids
                    ):
                        event_data = json.dumps(chunk, ensure_ascii=False)
                        data_queue.put(f"data: {event_data}\n\n".encode("utf-8"))

            except Exception as e:
                error_data = json.dumps(
                    {"type": "error", "error": str(e)}, ensure_ascii=False
                )
                data_queue.put(f"data: {error_data}\n\n".encode("utf-8"))
            finally:
                # 标记结束
                data_queue.put(None)

        # 在新线程中运行异步任务
        def run_async_in_thread():
            """在独立线程中创建新的事件循环并运行异步任务"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(async_producer())
            finally:
                loop.close()

        # 启动后台线程
        thread = threading.Thread(target=run_async_in_thread)
        thread.daemon = True
        thread.start()

        # 同步生成器:从队列中读取数据
        def sync_event_stream():
            """同步生成器 - 从队列中读取异步生成的数据"""
            while True:
                try:
                    # 从队列中获取数据(阻塞等待)
                    chunk = data_queue.get(timeout=timeout)

                    # None表示结束
                    if chunk is None:
                        break

                    yield chunk

                except queue.Empty:
                    # 超时
                    error_data = json.dumps(
                        {"type": "error", "error": "请求超时"}, ensure_ascii=False
                    )
                    yield f"data: {error_data}\n\n".encode("utf-8")
                    break
                except Exception as e:
                    error_data = json.dumps(
                        {"type": "error", "error": f"流式传输错误: {str(e)}"},
                        ensure_ascii=False,
                    )
                    yield f"data: {error_data}\n\n".encode("utf-8")
                    break

        # 返回SSE响应
        response = StreamingHttpResponse(
            sync_event_stream(), content_type="text/event-stream; charset=utf-8"
        )
        response["Cache-Control"] = "no-cache, no-transform"
        response["X-Accel-Buffering"] = "no"  # 禁用Nginx缓冲

        return response

    @action(detail=True, methods=["get"])
    def task_status(self, request, pk=None):
        """
        获取Celery任务状态
        GET /api/v1/projects/{id}/task-status/?task_id=xxx

        返回:
        {
            "task_id": "xxx",
            "state": "PENDING|STARTED|SUCCESS|FAILURE|RETRY",
            "result": {...},
            "info": {...}
        }
        """
        project = self.get_object()
        task_id = request.query_params.get("task_id")

        if not task_id:
            return Response(
                {"error": "缺少task_id参数"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 获取Celery任务结果
        task_result = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "state": task_result.state,
            "project_id": str(project.id),
        }

        if task_result.state == "PENDING":
            response_data["info"] = "任务等待执行"
        elif task_result.state == "STARTED":
            response_data["info"] = "任务正在执行"
        elif task_result.state == "SUCCESS":
            response_data["result"] = task_result.result
            response_data["info"] = "任务执行成功"
        elif task_result.state == "FAILURE":
            response_data["error"] = str(task_result.info)
            response_data["info"] = "任务执行失败"
        elif task_result.state == "RETRY":
            response_data["info"] = "任务正在重试"
        else:
            response_data["info"] = task_result.info

        return Response(response_data)

    @action(detail=True, methods=["post"])
    def retry_stage(self, request, pk=None):
        """
        重试失败的阶段
        POST /api/v1/projects/{id}/retry-stage/
        Body: {"stage_name": "rewrite"}
        """
        project = self.get_object()
        
        try:
            serializer = StageRetrySerializer(
                data=request.data, context={"project_id": str(project.id)}
            )
            serializer.is_valid(raise_exception=True)

            stage_name = serializer.validated_data["stage_name"]
            stage = get_object_or_404(ProjectStage, project=project, stage_type=stage_name)

            with transaction.atomic():
                # 增加重试次数
                stage.retry_count += 1
                stage.status = StageStatus.PROCESSING
                stage.error_message = ""
                stage.started_at = timezone.now()
                stage.save(update_fields=['retry_count', 'status', 'error_message', 'started_at'])

                # 启动Celery任务重试
                input_data = stage.input_data or {}

                # 使用统一的任务启动方法
                task = self._start_stage_task(
                    stage_name=stage_name,
                    project_id=str(project.id),
                    input_data=input_data,
                    user_id=self.request.user.id
                )

                # 保存task_id到阶段记录
                stage.task_id = task.id
                stage.save(update_fields=['task_id'])

                logger.info(
                    f"阶段 {stage_name} 开始重试 (第{stage.retry_count}次)，任务ID: {task.id}"
                )

                return Response(
                    {
                        "code": 200,
                        "msg": f"阶段 {stage.get_stage_type_display()} 开始重试 (第{stage.retry_count}次)",
                        "data": {
                            "stage": ProjectStageSerializer(stage).data,
                            "task_id": task.id,
                            "channel": f"ai_story:project:{project.id}:stage:{stage_name}",
                        }
                    }
                )
        except TaskStartFailedException as e:
            logger.error(f"重试阶段失败 - 任务启动失败: {str(e)}", exc_info=True)
            return Response(
                {
                    "code": ErrorCode.TASK_START_FAILED,
                    "msg": "阶段重试失败，任务启动失败",
                    "data": {"error_detail": str(e)}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except DatabaseError as e:
            logger.error(f"重试阶段失败 - 数据库错误: {str(e)}", exc_info=True)
            raise DatabaseException(error=str(e))
        except Exception as e:
            logger.error(f"重试阶段失败 - 系统错误: {str(e)}", exc_info=True)
            return Response(
                {
                    "code": ErrorCode.SYSTEM_ERROR,
                    "msg": "阶段重试失败，请稍后重试",
                    "data": {"error_detail": str(e)}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        """
        暂停项目
        POST /api/v1/projects/{id}/pause/
        
        功能:
        1. 验证项目状态（只有processing状态可暂停）
        2. 取消所有正在运行的Celery任务
        3. 更新项目状态为paused
        4. 使用事务保证数据一致性
        
        返回:
        {
            "code": 200,
            "msg": "项目已暂停",
            "data": {
                "project": {...},
                "cancelled_tasks": [{"stage": "rewrite", "task_id": "xxx"}]
            }
        }
        """
        project = self.get_object()

        # 状态校验：只有processing状态可暂停
        if project.status not in ProjectStatus.PAUSABLE_STATUSES:
            raise ProjectNotPausableException()

        try:
            with transaction.atomic():
                # 更新项目状态
                project.status = ProjectStatus.PAUSED
                project.save(update_fields=['status', 'updated_at'])

                # 取消正在运行的Celery任务
                cancelled_tasks = []
                running_stages = project.stages.filter(
                    status=StageStatus.PROCESSING,
                    task_id__isnull=False
                ).exclude(task_id='')
                
                for stage in running_stages:
                    try:
                        AsyncResult(stage.task_id).revoke(terminate=True)
                        cancelled_tasks.append({
                            'stage': stage.stage_type,
                            'stage_display': stage.get_stage_type_display(),
                            'task_id': stage.task_id
                        })
                        logger.info(f"已取消阶段 {stage.stage_type} 的任务: {stage.task_id}")
                    except Exception as e:
                        logger.warning(f"取消任务 {stage.task_id} 失败: {str(e)}")

                logger.info(f"项目 {project.id} 已暂停，取消了 {len(cancelled_tasks)} 个任务")

                return Response(
                    {
                        "code": ErrorCode.PROJECT_INVALID_STATUS if not cancelled_tasks else 200,
                        "msg": "项目已暂停",
                        "data": {
                            "project": ProjectDetailSerializer(project).data,
                            "cancelled_tasks": cancelled_tasks,
                            "cancelled_count": len(cancelled_tasks),
                        }
                    }
                )
        except DatabaseError as e:
            logger.error(f"暂停项目失败 - 数据库错误: {str(e)}", exc_info=True)
            raise DatabaseException(error=str(e))
        except Exception as e:
            logger.error(f"暂停项目失败 - 系统错误: {str(e)}", exc_info=True)
            return Response(
                {
                    "code": ErrorCode.SYSTEM_ERROR,
                    "msg": "项目暂停失败，请稍后重试",
                    "data": {"error_detail": str(e)}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        """
        恢复暂停的项目
        POST /api/v1/projects/{id}/resume/
        
        功能:
        1. 严格验证项目状态（只有paused状态可恢复）
        2. 查找当前需要执行的阶段（第一个pending或failed的阶段）
        3. 启动对应的Celery任务继续执行Pipeline
        4. 使用事务保证数据一致性
        5. 支持幂等性（重复调用不会重复启动任务）
        
        返回:
        {
            "code": 200,
            "msg": "项目已恢复，从阶段 文案改写 继续执行",
            "data": {
                "project": {...},
                "task_id": "celery-task-id",
                "channel": "ai_story:project:xxx:stage:rewrite",
                "current_stage": "rewrite",
                "current_stage_display": "文案改写"
            }
        }
        
        错误码:
        - 1003: 项目状态不是paused，无法恢复
        - 2005: 没有可恢复的阶段（所有阶段已完成）
        - 3001: 任务启动失败
        - 5001: 数据库错误
        """
        project = self.get_object()

        # 状态校验：只有paused状态可恢复
        if project.status not in ProjectStatus.RESUMABLE_STATUSES:
            raise ProjectNotResumableException()

        try:
            with transaction.atomic():
                # 查找当前需要执行的阶段（第一个未完成的阶段）
                current_stage = project.stages.filter(
                    status__in=StageStatus.RESUMABLE_STATUSES
                ).order_by("created_at").first()

                if not current_stage:
                    # 所有阶段都已完成
                    project.status = ProjectStatus.COMPLETED
                    project.completed_at = timezone.now()
                    project.save(update_fields=['status', 'completed_at', 'updated_at'])
                    
                    logger.info(f"项目 {project.id} 所有阶段已完成")
                    
                    return Response(
                        {
                            "code": 200,
                            "msg": ErrorMessage.PROJECT_ALREADY_COMPLETED,
                            "data": {
                                "project": ProjectDetailSerializer(project).data,
                                "all_stages_completed": True,
                            }
                        }
                    )

                # 幂等性检查：如果阶段已经在处理中，直接返回当前状态
                if current_stage.status == StageStatus.PROCESSING and current_stage.task_id:
                    logger.warning(
                        f"项目 {project.id} 阶段 {current_stage.stage_type} 已在处理中，任务ID: {current_stage.task_id}"
                    )
                    return Response(
                        {
                            "code": 200,
                            "msg": f"项目已在处理中，当前阶段: {current_stage.get_stage_type_display()}",
                            "data": {
                                "project": ProjectDetailSerializer(project).data,
                                "task_id": current_stage.task_id,
                                "channel": f"ai_story:project:{project.id}:stage:{current_stage.stage_type}",
                                "current_stage": current_stage.stage_type,
                                "current_stage_display": current_stage.get_stage_type_display(),
                                "already_running": True,
                            }
                        }
                    )

                # 更新项目状态为processing
                project.status = ProjectStatus.PROCESSING
                project.save(update_fields=['status', 'updated_at'])

                # 重新启动Pipeline - 从当前阶段继续
                stage_name = current_stage.stage_type
                input_data = current_stage.input_data or {}

                # 启动对应的Celery任务
                task = self._start_stage_task(
                    stage_name=stage_name,
                    project_id=str(project.id),
                    input_data=input_data,
                    user_id=self.request.user.id
                )

                # 更新阶段状态并保存task_id
                current_stage.status = StageStatus.PROCESSING
                current_stage.started_at = timezone.now()
                current_stage.task_id = task.id
                current_stage.error_message = ""  # 清空之前的错误信息
                current_stage.save(update_fields=['status', 'started_at', 'task_id', 'error_message'])

                channel = f"ai_story:project:{project.id}:stage:{stage_name}"

                logger.info(
                    f"项目 {project.id} 已恢复，从阶段 {stage_name} 继续执行，任务ID: {task.id}"
                )

                return Response(
                    {
                        "code": 200,
                        "msg": f"项目已恢复，从阶段 {current_stage.get_stage_type_display()} 继续执行",
                        "data": {
                            "project": ProjectDetailSerializer(project).data,
                            "task_id": task.id,
                            "channel": channel,
                            "current_stage": stage_name,
                            "current_stage_display": current_stage.get_stage_type_display(),
                            "resumed_at": timezone.now().isoformat(),
                        }
                    }
                )

        except DatabaseError as e:
            logger.error(f"恢复项目失败 - 数据库错误: {str(e)}", exc_info=True)
            raise DatabaseException(error=str(e))
        except TaskStartFailedException:
            raise
        except Exception as e:
            logger.error(f"恢复项目失败 - 系统错误: {str(e)}", exc_info=True)
            return Response(
                {
                    "code": ErrorCode.SYSTEM_ERROR,
                    "msg": "项目恢复失败，请稍后重试",
                    "data": {"error_detail": str(e)}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _start_stage_task(self, stage_name: str, project_id: str, input_data: dict, user_id: int):
        """
        启动阶段任务的辅助方法
        
        Args:
            stage_name: 阶段名称
            project_id: 项目ID
            input_data: 输入数据
            user_id: 用户ID
            
        Returns:
            Celery AsyncResult对象
            
        Raises:
            TaskStartFailedException: 任务启动失败
        """
        try:
            from apps.projects.tasks import (
                execute_image2video_stage,
                execute_llm_stage,
                execute_text2image_stage,
            )

            # 根据阶段类型启动对应的Celery任务
            if stage_name in StageType.LLM_STAGES:
                task = execute_llm_stage.delay(
                    project_id=project_id,
                    stage_name=stage_name,
                    input_data=input_data,
                    user_id=user_id,
                )
            elif stage_name == StageType.IMAGE_GENERATION:
                storyboard_ids = input_data.get("storyboard_ids", None)
                task = execute_text2image_stage.delay(
                    project_id=project_id,
                    storyboard_ids=storyboard_ids,
                    user_id=user_id,
                )
            elif stage_name == StageType.VIDEO_GENERATION:
                storyboard_ids = input_data.get("storyboard_ids", None)
                task = execute_image2video_stage.delay(
                    project_id=project_id,
                    storyboard_ids=storyboard_ids,
                    user_id=user_id,
                )
            else:
                raise TaskStartFailedException(
                    error=ErrorMessage.STAGE_UNKNOWN_TYPE.format(stage_name=stage_name)
                )

            return task

        except Exception as e:
            logger.error(f"启动阶段 {stage_name} 任务失败: {str(e)}", exc_info=True)
            raise TaskStartFailedException(error=str(e))

    @action(detail=True, methods=["post"])
    def rollback_stage(self, request, pk=None):
        """
        回滚到指定阶段
        POST /api/v1/projects/{id}/rollback-stage/
        Body: {"stage_name": "rewrite"}
        """
        project = self.get_object()
        stage_name = request.data.get("stage_name")

        if not stage_name:
            return Response(
                {"error": "缺少阶段名称"}, status=status.HTTP_400_BAD_REQUEST
            )

        stage = get_object_or_404(ProjectStage, project=project, stage_type=stage_name)

        # 重置该阶段及后续阶段
        stage_order = [
            "rewrite",
            "storyboard",
            "image_generation",
            "camera_movement",
            "video_generation",
        ]
        current_index = stage_order.index(stage_name)

        # 重置当前及后续阶段
        for stage_type in stage_order[current_index:]:
            ProjectStage.objects.filter(project=project, stage_type=stage_type).update(
                status=StageStatus.PENDING,
                output_data={},
                error_message="",
                retry_count=0,
                started_at=None,
                completed_at=None,
            )

        # 更新项目状态
        project.status = ProjectStatus.DRAFT
        project.save(update_fields=['status', 'updated_at'])

        return Response(
            {
                "message": f"已回滚到阶段 {stage.get_stage_type_display()}",
                "project": ProjectDetailSerializer(project).data,
            }
        )

    @action(detail=True, methods=["get"])
    def model_config(self, request, pk=None):
        """
        获取项目模型配置
        GET /api/v1/projects/{id}/model-config/
        """
        project = self.get_object()
        config, created = ProjectModelConfig.objects.get_or_create(project=project)
        serializer = ProjectModelConfigSerializer(config)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def update_model_config(self, request, pk=None):
        """
        更新项目模型配置
        PATCH /api/v1/projects/{id}/update-model-config/
        """
        project = self.get_object()
        config, created = ProjectModelConfig.objects.get_or_create(project=project)
        serializer = ProjectModelConfigSerializer(
            config, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def save_as_template(self, request, pk=None):
        """
        将项目保存为模板
        POST /api/v1/projects/{id}/save-as-template/
        Body: {
            "template_name": "我的模板",
            "description": "模板描述",
            "include_model_config": true,
            "is_public": false
        }
        """
        from apps.projects.services.template_service import ProjectTemplateService
        
        project = self.get_object()
        serializer = ProjectTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template_name = serializer.validated_data["template_name"]
        description = serializer.validated_data.get("description", "")
        include_model_config = serializer.validated_data.get("include_model_config", True)
        is_public = serializer.validated_data.get("is_public", False)

        # 使用服务保存模板
        template = ProjectTemplateService.save_as_template(
            project=project,
            template_name=template_name,
            description=description,
            include_model_config=include_model_config,
            is_public=is_public
        )

        return Response(
            {
                "message": f"项目已保存为模板: {template_name}",
                "template_id": str(template.id),
                "template_name": template_name,
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def export(self, request, pk=None):
        """
        导出项目(合成视频、生成字幕)
        POST /api/v1/projects/{id}/export/
        Body: {"include_subtitles": true, "video_format": "mp4"}
        
        Returns:
        {
            "task_id": "celery-task-id",
            "channel": "ai_story:project:xxx:export",
            "message": "导出任务已启动"
        }
        """
        from apps.projects.tasks import export_project_video
        
        project = self.get_object()

        if project.status != ProjectStatus.COMPLETED:
            return Response(
                {
                    "error": ErrorMessage.PROJECT_ONLY_COMPLETED_CAN_EXPORT,
                    "code": ErrorCode.PROJECT_NOT_EXPORTABLE
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        include_subtitles = request.data.get("include_subtitles", True)
        video_format = request.data.get("video_format", "mp4")

        # 启动Celery导出任务
        task = export_project_video.delay(
            project_id=str(project.id),
            user_id=self.request.user.id,
            include_subtitles=include_subtitles,
            video_format=video_format
        )

        # 构建Redis频道名称
        channel = f"ai_story:project:{project.id}:export"

        return Response(
            {
                "task_id": task.id,
                "channel": channel,
                "message": "导出任务已启动",
                "project_id": str(project.id),
            },
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        获取项目统计信息
        GET /api/v1/projects/statistics/
        """
        user = request.user
        projects = Project.objects.filter(user=user)

        stats = {
            "total_projects": projects.count(),
            "draft_projects": projects.filter(status="draft").count(),
            "processing_projects": projects.filter(status="processing").count(),
            "completed_projects": projects.filter(status="completed").count(),
            "failed_projects": projects.filter(status="failed").count(),
            "paused_projects": projects.filter(status="paused").count(),
        }

        return Response(stats)

    @action(detail=True, methods=["patch"])
    def update_stage_data(self, request, pk=None):
        """
        更新指定阶段的输入/输出数据
        PATCH /api/v1/projects/{id}/update-stage-data/
        Body: {
            "stage_name": "rewrite",
            "input_data": {...},
            "output_data": {...}
        }
        """
        project = self.get_object()
        stage_name = request.data.get("stage_name")

        if not stage_name:
            return Response(
                {"error": "缺少阶段名称"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 获取阶段
        try:
            stage = ProjectStage.objects.get(project=project, stage_type=stage_name)
        except ProjectStage.DoesNotExist:
            return Response(
                {"error": f"阶段 {stage_name} 不存在"}, status=status.HTTP_404_NOT_FOUND
            )

        # 更新输入数据(如果提供)
        if "input_data" in request.data:
            stage.input_data = request.data["input_data"]

        # 更新输出数据(如果提供)
        if "output_data" in request.data:
            stage.output_data = request.data["output_data"]

        stage.save()

        return Response(
            {
                "message": f"阶段 {stage.get_stage_type_display()} 数据已更新",
                "stage": ProjectStageSerializer(stage).data,
            }
        )

    @action(detail=True, methods=["post"])
    def generate_jianying_draft(self, request, pk=None):
        """
        生成剪映草稿
        POST /api/v1/projects/{id}/generate_jianying_draft/
        Body: {
            "background_music": "/path/to/music.mp3",  // 可选
            "draft_folder_path": "/path/to/drafts",    // 可选
            "music_volume": 0.6,                       // 可选，默认0.6
            "add_intro_animation": true,               // 可选，默认true
            "subtitle_size": 15,                       // 可选，默认15
            "width": 1080,                             // 可选，默认1080
            "height": 1920                             // 可选，默认1920（竖屏）
        }

        返回:
        {
            "task_id": "celery-task-id",
            "channel": "ai_story:project:xxx:jianying_draft",
            "message": "剪映草稿生成任务已启动"
        }
        """
        from apps.projects.tasks import generate_jianying_draft

        project = self.get_object()

        # 检查视频生成阶段是否完成
        video_stage = ProjectStage.objects.filter(
            project=project, stage_type="video_generation", status="completed"
        ).first()

        if not video_stage:
            return Response(
                {"error": "视频生成阶段未完成，无法生成剪映草稿"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取可选参数
        background_music = request.data.get("background_music")
        options = {
            "draft_folder_path": request.data.get("draft_folder_path"),
            "music_volume": request.data.get("music_volume", 0.6),
            "add_intro_animation": request.data.get("add_intro_animation", True),
            "subtitle_size": request.data.get("subtitle_size", 15),
            "width": request.data.get("width", 1080),
            "height": request.data.get("height", 1920),
        }

        # 过滤掉None值
        options = {k: v for k, v in options.items() if v is not None}

        # 启动Celery任务
        task = generate_jianying_draft.delay(
            project_id=str(project.id),
            user_id=self.request.user.id,
            background_music=background_music,
            **options
        )

        # 构建Redis频道名称
        channel = f"ai_story:project:{project.id}:jianying_draft"

        return Response(
            {
                "task_id": task.id,
                "channel": channel,
                "draft_path": task.result.get("draft_path", "todo"),
            },
            status=status.HTTP_200_OK,
        )


class ProjectStageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    项目阶段ViewSet

    只读API,用于查询阶段信息
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectStageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["stage_type", "status", "project"]
    ordering = ["created_at"]

    def get_queryset(self):
        """只返回当前用户项目的阶段"""
        return ProjectStage.objects.filter(
            project__user=self.request.user
        ).select_related("project")


class ProjectModelConfigViewSet(viewsets.ModelViewSet):
    """
    项目模型配置ViewSet
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectModelConfigSerializer

    def get_queryset(self):
        """只返回当前用户项目的配置"""
        return (
            ProjectModelConfig.objects.filter(project__user=self.request.user)
            .select_related("project")
            .prefetch_related(
                "rewrite_providers",
                "storyboard_providers",
                "image_providers",
                "camera_providers",
                "video_providers",
            )
        )
