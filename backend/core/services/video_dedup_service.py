"""
视频去重和混剪服务
用于避免平台查重，提高原创度
"""

import os
import cv2
import numpy as np
import logging
import subprocess
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


class VideoDeduplicationService:
    """视频去重服务"""
    
    def __init__(self):
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_dedup')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def apply_deduplication(
        self,
        video_path: str,
        output_path: str,
        methods: List[str] = None,
        intensity: str = 'medium'
    ) -> str:
        """
        应用去重处理
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            methods: 去重方法列表 ['mirror', 'crop', 'speed', 'filter', 'flip']
            intensity: 强度 (low/medium/high)
            
        Returns:
            str: 处理后的视频路径
        """
        if methods is None:
            methods = ['mirror', 'crop', 'filter', 'speed']
        
        try:
            current_video = video_path
            temp_files = []
            
            # 按顺序应用各种去重方法
            for i, method in enumerate(methods):
                temp_output = os.path.join(
                    self.temp_dir,
                    f'temp_{i}_{os.path.basename(video_path)}'
                )
                
                if method == 'mirror':
                    current_video = self._apply_mirror(current_video, temp_output)
                elif method == 'crop':
                    current_video = self._apply_crop(current_video, temp_output, intensity)
                elif method == 'speed':
                    current_video = self._apply_speed_change(current_video, temp_output, intensity)
                elif method == 'filter':
                    current_video = self._apply_filter(current_video, temp_output, intensity)
                elif method == 'flip':
                    current_video = self._apply_flip(current_video, temp_output)
                elif method == 'rotate':
                    current_video = self._apply_rotate(current_video, temp_output, intensity)
                
                temp_files.append(temp_output)
            
            # 复制最终结果
            if current_video != output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                subprocess.run(['ffmpeg', '-i', current_video, '-c', 'copy', '-y', output_path], check=True)
            
            # 清理临时文件
            for temp_file in temp_files:
                if os.path.exists(temp_file) and temp_file != output_path:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            logger.info(f"视频去重处理完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"视频去重失败: {str(e)}")
            raise
    
    def _apply_mirror(self, input_path: str, output_path: str) -> str:
        """镜像翻转（水平翻转）"""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'hflip',
            '-c:a', 'copy',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def _apply_crop(self, input_path: str, output_path: str, intensity: str) -> str:
        """裁剪视频（去除边缘）"""
        # 根据强度决定裁剪比例
        crop_ratios = {
            'low': 0.02,    # 裁剪2%
            'medium': 0.05, # 裁剪5%
            'high': 0.08    # 裁剪8%
        }
        ratio = crop_ratios.get(intensity, 0.05)
        
        # 获取视频尺寸
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            input_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split('x'))
        
        # 计算裁剪后的尺寸
        crop_w = int(width * (1 - ratio * 2))
        crop_h = int(height * (1 - ratio * 2))
        crop_x = int(width * ratio)
        crop_y = int(height * ratio)
        
        # 应用裁剪
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'crop={crop_w}:{crop_h}:{crop_x}:{crop_y}',
            '-c:a', 'copy',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def _apply_speed_change(self, input_path: str, output_path: str, intensity: str) -> str:
        """改变播放速度"""
        # 根据强度决定速度变化
        speed_factors = {
            'low': 1.05,    # 加速5%
            'medium': 1.10, # 加速10%
            'high': 1.15    # 加速15%
        }
        speed = speed_factors.get(intensity, 1.10)
        
        # 计算音频速度（保持音调）
        atempo = speed
        if atempo > 2.0:
            atempo = 2.0
        elif atempo < 0.5:
            atempo = 0.5
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-filter_complex',
            f'[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={atempo}[a]',
            '-map', '[v]',
            '-map', '[a]',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def _apply_filter(self, input_path: str, output_path: str, intensity: str) -> str:
        """应用滤镜效果"""
        # 根据强度选择滤镜
        filters = {
            'low': 'eq=brightness=0.05:contrast=1.05',
            'medium': 'eq=brightness=0.08:contrast=1.08:saturation=1.1',
            'high': 'eq=brightness=0.1:contrast=1.1:saturation=1.15:gamma=1.05'
        }
        filter_str = filters.get(intensity, filters['medium'])
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def _apply_flip(self, input_path: str, output_path: str) -> str:
        """垂直翻转"""
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'vflip',
            '-c:a', 'copy',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def _apply_rotate(self, input_path: str, output_path: str, intensity: str) -> str:
        """轻微旋转"""
        # 根据强度决定旋转角度
        angles = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.5
        }
        angle = angles.get(intensity, 1.0)
        
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'rotate={angle}*PI/180:fillcolor=black',
            '-c:a', 'copy',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    
    def shuffle_scenes(
        self,
        video_paths: List[str],
        output_path: str,
        shuffle_ratio: float = 0.3
    ) -> str:
        """
        打乱场景顺序
        
        Args:
            video_paths: 视频片段列表
            output_path: 输出路径
            shuffle_ratio: 打乱比例 (0.0-1.0)
            
        Returns:
            str: 输出视频路径
        """
        try:
            # 计算需要打乱的片段数量
            shuffle_count = int(len(video_paths) * shuffle_ratio)
            
            if shuffle_count < 2:
                # 不需要打乱，直接合并
                return self._concatenate_videos(video_paths, output_path)
            
            # 复制列表
            shuffled_paths = video_paths.copy()
            
            # 随机选择片段进行打乱
            indices = list(range(len(shuffled_paths)))
            shuffle_indices = random.sample(indices, shuffle_count)
            
            # 打乱选中的片段
            selected_videos = [shuffled_paths[i] for i in shuffle_indices]
            random.shuffle(selected_videos)
            
            # 放回打乱后的片段
            for i, idx in enumerate(shuffle_indices):
                shuffled_paths[idx] = selected_videos[i]
            
            # 合并视频
            return self._concatenate_videos(shuffled_paths, output_path)
            
        except Exception as e:
            logger.error(f"场景打乱失败: {str(e)}")
            raise
    
    def _concatenate_videos(self, video_paths: List[str], output_path: str) -> str:
        """合并视频片段"""
        # 创建 concat 文件
        concat_file = os.path.join(self.temp_dir, 'concat_list.txt')
        
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video_path in video_paths:
                abs_path = os.path.abspath(video_path).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        # 合并
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y', output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # 清理
        os.remove(concat_file)
        
        return output_path
    
    def add_random_elements(
        self,
        video_path: str,
        output_path: str,
        elements: List[str] = None
    ) -> str:
        """
        添加随机元素（水印、贴纸等）
        
        Args:
            video_path: 输入视频
            output_path: 输出视频
            elements: 元素类型列表 ['watermark', 'timestamp', 'border']
            
        Returns:
            str: 输出视频路径
        """
        if elements is None:
            elements = ['timestamp']
        
        try:
            filters = []
            
            if 'watermark' in elements:
                # 添加半透明水印文字
                text = f"ID:{random.randint(10000, 99999)}"
                filters.append(
                    f"drawtext=text='{text}':fontsize=20:fontcolor=white@0.3:"
                    f"x=(w-text_w)/2:y=h-50"
                )
            
            if 'timestamp' in elements:
                # 添加时间戳
                filters.append(
                    "drawtext=text='%{localtime}':fontsize=16:fontcolor=white@0.4:"
                    "x=10:y=10"
                )
            
            if 'border' in elements:
                # 添加边框
                filters.append(
                    "pad=width=iw+20:height=ih+20:x=10:y=10:color=black"
                )
            
            if not filters:
                # 没有元素，直接复制
                subprocess.run(['ffmpeg', '-i', video_path, '-c', 'copy', '-y', output_path], check=True)
                return output_path
            
            # 应用滤镜
            filter_str = ','.join(filters)
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_str,
                '-c:a', 'copy',
                '-y', output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info(f"添加随机元素完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"添加随机元素失败: {str(e)}")
            raise


class VideoRemixService:
    """视频混剪服务"""
    
    def __init__(self):
        self.dedup_service = VideoDeduplicationService()
    
    def create_remix(
        self,
        video_paths: List[str],
        output_path: str,
        remix_config: Dict = None
    ) -> str:
        """
        创建混剪视频
        
        Args:
            video_paths: 原始视频列表
            output_path: 输出路径
            remix_config: 混剪配置
                {
                    'shuffle': True,
                    'shuffle_ratio': 0.3,
                    'dedup_methods': ['mirror', 'crop', 'filter'],
                    'dedup_intensity': 'medium',
                    'add_elements': ['timestamp']
                }
            
        Returns:
            str: 混剪视频路径
        """
        if remix_config is None:
            remix_config = {
                'shuffle': True,
                'shuffle_ratio': 0.3,
                'dedup_methods': ['crop', 'filter'],
                'dedup_intensity': 'medium',
                'add_elements': ['timestamp']
            }
        
        try:
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_remix')
            os.makedirs(temp_dir, exist_ok=True)
            
            processed_videos = []
            
            # 1. 对每个视频片段应用去重处理
            for i, video_path in enumerate(video_paths):
                temp_output = os.path.join(temp_dir, f'processed_{i}.mp4')
                
                # 应用去重
                if remix_config.get('dedup_methods'):
                    self.dedup_service.apply_deduplication(
                        video_path,
                        temp_output,
                        methods=remix_config['dedup_methods'],
                        intensity=remix_config.get('dedup_intensity', 'medium')
                    )
                else:
                    # 不去重，直接复制
                    subprocess.run(['ffmpeg', '-i', video_path, '-c', 'copy', '-y', temp_output], check=True)
                
                processed_videos.append(temp_output)
            
            # 2. 打乱顺序（如果启用）
            if remix_config.get('shuffle', False):
                shuffled_output = os.path.join(temp_dir, 'shuffled.mp4')
                self.dedup_service.shuffle_scenes(
                    processed_videos,
                    shuffled_output,
                    shuffle_ratio=remix_config.get('shuffle_ratio', 0.3)
                )
                final_video = shuffled_output
            else:
                # 直接合并
                merged_output = os.path.join(temp_dir, 'merged.mp4')
                self.dedup_service._concatenate_videos(processed_videos, merged_output)
                final_video = merged_output
            
            # 3. 添加随机元素
            if remix_config.get('add_elements'):
                self.dedup_service.add_random_elements(
                    final_video,
                    output_path,
                    elements=remix_config['add_elements']
                )
            else:
                # 直接复制为最终输出
                subprocess.run(['ffmpeg', '-i', final_video, '-c', 'copy', '-y', output_path], check=True)
            
            # 4. 清理临时文件
            for temp_file in processed_videos + [final_video]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            logger.info(f"混剪视频创建完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"混剪视频创建失败: {str(e)}")
            raise
    
    def batch_remix(
        self,
        video_paths: List[str],
        output_dir: str,
        count: int = 3,
        remix_config: Dict = None
    ) -> List[str]:
        """
        批量生成多个混剪版本
        
        Args:
            video_paths: 原始视频列表
            output_dir: 输出目录
            count: 生成数量
            remix_config: 混剪配置
            
        Returns:
            List[str]: 生成的视频路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        
        output_paths = []
        
        for i in range(count):
            output_path = os.path.join(output_dir, f'remix_{i+1}.mp4')
            
            # 每次使用不同的配置
            config = remix_config.copy() if remix_config else {}
            config['shuffle_ratio'] = random.uniform(0.2, 0.5)
            
            # 随机选择去重方法
            all_methods = ['mirror', 'crop', 'filter', 'speed']
            config['dedup_methods'] = random.sample(all_methods, random.randint(2, 3))
            
            # 创建混剪
            output = self.create_remix(video_paths, output_path, config)
            output_paths.append(output)
        
        return output_paths
