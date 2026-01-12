"""
多模态故事生成服务
集成图像生成、语音合成、视频生成等功能
"""

import logging
import requests
import json
from typing import Dict, List, Any, Optional
from django.conf import settings
import base64
from io import BytesIO

logger = logging.getLogger('ai_story.multimodal')


class IllustrationGenerationService:
    """插画生成服务"""
    
    def __init__(self):
        self.sd_api_url = getattr(settings, 'STABLE_DIFFUSION_API_URL', 'http://localhost:7860')
        self.sd_api_key = getattr(settings, 'STABLE_DIFFUSION_API_KEY', '')
    
    def generate_illustrations(
        self,
        story_content: str,
        style: str = 'cartoon',
        num_illustrations: int = 4,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        为故事生成插画
        
        Args:
            story_content: 故事内容
            style: 插画风格 (cartoon/watercolor/realistic/anime)
            num_illustrations: 插画数量
        
        Returns:
            [{'scene': '场景描述', 'image_url': 'URL', 'prompt': '提示词'}]
        """
        # 1. 提取关键场景
        scenes = self._extract_key_scenes(story_content, num_illustrations)
        
        # 2. 为每个场景生成插画
        illustrations = []
        for i, scene in enumerate(scenes):
            try:
                # 构建图像生成提示词
                prompt = self._build_image_prompt(scene, style)
                
                # 调用Stable Diffusion API
                image_data = self._call_sd_api(prompt, **kwargs)
                
                # 保存图片并获取URL
                image_url = self._save_image(image_data, f"story_illustration_{i}")
                
                illustrations.append({
                    'position': i,
                    'scene': scene,
                    'prompt': prompt,
                    'image_url': image_url,
                    'style': style
                })
                
                logger.info(f"生成插画 {i+1}/{num_illustrations}")
                
            except Exception as e:
                logger.error(f"生成插画失败: {str(e)}")
                illustrations.append({
                    'position': i,
                    'scene': scene,
                    'error': str(e)
                })
        
        return illustrations
    
    def _extract_key_scenes(self, story: str, num_scenes: int) -> List[str]:
        """提取故事中的关键场景"""
        # 简单实现：按段落分割
        paragraphs = [p.strip() for p in story.split('\n\n') if p.strip()]
        
        if len(paragraphs) <= num_scenes:
            return paragraphs
        
        # 均匀采样
        step = len(paragraphs) / num_scenes
        scenes = [paragraphs[int(i * step)] for i in range(num_scenes)]
        
        return scenes
    
    def _build_image_prompt(self, scene: str, style: str) -> str:
        """构建图像生成提示词"""
        
        style_prompts = {
            'cartoon': 'cute cartoon style, colorful, children book illustration',
            'watercolor': 'watercolor painting, soft colors, artistic',
            'realistic': 'photorealistic, detailed, high quality',
            'anime': 'anime style, manga, vibrant colors',
            'hand_drawn': 'hand drawn illustration, sketch style'
        }
        
        style_prompt = style_prompts.get(style, style_prompts['cartoon'])
        
        # 提取场景关键词（简化版）
        scene_keywords = scene[:200]  # 取前200字符
        
        prompt = f"{scene_keywords}, {style_prompt}, high quality, detailed"
        
        # 添加负面提示词
        negative_prompt = "ugly, blurry, low quality, distorted, nsfw"
        
        return prompt
    
    def _call_sd_api(self, prompt: str, **kwargs) -> bytes:
        """调用Stable Diffusion API"""
        
        payload = {
            "prompt": prompt,
            "negative_prompt": kwargs.get('negative_prompt', 'ugly, blurry, low quality'),
            "steps": kwargs.get('steps', 20),
            "width": kwargs.get('width', 512),
            "height": kwargs.get('height', 512),
            "cfg_scale": kwargs.get('cfg_scale', 7),
            "sampler_name": kwargs.get('sampler', 'DPM++ 2M Karras'),
        }
        
        try:
            response = requests.post(
                f"{self.sd_api_url}/sdapi/v1/txt2img",
                json=payload,
                headers={'Authorization': f'Bearer {self.sd_api_key}'} if self.sd_api_key else {},
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 解码base64图片
            image_data = base64.b64decode(result['images'][0])
            return image_data
            
        except Exception as e:
            logger.error(f"Stable Diffusion API调用失败: {str(e)}")
            raise
    
    def _save_image(self, image_data: bytes, filename: str) -> str:
        """保存图片并返回URL"""
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        
        file_path = f"illustrations/{filename}.png"
        saved_path = default_storage.save(file_path, ContentFile(image_data))
        
        # 返回完整URL
        return default_storage.url(saved_path)


class AudioStoryService:
    """有声故事生成服务"""
    
    def __init__(self):
        self.tts_provider = getattr(settings, 'TTS_PROVIDER', 'edge_tts')
    
    def generate_audio_story(
        self,
        story_content: str,
        voice_config: Dict[str, str] = None,
        add_background_music: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成有声故事
        
        Args:
            story_content: 故事内容
            voice_config: 角色音色配置 {'角色名': '音色ID'}
            add_background_music: 是否添加背景音乐
        
        Returns:
            {'audio_url': 'URL', 'duration': 秒数, 'segments': [片段列表]}
        """
        # 1. 解析故事，分离对话和旁白
        segments = self._parse_story_segments(story_content)
        
        # 2. 为每个片段生成音频
        audio_segments = []
        for segment in segments:
            try:
                voice = self._select_voice(segment, voice_config)
                audio_data = self._synthesize_speech(segment['text'], voice, **kwargs)
                
                audio_segments.append({
                    'text': segment['text'],
                    'type': segment['type'],
                    'character': segment.get('character'),
                    'audio_data': audio_data,
                    'duration': self._get_audio_duration(audio_data)
                })
                
            except Exception as e:
                logger.error(f"语音合成失败: {str(e)}")
        
        # 3. 合并音频片段
        final_audio = self._merge_audio_segments(audio_segments)
        
        # 4. 添加背景音乐（可选）
        if add_background_music:
            final_audio = self._add_background_music(final_audio)
        
        # 5. 保存音频文件
        audio_url = self._save_audio(final_audio, 'story_audio')
        
        return {
            'audio_url': audio_url,
            'duration': sum(seg['duration'] for seg in audio_segments),
            'segments': audio_segments
        }
    
    def _parse_story_segments(self, story: str) -> List[Dict[str, Any]]:
        """解析故事，分离对话和旁白"""
        import re
        
        segments = []
        lines = story.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测对话（引号内容）
            dialogue_match = re.search(r'[""]([^""]+)[""]', line)
            
            if dialogue_match:
                # 提取角色名（简化版）
                character = self._extract_character_name(line)
                
                segments.append({
                    'type': 'dialogue',
                    'text': dialogue_match.group(1),
                    'character': character
                })
                
                # 添加旁白部分
                narration = line.replace(dialogue_match.group(0), '').strip()
                if narration:
                    segments.append({
                        'type': 'narration',
                        'text': narration
                    })
            else:
                # 纯旁白
                segments.append({
                    'type': 'narration',
                    'text': line
                })
        
        return segments
    
    def _extract_character_name(self, text: str) -> Optional[str]:
        """从文本中提取角色名"""
        import re
        
        # 简单模式匹配：角色名+说/道/问等
        match = re.search(r'([^，。！？\s]+)(说|道|问|答|叫|喊)：?', text)
        if match:
            return match.group(1)
        
        return None
    
    def _select_voice(
        self,
        segment: Dict[str, Any],
        voice_config: Dict[str, str] = None
    ) -> str:
        """选择合适的音色"""
        
        default_voices = {
            'narrator': 'zh-CN-XiaoxiaoNeural',  # 旁白
            'child': 'zh-CN-XiaoyiNeural',       # 儿童角色
            'adult_male': 'zh-CN-YunxiNeural',   # 成年男性
            'adult_female': 'zh-CN-XiaoxiaoNeural',  # 成年女性
        }
        
        if segment['type'] == 'narration':
            return default_voices['narrator']
        
        # 对话根据角色选择
        character = segment.get('character', '')
        
        if voice_config and character in voice_config:
            return voice_config[character]
        
        # 默认音色
        return default_voices['child']
    
    def _synthesize_speech(self, text: str, voice: str, **kwargs) -> bytes:
        """调用TTS API合成语音"""
        
        if self.tts_provider == 'edge_tts':
            return self._edge_tts_synthesize(text, voice, **kwargs)
        else:
            raise NotImplementedError(f"TTS provider {self.tts_provider} not implemented")
    
    def _edge_tts_synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        """使用Edge TTS合成语音"""
        import edge_tts
        import asyncio
        
        async def _synthesize():
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b''
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
        
        return asyncio.run(_synthesize())
    
    def _get_audio_duration(self, audio_data: bytes) -> float:
        """获取音频时长"""
        from pydub import AudioSegment
        from io import BytesIO
        
        audio = AudioSegment.from_file(BytesIO(audio_data))
        return len(audio) / 1000.0  # 转换为秒
    
    def _merge_audio_segments(self, segments: List[Dict[str, Any]]) -> bytes:
        """合并音频片段"""
        from pydub import AudioSegment
        from io import BytesIO
        
        combined = AudioSegment.empty()
        
        for segment in segments:
            audio = AudioSegment.from_file(BytesIO(segment['audio_data']))
            combined += audio
            # 添加短暂停顿
            combined += AudioSegment.silent(duration=300)  # 300ms
        
        # 导出为bytes
        output = BytesIO()
        combined.export(output, format='mp3')
        return output.getvalue()
    
    def _add_background_music(self, audio_data: bytes) -> bytes:
        """添加背景音乐"""
        from pydub import AudioSegment
        from io import BytesIO
        
        # 加载主音频
        main_audio = AudioSegment.from_file(BytesIO(audio_data))
        
        # 加载背景音乐（需要预先准备）
        # background_music = AudioSegment.from_file('path/to/background.mp3')
        # background_music = background_music - 20  # 降低音量
        
        # 合并
        # combined = main_audio.overlay(background_music)
        
        # 暂时返回原音频
        return audio_data
    
    def _save_audio(self, audio_data: bytes, filename: str) -> str:
        """保存音频文件"""
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        
        file_path = f"audio/{filename}.mp3"
        saved_path = default_storage.save(file_path, ContentFile(audio_data))
        
        return default_storage.url(saved_path)


# 导出服务实例
illustration_service = IllustrationGenerationService()
audio_story_service = AudioStoryService()
