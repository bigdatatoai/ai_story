"""
项目相关的Celery异步任务
职责: 执行耗时的AI生成任务，通过Redis Pub/Sub推送实时进度
遵循单一职责原则(SRP)
"""

from email import message
import logging
from typing import Dict, Any
from django.utils import timezone

from core.redis import RedisStreamPublisher
from core.services.jianying_draft_service import JianyingDraftGenerator
from apps.content.processors.llm_stage import LLMStageProcessor
from apps.content.processors.text2image_stage import Text2ImageStageProcessor
from apps.content.processors.image2video_stage import Image2VideoStageProcessor
from apps.projects.models import Project, ProjectStage
from config.celery import app

logger = logging.getLogger(__name__)


@app.task(
    bind=True,
    max_retries=0,
    default_retry_delay=60,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=600,  # 10分钟软超时
    time_limit=900  # 15分钟硬超时
)
def execute_llm_stage(
    self,
    project_id: str,
    stage_name: str,
    input_data: Dict[str, Any],
    user_id: int
) -> Dict[str, Any]:
    """
    执行LLM阶段任务 (文案改写/分镜生成/运镜生成)

    Args:
        self: Celery任务实例
        project_id: 项目ID
        stage_name: 阶段名称 (rewrite/storyboard/camera_movement)
        input_data: 输入数据
        user_id: 用户ID

    Returns:
        Dict包含: success, task_id, channel, result
    """

    task_id = self.request.id
    channel = f"ai_story:project:{project_id}:stage:{stage_name}"

    logger.info(f"开始执行LLM阶段任务: {stage_name}, 项目: {project_id}, 任务ID: {task_id}")

    # 初始化Redis发布器
    publisher = RedisStreamPublisher(project_id, stage_name)

    try:
        # 获取项目和阶段
        project = Project.objects.get(id=project_id, user_id=user_id)
        stage = ProjectStage.objects.get(project=project, stage_type=stage_name)

        # 更新阶段状态
        stage.status = 'processing'
        stage.started_at = timezone.now()
        stage.save()

        # 发布开始消息
        publisher.publish_stage_update(
            status='processing',
            progress=0,
            message=f'开始执行{stage.get_stage_type_display()}'
        )

        # 创建处理器
        processor = LLMStageProcessor(stage_type=stage_name)

        # 执行流式处理
        full_text = ""

        for chunk in processor.process_stream(
            project_id=project_id,
            input_data=input_data
        ):
            chunk_type = chunk.get('type')

            if chunk_type == 'token':
                # 发布token消息
                content = chunk.get('content', '')
                full_text = chunk.get('full_text', full_text)
                publisher.publish_token(content, full_text)

            elif chunk_type == 'stage_update':
                # 发布阶段更新
                publisher.publish_stage_update(
                    status=chunk.get('status', 'processing'),
                    progress=chunk.get('progress'),
                    message=chunk.get('message')
                )

            elif chunk_type == 'done':
                # 处理完成
                full_text = chunk.get('full_text', full_text)
                metadata = chunk.get('metadata', {})

                # 更新阶段状态
                ProjectStage.objects.filter(id=stage.id).update(
                    completed_at=timezone.now(),
                    status='completed'
                )
                # 发布完成消息
                publisher.publish_done(full_text, metadata)

            elif chunk_type == 'error':
                # 处理错误
                error_msg = chunk.get('error', '未知错误')
                raise Exception(error_msg)

        logger.info(f"LLM阶段任务完成: {stage_name}, 项目: {project_id}")

        return {
            'success': True,
            'task_id': task_id,
            'channel': channel,
            'result': full_text
        }

    except Project.DoesNotExist:
        error_msg = f'项目不存在: {project_id}'
        logger.error(error_msg)
        publisher.publish_error(error_msg)
        return {'success': False, 'error': error_msg}

    except ProjectStage.DoesNotExist:
        error_msg = f'阶段不存在: {stage_name}'
        logger.error(error_msg)
        publisher.publish_error(error_msg)
        return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f'任务执行失败: {str(e)}'
        logger.exception(error_msg)

        # 更新阶段状态
        try:
            stage = ProjectStage.objects.get(
                project_id=project_id,
                stage_type=stage_name
            )
            stage.status = 'failed'
            stage.error_message = error_msg
            stage.retry_count += 1
            stage.save()
        except Exception:
            pass

        # 发布错误消息
        publisher.publish_error(error_msg, retry_count=self.request.retries)

        # 重试
        if self.request.retries < self.max_retries:
            logger.info(f"任务将在60秒后重试 (第{self.request.retries + 1}次)")
            raise self.retry(exc=e, countdown=60)

        return {'success': False, 'error': error_msg}

    finally:
        publisher.close()


