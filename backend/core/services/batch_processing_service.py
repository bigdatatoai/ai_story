"""
批量处理服务
支持批量生成、批量导出、批量发布
"""

import os
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings

logger = logging.getLogger(__name__)


class BatchProcessingService:
    """批量处理服务"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
    
    def batch_generate_videos(
        self,
        topics: List[str],
        output_dir: str,
        template_id: Optional[str] = None,
        config: Dict = None
    ) -> List[Dict]:
        """
        批量生成视频
        
        Args:
            topics: 主题列表
            output_dir: 输出目录
            template_id: 模板ID
            config: 生成配置
            
        Returns:
            List[Dict]: 生成结果列表
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for i, topic in enumerate(topics):
                future = executor.submit(
                    self._generate_single_video,
                    topic=topic,
                    index=i,
                    output_dir=output_dir,
                    template_id=template_id,
                    config=config
                )
                futures[future] = topic
            
            for future in as_completed(futures):
                topic = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"批量生成完成: {topic}")
                except Exception as e:
                    logger.error(f"生成失败 {topic}: {str(e)}")
                    results.append({
                        'success': False,
                        'topic': topic,
                        'error': str(e)
                    })
        
        return results
    
    def _generate_single_video(
        self,
        topic: str,
        index: int,
        output_dir: str,
        template_id: Optional[str] = None,
        config: Dict = None
    ) -> Dict:
        """生成单个视频"""
        from apps.projects.models import Project
        from apps.projects.services.template_service import ProjectTemplateService
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        try:
            # 创建项目
            if template_id:
                # 从模板创建
                from apps.projects.models_template import ProjectTemplate
                template = ProjectTemplate.objects.get(id=template_id)
                
                # 需要一个用户，这里使用系统用户或配置的用户
                user = User.objects.first()  # 简化处理
                
                project = ProjectTemplateService.create_from_template(
                    template=template,
                    user=user,
                    project_name=f"批量生成_{index+1}",
                    original_topic=topic
                )
            else:
                # 直接创建
                user = User.objects.first()
                project = Project.objects.create(
                    name=f"批量生成_{index+1}",
                    original_topic=topic,
                    user=user,
                    status='draft'
                )
            
            # 执行工作流
            from apps.projects.tasks import (
                execute_llm_stage,
                execute_text2image_stage,
                execute_image2video_stage,
                export_project_video
            )
            
            # 1. 文案改写
            execute_llm_stage(
                project_id=str(project.id),
                stage_name='rewrite',
                input_data={},
                user_id=user.id
            )
            
            # 2. 分镜生成
            execute_llm_stage(
                project_id=str(project.id),
                stage_name='storyboard',
                input_data={},
                user_id=user.id
            )
            
            # 3. 文生图
            execute_text2image_stage(
                project_id=str(project.id),
                storyboard_ids=None,
                user_id=user.id
            )
            
            # 4. 图生视频
            execute_image2video_stage(
                project_id=str(project.id),
                storyboard_ids=None,
                user_id=user.id
            )
            
            # 5. 导出
            output_path = os.path.join(output_dir, f'video_{index+1}.mp4')
            export_result = export_project_video(
                project_id=str(project.id),
                user_id=user.id,
                include_subtitles=True,
                video_format='mp4'
            )
            
            return {
                'success': True,
                'topic': topic,
                'project_id': str(project.id),
                'output_path': export_result.get('video_path')
            }
            
        except Exception as e:
            logger.error(f"生成视频失败: {str(e)}")
            raise
    
    def batch_export_with_variations(
        self,
        project_id: str,
        output_dir: str,
        variations: List[Dict]
    ) -> List[Dict]:
        """
        批量导出不同版本
        
        Args:
            project_id: 项目ID
            output_dir: 输出目录
            variations: 变体配置列表
                [
                    {
                        'name': 'douyin',
                        'resolution': '9:16_1080p',
                        'watermark': {...},
                        'dedup': True
                    },
                    ...
                ]
            
        Returns:
            List[Dict]: 导出结果
        """
        from core.services.video_export_advanced import AdvancedVideoExportService
        from core.services.video_dedup_service import VideoDeduplicationService
        
        export_service = AdvancedVideoExportService()
        dedup_service = VideoDeduplicationService()
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        # 获取原始视频
        from apps.projects.models import Project
        project = Project.objects.get(id=project_id)
        
        # 假设已有导出的视频
        base_video = f"/path/to/project/{project_id}/video.mp4"  # 需要实际路径
        
        for variation in variations:
            try:
                name = variation.get('name', 'default')
                output_path = os.path.join(output_dir, f'{name}.mp4')
                
                # 应用去重
                if variation.get('dedup', False):
                    temp_path = os.path.join(output_dir, f'temp_{name}.mp4')
                    dedup_service.apply_deduplication(
                        base_video,
                        temp_path,
                        methods=variation.get('dedup_methods', ['crop', 'filter']),
                        intensity=variation.get('dedup_intensity', 'medium')
                    )
                    current_video = temp_path
                else:
                    current_video = base_video
                
                # 导出指定分辨率
                resolution = variation.get('resolution', '1080p')
                preset = export_service.RESOLUTION_PRESETS.get(resolution)
                
                if preset:
                    export_service.export_with_resolution(
                        current_video,
                        output_path,
                        width=preset['width'],
                        height=preset['height'],
                        bitrate=preset['bitrate'],
                        watermark_config=variation.get('watermark')
                    )
                
                results.append({
                    'success': True,
                    'name': name,
                    'output_path': output_path
                })
                
                # 清理临时文件
                if variation.get('dedup', False) and os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            except Exception as e:
                logger.error(f"导出变体 {name} 失败: {str(e)}")
                results.append({
                    'success': False,
                    'name': name,
                    'error': str(e)
                })
        
        return results
    
    def batch_publish(
        self,
        video_paths: List[str],
        platforms: List[str],
        title_template: str,
        description_template: str,
        tags: List[str] = None
    ) -> List[Dict]:
        """
        批量发布到多个平台
        
        Args:
            video_paths: 视频路径列表
            platforms: 平台列表
            title_template: 标题模板 (支持 {index} 占位符)
            description_template: 描述模板
            tags: 标签列表
            
        Returns:
            List[Dict]: 发布结果
        """
        from core.services.platform_publish_service import PlatformPublishService
        
        publish_service = PlatformPublishService()
        
        results = []
        
        for i, video_path in enumerate(video_paths, 1):
            title = title_template.format(index=i)
            description = description_template.format(index=i)
            
            # 发布到所有平台
            publish_results = publish_service.publish_to_multiple_platforms(
                platforms=platforms,
                video_path=video_path,
                title=title,
                description=description,
                tags=tags
            )
            
            results.append({
                'video_path': video_path,
                'index': i,
                'platforms': publish_results
            })
        
        return results
    
    def create_content_matrix(
        self,
        base_topic: str,
        variations: List[str],
        platforms: List[str],
        output_dir: str
    ) -> Dict:
        """
        创建内容矩阵（一稿多发）
        
        Args:
            base_topic: 基础主题
            variations: 变体列表（不同角度）
            platforms: 目标平台
            output_dir: 输出目录
            
        Returns:
            Dict: 矩阵生成结果
        """
        os.makedirs(output_dir, exist_ok=True)
        
        matrix_results = {
            'base_topic': base_topic,
            'variations': [],
            'total_videos': 0,
            'total_publishes': 0
        }
        
        # 为每个变体生成视频
        for variation in variations:
            topic = f"{base_topic} - {variation}"
            
            # 生成视频
            video_results = self.batch_generate_videos(
                topics=[topic],
                output_dir=os.path.join(output_dir, variation),
                config={'variation': variation}
            )
            
            if video_results and video_results[0].get('success'):
                video_path = video_results[0].get('output_path')
                
                # 为不同平台导出
                platform_exports = self.batch_export_with_variations(
                    project_id=video_results[0].get('project_id'),
                    output_dir=os.path.join(output_dir, variation, 'exports'),
                    variations=[
                        {'name': 'douyin', 'resolution': '9:16_1080p'},
                        {'name': 'kuaishou', 'resolution': '9:16_1080p'},
                        {'name': 'bilibili', 'resolution': '1080p'},
                    ]
                )
                
                # 发布到各平台
                publish_results = self.batch_publish(
                    video_paths=[e['output_path'] for e in platform_exports if e.get('success')],
                    platforms=platforms,
                    title_template=f"{base_topic} - {variation}",
                    description_template=f"精彩内容：{variation}",
                    tags=[base_topic, variation]
                )
                
                matrix_results['variations'].append({
                    'variation': variation,
                    'video_generated': True,
                    'exports': platform_exports,
                    'publishes': publish_results
                })
                
                matrix_results['total_videos'] += 1
                matrix_results['total_publishes'] += len(publish_results)
        
        return matrix_results


