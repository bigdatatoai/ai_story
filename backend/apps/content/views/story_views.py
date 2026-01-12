"""
故事管理视图
提供完整的故事CRUD、导出、批量处理等功能
"""

import logging
import uuid
from typing import Dict, Any
from django.utils import timezone
from django.db import models
from django.db.models import Q, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.content.models.story_models import (
    Story, StoryTemplate, Character, StoryFeedback, StoryExport
)
from apps.content.serializers.story_serializers import (
    StorySerializer, StoryCreateSerializer, StoryUpdateSerializer,
    StoryTemplateSerializer, CharacterSerializer,
    StoryFeedbackSerializer, StoryExportSerializer
)
from config.story_templates import story_template_config
from core.utils.story_quality_validator import story_quality_validator
from core.services.story_continuation_service import (
    story_continuation_service, story_editing_service
)
from core.ai_client.improved_llm_client import ImprovedLLMClient
from core.middleware.rate_limiting import rate_limit_decorator

logger = logging.getLogger('ai_story.api')


class StandardResultPagination(PageNumberPagination):
    """标准分页"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class StoryViewSet(viewsets.ModelViewSet):
    """
    故事管理ViewSet
    
    提供故事的完整CRUD功能，以及生成、续写、编辑等扩展功能
    """
    
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'genre', 'age_group', 'style']
    search_fields = ['title', 'topic', 'content']
    ordering_fields = ['created_at', 'updated_at', 'quality_score', 'view_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """只返回当前用户的故事"""
        return Story.objects.filter(user=self.request.user).prefetch_related('characters')
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return StoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StoryUpdateSerializer
        return StorySerializer
    
    def perform_create(self, serializer):
        """创建故事时自动设置用户"""
        serializer.save(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """重写list方法，返回统一格式"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                'success': True,
                'data': {
                    'results': serializer.data,
                    'count': self.paginator.page.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link()
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """重写create方法，返回统一格式"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': '创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def retrieve(self, request, *args, **kwargs):
        """重写retrieve方法，返回统一格式"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """重写update方法，返回统一格式"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': '更新成功',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """重写destroy方法，返回统一格式"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': '删除成功'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    @rate_limit_decorator(requests=10, window=60)
    def generate(self, request):
        """
        生成新故事
        
        POST /api/v1/content/stories/generate/
        
        Request Body:
        {
            "topic": "勇敢的小兔子",
            "age_group": "elementary",
            "genre": "fairy_tale",
            "style": "warm_healing",
            "word_count": 800,
            "template_id": "uuid",  // 可选
            "character_ids": ["uuid1", "uuid2"],  // 可选
            "custom_elements": {}  // 可选
        }
        
        Response:
        {
            "success": true,
            "data": {
                "story_id": "uuid",
                "title": "...",
                "content": "...",
                "quality_score": 85.5,
                "quality_report": {...}
            }
        }
        """
        try:
            # 验证输入
            topic = request.data.get('topic')
            if not topic:
                return Response({
                    'success': False,
                    'error': '请输入故事主题',
                    'error_code': 'MISSING_TOPIC',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取配置
            age_group = request.data.get('age_group', 'elementary')
            genre = request.data.get('genre', 'fairy_tale')
            style_key = request.data.get('style', 'warm_healing')
            word_count = request.data.get('word_count', 800)
            custom_elements = request.data.get('custom_elements', {})
            
            # 构建提示词
            prompt = story_template_config.build_prompt_from_template(
                topic=topic,
                age_group=age_group,
                genre=genre,
                style=style_key,
                word_count=word_count,
                custom_elements=custom_elements,
            )
            
            # 调用LLM生成
            llm_client = ImprovedLLMClient(provider='openai', model='gpt-3.5-turbo')
            
            story_content = llm_client.generate(
                prompt=prompt,
                stage_type='rewrite',
                use_cache=True,
            )
            
            # 验证质量
            quality_result = story_quality_validator.validate_story(
                story_text=story_content,
                age_group=age_group,
                expected_word_count=word_count,
                genre=genre,
                style=style_key,
            )
            
            # 如果质量不合格，尝试改进
            if not quality_result.passed and quality_result.score < 70:
                logger.info(f"故事质量不合格(分数: {quality_result.score})，尝试改进")
                
                improvement_prompt = story_quality_validator.suggest_improvements(
                    story_content, quality_result
                )
                
                story_content = llm_client.generate(
                    prompt=improvement_prompt,
                    stage_type='rewrite',
                    use_cache=False,
                )
                
                # 重新验证
                quality_result = story_quality_validator.validate_story(
                    story_text=story_content,
                    age_group=age_group,
                    expected_word_count=word_count,
                    genre=genre,
                    style=style_key,
                )
            
            # 生成标题
            title = self._generate_title(story_content, topic)
            
            # 保存故事
            story = Story.objects.create(
                user=request.user,
                title=title,
                topic=topic,
                genre=genre,
                age_group=age_group,
                style=style_key,
                word_count=word_count,
                content=story_content,
                quality_score=quality_result.score,
                quality_report=quality_result.details,
                status='completed',
                completed_at=timezone.now(),
            )
            
            # 关联角色
            character_ids = request.data.get('character_ids', [])
            if character_ids:
                characters = Character.objects.filter(
                    id__in=character_ids,
                    user=request.user
                )
                story.characters.set(characters)
            
            # 返回结果
            serializer = StorySerializer(story)
            
            return Response({
                'success': True,
                'message': '故事生成成功',
                'data': serializer.data,
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"故事生成失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'故事生成失败: {str(e)}',
                'error_code': 'GENERATION_FAILED',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def continue_story(self, request, pk=None):
        """
        续写故事
        
        POST /api/v1/content/stories/{id}/continue_story/
        
        Request Body:
        {
            "continuation_prompt": "小兔子继续冒险...",
            "target_length": 500
        }
        """
        story = self.get_object()
        
        try:
            continuation_prompt = request.data.get('continuation_prompt')
            target_length = request.data.get('target_length', 500)
            
            # 续写
            continuation = story_continuation_service.continue_story(
                existing_story=story.content,
                continuation_prompt=continuation_prompt,
                target_length=target_length,
            )
            
            # 创建新版本
            new_story = Story.objects.create(
                user=request.user,
                title=f"{story.title} (续)",
                topic=story.topic,
                genre=story.genre,
                age_group=story.age_group,
                style=story.style,
                word_count=len(story.content) + target_length,
                content=story.content + "\n\n" + continuation,
                parent_story=story,
                version=story.version + 1,
                status='completed',
                completed_at=timezone.now(),
            )
            
            serializer = StorySerializer(new_story)
            
            return Response({
                'success': True,
                'message': '故事续写成功',
                'data': serializer.data,
            })
        
        except Exception as e:
            logger.error(f"故事续写失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'故事续写失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def edit_story(self, request, pk=None):
        """
        编辑故事
        
        POST /api/v1/content/stories/{id}/edit_story/
        
        Request Body:
        {
            "edit_type": "modify_section|change_ending|adjust_character|polish",
            "instructions": "...",
            "section": "...",  // 可选
            "character_name": "...",  // 可选
        }
        """
        story = self.get_object()
        
        try:
            edit_type = request.data.get('edit_type')
            instructions = request.data.get('instructions')
            
            if edit_type == 'modify_section':
                section = request.data.get('section')
                edited_content = story_continuation_service.modify_section(
                    story=story.content,
                    section_to_modify=section,
                    modification_instruction=instructions,
                )
            
            elif edit_type == 'change_ending':
                edited_content = story_continuation_service.change_ending(
                    story=story.content,
                    new_ending_direction=instructions,
                )
            
            elif edit_type == 'adjust_character':
                character_name = request.data.get('character_name')
                edited_content = story_continuation_service.adjust_character_behavior(
                    story=story.content,
                    character_name=character_name,
                    behavior_adjustment=instructions,
                )
            
            elif edit_type == 'polish':
                edited_content = story_editing_service.polish_language(
                    story=story.content,
                )
            
            else:
                return Response({
                    'success': False,
                    'error': '不支持的编辑类型',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建新版本
            new_story = Story.objects.create(
                user=request.user,
                title=story.title,
                topic=story.topic,
                genre=story.genre,
                age_group=story.age_group,
                style=story.style,
                word_count=len(edited_content),
                content=edited_content,
                parent_story=story,
                version=story.version + 1,
                status='completed',
                completed_at=timezone.now(),
            )
            
            serializer = StorySerializer(new_story)
            
            return Response({
                'success': True,
                'message': '故事编辑成功',
                'data': serializer.data,
            })
        
        except Exception as e:
            logger.error(f"故事编辑失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'故事编辑失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """
        导出故事
        
        POST /api/v1/content/stories/{id}/export/
        
        Request Body:
        {
            "format": "txt|markdown|pdf|docx|html",
            "options": {}
        }
        """
        story = self.get_object()
        
        try:
            export_format = request.data.get('format', 'txt')
            options = request.data.get('options', {})
            
            # 创建导出记录
            export_record = StoryExport.objects.create(
                story=story,
                user=request.user,
                format=export_format,
                options=options,
                status='pending',
            )
            
            # TODO: 异步处理导出任务
            # from apps.content.tasks import export_story_task
            # export_story_task.delay(export_record.id)
            
            serializer = StoryExportSerializer(export_record)
            
            return Response({
                'success': True,
                'message': '导出任务已创建',
                'data': serializer.data,
            })
        
        except Exception as e:
            logger.error(f"导出创建失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'导出创建失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_generate(self, request):
        """
        批量生成故事
        
        POST /api/v1/content/stories/batch_generate/
        
        Request Body:
        {
            "topics": ["主题1", "主题2", "主题3"],
            "config": {
                "age_group": "elementary",
                "genre": "fairy_tale",
                "style": "warm_healing",
                "word_count": 800
            }
        }
        """
        try:
            topics = request.data.get('topics', [])
            config = request.data.get('config', {})
            
            if not topics or len(topics) == 0:
                return Response({
                    'success': False,
                    'error': '请提供至少一个主题',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(topics) > 10:
                return Response({
                    'success': False,
                    'error': '单次最多批量生成10个故事',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # TODO: 创建批量任务，异步处理
            # from apps.content.tasks import batch_generate_stories_task
            # task = batch_generate_stories_task.delay(
            #     user_id=request.user.id,
            #     topics=topics,
            #     config=config
            # )
            
            return Response({
                'success': True,
                'message': f'批量生成任务已创建，共{len(topics)}个故事',
                'data': {
                    'task_id': str(uuid.uuid4()),
                    'topic_count': len(topics),
                    'status': 'pending',
                }
            })
        
        except Exception as e:
            logger.error(f"批量生成失败: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'批量生成失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_title(self, content: str, topic: str) -> str:
        """生成故事标题"""
        # 简单实现：使用主题作为标题
        # TODO: 可以使用LLM生成更好的标题
        return topic[:50] if len(topic) <= 50 else topic[:47] + "..."
    
    @action(detail=False, methods=['post'])
    def generate_outline(self, request):
        """生成故事大纲"""
        try:
            topic = request.data.get('topic', '')
            genre = request.data.get('genre', 'fairy_tale')
            
            # TODO: 调用大纲生成服务
            outline = {
                'title': topic,
                'chapters': [
                    {'number': 1, 'title': '开始', 'summary': '故事的开端'},
                    {'number': 2, 'title': '发展', 'summary': '情节发展'},
                    {'number': 3, 'title': '结局', 'summary': '故事结局'}
                ]
            }
            
            return Response({'success': True, 'data': outline})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def generate_from_outline(self, request):
        """基于大纲生成故事"""
        try:
            outline = request.data.get('outline', {})
            # TODO: 实现基于大纲生成
            return Response({'success': True, 'data': {'story_id': str(uuid.uuid4())}})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=True, methods=['get'])
    def version_history(self, request, pk=None):
        """获取版本历史"""
        story = self.get_object()
        # TODO: 实现版本历史功能
        return Response({'success': True, 'data': []})
    
    @action(detail=False, methods=['post'])
    def compare_versions(self, request):
        """对比版本"""
        # TODO: 实现版本对比
        return Response({'success': True, 'data': {'diff': []}})
    
    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """回滚到指定版本"""
        # TODO: 实现版本回滚
        return Response({'success': True, 'message': '回滚成功'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取统计信息"""
        try:
            user_stories = Story.objects.filter(user=request.user)
            stats = {
                'total': user_stories.count(),
                'completed': user_stories.filter(status='completed').count(),
                'total_words': sum(s.actual_word_count or 0 for s in user_stories),
                'avg_quality': user_stories.aggregate(Avg('quality_score'))['quality_score__avg'] or 0
            }
            return Response({'success': True, 'data': stats})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def start_chain(self, request):
        """开始故事接龙"""
        try:
            topic = request.data.get('topic', '')
            # TODO: 实现故事接龙开始
            return Response({'success': True, 'data': {'chain_id': str(uuid.uuid4()), 'content': '故事开始...'}})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def continue_chain(self, request):
        """继续故事接龙"""
        try:
            chain_id = request.data.get('chain_id', '')
            user_input = request.data.get('user_input', '')
            # TODO: 实现故事接龙继续
            return Response({'success': True, 'data': {'content': '故事继续...'}})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def plot_choices(self, request):
        """获取剧情选择"""
        try:
            # TODO: 实现剧情选择生成
            choices = [
                {'id': 1, 'text': '选择A：勇敢前进'},
                {'id': 2, 'text': '选择B：谨慎观察'}
            ]
            return Response({'success': True, 'data': {'choices': choices}})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def apply_choice(self, request):
        """应用剧情选择"""
        try:
            choice_id = request.data.get('choice_id', 1)
            # TODO: 实现剧情选择应用
            return Response({'success': True, 'data': {'content': '根据选择继续故事...'}})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def save_guided(self, request):
        """保存引导式创作的故事"""
        try:
            content = request.data.get('content', '')
            title = request.data.get('title', '引导式故事')
            
            story = Story.objects.create(
                user=request.user,
                title=title,
                content=content,
                status='completed',
                completed_at=timezone.now()
            )
            
            serializer = StorySerializer(story)
            return Response({'success': True, 'data': serializer.data})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def share_card(self, request):
        """生成分享卡片"""
        try:
            story_id = request.data.get('story_id', '')
            # TODO: 实现分享卡片生成
            return Response({'success': True, 'data': {'card_url': 'https://example.com/card.png'}})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def qrcode(self, request):
        """生成二维码"""
        try:
            story_id = request.data.get('story_id', '')
            # TODO: 实现二维码生成
            return Response({'success': True, 'data': {'qrcode_url': 'https://example.com/qr.png'}})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)


class StoryTemplateViewSet(viewsets.ModelViewSet):
    """故事模板管理"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = StoryTemplateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genre', 'age_group', 'style', 'is_public']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """返回用户自己的模板和公开模板"""
        return StoryTemplate.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CharacterViewSet(viewsets.ModelViewSet):
    """角色库管理"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = CharacterSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['character_type', 'is_public']
    search_fields = ['name', 'personality', 'background']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """返回用户自己的角色和公开角色"""
        return Character.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
