"""
故事相关的数据模型
扩展原有模型，支持更丰富的故事管理功能
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class StoryTemplate(models.Model):
    """故事模板"""
    
    GENRE_CHOICES = [
        ('fairy_tale', '童话故事'),
        ('adventure', '冒险故事'),
        ('sci_fi', '科幻故事'),
        ('fable', '寓言故事'),
        ('friendship', '友谊故事'),
        ('mystery', '悬疑推理'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('preschool', '学龄前儿童(3-6岁)'),
        ('elementary', '小学生(7-12岁)'),
        ('teenager', '青少年(13-18岁)'),
        ('adult', '成人(18岁以上)'),
    ]
    
    STYLE_CHOICES = [
        ('warm_healing', '温馨治愈'),
        ('humorous', '幽默诙谐'),
        ('inspirational', '励志向上'),
        ('poetic', '诗意唯美'),
        ('suspenseful', '紧张悬疑'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_templates')
    
    # 基本信息
    name = models.CharField(max_length=200, verbose_name='模板名称')
    description = models.TextField(blank=True, verbose_name='模板描述')
    
    # 模板配置
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, verbose_name='题材')
    age_group = models.CharField(max_length=50, choices=AGE_GROUP_CHOICES, verbose_name='年龄段')
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, verbose_name='风格')
    
    # 字数配置
    min_word_count = models.IntegerField(
        default=500,
        validators=[MinValueValidator(100)],
        verbose_name='最小字数'
    )
    max_word_count = models.IntegerField(
        default=1500,
        validators=[MinValueValidator(100)],
        verbose_name='最大字数'
    )
    
    # 自定义元素
    custom_elements = models.JSONField(default=dict, blank=True, verbose_name='自定义元素')
    
    # 提示词模板
    prompt_template = models.TextField(blank=True, verbose_name='提示词模板')
    
    # 是否公开
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    
    # 使用统计
    use_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'story_templates'
        verbose_name = '故事模板'
        verbose_name_plural = '故事模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Character(models.Model):
    """角色库"""
    
    CHARACTER_TYPE_CHOICES = [
        ('protagonist', '主角'),
        ('antagonist', '反派'),
        ('supporting', '配角'),
        ('mentor', '导师'),
        ('sidekick', '伙伴'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name='角色名称')
    character_type = models.CharField(
        max_length=50,
        choices=CHARACTER_TYPE_CHOICES,
        verbose_name='角色类型'
    )
    
    # 角色属性
    age = models.IntegerField(null=True, blank=True, verbose_name='年龄')
    gender = models.CharField(max_length=20, blank=True, verbose_name='性别')
    species = models.CharField(max_length=50, default='人类', verbose_name='种族/物种')
    
    # 角色特征
    personality = models.TextField(verbose_name='性格特征')
    appearance = models.TextField(blank=True, verbose_name='外貌描述')
    background = models.TextField(blank=True, verbose_name='背景故事')
    
    # 能力和特点
    abilities = models.JSONField(default=list, blank=True, verbose_name='能力特长')
    weaknesses = models.JSONField(default=list, blank=True, verbose_name='弱点')
    
    # 关系
    relationships = models.JSONField(default=dict, blank=True, verbose_name='人物关系')
    
    # 标签
    tags = models.JSONField(default=list, blank=True, verbose_name='标签')
    
    # 是否公开
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    
    # 使用统计
    use_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'characters'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_character_type_display()})"


class Story(models.Model):
    """故事记录"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('generating', '生成中'),
        ('completed', '已完成'),
        ('failed', '生成失败'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    
    # 基本信息
    title = models.CharField(max_length=200, verbose_name='故事标题')
    topic = models.TextField(verbose_name='故事主题')
    
    # 关联
    template = models.ForeignKey(
        StoryTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stories',
        verbose_name='使用的模板'
    )
    characters = models.ManyToManyField(
        Character,
        blank=True,
        related_name='stories',
        verbose_name='涉及的角色'
    )
    
    # 配置
    genre = models.CharField(max_length=50, verbose_name='题材')
    age_group = models.CharField(max_length=50, verbose_name='年龄段')
    style = models.CharField(max_length=50, verbose_name='风格')
    word_count = models.IntegerField(verbose_name='目标字数')
    custom_elements = models.JSONField(default=dict, blank=True, verbose_name='自定义元素')
    
    # 内容
    content = models.TextField(blank=True, verbose_name='故事内容')
    
    # 版本管理
    version = models.IntegerField(default=1, verbose_name='版本号')
    parent_story = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisions',
        verbose_name='父版本'
    )
    
    # 质量评分
    quality_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='质量评分'
    )
    quality_report = models.JSONField(default=dict, blank=True, verbose_name='质量报告')
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态'
    )
    
    # 统计
    actual_word_count = models.IntegerField(default=0, verbose_name='实际字数')
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    like_count = models.IntegerField(default=0, verbose_name='点赞次数')
    
    # 导出记录
    exported_formats = models.JSONField(default=list, blank=True, verbose_name='已导出格式')
    
    # 标签和分类
    tags = models.JSONField(default=list, blank=True, verbose_name='标签')
    category = models.CharField(max_length=100, blank=True, verbose_name='分类')
    
    # 是否公开
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'stories'
        verbose_name = '故事'
        verbose_name_plural = '故事'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['genre', 'age_group']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 自动计算实际字数
        if self.content:
            self.actual_word_count = len(self.content)
        super().save(*args, **kwargs)


class StoryFeedback(models.Model):
    """故事反馈"""
    
    RATING_CHOICES = [
        (1, '很差'),
        (2, '较差'),
        (3, '一般'),
        (4, '良好'),
        (5, '优秀'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_feedbacks')
    
    # 评分
    overall_rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='总体评分')
    plot_rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='情节评分'
    )
    language_rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='语言评分'
    )
    creativity_rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='创意评分'
    )
    
    # 反馈内容
    comment = models.TextField(blank=True, verbose_name='评论')
    
    # 改进建议
    suggestions = models.TextField(blank=True, verbose_name='改进建议')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'story_feedbacks'
        verbose_name = '故事反馈'
        verbose_name_plural = '故事反馈'
        ordering = ['-created_at']
        unique_together = [['story', 'user']]
    
    def __str__(self):
        return f"{self.story.title} - {self.get_overall_rating_display()}"


class StoryExport(models.Model):
    """故事导出记录"""
    
    FORMAT_CHOICES = [
        ('txt', '纯文本'),
        ('markdown', 'Markdown'),
        ('pdf', 'PDF'),
        ('docx', 'Word文档'),
        ('html', 'HTML'),
        ('epub', 'EPUB电子书'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='exports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_exports')
    
    # 导出配置
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, verbose_name='导出格式')
    options = models.JSONField(default=dict, blank=True, verbose_name='导出选项')
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    
    # 文件信息
    file_path = models.CharField(max_length=500, blank=True, verbose_name='文件路径')
    file_size = models.IntegerField(null=True, blank=True, verbose_name='文件大小(字节)')
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'story_exports'
        verbose_name = '故事导出'
        verbose_name_plural = '故事导出'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.story.title} - {self.get_format_display()}"