@app.task(
    bind=True,
    max_retries=0,
    default_retry_delay=60,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=600,
    time_limit=900
)
def execute_text2image_stage(
    self,
    project_id: str,
    storyboard_ids: list = None,
    user_id: int = None
) -> Dict[str, Any]:
    """
    执行文生图阶段任务

    Args:
        self: Celery任务实例
        project_id: 项目ID
        storyboard_ids: 分镜ID列表 (可选，为空则处理所有分镜)
        user_id: 用户ID

    Returns:
        Dict包含: success, task_id, channel, result
    """
    task_id = self.request.id
    stage_name = 'image_generation'
    channel = f"ai_story:project:{project_id}:stage:{stage_name}"

    logger.info(f"开始执行文生图任务, 项目: {project_id}, 任务ID: {task_id}")

    publisher = RedisStreamPublisher(project_id, stage_name)

    try:
        # 获取项目和阶段
        project = Project.objects.get(id=project_id)
        stage = ProjectStage.objects.get(project=project, stage_type=stage_name)

        # 更新阶段状态
        stage.status = 'processing'
        stage.started_at = timezone.now()
        stage.save()

        # 发布开始消息
        publisher.publish_stage_update(
            status='processing',
            progress=0,
            message='开始生成图片'
        )

        # 创建处理器
        processor = Text2ImageStageProcessor()

        # 执行流式处理
        for chunk in processor.process_stream(
            project_id=project_id,
            storyboard_ids=storyboard_ids
        ):
            chunk_type = chunk.get('type')

            if chunk_type == 'progress':
                # 发布进度消息
                publisher.publish_progress(
                    current=chunk.get('current', 0),
                    total=chunk.get('total', 0),
                    item_name=chunk.get('item_name', ''),
                )

            elif chunk_type == 'stage_update':
                # 发布阶段更新
                publisher.publish_stage_update(
                    status=chunk.get('status', 'processing'),
                    progress=chunk.get('progress'),
                    message=chunk.get('message')
                )

            elif chunk_type == 'done':
                # 处理完成
                metadata = chunk.get('metadata', {})

                # 更新阶段状态
                ProjectStage.objects.filter(id=stage.id).update(
                    status='completed',
                    completed_at=timezone.now()
                )
                # 发布完成消息
                publisher.publish_done(metadata=metadata)

            elif chunk_type == 'error':
                # 处理错误
                error_msg = chunk.get('error', '未知错误')
                raise Exception(error_msg)

        logger.info(f"文生图任务完成, 项目: {project_id}")

        return {
            'success': True,
            'task_id': task_id,
            'channel': channel
        }

    except Exception as e:
        error_msg = f'文生图任务失败: {str(e)}'
        logger.exception(error_msg)

        # 更新阶段状态
        try:
            stage = ProjectStage.objects.get(
                project_id=project_id,
                stage_type=stage_name
            )
            stage.status = 'failed'
            stage.error_message = error_msg
            stage.retry_count += 1
            stage.save()
        except Exception:
            pass

        # 发布错误消息
        publisher.publish_error(error_msg, retry_count=self.request.retries)

        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)

        return {'success': False, 'error': error_msg}

    finally:
        publisher.close()


