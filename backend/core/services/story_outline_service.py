"""
故事大纲生成服务
实现结构化大纲生成和基于大纲的故事创作
"""

import logging
from typing import Dict, List, Any, Optional
from core.ai_client.improved_llm_client import ImprovedLLMClient
from config.story_templates import story_template_config
from core.utils.validators import input_validator

logger = logging.getLogger('ai_story.outline')


class StoryOutlineService:
    """故事大纲生成服务"""
    
    def __init__(self, llm_client: ImprovedLLMClient = None):
        self.llm_client = llm_client or ImprovedLLMClient(
            provider='openai',
            model='gpt-3.5-turbo'
        )
    
    def generate_outline(
        self,
        topic: str,
        age_group: str = 'elementary',
        genre: str = 'fairy_tale',
        style: str = 'warm_healing',
        word_count: int = 800,
        character_count: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成故事大纲
        
        Args:
            topic: 故事主题
            age_group: 年龄段
            genre: 题材
            style: 风格
            word_count: 目标字数
            character_count: 角色数量
        
        Returns:
            {
                'theme': '主题',
                'characters': [角色列表],
                'plot_points': {
                    'opening': '开端',
                    'development': '发展',
                    'climax': '高潮',
                    'resolution': '结局'
                },
                'estimated_length': 字数,
                'tone': '基调',
                'setting': '背景设定'
            }
        """
        # 验证输入
        validated_topic = input_validator.validate_text_input(
            topic,
            field_name="主题",
            min_length=2,
            max_length=100
        )
        
        # 构建大纲生成提示词
        prompt = self._build_outline_prompt(
            topic=validated_topic,
            age_group=age_group,
            genre=genre,
            style=style,
            word_count=word_count,
            character_count=character_count
        )
        
        # 调用LLM生成大纲
        outline_text = self.llm_client.generate(
            prompt=prompt,
            stage_type='storyboard',
            temperature=0.8,
            **kwargs
        )
        
        # 解析大纲
        outline = self._parse_outline(outline_text)
        
        # 补充元数据
        outline['topic'] = validated_topic
        outline['age_group'] = age_group
        outline['genre'] = genre
        outline['style'] = style
        outline['estimated_length'] = word_count
        
        return outline
    
    def generate_from_outline(
        self,
        outline: Dict[str, Any],
        expand_level: str = 'detailed',
        **kwargs
    ) -> str:
        """
        基于大纲生成完整故事
        
        Args:
            outline: 故事大纲
            expand_level: 扩展级别 (brief/normal/detailed)
        
        Returns:
            完整故事文本
        """
        # 构建生成提示词
        prompt = self._build_story_from_outline_prompt(outline, expand_level)
        
        # 调用LLM生成故事
        story = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            temperature=0.7,
            max_tokens=outline.get('estimated_length', 800) * 2,
            **kwargs
        )
        
        return story
    
    def refine_outline_section(
        self,
        outline: Dict[str, Any],
        section: str,
        refinement_instruction: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        优化大纲的某个部分
        
        Args:
            outline: 原始大纲
            section: 要优化的部分 (opening/development/climax/resolution/characters)
            refinement_instruction: 优化指令
        
        Returns:
            优化后的大纲
        """
        prompt = f"""
请优化以下故事大纲的{section}部分：

当前大纲：
{self._format_outline_for_display(outline)}

优化要求：
{refinement_instruction}

请只返回优化后的{section}部分内容，保持与原大纲风格一致。
"""
        
        refined_content = self.llm_client.generate(
            prompt=prompt,
            stage_type='rewrite',
            **kwargs
        )
        
        # 更新大纲
        refined_outline = outline.copy()
        if section == 'characters':
            refined_outline['characters'] = self._parse_characters(refined_content)
        elif section in ['opening', 'development', 'climax', 'resolution']:
            refined_outline['plot_points'][section] = refined_content
        
        return refined_outline
    
    def _build_outline_prompt(
        self,
        topic: str,
        age_group: str,
        genre: str,
        style: str,
        word_count: int,
        character_count: int
    ) -> str:
        """构建大纲生成提示词"""
        
        genre_template = story_template_config.get_genre(genre)
        style_config = story_template_config.get_style(style)
        age_config = story_template_config.get_age_group(age_group)
        
        prompt = f"""
请为以下故事创作一个详细的结构化大纲：

主题：{topic}
目标读者：{age_config.description if age_config else age_group}
题材：{genre_template.name if genre_template else genre}
风格：{style_config.name if style_config else style}
目标字数：{word_count}字
角色数量：{character_count}个

请按以下格式输出大纲：

## 主题
[一句话概括故事的核心主题]

## 背景设定
[故事发生的时间、地点、世界观]

## 角色
"""
        
        for i in range(character_count):
            prompt += f"""
### 角色{i+1}
- 名称：[角色名字]
- 类型：[主角/配角/反派等]
- 性格：[性格特征]
- 目标：[角色的目标或动机]
"""
        
        prompt += """
## 情节结构

### 开端（约25%）
[介绍主角、建立背景、引出冲突]

### 发展（约50%）
[冲突升级、主角努力、遇到挫折、关键转折]

### 高潮（约15%）
[最激烈的冲突、关键决策、紧张时刻]

### 结局（约10%）
[问题解决、主题升华、结局]

## 情感基调
[整体情感氛围]

## 核心价值观
[故事要传递的价值观或教育意义]
"""
        
        return prompt
    
    def _build_story_from_outline_prompt(
        self,
        outline: Dict[str, Any],
        expand_level: str
    ) -> str:
        """构建基于大纲生成故事的提示词"""
        
        expansion_instructions = {
            'brief': '简洁地叙述，突出核心情节',
            'normal': '适度展开，包含必要的细节描写',
            'detailed': '详细展开，丰富场景描写、对话和心理活动'
        }
        
        prompt = f"""
请根据以下故事大纲，创作一个完整的故事：

{self._format_outline_for_display(outline)}

创作要求：
1. 严格遵循大纲的情节结构和角色设定
2. 扩展方式：{expansion_instructions.get(expand_level, expansion_instructions['normal'])}
3. 目标字数：约{outline.get('estimated_length', 800)}字
4. 保持{outline.get('style', '温馨')}的风格
5. 适合{outline.get('age_group', '小学生')}阅读
6. 语言流畅，情节连贯，符合逻辑

请直接输出完整故事，不要包含大纲标题。
"""
        
        return prompt
    
    def _parse_outline(self, outline_text: str) -> Dict[str, Any]:
        """解析LLM生成的大纲文本"""
        
        outline = {
            'theme': '',
            'setting': '',
            'characters': [],
            'plot_points': {
                'opening': '',
                'development': '',
                'climax': '',
                'resolution': ''
            },
            'tone': '',
            'core_values': ''
        }
        
        # 简单的文本解析（实际项目中可以使用更复杂的解析逻辑）
        lines = outline_text.split('\n')
        current_section = None
        current_character = None
        
        for line in lines:
            line = line.strip()
            
            if '## 主题' in line or line.startswith('主题：'):
                current_section = 'theme'
            elif '## 背景设定' in line or line.startswith('背景设定：'):
                current_section = 'setting'
            elif '## 角色' in line:
                current_section = 'characters'
            elif '### 开端' in line or '开端' in line:
                current_section = 'opening'
            elif '### 发展' in line or '发展' in line:
                current_section = 'development'
            elif '### 高潮' in line or '高潮' in line:
                current_section = 'climax'
            elif '### 结局' in line or '结局' in line:
                current_section = 'resolution'
            elif '## 情感基调' in line or line.startswith('情感基调：'):
                current_section = 'tone'
            elif '## 核心价值观' in line or line.startswith('核心价值观：'):
                current_section = 'core_values'
            elif line.startswith('### 角色'):
                current_character = {}
                outline['characters'].append(current_character)
            elif current_character is not None and line.startswith('- '):
                key_value = line[2:].split('：', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    current_character[key.lower()] = value
            elif line and current_section:
                if current_section in ['theme', 'setting', 'tone', 'core_values']:
                    outline[current_section] += line + ' '
                elif current_section in ['opening', 'development', 'climax', 'resolution']:
                    outline['plot_points'][current_section] += line + ' '
        
        # 清理空白
        for key in ['theme', 'setting', 'tone', 'core_values']:
            outline[key] = outline[key].strip()
        
        for key in outline['plot_points']:
            outline['plot_points'][key] = outline['plot_points'][key].strip()
        
        return outline
    
    def _parse_characters(self, text: str) -> List[Dict[str, str]]:
        """解析角色文本"""
        characters = []
        current_char = None
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('### 角色') or line.startswith('角色'):
                if current_char:
                    characters.append(current_char)
                current_char = {}
            elif current_char is not None and line.startswith('- '):
                key_value = line[2:].split('：', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    current_char[key.lower()] = value
        
        if current_char:
            characters.append(current_char)
        
        return characters
    
    def _format_outline_for_display(self, outline: Dict[str, Any]) -> str:
        """格式化大纲用于显示"""
        
        formatted = f"""
主题：{outline.get('theme', '')}

背景设定：{outline.get('setting', '')}

角色：
"""
        
        for i, char in enumerate(outline.get('characters', []), 1):
            formatted += f"\n角色{i}：\n"
            for key, value in char.items():
                formatted += f"  - {key}：{value}\n"
        
        formatted += f"""
情节结构：

开端：
{outline.get('plot_points', {}).get('opening', '')}

发展：
{outline.get('plot_points', {}).get('development', '')}

高潮：
{outline.get('plot_points', {}).get('climax', '')}

结局：
{outline.get('plot_points', {}).get('resolution', '')}

情感基调：{outline.get('tone', '')}

核心价值观：{outline.get('core_values', '')}
"""
        
        return formatted


# 导出服务实例
story_outline_service = StoryOutlineService()
