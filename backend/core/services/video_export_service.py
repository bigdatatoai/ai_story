"""
视频导出服务
职责: 合成视频片段、生成字幕、导出完整视频
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class VideoExportService:
    """视频导出服务"""

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化视频导出服务
        
        Args:
            output_dir: 输出目录，默认为临时目录
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def merge_videos(
        self,
        video_urls: List[str],
        output_filename: str,
        include_subtitles: bool = False,
        subtitle_data: Optional[List[Dict]] = None,
        video_format: str = "mp4"
    ) -> str:
        """
        合并多个视频片段为一个完整视频
        
        Args:
            video_urls: 视频URL列表（按顺序）
            output_filename: 输出文件名
            include_subtitles: 是否包含字幕
            subtitle_data: 字幕数据列表 [{"text": "...", "start": 0, "end": 3}, ...]
            video_format: 视频格式 (mp4, mov, avi等)
            
        Returns:
            str: 导出视频的路径
        """
        try:
            # 1. 下载所有视频到本地
            temp_videos = self._download_videos(video_urls)
            
            # 2. 创建FFmpeg concat文件
            concat_file = self._create_concat_file(temp_videos)
            
            # 3. 合并视频
            output_path = os.path.join(self.output_dir, f"{output_filename}.{video_format}")
            self._merge_with_ffmpeg(concat_file, output_path)
            
            # 4. 如果需要字幕，生成并嵌入
            if include_subtitles and subtitle_data:
                output_path = self._add_subtitles(output_path, subtitle_data)
            
            # 5. 清理临时文件
            self._cleanup_temp_files(temp_videos + [concat_file])
            
            logger.info(f"视频导出成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.exception(f"视频导出失败: {str(e)}")
            raise

    def _download_videos(self, video_urls: List[str]) -> List[str]:
        """
        下载视频到本地临时目录
        
        Args:
            video_urls: 视频URL列表
            
        Returns:
            List[str]: 本地视频文件路径列表
        """
        import requests
        
        temp_videos = []
        for i, url in enumerate(video_urls):
            try:
                # 如果是本地路径，直接使用
                if os.path.exists(url):
                    temp_videos.append(url)
                    continue
                
                # 下载远程视频
                response = requests.get(url, stream=True, timeout=60)
                response.raise_for_status()
                
                temp_path = os.path.join(tempfile.gettempdir(), f"temp_video_{i}.mp4")
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                temp_videos.append(temp_path)
                logger.info(f"下载视频 {i+1}/{len(video_urls)}: {url}")
                
            except Exception as e:
                logger.error(f"下载视频失败 {url}: {str(e)}")
                raise
        
        return temp_videos

    def _create_concat_file(self, video_paths: List[str]) -> str:
        """
        创建FFmpeg concat文件
        
        Args:
            video_paths: 视频文件路径列表
            
        Returns:
            str: concat文件路径
        """
        concat_file = os.path.join(tempfile.gettempdir(), "concat_list.txt")
        
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video_path in video_paths:
                # 转换为绝对路径并转义
                abs_path = os.path.abspath(video_path).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        return concat_file

    def _merge_with_ffmpeg(self, concat_file: str, output_path: str):
        """
        使用FFmpeg合并视频
        
        Args:
            concat_file: concat文件路径
            output_path: 输出文件路径
        """
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',  # 直接复制，不重新编码（更快）
            '-y',  # 覆盖输出文件
            output_path
        ]
        
        logger.info(f"执行FFmpeg命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5分钟超时
            )
            logger.info(f"FFmpeg输出: {result.stdout}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg错误: {e.stderr}")
            raise Exception(f"视频合并失败: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise Exception("视频合并超时")

    def _add_subtitles(self, video_path: str, subtitle_data: List[Dict]) -> str:
        """
        生成字幕并嵌入视频
        
        Args:
            video_path: 视频文件路径
            subtitle_data: 字幕数据
            
        Returns:
            str: 带字幕的视频路径
        """
        # 1. 生成SRT字幕文件
        srt_path = self._generate_srt(subtitle_data)
        
        # 2. 使用FFmpeg嵌入字幕
        output_path = video_path.replace('.mp4', '_with_subtitles.mp4')
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&HFFFFFF&'",
            '-c:a', 'copy',  # 音频直接复制
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
            logger.info(f"字幕嵌入成功: {output_path}")
            
            # 删除原视频
            os.remove(video_path)
            os.remove(srt_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"字幕嵌入失败: {str(e)}")
            raise

    def _generate_srt(self, subtitle_data: List[Dict]) -> str:
        """
        生成SRT字幕文件
        
        Args:
            subtitle_data: 字幕数据 [{"text": "...", "start": 0, "end": 3}, ...]
            
        Returns:
            str: SRT文件路径
        """
        srt_path = os.path.join(tempfile.gettempdir(), "subtitles.srt")
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, subtitle in enumerate(subtitle_data, 1):
                start_time = self._format_srt_time(subtitle['start'])
                end_time = self._format_srt_time(subtitle['end'])
                text = subtitle['text']
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        return srt_path

    def _format_srt_time(self, seconds: float) -> str:
        """
        格式化SRT时间戳
        
        Args:
            seconds: 秒数
            
        Returns:
            str: SRT时间格式 (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _cleanup_temp_files(self, file_paths: List[str]):
        """清理临时文件"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"清理临时文件失败 {file_path}: {str(e)}")

    def get_video_info(self, video_path: str) -> Dict:
        """
        获取视频信息
        
        Args:
            video_path: 视频路径
            
        Returns:
            Dict: 视频信息（时长、分辨率等）
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return {}