@app.task(
    bind=True,
    max_retries=0,
    default_retry_delay=60,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=1200,  # 20分钟软超时 (视频生成较慢)
    time_limit=1500  # 25分钟硬超时
)
def execute_image2video_stage(
    self,
    project_id: str,
    storyboard_ids: list = None,
    user_id: int = None
) -> Dict[str, Any]:
    """
    执行图生视频阶段任务

    Args:
        self: Celery任务实例
        project_id: 项目ID
        storyboard_ids: 分镜ID列表 (可选，为空则处理所有分镜)
        user_id: 用户ID

    Returns:
        Dict包含: success, task_id, channel, result
    """
    task_id = self.request.id
    stage_name = 'video_generation'
    channel = f"ai_story:project:{project_id}:stage:{stage_name}"

    logger.info(f"开始执行图生视频任务, 项目: {project_id}, 任务ID: {task_id}")

    publisher = RedisStreamPublisher(project_id, stage_name)

    try:
        # 获取项目和阶段
        project = Project.objects.get(id=project_id)
        stage = ProjectStage.objects.get(project=project, stage_type=stage_name)

        # 更新阶段状态
        stage.status = 'processing'
        stage.started_at = timezone.now()
        stage.save()

        # 发布开始消息
        publisher.publish_stage_update(
            status='processing',
            progress=0,
            message='开始生成视频'
        )

        # 创建处理器
        processor = Image2VideoStageProcessor()

        # 执行流式处理
        for chunk in processor.process_stream(
            project_id=project_id,
            storyboard_ids=storyboard_ids
        ):
            chunk_type = chunk.get('type')

            if chunk_type == 'progress':
                # 发布进度消息
                publisher.publish_progress(
                    current=chunk.get('current', 0),
                    total=chunk.get('total', 0),
                    item_name=chunk.get('item_name', '')
                )

            elif chunk_type == 'stage_update':
                # 发布阶段更新
                publisher.publish_stage_update(
                    status=chunk.get('status', 'processing'),
                    progress=chunk.get('progress'),
                    message=chunk.get('message')
                )

            elif chunk_type == 'done':
                # 处理完成
                metadata = chunk.get('metadata', {})
                # 发布完成消息
                publisher.publish_done(metadata=metadata)

            elif chunk_type == 'error':
                # 处理错误
                error_msg = chunk.get('error', '未知错误')
                raise Exception(error_msg)

        logger.info(f"图生视频任务完成, 项目: {project_id}")

        return {
            'success': True,
            'task_id': task_id,
            'channel': channel
        }

    except Exception as e:
        error_msg = f'图生视频任务失败: {str(e)}'
        logger.exception(error_msg)

        # 更新阶段状态
        try:
            stage = ProjectStage.objects.get(
                project_id=project_id,
                stage_type=stage_name
            )
            stage.status = 'failed'
            stage.error_message = error_msg
            stage.retry_count += 1
            stage.save()
        except Exception:
            pass

        # 发布错误消息
        publisher.publish_error(error_msg, retry_count=self.request.retries)

        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)

        return {'success': False, 'error': error_msg}

    finally:
        publisher.close()


@app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=300,  # 5分钟软超时
    time_limit=600  # 10分钟硬超时
)
def generate_jianying_draft(
    self,
    project_id: str,
    user_id: int = None,
    background_music: str = None,
    **options
) -> Dict[str, Any]:
    """
    生成剪映草稿任务

    Args:
        self: Celery任务实例
        project_id: 项目ID
        user_id: 用户ID
        background_music: 背景音乐文件路径（可选）
        **options: 其他可选参数
            - draft_folder_path: 草稿保存路径
            - music_volume: 背景音乐音量
            - add_intro_animation: 是否添加入场动画
            等等...

    Returns:
        Dict包含: success, draft_path, error
    """
    task_id = self.request.id
    channel = f"ai_story:project:{project_id}:jianying_draft"

    logger.info(f"开始生成剪映草稿, 项目: {project_id}, 任务ID: {task_id}")


    try:
        # 获取项目
        project = Project.objects.get(id=project_id)
        # 检查视频生成阶段是否完成
        video_stage = ProjectStage.objects.filter(
            project=project,
            stage_type='video_generation',
            status='completed'
        ).first()

        if not video_stage:
            raise ValueError('视频生成阶段未完成，无法生成剪映草稿')

        # 获取场景数据
        scenes = video_stage.output_data.get('human_text', {}).get('scenes', [])

        if not scenes:
            raise ValueError('没有找到视频场景数据')

        # 过滤出有视频的场景
        valid_scenes = [s for s in scenes if s.get('video_urls')]

        if not valid_scenes:
            raise ValueError('没有找到已生成的视频')

        logger.info(f"找到 {len(valid_scenes)} 个有效视频场景")


        # 创建剪映草稿生成器
        draft_folder_path = options.pop('draft_folder_path', None)
        generator = JianyingDraftGenerator(draft_folder_path=draft_folder_path)

        # 生成草稿
        draft_path = generator.generate_from_project_data(
            project_name=f"{project.name}_{project.id}",
            scenes=valid_scenes,
            background_music=background_music,
            **options
        )

        logger.info(f"剪映草稿生成成功: {draft_path}")

        # 更新项目的剪映草稿路径
        project.jianying_draft_path = draft_path
        project.save(update_fields=['jianying_draft_path'])


        return {
            'success': True,
            'task_id': task_id,
            'channel': channel,
            'draft_path': draft_path
        }

    except Project.DoesNotExist:
        error_msg = f'项目不存在: {project_id}'
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}

    except ValueError as e:
        error_msg = str(e)
        logger.error(f'参数错误: {error_msg}')
        return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f'生成剪映草稿失败: {str(e)}'
        logger.exception(error_msg)

        # 发布错误消息

        # 重试
        if self.request.retries < self.max_retries:
            logger.info(f"任务将在60秒后重试 (第{self.request.retries + 1}次)")
            raise self.retry(exc=e, countdown=60)

        return {'success': False, 'error': error_msg}

    finally:
        pass


