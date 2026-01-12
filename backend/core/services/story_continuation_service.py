"""
故事续写和编辑服务
提供故事续写、局部修改、结局调整等功能
"""

import logging
from typing import Dict, List, Any, Optional
from core.ai_client.improved_llm_client import ImprovedLLMClient
from core.utils.validators import input_validator
from config.llm_config import llm_config

logger = logging.getLogger('ai_story.continuation')


class StoryContinuationService:
    """故事续写服务"""
    
    def __init__(self, llm_client: ImprovedLLMClient = None):
        """
        初始化续写服务
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client or ImprovedLLMClient(
            provider='openai',
            model='gpt-3.5-turbo'
        )
    
    def continue_story(
        self,
        existing_story: str,
        continuation_prompt: str = None,
        target_length: int = 500,
        maintain_style: bool = True,
        **kwargs
    ) -> str:
        """
        续写故事
        
        Args:
            existing_story: 现有故事内容
            continuation_prompt: 续写方向提示
            target_length: 续写目标长度
            maintain_style: 是否保持原有风格
            **kwargs: 其他参数
        
        Returns:
            续写的内容
        """
        # 验证输入
        validated_story = input_validator.validate_text_input(
            existing_story,
            field_name="原故事",
            min_length=50,
            max_length=10000,
        )
        
        # 构建续写提示词
        prompt_parts = []
        prompt_parts.append("请为以下故事续写内容：\n")
        prompt_parts.append(f"原故事：\n{validated_story}\n")
        
        if continuation_prompt:
            prompt_parts.append(f"\n续写方向：{continuation_prompt}")
        
        prompt_parts.append(f"\n续写要求：")
        prompt_parts.append(f"1. 续写长度约{target_length}字")
        
        if maintain_style:
            prompt_parts.append("2. 保持原故事的风格、语气和叙事方式")
            prompt_parts.append("3. 确保情节连贯，角色行为一致")
        
        prompt_parts.append("4. 续写内容应该自然衔接原故事")
        prompt_parts.append("5. 保持故事的逻辑性和可读性")
        
        prompt = '\n'.join(prompt_parts)
        
        # 调用LLM生成续写
        continuation = self.llm_client.generate(
            prompt=prompt,
            stage_type='storyboard',  # 使用storyboard阶段的配置
            **kwargs
        )
        
        return continuation
    
    def modify_section(
        self,
        story: str,
        section_to_modify: str,
        modification_instruction: str,
        **kwargs
    ) -> str:
        """
        修改故事的特定部分
        
        Args:
            story: 完整故事
            section_to_modify: 要修改的部分（可以是关键词或描述）
            modification_instruction: 修改指令
            **kwargs: 其他参数
        
        Returns:
            修改后的完整故事
        """
        prompt_parts = []
        prompt_parts.append("请修改以下故事的特定部分：\n")
        prompt_parts.append(f"完整故事：\n{story}\n")
        prompt_parts.append(f"\n要修改的部分：{section_to_modify}")
        prompt_parts.append(f"修改指令：{modification_instruction}")
        prompt_parts.append("\n修改要求：")
        prompt_parts.append("1. 只修改指定的部分，其他内容保持不变")
        prompt_parts.append("2. 确保修改后的内容与前后文自然衔接")
        prompt_parts.append("3. 保持故事的整体风格和逻辑")
        prompt_parts.append("4. 返回修改后的完整故事")
        
        prompt = '\n'.join(prompt_parts)
        
        modified_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        return modified_story
    
    def change_ending(
        self,
        story: str,
        new_ending_direction: str,
        **kwargs
    ) -> str:
        """
        修改故事结局
        
        Args:
            story: 完整故事
            new_ending_direction: 新结局的方向
            **kwargs: 其他参数
        
        Returns:
            修改结局后的完整故事
        """
        prompt_parts = []
        prompt_parts.append("请修改以下故事的结局：\n")
        prompt_parts.append(f"原故事：\n{story}\n")
        prompt_parts.append(f"\n新结局方向：{new_ending_direction}")
        prompt_parts.append("\n修改要求：")
        prompt_parts.append("1. 保持故事开头和中间部分不变")
        prompt_parts.append("2. 从合适的转折点开始修改，自然过渡到新结局")
        prompt_parts.append("3. 确保新结局逻辑合理，与前文呼应")
        prompt_parts.append("4. 保持故事的整体风格")
        prompt_parts.append("5. 返回修改后的完整故事")
        
        prompt = '\n'.join(prompt_parts)
        
        modified_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        return modified_story
    
    def adjust_character_behavior(
        self,
        story: str,
        character_name: str,
        behavior_adjustment: str,
        **kwargs
    ) -> str:
        """
        调整角色行为
        
        Args:
            story: 完整故事
            character_name: 角色名称
            behavior_adjustment: 行为调整说明
            **kwargs: 其他参数
        
        Returns:
            调整后的完整故事
        """
        prompt_parts = []
        prompt_parts.append("请调整故事中角色的行为：\n")
        prompt_parts.append(f"原故事：\n{story}\n")
        prompt_parts.append(f"\n角色名称：{character_name}")
        prompt_parts.append(f"行为调整：{behavior_adjustment}")
        prompt_parts.append("\n调整要求：")
        prompt_parts.append(f"1. 修改{character_name}的相关行为和对话")
        prompt_parts.append("2. 确保角色性格保持一致")
        prompt_parts.append("3. 调整后的行为应该更加合理或符合要求")
        prompt_parts.append("4. 保持故事的整体逻辑和其他角色不变")
        prompt_parts.append("5. 返回调整后的完整故事")
        
        prompt = '\n'.join(prompt_parts)
        
        modified_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        return modified_story
    
    def expand_scene(
        self,
        story: str,
        scene_description: str,
        expansion_length: int = 300,
        **kwargs
    ) -> str:
        """
        扩展特定场景
        
        Args:
            story: 完整故事
            scene_description: 要扩展的场景描述
            expansion_length: 扩展长度
            **kwargs: 其他参数
        
        Returns:
            扩展后的完整故事
        """
        prompt_parts = []
        prompt_parts.append("请扩展故事中的特定场景：\n")
        prompt_parts.append(f"原故事：\n{story}\n")
        prompt_parts.append(f"\n要扩展的场景：{scene_description}")
        prompt_parts.append(f"扩展长度：约{expansion_length}字")
        prompt_parts.append("\n扩展要求：")
        prompt_parts.append("1. 增加场景的细节描写")
        prompt_parts.append("2. 丰富角色的对话和心理活动")
        prompt_parts.append("3. 保持场景与前后文的连贯性")
        prompt_parts.append("4. 不改变故事的主要情节")
        prompt_parts.append("5. 返回扩展后的完整故事")
        
        prompt = '\n'.join(prompt_parts)
        
        expanded_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='storyboard',
            **kwargs
        )
        
        return expanded_story
    
    def merge_stories(
        self,
        story1: str,
        story2: str,
        merge_instruction: str = None,
        **kwargs
    ) -> str:
        """
        合并两个故事
        
        Args:
            story1: 第一个故事
            story2: 第二个故事
            merge_instruction: 合并指令
            **kwargs: 其他参数
        
        Returns:
            合并后的故事
        """
        prompt_parts = []
        prompt_parts.append("请将以下两个故事合并为一个完整的故事：\n")
        prompt_parts.append(f"故事1：\n{story1}\n")
        prompt_parts.append(f"\n故事2：\n{story2}\n")
        
        if merge_instruction:
            prompt_parts.append(f"\n合并方式：{merge_instruction}")
        
        prompt_parts.append("\n合并要求：")
        prompt_parts.append("1. 找到两个故事的共同点或连接点")
        prompt_parts.append("2. 自然地将两个故事融合在一起")
        prompt_parts.append("3. 确保合并后的故事逻辑连贯")
        prompt_parts.append("4. 保持统一的叙事风格")
        prompt_parts.append("5. 创造一个完整的故事结构")
        
        prompt = '\n'.join(prompt_parts)
        
        merged_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='storyboard',
            **kwargs
        )
        
        return merged_story
    
    def create_alternative_version(
        self,
        story: str,
        variation_type: str = 'plot',
        **kwargs
    ) -> str:
        """
        创建故事的替代版本
        
        Args:
            story: 原故事
            variation_type: 变化类型 (plot/character/setting/tone)
            **kwargs: 其他参数
        
        Returns:
            替代版本的故事
        """
        variation_instructions = {
            'plot': '改变主要情节发展，但保持角色和背景设定',
            'character': '改变主要角色的性格或动机，但保持情节框架',
            'setting': '改变故事发生的时间或地点，但保持核心情节',
            'tone': '改变故事的整体氛围和语气，但保持情节内容',
        }
        
        instruction = variation_instructions.get(variation_type, variation_instructions['plot'])
        
        prompt_parts = []
        prompt_parts.append("请创建以下故事的替代版本：\n")
        prompt_parts.append(f"原故事：\n{story}\n")
        prompt_parts.append(f"\n变化要求：{instruction}")
        prompt_parts.append("\n创作要求：")
        prompt_parts.append("1. 保持故事的基本框架")
        prompt_parts.append("2. 根据变化类型进行创新")
        prompt_parts.append("3. 确保新版本同样精彩")
        prompt_parts.append("4. 保持故事的完整性和可读性")
        
        prompt = '\n'.join(prompt_parts)
        
        alternative_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        return alternative_story


class StoryEditingService:
    """故事编辑服务"""
    
    def __init__(self, llm_client: ImprovedLLMClient = None):
        self.llm_client = llm_client or ImprovedLLMClient(
            provider='openai',
            model='gpt-3.5-turbo'
        )
    
    def polish_language(
        self,
        story: str,
        focus_areas: List[str] = None,
        **kwargs
    ) -> str:
        """
        润色语言
        
        Args:
            story: 原故事
            focus_areas: 重点润色区域 (grammar/vocabulary/flow/description)
            **kwargs: 其他参数
        
        Returns:
            润色后的故事
        """
        focus_areas = focus_areas or ['grammar', 'vocabulary', 'flow']
        
        focus_descriptions = {
            'grammar': '修正语法错误，确保句子通顺',
            'vocabulary': '使用更丰富、更准确的词汇',
            'flow': '改善句子和段落之间的流畅性',
            'description': '增强描写的生动性和形象性',
        }
        
        prompt_parts = []
        prompt_parts.append("请润色以下故事的语言：\n")
        prompt_parts.append(f"原故事：\n{story}\n")
        prompt_parts.append("\n润色重点：")
        
        for area in focus_areas:
            if area in focus_descriptions:
                prompt_parts.append(f"- {focus_descriptions[area]}")
        
        prompt_parts.append("\n润色要求：")
        prompt_parts.append("1. 保持故事的原意和情节")
        prompt_parts.append("2. 提升语言的质量和可读性")
        prompt_parts.append("3. 保持故事的风格和语气")
        prompt_parts.append("4. 不添加或删除重要内容")
        
        prompt = '\n'.join(prompt_parts)
        
        polished_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        return polished_story
    
    def adjust_length(
        self,
        story: str,
        target_length: int,
        preserve_key_elements: bool = True,
        **kwargs
    ) -> str:
        """
        调整故事长度
        
        Args:
            story: 原故事
            target_length: 目标长度
            preserve_key_elements: 是否保留关键元素
            **kwargs: 其他参数
        
        Returns:
            调整后的故事
        """
        current_length = len(story)
        action = "扩展" if target_length > current_length else "压缩"
        
        prompt_parts = []
        prompt_parts.append(f"请{action}以下故事到约{target_length}字：\n")
        prompt_parts.append(f"原故事（{current_length}字）：\n{story}\n")
        prompt_parts.append(f"\n{action}要求：")
        
        if target_length > current_length:
            prompt_parts.append("1. 增加细节描写和场景刻画")
            prompt_parts.append("2. 丰富角色的对话和心理活动")
            prompt_parts.append("3. 扩展关键情节")
        else:
            prompt_parts.append("1. 删除冗余的描述和重复内容")
            prompt_parts.append("2. 保留核心情节和关键对话")
            prompt_parts.append("3. 简化次要场景")
        
        if preserve_key_elements:
            prompt_parts.append("4. 保留所有关键情节和角色")
        
        prompt_parts.append("5. 保持故事的完整性和可读性")
        
        prompt = '\n'.join(prompt_parts)
        
        adjusted_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        return adjusted_story
    
    def translate_style(
        self,
        story: str,
        target_style: str,
        **kwargs
    ) -> str:
        """
        转换故事风格
        
        Args:
            story: 原故事
            target_style: 目标风格
            **kwargs: 其他参数
        
        Returns:
            转换风格后的故事
        """
        prompt_parts = []
        prompt_parts.append("请将以下故事转换为指定风格：\n")
        prompt_parts.append(f"原故事：\n{story}\n")
        prompt_parts.append(f"\n目标风格：{target_style}")
        prompt_parts.append("\n转换要求：")
        prompt_parts.append("1. 保持故事的核心情节不变")
        prompt_parts.append("2. 调整叙事方式、语气和用词")
        prompt_parts.append("3. 确保新风格贯穿整个故事")
        prompt_parts.append("4. 保持故事的逻辑性和可读性")
        
        prompt = '\n'.join(prompt_parts)
        
        styled_story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        return styled_story


# 导出服务实例
story_continuation_service = StoryContinuationService()
story_editing_service = StoryEditingService()
