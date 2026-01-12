"""
背景音乐库模型
"""

import uuid
from django.db import models


class BackgroundMusic(models.Model):
    """背景音乐"""
    
    MOOD_CHOICES = [
        ('happy', '欢快'),
        ('sad', '悲伤'),
        ('tense', '紧张'),
        ('calm', '平静'),
        ('energetic', '激昂'),
        ('romantic', '浪漫'),
        ('mysterious', '神秘'),
        ('epic', '史诗'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="音乐名称")
    file_path = models.CharField(max_length=512, verbose_name="文件路径")
    
    # 音乐属性
    mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        verbose_name="情绪",
        db_index=True
    )
    duration = models.IntegerField(verbose_name="时长(秒)")
    bpm = models.IntegerField(null=True, blank=True, verbose_name="节奏(BPM)")
    
    # 标签和分类
    tags = models.JSONField(default=list, blank=True, verbose_name="标签")
    category = models.CharField(max_length=50, blank=True, verbose_name="分类")
    
    # 元数据
    artist = models.CharField(max_length=255, blank=True, verbose_name="艺术家")
    description = models.TextField(blank=True, verbose_name="描述")
    
    # 版权信息
    license_type = models.CharField(max_length=50, default='free', verbose_name="许可类型")
    copyright_info = models.TextField(blank=True, verbose_name="版权信息")
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'background_music'
        verbose_name = '背景音乐'
        verbose_name_plural = '背景音乐'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mood', 'is_active']),
            models.Index(fields=['duration', 'mood']),
            models.Index(fields=['-usage_count']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_mood_display()})"
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class TransitionEffect(models.Model):
    """转场效果"""
    
    EFFECT_TYPE_CHOICES = [
        ('fade', '淡入淡出'),
        ('dissolve', '溶解'),
        ('wipe', '擦除'),
        ('slide', '滑动'),
        ('zoom', '缩放'),
        ('rotate', '旋转'),
        ('blur', '模糊'),
        ('glitch', '故障'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="效果名称")
    effect_type = models.CharField(
        max_length=20,
        choices=EFFECT_TYPE_CHOICES,
        verbose_name="效果类型"
    )
    
    # FFmpeg 滤镜参数
    ffmpeg_filter = models.TextField(verbose_name="FFmpeg滤镜")
    duration = models.FloatField(default=0.5, verbose_name="持续时间(秒)")
    
    # 预览
    preview_image = models.CharField(max_length=512, blank=True, verbose_name="预览图")
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'transition_effects'
        verbose_name = '转场效果'
        verbose_name_plural = '转场效果'
        ordering = ['-usage_count']
    
    def __str__(self):
        return f"{self.name} ({self.get_effect_type_display()})"


class VideoFilter(models.Model):
    """视频滤镜"""
    
    FILTER_CATEGORY_CHOICES = [
        ('color', '色彩调整'),
        ('style', '风格化'),
        ('vintage', '复古'),
        ('cinematic', '电影感'),
        ('artistic', '艺术效果'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="滤镜名称")
    category = models.CharField(
        max_length=20,
        choices=FILTER_CATEGORY_CHOICES,
        verbose_name="分类"
    )
    
    # FFmpeg 滤镜参数
    ffmpeg_filter = models.TextField(verbose_name="FFmpeg滤镜")
    
    # 预览
    preview_image = models.CharField(max_length=512, blank=True, verbose_name="预览图")
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = 'video_filters'
        verbose_name = '视频滤镜'
        verbose_name_plural = '视频滤镜'
        ordering = ['-usage_count']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
