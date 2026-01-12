"""
工作流执行引擎
负责解析和执行节点工作流
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


class WorkflowNode:
    """工作流节点基类"""
    
    def __init__(self, node_id: str, node_type: str, config: Dict):
        self.node_id = node_id
        self.node_type = node_type
        self.config = config
        self.inputs = {}
        self.outputs = {}
    
    def set_input(self, port_name: str, value: Any):
        """设置输入值"""
        self.inputs[port_name] = value
    
    def execute(self) -> Dict[str, Any]:
        """
        执行节点处理
        
        Returns:
            Dict: 输出结果 {port_name: value}
        """
        raise NotImplementedError
    
    def validate(self) -> bool:
        """验证节点配置和输入"""
        return True


class ImageInputNode(WorkflowNode):
    """图片输入节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行图片输入"""
        image_url = self.config.get('image_url')
        image_file = self.config.get('image_file')
        
        if image_url:
            return {'image': {'type': 'url', 'value': image_url}}
        elif image_file:
            return {'image': {'type': 'file', 'value': image_file}}
        else:
            raise ValueError("未提供图片URL或文件")


class VideoInputNode(WorkflowNode):
    """视频输入节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行视频输入"""
        video_url = self.config.get('video_url')
        video_file = self.config.get('video_file')
        
        if video_url:
            return {'video': {'type': 'url', 'value': video_url}}
        elif video_file:
            return {'video': {'type': 'file', 'value': video_file}}
        else:
            raise ValueError("未提供视频URL或文件")


class TextInputNode(WorkflowNode):
    """文字输入节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行文字输入"""
        text = self.config.get('text', '')
        max_length = self.config.get('max_length', 1000)
        
        if len(text) > max_length:
            text = text[:max_length]
        
        return {'text': text}


class AIImageGenerationNode(WorkflowNode):
    """AI 绘图节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行 AI 图片生成"""
        from core.ai_client.text2image_client import Text2ImageClient
        
        prompt = self.inputs.get('prompt', self.config.get('prompt', ''))
        
        if not prompt:
            raise ValueError("未提供生成提示词")
        
        # 获取配置
        model = self.config.get('model', 'stable-diffusion')
        width = self.config.get('width', 1024)
        height = self.config.get('height', 1024)
        
        # 调用 AI 生成
        client = Text2ImageClient()
        result = client.generate_image(
            prompt=prompt,
            width=width,
            height=height
        )
        
        return {'image': result}


class AIVideoGenerationNode(WorkflowNode):
    """AI 视频生成节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行 AI 视频生成"""
        from core.ai_client.image2video_client import Image2VideoClient
        
        image = self.inputs.get('image')
        prompt = self.inputs.get('prompt', self.config.get('prompt', ''))
        
        if not image:
            raise ValueError("未提供输入图片")
        
        # 获取配置
        duration = self.config.get('duration', 5)
        
        # 调用 AI 生成
        client = Image2VideoClient()
        result = client.generate_video(
            image_url=image.get('value') if isinstance(image, dict) else image,
            prompt=prompt,
            duration=duration
        )
        
        return {'video': result}


class LLMProcessNode(WorkflowNode):
    """LLM 处理节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行 LLM 处理"""
        from core.ai_client.openai_client import OpenAIClient
        
        text = self.inputs.get('text', '')
        prompt_template = self.config.get('prompt_template', '{text}')
        
        # 渲染提示词
        prompt = prompt_template.format(text=text)
        
        # 调用 LLM
        client = OpenAIClient()
        result = client.generate_text(prompt=prompt)
        
        return {'text': result}


class VideoMergeNode(WorkflowNode):
    """视频合并节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行视频合并"""
        from core.services.video_export_service import VideoExportService
        
        videos = self.inputs.get('videos', [])
        
        if not videos:
            raise ValueError("未提供要合并的视频")
        
        # 提取视频路径
        video_paths = [v.get('value') if isinstance(v, dict) else v for v in videos]
        
        # 合并视频
        export_service = VideoExportService()
        output_path = export_service.merge_videos(
            video_urls=video_paths,
            output_filename=f"merged_{datetime.now().timestamp()}"
        )
        
        return {'video': {'type': 'file', 'value': output_path}}


class AddSubtitlesNode(WorkflowNode):
    """添加字幕节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行添加字幕"""
        from core.services.stt_service import STTService
        from core.services.video_export_service import VideoExportService
        
        video = self.inputs.get('video')
        audio = self.inputs.get('audio')
        
        if not video:
            raise ValueError("未提供视频")
        
        # 如果有音频，识别生成字幕
        if audio:
            stt_service = STTService()
            audio_path = audio.get('value') if isinstance(audio, dict) else audio
            subtitles = stt_service.generate_subtitles(audio_path)
        else:
            # 使用配置的字幕
            subtitles = self.config.get('subtitles', [])
        
        # 添加字幕到视频
        video_path = video.get('value') if isinstance(video, dict) else video
        export_service = VideoExportService()
        
        output_path = export_service._add_subtitles(video_path, subtitles)
        
        return {'video': {'type': 'file', 'value': output_path}}


class AddMusicNode(WorkflowNode):
    """添加背景音乐节点"""
    
    def execute(self) -> Dict[str, Any]:
        """执行添加背景音乐"""
        from core.services.music_service import MusicService
        
        video = self.inputs.get('video')
        music = self.inputs.get('music', self.config.get('music'))
        
        if not video:
            raise ValueError("未提供视频")
        
        if not music:
            raise ValueError("未提供背景音乐")
        
        # 添加音乐
        music_service = MusicService()
        video_path = video.get('value') if isinstance(video, dict) else video
        music_path = music.get('value') if isinstance(music, dict) else music
        
        output_path = music_service.mixer.mix_audio_with_music(
            voice_path=video_path,  # 视频的音轨
            music_path=music_path,
            output_path=f"output_{datetime.now().timestamp()}.mp4",
            music_volume=self.config.get('volume', 0.3)
        )
        
        return {'video': {'type': 'file', 'value': output_path}}


# 节点类型映射（基础节点）
NODE_TYPE_MAP = {
    'image_input': ImageInputNode,
    'video_input': VideoInputNode,
    'text_input': TextInputNode,
    'ai_image': AIImageGenerationNode,
    'ai_video': AIVideoGenerationNode,
    'llm_process': LLMProcessNode,
    'video_merge': VideoMergeNode,
    'add_subtitles': AddSubtitlesNode,
    'add_music': AddMusicNode,
}


def get_all_node_types():
    """获取所有节点类型（包括高级节点）"""
    try:
        from core.workflow.advanced_nodes import ADVANCED_NODE_TYPE_MAP
        return {**NODE_TYPE_MAP, **ADVANCED_NODE_TYPE_MAP}
    except ImportError:
        return NODE_TYPE_MAP


class WorkflowEngine:
    """工作流执行引擎"""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.execution_order = []
        self.results = {}
    
    def load_workflow(self, workflow_data: Dict):
        """
        加载工作流数据
        
        Args:
            workflow_data: 工作流数据
        """
        # 获取所有可用节点类型
        all_node_types = get_all_node_types()
        
        # 创建节点实例
        for node_data in workflow_data.get('nodes', []):
            node_id = node_data['id']
            node_type = node_data['type']
            config = node_data.get('data', {}).get('config', {})
            
            # 创建节点实例
            node_class = all_node_types.get(node_type)
            if node_class:
                self.nodes[node_id] = node_class(node_id, node_type, config)
            else:
                logger.warning(f"未知节点类型: {node_type}")
        
        # 保存边
        self.edges = workflow_data.get('edges', [])
        
        # 计算执行顺序（拓扑排序）
        self.execution_order = self._topological_sort()
    
    def _topological_sort(self) -> List[str]:
        """
        拓扑排序计算执行顺序
        
        Returns:
            List[str]: 节点ID列表（执行顺序）
        """
        # 构建依赖图
        in_degree = {node_id: 0 for node_id in self.nodes}
        adjacency = {node_id: [] for node_id in self.nodes}
        
        for edge in self.edges:
            source = edge['source']
            target = edge['target']
            
            if source in self.nodes and target in self.nodes:
                adjacency[source].append(target)
                in_degree[target] += 1
        
        # 拓扑排序
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for neighbor in adjacency[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 检查是否有环
        if len(result) != len(self.nodes):
            raise ValueError("工作流存在循环依赖")
        
        return result
    
    def execute(self, callback=None) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            callback: 进度回调函数 callback(node_id, status, result)
            
        Returns:
            Dict: 执行结果
        """
        try:
            total_nodes = len(self.execution_order)
            
            for i, node_id in enumerate(self.execution_order):
                node = self.nodes[node_id]
                
                logger.info(f"执行节点 {i+1}/{total_nodes}: {node_id} ({node.node_type})")
                
                # 通知开始
                if callback:
                    callback(node_id, 'running', None)
                
                # 设置输入（从前置节点获取）
                self._set_node_inputs(node)
                
                # 验证节点
                if not node.validate():
                    raise ValueError(f"节点验证失败: {node_id}")
                
                # 执行节点
                try:
                    outputs = node.execute()
                    self.results[node_id] = {
                        'status': 'completed',
                        'outputs': outputs,
                        'timestamp': timezone.now().isoformat()
                    }
                    
                    # 通知完成
                    if callback:
                        callback(node_id, 'completed', outputs)
                    
                except Exception as e:
                    error_msg = f"节点执行失败: {str(e)}"
                    logger.error(f"{node_id}: {error_msg}")
                    
                    self.results[node_id] = {
                        'status': 'failed',
                        'error': error_msg,
                        'timestamp': timezone.now().isoformat()
                    }
                    
                    # 通知失败
                    if callback:
                        callback(node_id, 'failed', {'error': error_msg})
                    
                    raise
            
            return {
                'status': 'completed',
                'results': self.results
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'results': self.results
            }
    
    def _set_node_inputs(self, node: WorkflowNode):
        """设置节点输入"""
        # 查找连接到此节点的边
        for edge in self.edges:
            if edge['target'] == node.node_id:
                source_node_id = edge['source']
                source_port = edge.get('sourceHandle', 'output')
                target_port = edge.get('targetHandle', 'input')
                
                # 获取源节点的输出
                if source_node_id in self.results:
                    source_outputs = self.results[source_node_id].get('outputs', {})
                    
                    # 设置输入值
                    if source_port in source_outputs:
                        node.set_input(target_port, source_outputs[source_port])
    
    def get_node_result(self, node_id: str) -> Optional[Dict]:
        """获取节点执行结果"""
        return self.results.get(node_id)
    
    def get_final_outputs(self) -> Dict[str, Any]:
        """获取最终输出（最后一个节点的输出）"""
        if not self.execution_order:
            return {}
        
        last_node_id = self.execution_order[-1]
        result = self.results.get(last_node_id, {})
        
        return result.get('outputs', {})
