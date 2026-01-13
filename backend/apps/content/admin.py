"""内容生成Admin配置"""
from django.contrib import admin
from .models import (
    Story,
    StoryTemplate,
    Character,
    StoryFeedback,
    StoryExport,
    Video,
    VideoScene,
    VideoExport,
    VideoTemplate,
)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'genre', 'age_group', 'status', 'quality_score', 'created_at']
    list_filter = ['status', 'genre', 'age_group', 'created_at']
    search_fields = ['title', 'topic', 'content']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(StoryTemplate)
class StoryTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'genre', 'age_group', 'style', 'is_public', 'created_at']
    list_filter = ['genre', 'age_group', 'style', 'is_public']
    search_fields = ['name', 'description']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'character_type', 'is_public', 'created_at']
    list_filter = ['character_type', 'is_public']
    search_fields = ['name', 'personality', 'background']


@admin.register(StoryFeedback)
class StoryFeedbackAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'overall_rating', 'created_at']
    list_filter = ['overall_rating', 'created_at']


@admin.register(StoryExport)
class StoryExportAdmin(admin.ModelAdmin):
    list_display = ['story', 'user', 'format', 'status', 'created_at']
    list_filter = ['format', 'status', 'created_at']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'generation_type', 'status', 'duration', 'created_at']
    list_filter = ['generation_type', 'status', 'created_at']
    search_fields = ['title', 'prompt']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(VideoScene)
class VideoSceneAdmin(admin.ModelAdmin):
    list_display = ['video', 'scene_number', 'duration', 'created_at']
    list_filter = ['created_at']
    ordering = ['video', 'scene_number']


@admin.register(VideoExport)
class VideoExportAdmin(admin.ModelAdmin):
    list_display = ['video', 'user', 'format', 'status', 'created_at']
    list_filter = ['format', 'status', 'created_at']


@admin.register(VideoTemplate)
class VideoTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_public', 'created_at']
    list_filter = ['category', 'is_public']
    search_fields = ['name', 'description']
