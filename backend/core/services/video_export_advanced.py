"""
高级视频导出服务
支持多分辨率、水印定制、批量导出
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


class AdvancedVideoExportService:
    """高级视频导出服务"""
    
    # 预设分辨率配置
    RESOLUTION_PRESETS = {
        '360p': {'width': 640, 'height': 360, 'bitrate': '800k'},
        '480p': {'width': 854, 'height': 480, 'bitrate': '1200k'},
        '720p': {'width': 1280, 'height': 720, 'bitrate': '2500k'},
        '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
        '2k': {'width': 2560, 'height': 1440, 'bitrate': '8000k'},
        '4k': {'width': 3840, 'height': 2160, 'bitrate': '15000k'},
        # 竖屏格式
        '9:16_720p': {'width': 720, 'height': 1280, 'bitrate': '2500k'},
        '9:16_1080p': {'width': 1080, 'height': 1920, 'bitrate': '5000k'},
        # 方屏格式
        '1:1_720p': {'width': 720, 'height': 720, 'bitrate': '2000k'},
        '1:1_1080p': {'width': 1080, 'height': 1080, 'bitrate': '4000k'},
    }
    
    def __init__(self):
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_export')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def export_multi_resolution(
        self,
        input_video: str,
        output_dir: str,
        resolutions: List[str] = None,
        watermark_config: Dict = None
    ) -> Dict[str, str]:
        """
        导出多个分辨率版本
        
        Args:
            input_video: 输入视频路径
            output_dir: 输出目录
            resolutions: 分辨率列表 ['720p', '1080p', '4k']
            watermark_config: 水印配置
            
        Returns:
            Dict[str, str]: {分辨率: 输出路径}
        """
        if resolutions is None:
            resolutions = ['720p', '1080p']
        
        os.makedirs(output_dir, exist_ok=True)
        
        output_files = {}
        
        for resolution in resolutions:
            if resolution not in self.RESOLUTION_PRESETS:
                logger.warning(f"不支持的分辨率: {resolution}")
                continue
            
            preset = self.RESOLUTION_PRESETS[resolution]
            output_path = os.path.join(output_dir, f'video_{resolution}.mp4')
            
            try:
                # 导出指定分辨率
                self.export_with_resolution(
                    input_video,
                    output_path,
                    width=preset['width'],
                    height=preset['height'],
                    bitrate=preset['bitrate'],
                    watermark_config=watermark_config
                )
                
                output_files[resolution] = output_path
                logger.info(f"导出 {resolution} 完成: {output_path}")
                
            except Exception as e:
                logger.error(f"导出 {resolution} 失败: {str(e)}")
        
        return output_files
    
    def export_with_resolution(
        self,
        input_video: str,
        output_path: str,
        width: int,
        height: int,
        bitrate: str = '5000k',
        watermark_config: Dict = None,
        fps: int = 30
    ) -> str:
        """
        导出指定分辨率的视频
        
        Args:
            input_video: 输入视频
            output_path: 输出路径
            width: 宽度
            height: 高度
            bitrate: 比特率
            watermark_config: 水印配置
            fps: 帧率
            
        Returns:
            str: 输出路径
        """
        try:
            # 构建 FFmpeg 命令
            cmd = ['ffmpeg', '-i', input_video]
            
            # 构建视频滤镜
            vf_filters = []
            
            # 缩放
            vf_filters.append(f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2')
            
            # 添加水印
            if watermark_config:
                watermark_filter = self._build_watermark_filter(watermark_config)
                if watermark_filter:
                    vf_filters.append(watermark_filter)
            
            # 设置帧率
            vf_filters.append(f'fps={fps}')
            
            # 组合滤镜
            vf_string = ','.join(vf_filters)
            
            cmd.extend([
                '-vf', vf_string,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-b:v', bitrate,
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',  # 优化网络播放
                '-y',
                output_path
            ])
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg 错误: {result.stderr}")
            
            logger.info(f"视频导出成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"视频导出失败: {str(e)}")
            raise
    
    def _build_watermark_filter(self, config: Dict) -> str:
        """
        构建水印滤镜
        
        Args:
            config: 水印配置
                {
                    'type': 'text' or 'image',
                    'text': '水印文字',
                    'image_path': '图片路径',
                    'position': 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center',
                    'opacity': 0.5,
                    'font_size': 24,
                    'font_color': 'white',
                    'offset_x': 10,
                    'offset_y': 10
                }
        """
        watermark_type = config.get('type', 'text')
        
        if watermark_type == 'text':
            return self._build_text_watermark(config)
        elif watermark_type == 'image':
            return self._build_image_watermark(config)
        
        return ''
    
    def _build_text_watermark(self, config: Dict) -> str:
        """构建文字水印滤镜"""
        text = config.get('text', '')
        if not text:
            return ''
        
        position = config.get('position', 'bottom-right')
        opacity = config.get('opacity', 0.5)
        font_size = config.get('font_size', 24)
        font_color = config.get('font_color', 'white')
        offset_x = config.get('offset_x', 10)
        offset_y = config.get('offset_y', 10)
        
        # 计算位置
        position_map = {
            'top-left': f'x={offset_x}:y={offset_y}',
            'top-right': f'x=w-text_w-{offset_x}:y={offset_y}',
            'bottom-left': f'x={offset_x}:y=h-text_h-{offset_y}',
            'bottom-right': f'x=w-text_w-{offset_x}:y=h-text_h-{offset_y}',
            'center': 'x=(w-text_w)/2:y=(h-text_h)/2'
        }
        
        pos_str = position_map.get(position, position_map['bottom-right'])
        
        # 构建 drawtext 滤镜
        filter_str = (
            f"drawtext=text='{text}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}@{opacity}:"
            f"{pos_str}"
        )
        
        return filter_str
    
    def _build_image_watermark(self, config: Dict) -> str:
        """构建图片水印滤镜"""
        image_path = config.get('image_path', '')
        if not image_path or not os.path.exists(image_path):
            return ''
        
        position = config.get('position', 'bottom-right')
        opacity = config.get('opacity', 0.5)
        offset_x = config.get('offset_x', 10)
        offset_y = config.get('offset_y', 10)
        scale = config.get('scale', 0.1)  # 水印大小相对于视频的比例
        
        # 计算位置
        position_map = {
            'top-left': f'x={offset_x}:y={offset_y}',
            'top-right': f'x=main_w-overlay_w-{offset_x}:y={offset_y}',
            'bottom-left': f'x={offset_x}:y=main_h-overlay_h-{offset_y}',
            'bottom-right': f'x=main_w-overlay_w-{offset_x}:y=main_h-overlay_h-{offset_y}',
            'center': 'x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2'
        }
        
        pos_str = position_map.get(position, position_map['bottom-right'])
        
        # 需要使用 overlay 滤镜（需要在主滤镜链之外处理）
        # 这里返回简化版本，实际使用时需要调整
        filter_str = f"movie={image_path},scale=iw*{scale}:ih*{scale},format=rgba,colorchannelmixer=aa={opacity}[wm];[in][wm]overlay={pos_str}[out]"
        
        return filter_str
    
    def add_watermark(
        self,
        input_video: str,
        output_path: str,
        watermark_config: Dict
    ) -> str:
        """
        单独添加水印
        
        Args:
            input_video: 输入视频
            output_path: 输出路径
            watermark_config: 水印配置
            
        Returns:
            str: 输出路径
        """
        try:
            watermark_type = watermark_config.get('type', 'text')
            
            if watermark_type == 'text':
                # 文字水印
                watermark_filter = self._build_text_watermark(watermark_config)
                
                cmd = [
                    'ffmpeg',
                    '-i', input_video,
                    '-vf', watermark_filter,
                    '-c:a', 'copy',
                    '-y', output_path
                ]
                
            elif watermark_type == 'image':
                # 图片水印
                image_path = watermark_config.get('image_path', '')
                position = watermark_config.get('position', 'bottom-right')
                opacity = watermark_config.get('opacity', 0.5)
                offset_x = watermark_config.get('offset_x', 10)
                offset_y = watermark_config.get('offset_y', 10)
                
                position_map = {
                    'top-left': f'{offset_x}:{offset_y}',
                    'top-right': f'main_w-overlay_w-{offset_x}:{offset_y}',
                    'bottom-left': f'{offset_x}:main_h-overlay_h-{offset_y}',
                    'bottom-right': f'main_w-overlay_w-{offset_x}:main_h-overlay_h-{offset_y}',
                    'center': '(main_w-overlay_w)/2:(main_h-overlay_h)/2'
                }
                
                pos_str = position_map.get(position, position_map['bottom-right'])
                
                cmd = [
                    'ffmpeg',
                    '-i', input_video,
                    '-i', image_path,
                    '-filter_complex',
                    f'[1:v]format=rgba,colorchannelmixer=aa={opacity}[wm];[0:v][wm]overlay={pos_str}',
                    '-c:a', 'copy',
                    '-y', output_path
                ]
            else:
                raise ValueError(f"不支持的水印类型: {watermark_type}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"添加水印失败: {result.stderr}")
            
            logger.info(f"水印添加成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"添加水印失败: {str(e)}")
            raise
    
    def batch_export(
        self,
        video_paths: List[str],
        output_dir: str,
        resolution: str = '1080p',
        watermark_config: Dict = None,
        naming_pattern: str = 'video_{index}'
    ) -> List[str]:
        """
        批量导出视频
        
        Args:
            video_paths: 视频路径列表
            output_dir: 输出目录
            resolution: 分辨率
            watermark_config: 水印配置
            naming_pattern: 命名模式，{index} 会被替换为序号
            
        Returns:
            List[str]: 导出的视频路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if resolution not in self.RESOLUTION_PRESETS:
            raise ValueError(f"不支持的分辨率: {resolution}")
        
        preset = self.RESOLUTION_PRESETS[resolution]
        output_paths = []
        
        for i, video_path in enumerate(video_paths, 1):
            try:
                # 生成输出文件名
                filename = naming_pattern.format(index=i) + '.mp4'
                output_path = os.path.join(output_dir, filename)
                
                # 导出
                self.export_with_resolution(
                    video_path,
                    output_path,
                    width=preset['width'],
                    height=preset['height'],
                    bitrate=preset['bitrate'],
                    watermark_config=watermark_config
                )
                
                output_paths.append(output_path)
                logger.info(f"批量导出 {i}/{len(video_paths)}: {output_path}")
                
            except Exception as e:
                logger.error(f"导出视频 {i} 失败: {str(e)}")
        
        return output_paths
    
    def export_for_platforms(
        self,
        input_video: str,
        output_dir: str,
        platforms: List[str] = None
    ) -> Dict[str, str]:
        """
        为不同平台导出优化版本
        
        Args:
            input_video: 输入视频
            output_dir: 输出目录
            platforms: 平台列表 ['douyin', 'kuaishou', 'bilibili', 'wechat']
            
        Returns:
            Dict[str, str]: {平台: 输出路径}
        """
        if platforms is None:
            platforms = ['douyin', 'kuaishou', 'bilibili']
        
        # 平台规格配置
        platform_specs = {
            'douyin': {
                'resolution': '9:16_1080p',
                'max_duration': 180,  # 3分钟
                'watermark': {'type': 'text', 'text': '@抖音', 'position': 'bottom-left'}
            },
            'kuaishou': {
                'resolution': '9:16_1080p',
                'max_duration': 300,  # 5分钟
                'watermark': {'type': 'text', 'text': '@快手', 'position': 'bottom-left'}
            },
            'bilibili': {
                'resolution': '1080p',
                'max_duration': 600,  # 10分钟
                'watermark': None
            },
            'wechat': {
                'resolution': '1:1_720p',
                'max_duration': 60,  # 1分钟
                'watermark': None
            }
        }
        
        os.makedirs(output_dir, exist_ok=True)
        output_files = {}
        
        for platform in platforms:
            if platform not in platform_specs:
                logger.warning(f"不支持的平台: {platform}")
                continue
            
            spec = platform_specs[platform]
            output_path = os.path.join(output_dir, f'{platform}.mp4')
            
            try:
                preset = self.RESOLUTION_PRESETS[spec['resolution']]
                
                # 导出
                self.export_with_resolution(
                    input_video,
                    output_path,
                    width=preset['width'],
                    height=preset['height'],
                    bitrate=preset['bitrate'],
                    watermark_config=spec.get('watermark')
                )
                
                output_files[platform] = output_path
                logger.info(f"导出 {platform} 版本完成: {output_path}")
                
            except Exception as e:
                logger.error(f"导出 {platform} 版本失败: {str(e)}")
        
        return output_files
