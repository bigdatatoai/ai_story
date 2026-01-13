"""
内容生成异步任务
职责: 处理图片/视频生成等耗时操作
"""

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import logging

from .models import GeneratedImage, GeneratedVideo, CameraMovement
from apps.models.models import ModelUsageLog

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, time_limit=3600, soft_time_limit=3500)
def generate_image_task(self, image_id):
    """
    图片生成任务
    
    Args:
        image_id: GeneratedImage实例的UUID
    
    Returns:
        dict: 生成结果
    """
    try:
        # 校验参数
        image = GeneratedImage.objects.filter(is_deleted=False, id=image_id).first()
        if not image:
            raise ValueError(f'图片记录不存在或已删除: {image_id}')
        
        # 更新状态为处理中
        image.status = 'processing'
        image.save(update_fields=['status', 'updated_at'])
        
        logger.info(f'开始生成图片: {image_id}')
        
        # TODO: 调用AI模型生成图片
        # 这里需要集成实际的图片生成逻辑
        # result = ai_client.generate_image(
        #     prompt=image.storyboard.image_prompt,
        #     params=image.generation_params
        # )
        
        # 模拟生成结果
        result = {
            'image_url': 'https://example.com/generated_image.jpg',
            'thumbnail_url': 'https://example.com/thumbnail.jpg',
            'width': 1024,
            'height': 768,
            'file_size': 524288
        }
        
        # 更新图片信息
        image.image_url = result['image_url']
        image.thumbnail_url = result.get('thumbnail_url', '')
        image.width = result.get('width', 0)
        image.height = result.get('height', 0)
        image.file_size = result.get('file_size', 0)
        image.status = 'completed'
        image.save()
        
        # 记录使用日志
        if image.model_provider:
            ModelUsageLog.objects.create(
                model_provider=image.model_provider,
                request_data={'prompt': image.storyboard.image_prompt},
                response_data=result,
                status='success',
                project_id=image.storyboard.project_id,
                stage_type='image_generation'
            )
        
        logger.info(f'图片生成成功: {image_id}')
        return {'status': 'success', 'image_id': str(image_id), 'image_url': result['image_url']}
        
    except SoftTimeLimitExceeded:
        logger.warning(f'图片生成超时: {image_id}')
        image.status = 'failed'
        image.error_message = '生成超时'
        image.retry_count += 1
        image.save()
        
        # 重试
        raise self.retry(countdown=60)
        
    except Exception as e:
        logger.error(f'图片生成失败: {image_id} - {str(e)}', exc_info=True)
        
        # 更新失败状态
        if 'image' in locals():
            image.status = 'failed'
            image.error_message = str(e)
            image.retry_count += 1
            image.save()
            
            # 记录失败日志
            if image.model_provider:
                ModelUsageLog.objects.create(
                    model_provider=image.model_provider,
                    request_data={'prompt': image.storyboard.image_prompt},
                    response_data={},
                    status='failed',
                    error_message=str(e),
                    project_id=image.storyboard.project_id,
                    stage_type='image_generation'
                )
        
        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30)
        
        return {'status': 'failed', 'image_id': str(image_id), 'error': str(e)}


@shared_task(bind=True, max_retries=3, time_limit=7200, soft_time_limit=7100)
def generate_video_task(self, video_id):
    """
    视频生成任务
    
    Args:
        video_id: GeneratedVideo实例的UUID
    
    Returns:
        dict: 生成结果
    """
    try:
        # 校验参数
        video = GeneratedVideo.objects.filter(is_deleted=False, id=video_id).select_related(
            'image', 'camera_movement', 'storyboard'
        ).first()
        
        if not video:
            raise ValueError(f'视频记录不存在或已删除: {video_id}')
        
        if not video.image or not video.camera_movement:
            raise ValueError(f'视频生成缺少必要数据: image或camera_movement')
        
        # 更新状态为处理中
        video.status = 'processing'
        video.save(update_fields=['status', 'updated_at'])
        
        logger.info(f'开始生成视频: {video_id}')
        
        # TODO: 调用AI模型生成视频
        # result = ai_client.generate_video(
        #     image_url=video.image.image_url,
        #     camera_params=video.camera_movement.movement_params,
        #     params=video.generation_params
        # )
        
        # 模拟生成结果
        result = {
            'video_url': 'https://example.com/generated_video.mp4',
            'thumbnail_url': 'https://example.com/video_thumbnail.jpg',
            'duration': 5.0,
            'width': 1024,
            'height': 768,
            'fps': 24,
            'file_size': 2097152
        }
        
        # 更新视频信息
        video.video_url = result['video_url']
        video.thumbnail_url = result.get('thumbnail_url', '')
        video.duration = result.get('duration', 0)
        video.width = result.get('width', 0)
        video.height = result.get('height', 0)
        video.fps = result.get('fps', 24)
        video.file_size = result.get('file_size', 0)
        video.status = 'completed'
        video.save()
        
        # 记录使用日志
        if video.model_provider:
            ModelUsageLog.objects.create(
                model_provider=video.model_provider,
                request_data={
                    'image_url': video.image.image_url,
                    'camera_params': video.camera_movement.movement_params
                },
                response_data=result,
                status='success',
                project_id=video.storyboard.project_id,
                stage_type='video_generation'
            )
        
        logger.info(f'视频生成成功: {video_id}')
        return {'status': 'success', 'video_id': str(video_id), 'video_url': result['video_url']}
        
    except SoftTimeLimitExceeded:
        logger.warning(f'视频生成超时: {video_id}')
        video.status = 'failed'
        video.error_message = '生成超时'
        video.retry_count += 1
        video.save()
        
        # 重试
        raise self.retry(countdown=120)
        
    except Exception as e:
        logger.error(f'视频生成失败: {video_id} - {str(e)}', exc_info=True)
        
        # 更新失败状态
        if 'video' in locals():
            video.status = 'failed'
            video.error_message = str(e)
            video.retry_count += 1
            video.save()
            
            # 记录失败日志
            if video.model_provider:
                ModelUsageLog.objects.create(
                    model_provider=video.model_provider,
                    request_data={},
                    response_data={},
                    status='failed',
                    error_message=str(e),
                    project_id=video.storyboard.project_id,
                    stage_type='video_generation'
                )
        
        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        
        return {'status': 'failed', 'video_id': str(video_id), 'error': str(e)}


