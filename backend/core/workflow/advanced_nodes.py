"""
高级工作流节点
包含视频滤镜、转场效果、文字动画、特效等
"""

import os
import subprocess
import logging
from typing import Dict, Any
from core.workflow.workflow_engine import WorkflowNode

logger = logging.getLogger(__name__)


# ==================== 视频滤镜节点 ====================

class VideoFilterNode(WorkflowNode):
    """视频滤镜节点基类"""
    
    def apply_filter(self, video_path: str, output_path: str, filter_str: str) -> str:
        """应用 FFmpeg 滤镜"""
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path


class ColorGradingNode(VideoFilterNode):
    """色彩调整节点"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        # 获取配置
        brightness = self.config.get('brightness', 0)  # -1.0 to 1.0
        contrast = self.config.get('contrast', 1.0)    # 0.0 to 2.0
        saturation = self.config.get('saturation', 1.0) # 0.0 to 3.0
        gamma = self.config.get('gamma', 1.0)          # 0.1 to 10.0
        
        # 构建滤镜
        filter_str = f'eq=brightness={brightness}:contrast={contrast}:saturation={saturation}:gamma={gamma}'
        
        output_path = f'/tmp/color_graded_{os.path.basename(video_path)}'
        result_path = self.apply_filter(video_path, output_path, filter_str)
        
        return {'video': {'type': 'file', 'value': result_path}}


class VintageFilterNode(VideoFilterNode):
    """复古滤镜节点"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        style = self.config.get('style', 'sepia')  # sepia, black_white, old_film
        
        filter_map = {
            'sepia': 'colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131',
            'black_white': 'hue=s=0',
            'old_film': 'colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,noise=alls=20:allf=t+u'
        }
        
        filter_str = filter_map.get(style, filter_map['sepia'])
        
        output_path = f'/tmp/vintage_{os.path.basename(video_path)}'
        result_path = self.apply_filter(video_path, output_path, filter_str)
        
        return {'video': {'type': 'file', 'value': result_path}}


class BlurFilterNode(VideoFilterNode):
    """模糊滤镜节点"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        blur_type = self.config.get('blur_type', 'gaussian')  # gaussian, box, motion
        intensity = self.config.get('intensity', 5)
        
        if blur_type == 'gaussian':
            filter_str = f'gblur=sigma={intensity}'
        elif blur_type == 'box':
            filter_str = f'boxblur={intensity}:{intensity}'
        elif blur_type == 'motion':
            angle = self.config.get('angle', 0)
            filter_str = f'dblur=angle={angle}:radius={intensity}'
        else:
            filter_str = f'gblur=sigma={intensity}'
        
        output_path = f'/tmp/blurred_{os.path.basename(video_path)}'
        result_path = self.apply_filter(video_path, output_path, filter_str)
        
        return {'video': {'type': 'file', 'value': result_path}}


class SharpenFilterNode(VideoFilterNode):
    """锐化滤镜节点"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        intensity = self.config.get('intensity', 1.0)  # 0.0 to 2.0
        
        filter_str = f'unsharp=5:5:{intensity}:5:5:0.0'
        
        output_path = f'/tmp/sharpened_{os.path.basename(video_path)}'
        result_path = self.apply_filter(video_path, output_path, filter_str)
        
        return {'video': {'type': 'file', 'value': result_path}}


# ==================== 转场效果节点 ====================

