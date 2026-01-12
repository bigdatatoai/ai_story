"""
AI动漫生成服务
专注于动漫风格的角色一致性、场景生成、动画效果
"""

import logging
from typing import Dict, List, Any, Optional
from core.services.multimodal_service import illustration_service

logger = logging.getLogger('ai_story.anime')


class AnimeGenerationService:
    """动漫生成服务"""
    
    ANIME_STYLES = {
        'shounen': {
            'name': '少年动漫',
            'characteristics': 'dynamic action, vibrant colors, energetic',
            'examples': 'Naruto, One Piece style'
        },
        'shoujo': {
            'name': '少女动漫',
            'characteristics': 'soft colors, romantic, detailed eyes',
            'examples': 'Sailor Moon, Cardcaptor Sakura style'
        },
        'seinen': {
            'name': '青年动漫',
            'characteristics': 'realistic, mature themes, detailed',
            'examples': 'Attack on Titan, Tokyo Ghoul style'
        },
        'chibi': {
            'name': 'Q版',
            'characteristics': 'cute, small proportions, simplified',
            'examples': 'chibi style, super deformed'
        },
        'ghibli': {
            'name': '吉卜力风格',
            'characteristics': 'hand-drawn, natural, warm colors',
            'examples': 'Studio Ghibli, Miyazaki style'
        }
    }
    
    def generate_anime_character(
        self,
        character_description: Dict[str, Any],
        anime_style: str = 'shounen',
        poses: List[str] = None,
        expressions: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成动漫角色（多角度、多表情）
        
        Args:
            character_description: 角色描述
            anime_style: 动漫风格
            poses: 姿势列表 ['standing', 'running', 'fighting']
            expressions: 表情列表 ['happy', 'angry', 'sad', 'surprised']
        
        Returns:
            {
                'character_id': '角色ID',
                'reference_sheet': '角色设定图URL',
                'poses': {姿势: 图片URL},
                'expressions': {表情: 图片URL}
            }
        """
        if poses is None:
            poses = ['standing', 'side_view', 'back_view']
        
        if expressions is None:
            expressions = ['neutral', 'happy', 'angry', 'surprised']
        
        style_config = self.ANIME_STYLES.get(anime_style, self.ANIME_STYLES['shounen'])
        
        # 1. 生成角色设定图（character sheet）
        reference_prompt = self._build_character_sheet_prompt(
            character_description,
            style_config
        )
        
        reference_images = illustration_service.generate_illustrations(
            story_content=reference_prompt,
            style='anime',
            num_illustrations=1
        )
        
        reference_sheet_url = reference_images[0]['image_url'] if reference_images else ''
        
        # 2. 生成不同姿势
        pose_images = {}
        for pose in poses:
            pose_prompt = self._build_pose_prompt(
                character_description,
                pose,
                style_config
            )
            
            images = illustration_service.generate_illustrations(
                story_content=pose_prompt,
                style='anime',
                num_illustrations=1
            )
            
            if images:
                pose_images[pose] = images[0]['image_url']
        
        # 3. 生成不同表情
        expression_images = {}
        for expression in expressions:
            expr_prompt = self._build_expression_prompt(
                character_description,
                expression,
                style_config
            )
            
            images = illustration_service.generate_illustrations(
                story_content=expr_prompt,
                style='anime',
                num_illustrations=1
            )
            
            if images:
                expression_images[expression] = images[0]['image_url']
        
        return {
            'character_id': character_description.get('name', 'character'),
            'reference_sheet': reference_sheet_url,
            'poses': pose_images,
            'expressions': expression_images,
            'style': anime_style
        }
    
    def generate_anime_scene(
        self,
        scene_description: str,
        characters: List[str],
        anime_style: str = 'shounen',
        camera_angle: str = 'medium_shot',
        lighting: str = 'natural',
        **kwargs
    ) -> str:
        """
        生成动漫场景
        
        Args:
            scene_description: 场景描述
            characters: 出场角色列表
            anime_style: 动漫风格
            camera_angle: 镜头角度
            lighting: 光照
        
        Returns:
            场景图片URL
        """
        style_config = self.ANIME_STYLES.get(anime_style, self.ANIME_STYLES['shounen'])
        
        prompt = f"""
{scene_description}
Characters: {', '.join(characters)}
Style: {style_config['characteristics']}, {style_config['examples']}
Camera: {camera_angle}
Lighting: {lighting}
High quality anime art, detailed background, professional illustration
"""
        
        images = illustration_service.generate_illustrations(
            story_content=prompt,
            style='anime',
            num_illustrations=1
        )
        
        return images[0]['image_url'] if images else ''
    
    def generate_comic_panels(
        self,
        script: Dict[str, Any],
        panel_layout: str = '4_panel',  # 4_panel/manga_page/webtoon
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        生成漫画分格
        
        Args:
            script: 剧本
            panel_layout: 分格布局
        
        Returns:
            分格列表
        """
        panels = []
        
        layout_config = self._get_panel_layout(panel_layout)
        
        for i, scene in enumerate(script.get('scenes', [])):
            panel = {
                'panel_number': i + 1,
                'layout': layout_config,
                'image_url': self.generate_anime_scene(
                    scene_description=scene['description'],
                    characters=scene.get('characters', []),
                    anime_style=script.get('style', 'shounen')
                ),
                'dialogue': scene.get('dialogue', ''),
                'sound_effects': scene.get('sound_effects', [])
            }
            panels.append(panel)
        
        return panels
    
    def _build_character_sheet_prompt(
        self,
        character: Dict[str, Any],
        style_config: Dict[str, str]
    ) -> str:
        """构建角色设定图提示词"""
        return f"""
Character design sheet, {character.get('name', 'character')}
Appearance: {character.get('appearance', '')}
Age: {character.get('age', 20)}
Personality: {character.get('personality', '')}
Multiple views: front, side, back
Full body, character turnaround
{style_config['characteristics']}
{style_config['examples']}
Professional anime character design, clean lines, detailed
"""
    
    def _build_pose_prompt(
        self,
        character: Dict[str, Any],
        pose: str,
        style_config: Dict[str, str]
    ) -> str:
        """构建姿势提示词"""
        return f"""
{character.get('name', 'character')} in {pose} pose
{character.get('appearance', '')}
{style_config['characteristics']}
Full body, dynamic pose, anime style
{style_config['examples']}
"""
    
    def _build_expression_prompt(
        self,
        character: Dict[str, Any],
        expression: str,
        style_config: Dict[str, str]
    ) -> str:
        """构建表情提示词"""
        return f"""
{character.get('name', 'character')} with {expression} expression
Close-up portrait, face focus
{character.get('appearance', '')}
{style_config['characteristics']}
Anime style, expressive eyes
{style_config['examples']}
"""
    
    def _get_panel_layout(self, layout_type: str) -> Dict[str, Any]:
        """获取分格布局配置"""
        layouts = {
            '4_panel': {
                'type': '4格漫画',
                'panels_per_page': 4,
                'arrangement': 'vertical'
            },
            'manga_page': {
                'type': '漫画页',
                'panels_per_page': 6,
                'arrangement': 'mixed'
            },
            'webtoon': {
                'type': '条漫',
                'panels_per_page': 1,
                'arrangement': 'vertical_scroll'
            }
        }
        
        return layouts.get(layout_type, layouts['4_panel'])


# 导出服务实例
anime_generation_service = AnimeGenerationService()