class ScheduledTaskService:
    """定时任务服务"""
    
    def schedule_batch_generation(
        self,
        topics: List[str],
        schedule_time: str,
        config: Dict = None
    ) -> str:
        """
        调度批量生成任务
        
        Args:
            topics: 主题列表
            schedule_time: 调度时间 (ISO格式)
            config: 配置
            
        Returns:
            str: 任务ID
        """
        from apps.projects.tasks import execute_llm_stage
        from datetime import datetime
        
        # 使用 Celery 的 eta 参数调度任务
        schedule_dt = datetime.fromisoformat(schedule_time)
        
        # 创建批量任务
        task_ids = []
        
        for topic in topics:
            task = execute_llm_stage.apply_async(
                kwargs={
                    'project_id': 'new',  # 需要先创建项目
                    'stage_name': 'rewrite',
                    'input_data': {'topic': topic},
                    'user_id': 1  # 需要实际用户ID
                },
                eta=schedule_dt
            )
            task_ids.append(task.id)
        
        return ','.join(task_ids)
    
    def schedule_daily_publish(
        self,
        video_dir: str,
        platforms: List[str],
        publish_time: str = "09:00"
    ) -> str:
        """
        调度每日发布任务
        
        Args:
            video_dir: 视频目录
            platforms: 平台列表
            publish_time: 发布时间 (HH:MM)
            
        Returns:
            str: 任务ID
        """
        from celery.schedules import crontab
        from apps.projects.tasks import app
        
        # 解析时间
        hour, minute = map(int, publish_time.split(':'))
        
        # 创建定时任务
        @app.task
        def daily_publish_task():
            batch_service = BatchProcessingService()
            
            # 获取待发布视频
            import glob
            videos = glob.glob(os.path.join(video_dir, '*.mp4'))
            
            if videos:
                # 发布第一个视频
                batch_service.batch_publish(
                    video_paths=[videos[0]],
                    platforms=platforms,
                    title_template="每日精选 {index}",
                    description_template="今日推荐内容",
                    tags=['每日更新']
                )
        
        # 注册定时任务
        app.conf.beat_schedule['daily-publish'] = {
            'task': 'daily_publish_task',
            'schedule': crontab(hour=hour, minute=minute),
        }
        
        return 'daily-publish'
