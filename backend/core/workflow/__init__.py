"""
工作流引擎模块
"""

from .workflow_engine import (
    WorkflowEngine,
    WorkflowNode,
    ImageInputNode,
    VideoInputNode,
    TextInputNode,
    AIImageGenerationNode,
    AIVideoGenerationNode,
    LLMProcessNode,
    VideoMergeNode,
    AddSubtitlesNode,
    AddMusicNode,
    NODE_TYPE_MAP,
    get_all_node_types
)

from .advanced_nodes import (
    ColorGradingNode,
    VintageFilterNode,
    BlurFilterNode,
    SharpenFilterNode,
    FadeTransitionNode,
    WipeTransitionNode,
    SlideTransitionNode,
    FadeInTextNode,
    TypewriterTextNode,
    ScrollingTextNode,
    GlitchEffectNode,
    ChromaKeyNode,
    ParticleEffectNode,
    ZoomEffectNode,
    ADVANCED_NODE_TYPE_MAP
)

# 合并所有节点类型
ALL_NODE_TYPES = {**NODE_TYPE_MAP, **ADVANCED_NODE_TYPE_MAP}

__all__ = [
    'WorkflowEngine',
    'WorkflowNode',
    'ALL_NODE_TYPES',
    'NODE_TYPE_MAP',
    'ADVANCED_NODE_TYPE_MAP',
    'get_all_node_types'
]
