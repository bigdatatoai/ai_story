"""
社交分享服务
生成分享卡片、集成社交平台API
"""

import logging
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode

logger = logging.getLogger('ai_story.sharing')


class SocialSharingService:
    """社交分享服务"""
    
    def generate_share_card(
        self,
        story: Any,
        illustration_url: str = None,
        card_style: str = 'default',
        **kwargs
    ) -> str:
        """
        生成分享卡片
        
        Args:
            story: 故事对象
            illustration_url: 插画URL
            card_style: 卡片样式 (default/minimal/colorful)
        
        Returns:
            卡片图片URL
        """
        # 创建卡片图片
        if card_style == 'minimal':
            img = self._create_minimal_card(story, illustration_url)
        elif card_style == 'colorful':
            img = self._create_colorful_card(story, illustration_url)
        else:
            img = self._create_default_card(story, illustration_url)
        
        # 保存图片
        card_url = self._save_card_image(img, f"share_card_{story.id}")
        
        return card_url
    
    def generate_wechat_share_data(
        self,
        story: Any,
        share_url: str = None
    ) -> Dict[str, str]:
        """
        生成微信分享数据
        
        Args:
            story: 故事对象
            share_url: 分享链接
        
        Returns:
            {
                'title': '标题',
                'description': '描述',
                'image_url': '图片URL',
                'url': '链接'
            }
        """
        return {
            'title': story.title,
            'description': self._generate_share_description(story),
            'image_url': self._get_story_cover_image(story),
            'url': share_url or f"https://yourdomain.com/story/{story.id}"
        }
    
    def generate_qrcode(
        self,
        story: Any,
        size: int = 300
    ) -> str:
        """
        生成故事二维码
        
        Args:
            story: 故事对象
            size: 二维码大小
        
        Returns:
            二维码图片URL
        """
        # 生成分享链接
        share_url = f"https://yourdomain.com/story/{story.id}"
        
        # 创建二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(share_url)
        qr.make(fit=True)
        
        # 生成图片
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size))
        
        # 保存
        qr_url = self._save_card_image(img, f"qrcode_{story.id}")
        
        return qr_url
    
    def _create_default_card(
        self,
        story: Any,
        illustration_url: str = None
    ) -> Image.Image:
        """创建默认样式卡片"""
        # 创建800x1200的卡片
        img = Image.new('RGB', (800, 1200), color='#F5F5F5')
        draw = ImageDraw.Draw(img)
        
        # 加载字体
        try:
            title_font = ImageFont.truetype('SimHei.ttf', 48)
            text_font = ImageFont.truetype('SimHei.ttf', 24)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # 绘制标题
        title = story.title[:20]  # 限制长度
        draw.text((50, 50), title, fill='#333333', font=title_font)
        
        # 绘制插画（如果有）
        if illustration_url:
            try:
                import requests
                response = requests.get(illustration_url)
                ill_img = Image.open(BytesIO(response.content))
                ill_img = ill_img.resize((700, 500))
                img.paste(ill_img, (50, 150))
            except:
                pass
        
        # 绘制摘要
        summary = story.content[:100] + '...'
        y_pos = 700
        for line in self._wrap_text(summary, 700, text_font):
            draw.text((50, y_pos), line, fill='#666666', font=text_font)
            y_pos += 35
        
        # 绘制底部信息
        draw.text((50, 1100), 'AI故事生成器', fill='#999999', font=text_font)
        
        return img
    
    def _create_minimal_card(self, story: Any, illustration_url: str = None) -> Image.Image:
        """创建简约样式卡片"""
        img = Image.new('RGB', (800, 1200), color='#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype('SimHei.ttf', 42)
            text_font = ImageFont.truetype('SimHei.ttf', 20)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # 简约设计：只有标题和关键信息
        draw.text((100, 500), story.title, fill='#000000', font=title_font)
        draw.text((100, 600), f"字数：{story.actual_word_count}", fill='#666666', font=text_font)
        
        return img
    
    def _create_colorful_card(self, story: Any, illustration_url: str = None) -> Image.Image:
        """创建彩色样式卡片"""
        # 渐变背景
        img = Image.new('RGB', (800, 1200), color='#FF6B6B')
        draw = ImageDraw.Draw(img)
        
        # 添加渐变效果（简化版）
        for y in range(1200):
            color = self._interpolate_color('#FF6B6B', '#4ECDC4', y / 1200)
            draw.rectangle([(0, y), (800, y+1)], fill=color)
        
        # 其他内容...
        return img
    
    def _wrap_text(self, text: str, max_width: int, font) -> List[str]:
        """文字换行"""
        words = text
        lines = []
        current_line = ""
        
        for char in words:
            test_line = current_line + char
            try:
                bbox = font.getbbox(test_line)
                width = bbox[2] - bbox[0]
            except:
                width = len(test_line) * 12
            
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _interpolate_color(self, color1: str, color2: str, ratio: float) -> str:
        """颜色插值"""
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _save_card_image(self, img: Image.Image, filename: str) -> str:
        """保存卡片图片"""
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        file_path = f"share_cards/{filename}.png"
        saved_path = default_storage.save(file_path, ContentFile(buffer.getvalue()))
        
        return default_storage.url(saved_path)
    
    def _generate_share_description(self, story: Any) -> str:
        """生成分享描述"""
        return story.content[:80] + '...'
    
    def _get_story_cover_image(self, story: Any) -> str:
        """获取故事封面图"""
        # 如果有插画，返回第一张
        # 否则返回默认封面
        return "https://yourdomain.com/default_cover.png"


# 导出服务实例
social_sharing_service = SocialSharingService()
