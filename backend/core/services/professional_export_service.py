"""
专业格式导出服务
支持绘本PDF、EPUB电子书、动画脚本等格式
"""

import logging
from typing import Dict, List, Any, Optional
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColo

logger = logging.getLogger('ai_story.export')


class ProfessionalExportService:
    """专业格式导出服务"""
    
    def export_as_picture_book_pdf(
        self,
        story: Any,
        illustrations: List[Dict[str, Any]] = None,
        layout: str = 'standard',
        **kwargs
    ) -> bytes:
        """
        导出为绘本格式PDF
        
        Args:
            story: 故事对象
            illustrations: 插画列表
            layout: 布局样式 (standard/full_page/side_by_side)
        
        Returns:
            PDF文件的bytes数据
        """
    
        
        # 创建PDF
        buffer = BytesIO()
        
        # 使用横向A4
        page_width, page_height = landscape(A4)
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        
        # 注册中文字体
        try:
            pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
            font_name = 'SimSun'
        except:
            font_name = 'Helvetica'
        
        # 分页处理故事内容
        story_pages = self._split_story_into_pages(
            story.content,
            illustrations or []
        )
        
        for page_num, page_data in enumerate(story_pages, 1):
            # 绘制页面
            self._draw_picture_book_page(
                c,
                page_data,
                page_width,
                page_height,
                font_name,
                layout
            )
            
            # 添加页码
            c.setFont(font_name, 10)
            c.drawCentredString(page_width / 2, 1 * cm, str(page_num))
            
            c.showPage()
        
        # 添加封面
        self._draw_cover_page(c, story, page_width, page_height, font_name)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def export_as_epub(
        self,
        story: Any,
        illustrations: List[Dict[str, Any]] = None,
        **kwargs
    ) -> bytes:
        """
        导出为EPUB电子书
        
        Args:
            story: 故事对象
            illustrations: 插画列表
        
        Returns:
            EPUB文件的bytes数据
        """
        from ebooklib import epub
        
        # 创建EPUB书籍
        book = epub.EpubBook()
        
        # 设置元数据
        book.set_identifier(f'story_{story.id}')
        book.set_title(story.title)
        book.set_language('zh')
        book.add_author(story.user.username if hasattr(story, 'user') else 'AI Story Generator')
        
        # 创建章节
        chapters = self._split_story_into_chapters(story.content)
        
        epub_chapters = []
        for i, chapter_content in enumerate(chapters, 1):
            chapter = epub.EpubHtml(
                title=f'第{i}章',
                file_name=f'chapter_{i}.xhtml',
                lang='zh'
            )
            
            # 添加章节内容
            html_content = f'<h1>第{i}章</h1>'
            
            # 如果有对应的插画，添加插画
            if illustrations and i - 1 < len(illustrations):
                ill = illustrations[i - 1]
                html_content += f'<img src="{ill["image_url"]}" alt="插画" />'
            
            html_content += f'<p>{chapter_content}</p>'
            chapter.content = html_content
            
            book.add_item(chapter)
            epub_chapters.append(chapter)
        
        # 定义目录
        book.toc = tuple(epub_chapters)
        
        # 添加导航文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # 定义CSS样式
        style = '''
        @namespace epub "http://www.idpf.org/2007/ops";
        body {
            font-family: SimSun, serif;
            line-height: 1.8;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        p {
            text-indent: 2em;
            margin: 1em 0;
        }
        img {
            max-width: 100%;
            display: block;
            margin: 1em auto;
        }
        '''
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)
        
        # 创建spine
        book.spine = ['nav'] + epub_chapters
        
        # 生成EPUB文件
        buffer = BytesIO()
        epub.write_epub(buffer, book)
        buffer.seek(0)
        return buffer.getvalue()
    
    def export_as_animation_script(
        self,
        story: Any,
        illustrations: List[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        导出为动画分镜脚本
        
        Args:
            story: 故事对象
            illustrations: 插画列表
        
        Returns:
            脚本文本
        """
        script_lines = []
        
        # 标题
        script_lines.append(f"动画分镜脚本：{story.title}")
        script_lines.append("=" * 50)
        script_lines.append("")
        
        # 基本信息
        script_lines.append(f"创作时间：{datetime.now().strftime('%Y-%m-%d')}")
        script_lines.append(f"总字数：{story.actual_word_count}字")
        script_lines.append(f"题材：{story.genre}")
        script_lines.append("")
        script_lines.append("=" * 50)
        script_lines.append("")
        
        # 分析故事，提取场景
        scenes = self._extract_scenes_for_script(story.content)
        
        for i, scene in enumerate(scenes, 1):
            script_lines.append(f"【镜头 {i}】")
            script_lines.append("-" * 40)
            
            # 场景描述
            script_lines.append(f"场景：{scene['setting']}")
            script_lines.append(f"时间：{scene['time']}")
            script_lines.append(f"镜头类型：{scene['shot_type']}")
            script_lines.append("")
            
            # 画面内容
            script_lines.append("画面：")
            script_lines.append(f"  {scene['visual']}")
            script_lines.append("")
            
            # 台词/旁白
            if scene.get('dialogue'):
                script_lines.append("台词：")
                for line in scene['dialogue']:
                    script_lines.append(f"  {line}")
                script_lines.append("")
            
            if scene.get('narration'):
                script_lines.append("旁白：")
                script_lines.append(f"  {scene['narration']}")
                script_lines.append("")
            
            # 音效
            if scene.get('sound_effects'):
                script_lines.append("音效：")
                script_lines.append(f"  {scene['sound_effects']}")
                script_lines.append("")
            
            # 转场
            if i < len(scenes):
                script_lines.append(f"转场：{scene.get('transition', '切换')}")
            
            script_lines.append("")
        
        return '\n'.join(script_lines)
    
    def _split_story_into_pages(
        self,
        content: str,
        illustrations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """将故事分页"""
        pages = []
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # 每页一个段落+一张插画
        for i, para in enumerate(paragraphs):
            page = {
                'text': para,
                'illustration': illustrations[i] if i < len(illustrations) else None
            }
            pages.append(page)
        
        return pages
    
    def _draw_picture_book_page(
        self,
        c,
        page_data: Dict[str, Any],
        width: float,
        height: float,
        font_name: str,
        layout: str
    ):
        """绘制绘本页面"""
        from reportlab.lib.utils import ImageReader
        from reportlab.lib.colors import HexColor
        
        margin = 2
        
        if layout == 'standard':
            # 上半部分：插画，下半部分：文字
            if page_data.get('illustration'):
                # 绘制插画
                img_height = height * 0.6
                try:
                    img = ImageReader(page_data['illustration']['image_url'])
                    c.drawImage(
                        img,
                        margin,
                        height - img_height - margin,
                        width - 2 * margin,
                        img_height,
                        preserveAspectRatio=True
                    )
                except:
                    pass
            
            # 绘制文字
            text_y = height * 0.35
            c.setFont(font_name, 14)
            c.setFillColor(HexColor('#333333'))
            
            # 文字换行
            text = page_data['text']
            lines = self._wrap_text(text, width - 4 * margin, font_name, 14)
            
            for line in lines:
                c.drawString(margin * 2, text_y, line)
                text_y -= 20
        
        elif layout == 'side_by_side':
            # 左侧：插画，右侧：文字
            mid_x = width / 2
            
            if page_data.get('illustration'):
                try:
                    img = ImageReader(page_data['illustration']['image_url'])
                    c.drawImage(
                        img,
                        margin,
                        margin,
                        mid_x - 2 * margin,
                        height - 2 * margin,
                        preserveAspectRatio=True
                    )
                except:
                    pass
            
            # 右侧文字
            text_y = height - 3 * margin
            c.setFont(font_name, 12)
            
            text = page_data['text']
            lines = self._wrap_text(text, mid_x - 3 * margin, font_name, 12)
            
            for line in lines:
                c.drawString(mid_x + margin, text_y, line)
                text_y -= 18
    
    def _draw_cover_page(
        self,
        c,
        story: Any,
        width: float,
        height: float,
        font_name: str
    ):
        """绘制封面"""
        from reportlab.lib.colors import HexColor
        
        # 背景色
        c.setFillColor(HexColor('#F0F8FF'))
        c.rect(0, 0, width, height, fill=1)
        
        # 标题
        c.setFillColor(HexColor('#333333'))
        c.setFont(font_name, 32)
        c.drawCentredString(width / 2, height * 0.6, story.title)
        
        # 作者
        c.setFont(font_name, 16)
        author = story.user.username if hasattr(story, 'user') else 'AI创作'
        c.drawCentredString(width / 2, height * 0.4, f"作者：{author}")
        
        # 日期
        c.setFont(font_name, 12)
        c.drawCentredString(
            width / 2,
            height * 0.3,
            datetime.now().strftime('%Y年%m月%d日')
        )
    
    def _wrap_text(self, text: str, max_width: float, font_name: str, font_size: int) -> List[str]:
        """文字换行"""
        from reportlab.pdfbase.pdfmetrics import stringWidth
        
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            if stringWidth(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _split_story_into_chapters(self, content: str) -> List[str]:
        """将故事分章节"""
        # 简单实现：按段落分章
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # 每3-4个段落一章
        chapters = []
        current_chapter = []
        
        for para in paragraphs:
            current_chapter.append(para)
            if len(current_chapter) >= 3:
                chapters.append('\n\n'.join(current_chapter))
                current_chapter = []
        
        if current_chapter:
            chapters.append('\n\n'.join(current_chapter))
        
        return chapters
    
    def _extract_scenes_for_script(self, content: str) -> List[Dict[str, Any]]:
        """提取场景用于脚本"""
        scenes = []
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for i, para in enumerate(paragraphs):
            # 简化的场景分析
            scene = {
                'setting': self._infer_setting(para),
                'time': self._infer_time(para),
                'shot_type': self._infer_shot_type(i, len(paragraphs)),
                'visual': para[:100],  # 前100字作为画面描述
                'narration': para,
                'dialogue': self._extract_dialogue(para),
                'sound_effects': self._infer_sound_effects(para),
                'transition': '切换'
            }
            scenes.append(scene)
        
        return scenes
    
    def _infer_setting(self, text: str) -> str:
        """推断场景"""
        keywords = {
            '森林': '森林',
            '家': '室内-家',
            '学校': '学校',
            '公园': '公园',
            '城堡': '城堡',
        }
        
        for keyword, setting in keywords.items():
            if keyword in text:
                return setting
        
        return '未指定'
    
    def _infer_time(self, text: str) -> str:
        """推断时间"""
        if '早晨' in text or '清晨' in text:
            return '早晨'
        elif '中午' in text:
            return '中午'
        elif '傍晚' in text or '黄昏' in text:
            return '傍晚'
        elif '晚上' in text or '夜晚' in text:
            return '夜晚'
        
        return '白天'
    
    def _infer_shot_type(self, index: int, total: int) -> str:
        """推断镜头类型"""
        if index == 0:
            return '远景'
        elif index == total - 1:
            return '特写'
        elif index < total * 0.3:
            return '全景'
        else:
            return '中景'
    
    def _extract_dialogue(self, text: str) -> List[str]:
        """提取对话"""
        import re
        
        dialogues = re.findall(r'[""]([^""]+)[""]', text)
        return dialogues
    
    def _infer_sound_effects(self, text: str) -> str:
        """推断音效"""
        sound_keywords = {
            '风': '风声',
            '雨': '雨声',
            '鸟': '鸟鸣',
            '笑': '笑声',
            '哭': '哭声',
        }
        
        for keyword, sound in sound_keywords.items():
            if keyword in text:
                return sound
        
        return '环境音'


# 导出服务实例
professional_export_service = ProfessionalExportService()
