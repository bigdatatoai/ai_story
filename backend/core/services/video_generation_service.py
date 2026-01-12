"""
AI视频生成服务
支持文本转视频、图片转视频、故事板转视频等功能
"""

import logging
import requests
import json
from typing import Dict, List, Any, Optional
from django.conf import settings
from pathlib import Path
import subprocess
import os

logger = logging.getLogger('ai_story.video')


class VideoGenerationService:
    """视频生成服务"""
    
    def __init__(self):
        self.runway_api_key = getattr(settings, 'RUNWAY_API_KEY', '')
        self.stability_api_key = getattr(settings, 'STABILITY_API_KEY', '')
        self.pika_api_key = getattr(settings, 'PIKA_API_KEY', '')
        
    def text_to_video(
        self,
        prompt: str,
        duration: int = 4,
        resolution: str = '1280x720',
        fps: int = 24,
        style: str = 'realistic',
        **kwargs
    ) -> Dict[str, Any]:
        """
        文本转视频
        
        Args:
            prompt: 视频描述文本
            duration: 视频时长（秒）
            resolution: 分辨率
            fps: 帧率
            style: 视频风格 (realistic/anime/cartoon/cinematic)
        
        Returns:
            {
                'video_url': '视频URL',
                'thumbnail_url': '缩略图URL',
                'duration': 时长,
                'resolution': 分辨率,
                'file_size': 文件大小
            }
        """
        logger.info(f"开始文本转视频: {prompt[:50]}...")
        
        try:
            # 使用Runway Gen-2 API
            video_data = self._generate_with_runway(
                prompt=prompt,
                duration=duration,
                resolution=resolution,
                **kwargs
            )
            
            return video_data
            
        except Exception as e:
            logger.error(f"文本转视频失败: {str(e)}")
            # 降级到Pika API
            try:
                return self._generate_with_pika(prompt, duration, **kwargs)
            except Exception as e2:
                logger.error(f"备用API也失败: {str(e2)}")
                raise
    
    def image_to_video(
        self,
        image_url: str,
        motion_prompt: str = '',
        duration: int = 4,
        motion_strength: float = 0.5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        图片转视频（添加动态效果）
        
        Args:
            image_url: 输入图片URL
            motion_prompt: 运动描述
            duration: 视频时长
            motion_strength: 运动强度 (0-1)
        
        Returns:
            视频信息字典
        """
        logger.info(f"开始图片转视频: {image_url}")
        
        try:
            # 使用Stability AI Video API
            video_data = self._image_to_video_stability(
                image_url=image_url,
                motion_prompt=motion_prompt,
                duration=duration,
                motion_strength=motion_strength,
                **kwargs
            )
            
            return video_data
            
        except Exception as e:
            logger.error(f"图片转视频失败: {str(e)}")
            raise
    
    def storyboard_to_video(
        self,
        storyboard: List[Dict[str, Any]],
        transition_style: str = 'fade',
        background_music_url: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        故事板转视频
        
        Args:
            storyboard: 故事板列表 [
                {
                    'image_url': '图片URL',
                    'narration': '旁白文本',
                    'duration': 持续时间,
                    'motion': '运动效果'
                }
            ]
            transition_style: 转场效果
            background_music_url: 背景音乐URL
        
        Returns:
            完整视频信息
        """
        logger.info(f"开始故事板转视频，共{len(storyboard)}个场景")
        
        # 1. 为每个场景生成视频片段
        video_clips = []
        for i, scene in enumerate(storyboard):
            try:
                clip = self.image_to_video(
                    image_url=scene['image_url'],
                    motion_prompt=scene.get('motion', ''),
                    duration=scene.get('duration', 4),
                )
                
                # 添加旁白
                if scene.get('narration'):
                    clip['narration'] = scene['narration']
                
                video_clips.append(clip)
                logger.info(f"场景 {i+1}/{len(storyboard)} 生成完成")
                
            except Exception as e:
                logger.error(f"场景 {i+1} 生成失败: {str(e)}")
                # 使用静态图片作为降级方案
                video_clips.append({
                    'image_url': scene['image_url'],
                    'duration': scene.get('duration', 4),
                    'narration': scene.get('narration', '')
                })
        
        # 2. 合成完整视频
        final_video = self._compose_video_clips(
            clips=video_clips,
            transition_style=transition_style,
            background_music_url=background_music_url,
            **kwargs
        )
        
        return final_video
    
    def _generate_with_runway(
        self,
        prompt: str,
        duration: int,
        resolution: str,
        **kwargs
    ) -> Dict[str, Any]:
        """使用Runway API生成视频"""
        
        api_url = "https://api.runwayml.com/v1/gen2/generate"
        
        headers = {
            'Authorization': f'Bearer {self.runway_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'prompt': prompt,
            'duration': duration,
            'resolution': resolution,
            'seed': kwargs.get('seed', -1),
            'watermark': False
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        # 轮询直到视频生成完成
        task_id = result['id']
        video_url = self._poll_runway_task(task_id)
        
        return {
            'video_url': video_url,
            'thumbnail_url': result.get('thumbnail_url', ''),
            'duration': duration,
            'resolution': resolution,
            'provider': 'runway'
        }
    
    def _generate_with_pika(
        self,
        prompt: str,
        duration: int,
        **kwargs
    ) -> Dict[str, Any]:
        """使用Pika API生成视频"""
        
        api_url = "https://api.pika.art/v1/generate"
        
        headers = {
            'Authorization': f'Bearer {self.pika_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'prompt': prompt,
            'duration': duration,
            'aspect_ratio': '16:9'
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        return {
            'video_url': result['video_url'],
            'thumbnail_url': result.get('thumbnail_url', ''),
            'duration': duration,
            'provider': 'pika'
        }
    
    def _image_to_video_stability(
        self,
        image_url: str,
        motion_prompt: str,
        duration: int,
        motion_strength: float,
        **kwargs
    ) -> Dict[str, Any]:
        """使用Stability AI将图片转为视频"""
        
        api_url = "https://api.stability.ai/v2alpha/generation/image-to-video"
        
        headers = {
            'Authorization': f'Bearer {self.stability_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'image': image_url,
            'cfg_scale': 2.5,
            'motion_bucket_id': int(motion_strength * 255),
            'seed': kwargs.get('seed', 0)
        }
        
        if motion_prompt:
            payload['motion_prompt'] = motion_prompt
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        # 轮询任务状态
        generation_id = result['id']
        video_url = self._poll_stability_task(generation_id)
        
        return {
            'video_url': video_url,
            'duration': duration,
            'provider': 'stability'
        }
    
    def _compose_video_clips(
        self,
        clips: List[Dict[str, Any]],
        transition_style: str,
        background_music_url: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """使用FFmpeg合成视频片段"""
        
        try:
            from moviepy.editor import (
                VideoFileClip, ImageClip, AudioFileClip,
                concatenate_videoclips, CompositeVideoClip
            )
            
            video_clips_list = []
            
            for clip_data in clips:
                if 'video_url' in clip_data:
                    # 视频片段
                    clip = VideoFileClip(clip_data['video_url'])
                else:
                    # 静态图片
                    clip = ImageClip(clip_data['image_url']).set_duration(clip_data['duration'])
                
                # 添加旁白
                if clip_data.get('narration'):
                    # TODO: 生成旁白音频并添加
                    pass
                
                video_clips_list.append(clip)
            
            # 合并视频片段
            final_clip = concatenate_videoclips(
                video_clips_list,
                method='compose' if transition_style == 'fade' else 'chain'
            )
            
            # 添加背景音乐
            if background_music_url:
                audio = AudioFileClip(background_music_url)
                audio = audio.volumex(0.3)  # 降低音量
                final_clip = final_clip.set_audio(audio)
            
            # 导出视频
            output_path = f"/tmp/composed_video_{id(clips)}.mp4"
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            
            # 上传到存储
            video_url = self._upload_video(output_path)
            
            return {
                'video_url': video_url,
                'duration': final_clip.duration,
                'resolution': f"{final_clip.w}x{final_clip.h}",
                'file_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            logger.error(f"视频合成失败: {str(e)}")
            raise
    
    def _poll_runway_task(self, task_id: str, max_attempts: int = 60) -> str:
        """轮询Runway任务状态"""
        import time
        
        api_url = f"https://api.runwayml.com/v1/tasks/{task_id}"
        headers = {'Authorization': f'Bearer {self.runway_api_key}'}
        
        for attempt in range(max_attempts):
            response = requests.get(api_url, headers=headers)
            result = response.json()
            
            if result['status'] == 'succeeded':
                return result['output']['video_url']
            elif result['status'] == 'failed':
                raise Exception(f"视频生成失败: {result.get('error', 'Unknown error')}")
            
            time.sleep(5)
        
        raise TimeoutError("视频生成超时")
    
    def _poll_stability_task(self, generation_id: str, max_attempts: int = 60) -> str:
        """轮询Stability AI任务状态"""
        import time
        
        api_url = f"https://api.stability.ai/v2alpha/generation/image-to-video/result/{generation_id}"
        headers = {'Authorization': f'Bearer {self.stability_api_key}'}
        
        for attempt in range(max_attempts):
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return result['video']
            elif response.status_code == 202:
                time.sleep(10)
            else:
                raise Exception(f"任务失败: {response.text}")
        
        raise TimeoutError("视频生成超时")
    
    def _upload_video(self, file_path: str) -> str:
        """上传视频到存储"""
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        filename = f"videos/{Path(file_path).name}"
        saved_path = default_storage.save(filename, ContentFile(content))
        
        return default_storage.url(saved_path)


# 导出服务实例
video_generation_service = VideoGenerationService()