@app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=600,
    time_limit=900
)
def export_project_video(
    self,
    project_id: str,
    user_id: int,
    include_subtitles: bool = True,
    video_format: str = "mp4"
) -> Dict[str, Any]:
    """
    导出项目完整视频任务
    
    Args:
        self: Celery任务实例
        project_id: 项目ID
        user_id: 用户ID
        include_subtitles: 是否包含字幕
        video_format: 视频格式
        
    Returns:
        Dict包含: success, video_path, error
    """
    from core.services.video_export_service import VideoExportService
    from apps.content.models import Storyboard
    
    task_id = self.request.id
    channel = f"ai_story:project:{project_id}:export"
    
    logger.info(f"开始导出项目视频, 项目: {project_id}, 任务ID: {task_id}")
    
    publisher = RedisStreamPublisher(project_id, 'export')
    
    try:
        # 获取项目
        project = Project.objects.get(id=project_id, user_id=user_id)
        
        # 检查项目状态
        if project.status != 'completed':
            raise ValueError('项目未完成，无法导出')
        
        # 发布开始消息
        publisher.publish_stage_update(
            status='processing',
            progress=0,
            message='开始导出视频'
        )
        
        # 获取所有分镜及其视频
        storyboards = Storyboard.objects.filter(
            project=project
        ).order_by('sequence_number').prefetch_related('videos')
        
        if not storyboards.exists():
            raise ValueError('项目没有分镜数据')
        
        # 收集视频URL和字幕数据
        video_urls = []
        subtitle_data = []
        current_time = 0.0
        
        for storyboard in storyboards:
            # 获取该分镜的视频（取最新的成功生成的）
            video = storyboard.videos.filter(status='completed').order_by('-created_at').first()
            
            if not video:
                logger.warning(f"分镜 {storyboard.sequence_number} 没有可用视频，跳过")
                continue
            
            video_urls.append(video.video_url)
            
            # 添加字幕数据
            if include_subtitles and storyboard.narration_text:
                duration = video.duration or 3.0
                subtitle_data.append({
                    'text': storyboard.narration_text,
                    'start': current_time,
                    'end': current_time + duration
                })
                current_time += duration
        
        if not video_urls:
            raise ValueError('没有可用的视频片段')
        
        logger.info(f"找到 {len(video_urls)} 个视频片段")
        
        # 发布进度
        publisher.publish_stage_update(
            status='processing',
            progress=0.3,
            message=f'正在合并 {len(video_urls)} 个视频片段'
        )
        
        # 创建导出服务
        export_service = VideoExportService()
        
        # 合并视频
        output_filename = f"{project.name}_{project.id}"
        video_path = export_service.merge_videos(
            video_urls=video_urls,
            output_filename=output_filename,
            include_subtitles=include_subtitles,
            subtitle_data=subtitle_data if include_subtitles else None,
            video_format=video_format
        )
        
        # 发布完成消息
        publisher.publish_done(
            result=video_path,
            metadata={
                'video_count': len(video_urls),
                'has_subtitles': include_subtitles,
                'format': video_format
            }
        )
        
        logger.info(f"视频导出成功: {video_path}")
        
        return {
            'success': True,
            'task_id': task_id,
            'channel': channel,
            'video_path': video_path
        }
        
    except Project.DoesNotExist:
        error_msg = f'项目不存在: {project_id}'
        logger.error(error_msg)
        publisher.publish_error(error_msg)
        return {'success': False, 'error': error_msg}
        
    except ValueError as e:
        error_msg = str(e)
        logger.error(f'参数错误: {error_msg}')
        publisher.publish_error(error_msg)
        return {'success': False, 'error': error_msg}
        
    except Exception as e:
        error_msg = f'视频导出失败: {str(e)}'
        logger.exception(error_msg)
        
        publisher.publish_error(error_msg, retry_count=self.request.retries)
        
        # 重试
        if self.request.retries < self.max_retries:
            logger.info(f"任务将在60秒后重试 (第{self.request.retries + 1}次)")
            raise self.retry(exc=e, countdown=60)
        
        return {'success': False, 'error': error_msg}
        
    finally:
        publisher.close()
