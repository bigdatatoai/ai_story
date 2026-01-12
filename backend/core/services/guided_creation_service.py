"""
引导式创作服务
为儿童提供故事接龙、剧情选择等引导式创作功能
"""

import logging
from typing import Dict, List, Any, Optional
from core.ai_client.improved_llm_client import ImprovedLLMClient

logger = logging.getLogger('ai_story.guided')


class GuidedCreationService:
    """引导式创作服务"""
    
    def __init__(self, llm_client: ImprovedLLMClient = None):
        self.llm_client = llm_client or ImprovedLLMClient(
            provider='openai',
            model='gpt-3.5-turbo'
        )
    
    def start_story_chain(
        self,
        topic: str,
        age_group: str = 'elementary',
        **kwargs
    ) -> Dict[str, Any]:
        """
        开始故事接龙
        
        Args:
            topic: 故事主题
            age_group: 年龄段
        
        Returns:
            {
                'chain_id': '接龙ID',
                'first_sentence': 'AI生成的第一句',
                'next_prompt': '给孩子的提示',
                'suggestions': ['建议1', '建议2', '建议3']
            }
        """
        # 生成开场句
        prompt = f"""
请为主题"{topic}"写一个吸引人的故事开头，要求：
1. 只写一句话
2. 适合{age_group}年龄段的孩子
3. 引发好奇心，让孩子想继续故事
4. 使用简单易懂的词汇

直接输出开头句子，不要其他内容。
"""
        
        first_sentence = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            temperature=0.8,
            max_tokens=100,
            **kwargs
        )
        
        # 生成建议
        suggestions = self._generate_continuation_suggestions(
            first_sentence,
            age_group
        )
        
        return {
            'chain_id': self._generate_chain_id(),
            'first_sentence': first_sentence.strip(),
            'next_prompt': '接下来会发生什么呢？你来写下一句吧！',
            'suggestions': suggestions
        }
    
    def continue_chain(
        self,
        chain_id: str,
        previous_content: str,
        child_input: str,
        age_group: str = 'elementary',
        **kwargs
    ) -> Dict[str, Any]:
        """
        继续故事接龙
        
        Args:
            chain_id: 接龙ID
            previous_content: 之前的故事内容
            child_input: 孩子的输入
            age_group: 年龄段
        
        Returns:
            {
                'ai_continuation': 'AI续写的内容',
                'next_prompt': '下一个提示',
                'suggestions': ['建议列表']
            }
        """
        # AI基于孩子的输入续写
        prompt = f"""
故事到目前为止：
{previous_content}

孩子写的内容：
{child_input}

请基于孩子的想法，自然地续写2-3句话，要求：
1. 承接孩子的创意
2. 适合{age_group}年龄段
3. 推动故事发展
4. 保持趣味性

直接输出续写内容。
"""
        
        ai_continuation = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            temperature=0.7,
            max_tokens=200,
            **kwargs
        )
        
        # 生成新的建议
        full_story = f"{previous_content}\n{child_input}\n{ai_continuation}"
        suggestions = self._generate_continuation_suggestions(
            full_story,
            age_group
        )
        
        return {
            'ai_continuation': ai_continuation.strip(),
            'next_prompt': '故事越来越精彩了！你想让主角做什么呢？',
            'suggestions': suggestions
        }
    
    def offer_plot_choices(
        self,
        current_story: str,
        age_group: str = 'elementary',
        num_choices: int = 3,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        提供剧情分支选择
        
        Args:
            current_story: 当前故事
            age_group: 年龄段
            num_choices: 选项数量
        
        Returns:
            [
                {'id': 'A', 'description': '选项描述', 'preview': '预览'},
                ...
            ]
        """
        prompt = f"""
当前故事：
{current_story}

请为这个故事提供{num_choices}个不同的剧情发展方向，要求：
1. 每个方向都有趣且合理
2. 适合{age_group}年龄段
3. 给出简短描述（20字内）

格式：
A: [描述]
B: [描述]
C: [描述]
"""
        
        choices_text = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            temperature=0.9,
            max_tokens=300,
            **kwargs
        )
        
        # 解析选项
        choices = self._parse_plot_choices(choices_text)
        
        # 为每个选项生成预览
        for choice in choices:
            choice['preview'] = self._generate_choice_preview(
                current_story,
                choice['description'],
                age_group
            )
        
        return choices
    
    def apply_plot_choice(
        self,
        current_story: str,
        choice_id: str,
        choice_description: str,
        age_group: str = 'elementary',
        **kwargs
    ) -> str:
        """
        应用剧情选择，生成后续内容
        
        Args:
            current_story: 当前故事
            choice_id: 选择的ID
            choice_description: 选择的描述
            age_group: 年龄段
        
        Returns:
            续写的故事内容
        """
        prompt = f"""
故事到目前为止：
{current_story}

孩子选择的剧情方向：
{choice_description}

请基于这个选择，续写2-3段故事内容，要求：
1. 符合选择的方向
2. 适合{age_group}年龄段
3. 情节生动有趣
4. 保持故事连贯性

直接输出续写内容。
"""
        
        continuation = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            temperature=0.7,
            max_tokens=500,
            **kwargs
        )
        
        return continuation.strip()
    
    def _generate_continuation_suggestions(
        self,
        current_story: str,
        age_group: str
    ) -> List[str]:
        """生成续写建议"""
        prompt = f"""
当前故事：
{current_story}

请为{age_group}年龄段的孩子提供3个简短的续写建议（每个10字内），帮助他们继续故事。

格式：
1. [建议]
2. [建议]
3. [建议]
"""
        
        suggestions_text = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            temperature=0.8,
            max_tokens=150
        )
        
        # 解析建议
        suggestions = []
        for line in suggestions_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                suggestion = line.split('.', 1)[-1].split(':', 1)[-1].strip()
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions[:3]
    
    def _parse_plot_choices(self, text: str) -> List[Dict[str, str]]:
        """解析剧情选项"""
        choices = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # 匹配 "A: 描述" 格式
            if ':' in line and len(line) > 2:
                parts = line.split(':', 1)
                choice_id = parts[0].strip()
                description = parts[1].strip()
                
                choices.append({
                    'id': choice_id,
                    'description': description,
                    'preview': ''
                })
        
        return choices
    
    def _generate_choice_preview(
        self,
        current_story: str,
        choice_description: str,
        age_group: str
    ) -> str:
        """生成选项预览"""
        prompt = f"""
故事：{current_story[-100:]}

如果选择：{choice_description}

请用一句话（15字内）预览这个选择会带来什么结果。
"""
        
        preview = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            temperature=0.7,
            max_tokens=50
        )
        
        return preview.strip()
    
    def _generate_chain_id(self) -> str:
        """生成接龙ID"""
        import uuid
        return str(uuid.uuid4())


# 导出服务实例
guided_creation_service = GuidedCreationService()
