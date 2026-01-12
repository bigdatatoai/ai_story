"""
背景音乐服务
支持音乐库管理、自动混音、音频处理
"""

import os
import time
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from django.conf import settings
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

logger = logging.getLogger(__name__)


class AudioMixer:
    """音频混合器"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 2
    
    def mix_audio_with_music(
        self,
        voice_path: str,
        music_path: str,
        output_path: str,
        music_volume: float = 0.3,
        fade_in: int = 1000,
        fade_out: int = 1000,
        auto_duck: bool = True
    ) -> str:
        """
        混合配音和背景音乐
        
        Args:
            voice_path: 配音文件路径
            music_path: 背景音乐路径
            output_path: 输出文件路径
            music_volume: 音乐音量 (0.0-1.0)
            fade_in: 淡入时长(毫秒)
            fade_out: 淡出时长(毫秒)
            auto_duck: 自动闪避（配音时降低音乐音量）
            
        Returns:
            str: 混合后的音频文件路径
        """
        try:
            # 加载音频文件
            voice = AudioSegment.from_file(voice_path)
            music = AudioSegment.from_file(music_path)
            
            # 调整音乐长度以匹配配音
            voice_duration = len(voice)
            
            if len(music) < voice_duration:
                # 音乐太短，循环播放
                loops_needed = (voice_duration // len(music)) + 1
                music = music * loops_needed
            
            # 裁剪音乐到配音长度
            music = music[:voice_duration]
            
            # 添加淡入淡出
            if fade_in > 0:
                music = music.fade_in(fade_in)
            if fade_out > 0:
                music = music.fade_out(fade_out)
            
            # 调整音乐音量
            music = music - (20 * (1 - music_volume))  # 降低音量
            
            # 自动闪避：在有配音的地方降低音乐音量
            if auto_duck:
                music = self._apply_ducking(voice, music)
            
            # 混合音频
            mixed = voice.overlay(music)
            
            # 标准化音量
            mixed = normalize(mixed)
            
            # 动态范围压缩
            mixed = compress_dynamic_range(mixed)
            
            # 导出
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            mixed.export(output_path, format='mp3', bitrate='192k')
            
            logger.info(f"音频混合成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"音频混合失败: {str(e)}")
            raise
    
    def _apply_ducking(
        self,
        voice: AudioSegment,
        music: AudioSegment,
        threshold: int = -40,
        duck_amount: int = -15
    ) -> AudioSegment:
        """
        应用自动闪避效果
        
        Args:
            voice: 配音音频
            music: 背景音乐
            threshold: 检测阈值(dB)
            duck_amount: 闪避量(dB)
            
        Returns:
            AudioSegment: 处理后的音乐
        """
        # 检测配音的响度
        chunk_size = 100  # 100ms 为一个检测单位
        ducked_music = AudioSegment.empty()
        
        for i in range(0, len(music), chunk_size):
            music_chunk = music[i:i + chunk_size]
            voice_chunk = voice[i:i + chunk_size] if i < len(voice) else AudioSegment.silent(duration=chunk_size)
            
            # 检测配音音量
            if voice_chunk.dBFS > threshold:
                # 有配音，降低音乐音量
                music_chunk = music_chunk + duck_amount
            
            ducked_music += music_chunk
        
        return ducked_music
    
    def concatenate_audio(
        self,
        audio_files: List[str],
        output_path: str,
        crossfade: int = 500
    ) -> str:
        """
        拼接多个音频文件
        
        Args:
            audio_files: 音频文件路径列表
            output_path: 输出路径
            crossfade: 交叉淡化时长(毫秒)
            
        Returns:
            str: 拼接后的音频路径
        """
        try:
            if not audio_files:
                raise ValueError("音频文件列表为空")
            
            # 加载第一个文件
            combined = AudioSegment.from_file(audio_files[0])
            
            # 依次拼接其他文件
            for audio_file in audio_files[1:]:
                audio = AudioSegment.from_file(audio_file)
                
                if crossfade > 0:
                    combined = combined.append(audio, crossfade=crossfade)
                else:
                    combined = combined + audio
            
            # 导出
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            combined.export(output_path, format='mp3', bitrate='192k')
            
            logger.info(f"音频拼接成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"音频拼接失败: {str(e)}")
            raise
    
    def trim_audio(
        self,
        audio_path: str,
        output_path: str,
        start_ms: int = 0,
        end_ms: Optional[int] = None
    ) -> str:
        """
        裁剪音频
        
        Args:
            audio_path: 输入音频路径
            output_path: 输出路径
            start_ms: 开始时间(毫秒)
            end_ms: 结束时间(毫秒)，None表示到结尾
            
        Returns:
            str: 裁剪后的音频路径
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            
            if end_ms is None:
                trimmed = audio[start_ms:]
            else:
                trimmed = audio[start_ms:end_ms]
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            trimmed.export(output_path, format='mp3', bitrate='192k')
            
            logger.info(f"音频裁剪成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"音频裁剪失败: {str(e)}")
            raise


class MusicLibrary:
    """音乐库管理"""
    
    def __init__(self, library_path: str = None):
        self.library_path = library_path or os.path.join(settings.MEDIA_ROOT, 'music_library')
        os.makedirs(self.library_path, exist_ok=True)
    
    def get_music_by_mood(self, mood: str) -> List[Dict]:
        """
        根据情绪获取音乐
        
        Args:
            mood: 情绪类型 (happy, sad, tense, calm, energetic)
            
        Returns:
            List[Dict]: 音乐列表
        """
        from apps.content.models import BackgroundMusic
        
        music_list = BackgroundMusic.objects.filter(
            mood=mood,
            is_active=True
        ).values('id', 'name', 'file_path', 'duration', 'mood', 'tags')
        
        return list(music_list)
    
    def get_music_by_duration(
        self,
        min_duration: int,
        max_duration: int,
        mood: Optional[str] = None
    ) -> List[Dict]:
        """
        根据时长获取音乐
        
        Args:
            min_duration: 最小时长(秒)
            max_duration: 最大时长(秒)
            mood: 情绪类型(可选)
            
        Returns:
            List[Dict]: 音乐列表
        """
        from apps.content.models import BackgroundMusic
        from django.db.models import Q
        
        query = Q(
            duration__gte=min_duration,
            duration__lte=max_duration,
            is_active=True
        )
        
        if mood:
            query &= Q(mood=mood)
        
        music_list = BackgroundMusic.objects.filter(query).values(
            'id', 'name', 'file_path', 'duration', 'mood', 'tags'
        )
        
        return list(music_list)
    
    def search_music(
        self,
        keyword: str = None,
        mood: str = None,
        tags: List[str] = None
    ) -> List[Dict]:
        """
        搜索音乐
        
        Args:
            keyword: 关键词
            mood: 情绪
            tags: 标签列表
            
        Returns:
            List[Dict]: 音乐列表
        """
        from apps.content.models import BackgroundMusic
        from django.db.models import Q
        
        query = Q(is_active=True)
        
        if keyword:
            query &= Q(name__icontains=keyword) | Q(description__icontains=keyword)
        
        if mood:
            query &= Q(mood=mood)
        
        if tags:
            for tag in tags:
                query &= Q(tags__contains=tag)
        
        music_list = BackgroundMusic.objects.filter(query).values(
            'id', 'name', 'file_path', 'duration', 'mood', 'tags', 'description'
        )
        
        return list(music_list)
    
    def add_music(
        self,
        name: str,
        file_path: str,
        mood: str,
        duration: int,
        tags: List[str] = None,
        description: str = ""
    ) -> Dict:
        """
        添加音乐到库
        
        Args:
            name: 音乐名称
            file_path: 文件路径
            mood: 情绪
            duration: 时长(秒)
            tags: 标签
            description: 描述
            
        Returns:
            Dict: 音乐信息
        """
        from apps.content.models import BackgroundMusic
        
        music = BackgroundMusic.objects.create(
            name=name,
            file_path=file_path,
            mood=mood,
            duration=duration,
            tags=tags or [],
            description=description,
            is_active=True
        )
        
        return {
            'id': str(music.id),
            'name': music.name,
            'file_path': music.file_path,
            'mood': music.mood,
            'duration': music.duration,
            'tags': music.tags
        }


class MusicService:
    """音乐服务管理器"""
    
    def __init__(self):
        self.library = MusicLibrary()
        self.mixer = AudioMixer()
    
    def auto_select_music(
        self,
        duration: int,
        mood: str = 'calm',
        tags: List[str] = None
    ) -> Optional[str]:
        """
        自动选择合适的背景音乐
        
        Args:
            duration: 需要的时长(秒)
            mood: 情绪
            tags: 标签
            
        Returns:
            Optional[str]: 音乐文件路径
        """
        # 搜索合适的音乐
        music_list = self.library.get_music_by_duration(
            min_duration=duration - 5,
            max_duration=duration + 30,
            mood=mood
        )
        
        if not music_list:
            # 没有找到，尝试任意时长
            music_list = self.library.get_music_by_mood(mood)
        
        if not music_list:
            logger.warning(f"未找到合适的背景音乐: mood={mood}, duration={duration}")
            return None
        
        # 选择第一个
        selected = music_list[0]
        return selected['file_path']
    
    def create_audio_track(
        self,
        voice_files: List[str],
        music_path: Optional[str] = None,
        output_path: str = None,
        music_volume: float = 0.3,
        auto_select_music: bool = True,
        mood: str = 'calm'
    ) -> str:
        """
        创建完整音轨（配音 + 背景音乐）
        
        Args:
            voice_files: 配音文件列表
            music_path: 背景音乐路径
            output_path: 输出路径
            music_volume: 音乐音量
            auto_select_music: 自动选择音乐
            mood: 音乐情绪
            
        Returns:
            str: 音轨文件路径
        """
        try:
            # 1. 拼接所有配音
            import tempfile
            temp_voice = os.path.join(tempfile.gettempdir(), f'voice_{int(time.time())}.mp3')
            
            if len(voice_files) == 1:
                temp_voice = voice_files[0]
            else:
                temp_voice = self.mixer.concatenate_audio(
                    voice_files,
                    temp_voice,
                    crossfade=300
                )
            
            # 2. 获取配音时长
            voice_audio = AudioSegment.from_file(temp_voice)
            voice_duration = len(voice_audio) / 1000  # 转换为秒
            
            # 3. 选择或使用指定的背景音乐
            if not music_path and auto_select_music:
                music_path = self.auto_select_music(
                    duration=int(voice_duration),
                    mood=mood
                )
            
            if not music_path:
                logger.warning("没有背景音乐，仅返回配音")
                return temp_voice
            
            # 4. 混合配音和音乐
            if not output_path:
                output_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'audio_tracks',
                    f'track_{int(time.time())}.mp3'
                )
            
            final_audio = self.mixer.mix_audio_with_music(
                voice_path=temp_voice,
                music_path=music_path,
                output_path=output_path,
                music_volume=music_volume,
                auto_duck=True
            )
            
            # 5. 清理临时文件
            if temp_voice != voice_files[0] and os.path.exists(temp_voice):
                os.remove(temp_voice)
            
            return final_audio
            
        except Exception as e:
            logger.error(f"创建音轨失败: {str(e)}")
            raise
