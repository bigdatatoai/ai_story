"""
故事模板配置
提供年龄段、题材、风格的预设模板
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class AgeGroupConfig:
    """年龄段配置"""
    name: str
    min_age: int
    max_age: int
    vocabulary_level: str  # simple/medium/complex
    sentence_length: str  # short/medium/long
    theme_restrictions: List[str]  # 主题限制
    word_count_range: tuple  # (min, max)
    description: str


@dataclass
class GenreTemplate:
    """题材模板"""
    name: str
    description: str
    key_elements: List[str]  # 关键元素
    structure: Dict[str, str]  # 故事结构
    tone: str  # 语气风格
    suitable_ages: List[str]  # 适合年龄段
    example_prompts: List[str]  # 示例提示词


@dataclass
class StoryStyle:
    """故事风格"""
    name: str
    description: str
    characteristics: List[str]  # 特征
    keywords: List[str]  # 关键词
    avoid_keywords: List[str]  # 避免的关键词


class StoryTemplateConfig:
    """故事模板配置类"""
    
    # ==================== 年龄段配置 ====================
    AGE_GROUPS = {
        'preschool': AgeGroupConfig(
            name='学龄前儿童',
            min_age=3,
            max_age=6,
            vocabulary_level='simple',
            sentence_length='short',
            theme_restrictions=['violence', 'horror', 'complex_emotions'],
            word_count_range=(200, 500),
            description='适合3-6岁儿童，使用简单词汇和短句，主题温馨积极',
        ),
        'elementary': AgeGroupConfig(
            name='小学生',
            min_age=7,
            max_age=12,
            vocabulary_level='medium',
            sentence_length='medium',
            theme_restrictions=['violence', 'horror', 'adult_themes'],
            word_count_range=(500, 1500),
            description='适合7-12岁儿童，词汇量适中，可包含简单冒险和友谊主题',
        ),
        'teenager': AgeGroupConfig(
            name='青少年',
            min_age=13,
            max_age=18,
            vocabulary_level='complex',
            sentence_length='long',
            theme_restrictions=['explicit_content'],
            word_count_range=(1000, 3000),
            description='适合13-18岁青少年，可包含复杂情节和深度主题',
        ),
        'adult': AgeGroupConfig(
            name='成人',
            min_age=18,
            max_age=100,
            vocabulary_level='complex',
            sentence_length='long',
            theme_restrictions=[],
            word_count_range=(1500, 5000),
            description='适合成人读者，无主题限制',
        ),
    }
    
    # ==================== 题材模板 ====================
    GENRE_TEMPLATES = {
        'fairy_tale': GenreTemplate(
            name='童话故事',
            description='经典童话风格，包含魔法、善恶对比、美好结局',
            key_elements=['主角', '挑战', '魔法元素', '美好结局'],
            structure={
                'opening': '介绍主角和背景环境',
                'conflict': '主角遇到困难或挑战',
                'development': '主角努力克服困难',
                'climax': '关键转折点',
                'resolution': '问题解决，美好结局',
            },
            tone='温馨、积极、充满希望',
            suitable_ages=['preschool', 'elementary'],
            example_prompts=[
                '一只勇敢的小兔子寻找魔法胡萝卜的故事',
                '善良的公主帮助森林动物的童话',
            ],
        ),
        'adventure': GenreTemplate(
            name='冒险故事',
            description='充满探索和挑战的冒险旅程',
            key_elements=['探险目标', '团队合作', '未知挑战', '成长'],
            structure={
                'opening': '介绍冒险背景和目标',
                'journey': '踏上冒险旅程',
                'challenges': '遇到各种挑战和困难',
                'climax': '最大的挑战',
                'resolution': '完成冒险，获得成长',
            },
            tone='激动人心、充满活力',
            suitable_ages=['elementary', 'teenager'],
            example_prompts=[
                '少年探险队寻找失落宝藏',
                '穿越神秘森林的冒险之旅',
            ],
        ),
        'sci_fi': GenreTemplate(
            name='科幻故事',
            description='基于科学想象的未来世界故事',
            key_elements=['科技元素', '未来设定', '创新思维', '人性探讨'],
            structure={
                'opening': '展示未来世界设定',
                'conflict': '科技带来的问题或挑战',
                'exploration': '探索解决方案',
                'climax': '关键发现或决策',
                'resolution': '问题解决，引发思考',
            },
            tone='富有想象力、引人思考',
            suitable_ages=['teenager', 'adult'],
            example_prompts=[
                'AI机器人与人类的友谊故事',
                '太空探险中的意外发现',
            ],
        ),
        'fable': GenreTemplate(
            name='寓言故事',
            description='蕴含道德教训的短篇故事',
            key_elements=['动物角色', '道德教训', '简洁情节', '明确寓意'],
            structure={
                'opening': '介绍角色和情境',
                'conflict': '角色面临选择或困境',
                'consequence': '选择带来的结果',
                'moral': '明确的道德教训',
            },
            tone='简洁、富有教育意义',
            suitable_ages=['preschool', 'elementary'],
            example_prompts=[
                '骄傲的孔雀学会谦虚',
                '勤劳的蚂蚁和懒惰的蝉',
            ],
        ),
        'friendship': GenreTemplate(
            name='友谊故事',
            description='关于友情、团结、互助的温馨故事',
            key_elements=['友谊', '互助', '理解', '成长'],
            structure={
                'opening': '介绍朋友们的背景',
                'conflict': '友谊面临考验',
                'understanding': '互相理解和沟通',
                'resolution': '友谊更加深厚',
            },
            tone='温暖、感人、积极',
            suitable_ages=['preschool', 'elementary', 'teenager'],
            example_prompts=[
                '不同性格的朋友如何相处',
                '克服误会重建友谊',
            ],
        ),
        'mystery': GenreTemplate(
            name='悬疑推理',
            description='充满谜题和推理的故事',
            key_elements=['谜题', '线索', '推理', '真相揭示'],
            structure={
                'opening': '介绍谜题或事件',
                'investigation': '收集线索和调查',
                'red_herrings': '误导性线索',
                'revelation': '真相逐步揭示',
                'resolution': '谜题完全解开',
            },
            tone='紧张、引人入胜',
            suitable_ages=['elementary', 'teenager', 'adult'],
            example_prompts=[
                '校园里的神秘失窃案',
                '古堡中的秘密房间',
            ],
        ),
    }
    
    # ==================== 故事风格 ====================
    STORY_STYLES = {
        'warm_healing': StoryStyle(
            name='温馨治愈',
            description='温暖人心、抚慰心灵的故事风格',
            characteristics=['温暖', '积极', '充满希望', '情感细腻'],
            keywords=['温暖', '治愈', '希望', '美好', '温柔', '关怀'],
            avoid_keywords=['恐怖', '惊悚', '暴力', '黑暗', '绝望'],
        ),
        'humorous': StoryStyle(
            name='幽默诙谐',
            description='轻松有趣、充满笑点的故事风格',
            characteristics=['幽默', '轻松', '有趣', '欢快'],
            keywords=['有趣', '搞笑', '幽默', '欢乐', '滑稽'],
            avoid_keywords=['严肃', '沉重', '悲伤', '压抑'],
        ),
        'inspirational': StoryStyle(
            name='励志向上',
            description='激励人心、传递正能量的故事风格',
            characteristics=['励志', '积极', '奋斗', '成长'],
            keywords=['努力', '坚持', '梦想', '成长', '勇气', '克服'],
            avoid_keywords=['放弃', '失败', '绝望', '消极'],
        ),
        'poetic': StoryStyle(
            name='诗意唯美',
            description='文字优美、意境深远的故事风格',
            characteristics=['优美', '诗意', '意境', '细腻'],
            keywords=['美丽', '诗意', '梦幻', '优雅', '意境'],
            avoid_keywords=['粗俗', '直白', '简陋'],
        ),
        'suspenseful': StoryStyle(
            name='紧张悬疑',
            description='扣人心弦、充满悬念的故事风格',
            characteristics=['紧张', '悬疑', '引人入胜', '意外'],
            keywords=['神秘', '悬疑', '紧张', '意外', '谜团'],
            avoid_keywords=['平淡', '无聊', '可预测'],
        ),
    }
    
    # ==================== 故事结构模板 ====================
    STRUCTURE_TEMPLATES = {
        'three_act': {
            'name': '三幕式结构',
            'description': '经典的三幕剧结构',
            'acts': {
                'act1': {
                    'name': '开端',
                    'percentage': 25,
                    'elements': ['介绍主角', '建立背景', '引出冲突'],
                },
                'act2': {
                    'name': '发展',
                    'percentage': 50,
                    'elements': ['冲突升级', '主角努力', '遇到挫折', '转折点'],
                },
                'act3': {
                    'name': '结局',
                    'percentage': 25,
                    'elements': ['高潮', '问题解决', '结局'],
                },
            },
        },
        'heros_journey': {
            'name': '英雄之旅',
            'description': '经典的英雄旅程结构',
            'stages': [
                '平凡世界',
                '冒险召唤',
                '拒绝召唤',
                '遇见导师',
                '跨越第一道门槛',
                '试炼、盟友与敌人',
                '接近最深的洞穴',
                '磨难',
                '奖赏',
                '回归之路',
                '复活',
                '带着灵药归来',
            ],
        },
        'simple': {
            'name': '简单结构',
            'description': '适合短篇故事的简单结构',
            'parts': {
                'beginning': '开头：介绍角色和背景',
                'middle': '中间：发生事件和冲突',
                'end': '结尾：问题解决和结局',
            },
        },
    }
    
    @classmethod
    def get_age_group(cls, age_group_key: str) -> AgeGroupConfig:
        """获取年龄段配置"""
        return cls.AGE_GROUPS.get(age_group_key)
    
    @classmethod
    def get_genre(cls, genre_key: str) -> GenreTemplate:
        """获取题材模板"""
        return cls.GENRE_TEMPLATES.get(genre_key)
    
    @classmethod
    def get_style(cls, style_key: str) -> StoryStyle:
        """获取故事风格"""
        return cls.STORY_STYLES.get(style_key)
    
    @classmethod
    def get_suitable_genres_for_age(cls, age_group_key: str) -> List[GenreTemplate]:
        """获取适合特定年龄段的题材"""
        suitable_genres = []
        for genre in cls.GENRE_TEMPLATES.values():
            if age_group_key in genre.suitable_ages:
                suitable_genres.append(genre)
        return suitable_genres
    
    @classmethod
    def build_prompt_from_template(
        cls,
        topic: str,
        age_group: str = 'elementary',
        genre: str = 'fairy_tale',
        style: str = 'warm_healing',
        word_count: int = None,
        custom_elements: Dict[str, Any] = None,
    ) -> str:
        """
        根据模板构建提示词
        
        Args:
            topic: 故事主题
            age_group: 年龄段
            genre: 题材
            style: 风格
            word_count: 字数要求
            custom_elements: 自定义元素
        
        Returns:
            构建好的提示词
        """
        age_config = cls.get_age_group(age_group)
        genre_template = cls.get_genre(genre)
        style_config = cls.get_style(style)
        
        # 确定字数
        if word_count is None:
            word_count = (age_config.word_count_range[0] + age_config.word_count_range[1]) // 2
        
        # 构建提示词
        prompt_parts = []
        
        # 基本要求
        prompt_parts.append(f"请创作一个{genre_template.name}，主题是：{topic}")
        
        # 年龄段要求
        prompt_parts.append(f"\n目标读者：{age_config.description}")
        prompt_parts.append(f"词汇难度：{age_config.vocabulary_level}")
        prompt_parts.append(f"句子长度：{age_config.sentence_length}")
        
        # 风格要求
        prompt_parts.append(f"\n故事风格：{style_config.description}")
        prompt_parts.append(f"风格特征：{', '.join(style_config.characteristics)}")
        prompt_parts.append(f"必须包含的元素：{', '.join(style_config.keywords[:3])}")
        prompt_parts.append(f"避免的元素：{', '.join(style_config.avoid_keywords[:3])}")
        
        # 结构要求
        prompt_parts.append(f"\n故事结构：")
        for key, value in genre_template.structure.items():
            prompt_parts.append(f"- {value}")
        
        # 字数要求
        prompt_parts.append(f"\n字数要求：严格控制在{word_count}字左右（允许±10%的浮动）")
        
        # 关键元素
        prompt_parts.append(f"\n必须包含的关键元素：{', '.join(genre_template.key_elements)}")
        
        # 自定义元素
        if custom_elements:
            prompt_parts.append(f"\n额外要求：")
            for key, value in custom_elements.items():
                prompt_parts.append(f"- {key}: {value}")
        
        # 质量要求
        prompt_parts.append(f"\n质量要求：")
        prompt_parts.append("- 情节连贯，逻辑清晰")
        prompt_parts.append("- 语言流畅，无重复内容")
        prompt_parts.append("- 符合目标年龄段的理解能力")
        prompt_parts.append("- 传递积极正面的价值观")
        
        return '\n'.join(prompt_parts)


# 导出配置实例
story_template_config = StoryTemplateConfig()