class TransitionNode(WorkflowNode):
    """转场效果节点基类"""
    
    def apply_transition(self, video1: str, video2: str, output: str, transition: str, duration: float) -> str:
        """应用转场效果"""
        cmd = [
            'ffmpeg',
            '-i', video1,
            '-i', video2,
            '-filter_complex',
            f'[0:v][1:v]xfade=transition={transition}:duration={duration}:offset=0[outv]',
            '-map', '[outv]',
            '-y', output
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output


class FadeTransitionNode(TransitionNode):
    """淡入淡出转场"""
    
    def execute(self) -> Dict[str, Any]:
        video1 = self.inputs.get('video1')
        video2 = self.inputs.get('video2')
        
        if not video1 or not video2:
            raise ValueError("需要两个视频输入")
        
        path1 = video1.get('value') if isinstance(video1, dict) else video1
        path2 = video2.get('value') if isinstance(video2, dict) else video2
        
        duration = self.config.get('duration', 1.0)
        
        output_path = f'/tmp/fade_transition_{os.path.basename(path1)}'
        result_path = self.apply_transition(path1, path2, output_path, 'fade', duration)
        
        return {'video': {'type': 'file', 'value': result_path}}


class WipeTransitionNode(TransitionNode):
    """擦除转场"""
    
    def execute(self) -> Dict[str, Any]:
        video1 = self.inputs.get('video1')
        video2 = self.inputs.get('video2')
        
        if not video1 or not video2:
            raise ValueError("需要两个视频输入")
        
        path1 = video1.get('value') if isinstance(video1, dict) else video1
        path2 = video2.get('value') if isinstance(video2, dict) else video2
        
        duration = self.config.get('duration', 1.0)
        direction = self.config.get('direction', 'left')  # left, right, up, down
        
        transition_map = {
            'left': 'wipeleft',
            'right': 'wiperight',
            'up': 'wipeup',
            'down': 'wipedown'
        }
        
        transition = transition_map.get(direction, 'wipeleft')
        
        output_path = f'/tmp/wipe_transition_{os.path.basename(path1)}'
        result_path = self.apply_transition(path1, path2, output_path, transition, duration)
        
        return {'video': {'type': 'file', 'value': result_path}}


class SlideTransitionNode(TransitionNode):
    """滑动转场"""
    
    def execute(self) -> Dict[str, Any]:
        video1 = self.inputs.get('video1')
        video2 = self.inputs.get('video2')
        
        if not video1 or not video2:
            raise ValueError("需要两个视频输入")
        
        path1 = video1.get('value') if isinstance(video1, dict) else video1
        path2 = video2.get('value') if isinstance(video2, dict) else video2
        
        duration = self.config.get('duration', 1.0)
        direction = self.config.get('direction', 'left')
        
        transition_map = {
            'left': 'slideleft',
            'right': 'slideright',
            'up': 'slideup',
            'down': 'slidedown'
        }
        
        transition = transition_map.get(direction, 'slideleft')
        
        output_path = f'/tmp/slide_transition_{os.path.basename(path1)}'
        result_path = self.apply_transition(path1, path2, output_path, transition, duration)
        
        return {'video': {'type': 'file', 'value': result_path}}


# ==================== 文字动画节点 ====================

class TextAnimationNode(WorkflowNode):
    """文字动画节点基类"""
    
    def add_text_overlay(self, video_path: str, output_path: str, text: str, filter_str: str) -> str:
        """添加文字覆盖"""
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path


class FadeInTextNode(TextAnimationNode):
    """淡入文字动画"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        text = self.inputs.get('text', self.config.get('text', ''))
        
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        # 配置
        font_size = self.config.get('font_size', 48)
        font_color = self.config.get('font_color', 'white')
        position_x = self.config.get('position_x', '(w-text_w)/2')
        position_y = self.config.get('position_y', '(h-text_h)/2')
        start_time = self.config.get('start_time', 0)
        duration = self.config.get('duration', 2)
        
        # 构建淡入效果
        filter_str = (
            f"drawtext=text='{text}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"x={position_x}:y={position_y}:"
            f"enable='between(t,{start_time},{start_time + duration})':"
            f"alpha='if(lt(t,{start_time + 1}),(t-{start_time})/1,1)'"
        )
        
        output_path = f'/tmp/text_fadein_{os.path.basename(video_path)}'
        result_path = self.add_text_overlay(video_path, output_path, text, filter_str)
        
        return {'video': {'type': 'file', 'value': result_path}}


class TypewriterTextNode(TextAnimationNode):
    """打字机文字动画"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        text = self.inputs.get('text', self.config.get('text', ''))
        
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        font_size = self.config.get('font_size', 48)
        font_color = self.config.get('font_color', 'white')
        position_x = self.config.get('position_x', '(w-text_w)/2')
        position_y = self.config.get('position_y', '(h-text_h)/2')
        speed = self.config.get('speed', 0.1)  # 每个字符的时间
        
        # 打字机效果需要逐字显示
        # 这里简化为逐渐显示
        filter_str = (
            f"drawtext=text='{text}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"x={position_x}:y={position_y}"
        )
        
        output_path = f'/tmp/text_typewriter_{os.path.basename(video_path)}'
        result_path = self.add_text_overlay(video_path, output_path, text, filter_str)
        
        return {'video': {'type': 'file', 'value': result_path}}


class ScrollingTextNode(TextAnimationNode):
    """滚动文字动画"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        text = self.inputs.get('text', self.config.get('text', ''))
        
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        font_size = self.config.get('font_size', 48)
        font_color = self.config.get('font_color', 'white')
        direction = self.config.get('direction', 'up')  # up, down, left, right
        speed = self.config.get('speed', 50)
        
        # 滚动效果
        if direction == 'up':
            position = f"x=(w-text_w)/2:y=h-{speed}*t"
        elif direction == 'down':
            position = f"x=(w-text_w)/2:y={speed}*t"
        elif direction == 'left':
            position = f"x=w-{speed}*t:y=(h-text_h)/2"
        else:  # right
            position = f"x={speed}*t:y=(h-text_h)/2"
        
        filter_str = (
            f"drawtext=text='{text}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"{position}"
        )
        
        output_path = f'/tmp/text_scroll_{os.path.basename(video_path)}'
        result_path = self.add_text_overlay(video_path, output_path, text, filter_str)
        
        return {'video': {'type': 'file', 'value': result_path}}


# ==================== 特效节点 ====================

class GlitchEffectNode(WorkflowNode):
    """故障艺术特效"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        intensity = self.config.get('intensity', 0.1)
        
        # 故障效果：随机噪声 + RGB 通道偏移
        filter_str = (
            f"noise=alls={int(intensity * 100)}:allf=t+u,"
            f"split[a][b];"
            f"[a]lutrgb=r=val:g=0:b=0[r];"
            f"[b]lutrgb=r=0:g=val:b=val[gb];"
            f"[r][gb]blend=all_mode=addition"
        )
        
        output_path = f'/tmp/glitch_{os.path.basename(video_path)}'
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-filter_complex', filter_str,
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        return {'video': {'type': 'file', 'value': output_path}}


class ChromaKeyNode(WorkflowNode):
    """色度键（绿幕抠图）"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        background = self.inputs.get('background')
        
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        # 配置
        key_color = self.config.get('key_color', 'green')  # green, blue
        similarity = self.config.get('similarity', 0.3)
        blend = self.config.get('blend', 0.1)
        
        if key_color == 'green':
            filter_str = f"chromakey=0x00FF00:{similarity}:{blend}"
        else:  # blue
            filter_str = f"chromakey=0x0000FF:{similarity}:{blend}"
        
        output_path = f'/tmp/chromakey_{os.path.basename(video_path)}'
        
        if background:
            # 如果有背景，合成
            bg_path = background.get('value') if isinstance(background, dict) else background
            
            cmd = [
                'ffmpeg',
                '-i', bg_path,
                '-i', video_path,
                '-filter_complex',
                f"[1:v]{filter_str}[fg];[0:v][fg]overlay",
                '-c:a', 'copy',
                '-y', output_path
            ]
        else:
            # 只抠图
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', filter_str,
                '-c:a', 'copy',
                '-y', output_path
            ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        return {'video': {'type': 'file', 'value': output_path}}


class ParticleEffectNode(WorkflowNode):
    """粒子特效（雪花、雨滴等）"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        effect_type = self.config.get('effect_type', 'snow')  # snow, rain
        density = self.config.get('density', 0.01)
        
        if effect_type == 'snow':
            # 雪花效果
            filter_str = f"noise=alls=20:allf=t+u,threshold=0.95"
        else:  # rain
            # 雨滴效果
            filter_str = f"noise=alls=30:allf=t+u,threshold=0.98"
        
        output_path = f'/tmp/particle_{os.path.basename(video_path)}'
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        return {'video': {'type': 'file', 'value': output_path}}


class ZoomEffectNode(WorkflowNode):
    """缩放特效"""
    
    def execute(self) -> Dict[str, Any]:
        video = self.inputs.get('video')
        if not video:
            raise ValueError("未提供视频")
        
        video_path = video.get('value') if isinstance(video, dict) else video
        
        zoom_type = self.config.get('zoom_type', 'in')  # in, out
        duration = self.config.get('duration', 2)
        max_zoom = self.config.get('max_zoom', 1.5)
        
        if zoom_type == 'in':
            # 放大
            filter_str = f"zoompan=z='min(zoom+0.0015,{max_zoom})':d={duration * 25}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        else:
            # 缩小
            filter_str = f"zoompan=z='max(zoom-0.0015,1)':d={duration * 25}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        
        output_path = f'/tmp/zoom_{os.path.basename(video_path)}'
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        return {'video': {'type': 'file', 'value': output_path}}


# 更新节点类型映射
ADVANCED_NODE_TYPE_MAP = {
    # 滤镜
    'color_grading': ColorGradingNode,
    'vintage_filter': VintageFilterNode,
    'blur_filter': BlurFilterNode,
    'sharpen_filter': SharpenFilterNode,
    
    # 转场
    'fade_transition': FadeTransitionNode,
    'wipe_transition': WipeTransitionNode,
    'slide_transition': SlideTransitionNode,
    
    # 文字动画
    'text_fadein': FadeInTextNode,
    'text_typewriter': TypewriterTextNode,
    'text_scroll': ScrollingTextNode,
    
    # 特效
    'glitch_effect': GlitchEffectNode,
    'chroma_key': ChromaKeyNode,
    'particle_effect': ParticleEffectNode,
    'zoom_effect': ZoomEffectNode,
}