@shared_task(bind=True, max_retries=3, time_limit=600, soft_time_limit=580)
def generate_camera_movement_task(self, camera_movement_id):
    """
    运镜参数生成任务
    
    Args:
        camera_movement_id: CameraMovement实例的UUID
    
    Returns:
        dict: 生成结果
    """
    try:
        # 校验参数
        cm = CameraMovement.objects.filter(is_deleted=False, id=camera_movement_id).select_related(
            'storyboard'
        ).first()
        
        if not cm:
            raise ValueError(f'运镜数据不存在或已删除: {camera_movement_id}')
        
        logger.info(f'开始生成运镜参数: {camera_movement_id}')
        
        # TODO: 调用AI模型生成运镜参数
        # result = ai_client.generate_camera_movement(
        #     scene_description=cm.storyboard.scene_description,
        #     movement_type=cm.movement_type
        # )
        
        # 模拟生成结果
        result = {
            'movement_params': {
                'speed': 1.5,
                'duration': 3.0,
                'easing': 'ease-in-out',
                'intensity': 0.8
            },
            'prompt_used': f'生成{cm.get_movement_type_display()}运镜参数'
        }
        
        # 更新运镜参数
        cm.movement_params = result['movement_params']
        cm.prompt_used = result.get('prompt_used', '')
        cm.save()
        
        # 记录使用日志
        if cm.model_provider:
            ModelUsageLog.objects.create(
                model_provider=cm.model_provider,
                request_data={'scene_description': cm.storyboard.scene_description},
                response_data=result,
                status='success',
                project_id=cm.storyboard.project_id,
                stage_type='camera_movement'
            )
        
        logger.info(f'运镜参数生成成功: {camera_movement_id}')
        return {'status': 'success', 'camera_movement_id': str(camera_movement_id)}
        
    except SoftTimeLimitExceeded:
        logger.warning(f'运镜参数生成超时: {camera_movement_id}')
        raise self.retry(countdown=30)
        
    except Exception as e:
        logger.error(f'运镜参数生成失败: {camera_movement_id} - {str(e)}', exc_info=True)
        
        # 记录失败日志
        if 'cm' in locals() and cm.model_provider:
            ModelUsageLog.objects.create(
                model_provider=cm.model_provider,
                request_data={},
                response_data={},
                status='failed',
                error_message=str(e),
                project_id=cm.storyboard.project_id,
                stage_type='camera_movement'
            )
        
        # 重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=20)
        
        return {'status': 'failed', 'camera_movement_id': str(camera_movement_id), 'error': str(e)}


@shared_task
def batch_generate_images(storyboard_ids):
    """
    批量生成图片
    
    Args:
        storyboard_ids: 分镜ID列表
    
    Returns:
        dict: 批量生成结果
    """
    results = {'success': [], 'failed': []}
    
    for storyboard_id in storyboard_ids:
        try:
            # 为每个分镜创建图片生成任务
            image = GeneratedImage.objects.create(
                storyboard_id=storyboard_id,
                status='pending'
            )
            
            # 异步调用图片生成任务
            generate_image_task.delay(str(image.id))
            results['success'].append(str(storyboard_id))
            
        except Exception as e:
            logger.error(f'创建图片生成任务失败: {storyboard_id} - {str(e)}')
            results['failed'].append({'storyboard_id': str(storyboard_id), 'error': str(e)})
    
    return results


@shared_task
def cleanup_failed_tasks():
    """
    清理失败的任务（定期任务）
    重置超过最大重试次数的失败任务
    """
    from datetime import timedelta
    
    # 清理24小时前失败的图片任务
    cutoff_time = timezone.now() - timedelta(hours=24)
    
    failed_images = GeneratedImage.objects.filter(
        status='failed',
        retry_count__gte=3,
        updated_at__lt=cutoff_time,
        is_deleted=False
    )
    
    failed_videos = GeneratedVideo.objects.filter(
        status='failed',
        retry_count__gte=3,
        updated_at__lt=cutoff_time,
        is_deleted=False
    )
    
    images_count = failed_images.count()
    videos_count = failed_videos.count()
    
    # 软删除失败任务
    failed_images.update(is_deleted=True)
    failed_videos.update(is_deleted=True)
    
    logger.info(f'清理失败任务完成: 图片={images_count}, 视频={videos_count}')
    
    return {'images_cleaned': images_count, 'videos_cleaned': videos_count}
