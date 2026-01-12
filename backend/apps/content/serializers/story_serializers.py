"""
故事相关的序列化器
"""

from rest_framework import serializers
from apps.content.models.story_models import (
    Story, StoryTemplate, Character, StoryFeedback, StoryExport
)


class CharacterSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    
    character_type_display = serializers.CharField(
        source='get_character_type_display',
        read_only=True
    )
    
    class Meta:
        model = Character
        fields = [
            'id', 'name', 'character_type', 'character_type_display',
            'age', 'gender', 'species', 'personality', 'appearance',
            'background', 'abilities', 'weaknesses', 'relationships',
            'tags', 'is_public', 'use_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'created_at', 'updated_at']


class StoryTemplateSerializer(serializers.ModelSerializer):
    """故事模板序列化器"""
    
    genre_display = serializers.CharField(source='get_genre_display', read_only=True)
    age_group_display = serializers.CharField(source='get_age_group_display', read_only=True)
    style_display = serializers.CharField(source='get_style_display', read_only=True)
    
    class Meta:
        model = StoryTemplate
        fields = [
            'id', 'name', 'description', 'genre', 'genre_display',
            'age_group', 'age_group_display', 'style', 'style_display',
            'min_word_count', 'max_word_count', 'custom_elements',
            'prompt_template', 'is_public', 'use_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'created_at', 'updated_at']


class StorySerializer(serializers.ModelSerializer):
    """故事序列化器（详细）"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)
    characters = CharacterSerializer(many=True, read_only=True)
    
    # 版本信息
    has_revisions = serializers.SerializerMethodField()
    revision_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            'id', 'user', 'user_name', 'title', 'topic',
            'template', 'template_name', 'characters',
            'genre', 'age_group', 'style', 'word_count',
            'content', 'version', 'parent_story',
            'has_revisions', 'revision_count',
            'quality_score', 'quality_report',
            'status', 'status_display',
            'actual_word_count', 'view_count', 'like_count',
            'exported_formats', 'tags', 'category', 'is_public',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'actual_word_count',
            'view_count', 'like_count', 'created_at', 'updated_at'
        ]
    
    def get_has_revisions(self, obj):
        """是否有修订版本"""
        return obj.revisions.exists()
    
    def get_revision_count(self, obj):
        """修订版本数量"""
        return obj.revisions.count()


class StoryListSerializer(serializers.ModelSerializer):
    """故事列表序列化器（简化）"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    character_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            'id', 'title', 'topic', 'genre', 'age_group', 'style',
            'status', 'status_display', 'quality_score',
            'actual_word_count', 'view_count', 'like_count',
            'character_count', 'is_public',
            'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_character_count(self, obj):
        """角色数量"""
        return obj.characters.count()


class StoryCreateSerializer(serializers.ModelSerializer):
    """故事创建序列化器"""
    
    character_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Story
        fields = [
            'title', 'topic', 'template', 'character_ids',
            'genre', 'age_group', 'style', 'word_count',
            'custom_elements', 'tags', 'category'
        ]
    
    def create(self, validated_data):
        character_ids = validated_data.pop('character_ids', [])
        story = Story.objects.create(**validated_data)
        
        if character_ids:
            characters = Character.objects.filter(id__in=character_ids)
            story.characters.set(characters)
        
        return story


class StoryUpdateSerializer(serializers.ModelSerializer):
    """故事更新序列化器"""
    
    class Meta:
        model = Story
        fields = [
            'title', 'content', 'tags', 'category', 'is_public'
        ]


class StoryFeedbackSerializer(serializers.ModelSerializer):
    """故事反馈序列化器"""
    
    overall_rating_display = serializers.CharField(
        source='get_overall_rating_display',
        read_only=True
    )
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StoryFeedback
        fields = [
            'id', 'story', 'user', 'user_name',
            'overall_rating', 'overall_rating_display',
            'plot_rating', 'language_rating', 'creativity_rating',
            'comment', 'suggestions', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'user_name', 'created_at']


class StoryExportSerializer(serializers.ModelSerializer):
    """故事导出序列化器"""
    
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    story_title = serializers.CharField(source='story.title', read_only=True)
    
    class Meta:
        model = StoryExport
        fields = [
            'id', 'story', 'story_title', 'user',
            'format', 'format_display', 'options',
            'status', 'status_display',
            'file_path', 'file_size', 'error_message',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'file_path', 'file_size',
            'error_message', 'created_at', 'completed_at'
        ]
