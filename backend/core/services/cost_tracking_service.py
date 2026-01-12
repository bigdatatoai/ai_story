"""
成本追踪服务
职责: 追踪和统计AI模型使用成本
"""

from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.core.cache import cache
from apps.models.models import ModelProvider


class CostTrackingService:
    """成本追踪服务"""
    
    # 默认价格（每1000 tokens或每次调用）
    DEFAULT_PRICES = {
        'llm': {
            'input_tokens': Decimal('0.0001'),  # $0.0001 per 1K tokens
            'output_tokens': Decimal('0.0002'),  # $0.0002 per 1K tokens
        },
        'text2image': {
            'per_image': Decimal('0.04'),  # $0.04 per image
        },
        'image2video': {
            'per_video': Decimal('0.10'),  # $0.10 per video
        }
    }
    
    def __init__(self):
        self.cache_timeout = 300  # 5分钟缓存
    
    def record_llm_usage(
        self,
        provider: ModelProvider,
        project_id: str,
        user_id: int,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        记录LLM使用量
        
        Args:
            provider: 模型提供商
            project_id: 项目ID
            user_id: 用户ID
            input_tokens: 输入token数
            output_tokens: 输出token数
            metadata: 额外元数据
            
        Returns:
            Dict: 使用记录和成本信息
        """
        from apps.models.models import ModelUsageRecord
        
        # 计算成本
        input_cost = (Decimal(input_tokens) / 1000) * self.DEFAULT_PRICES['llm']['input_tokens']
        output_cost = (Decimal(output_tokens) / 1000) * self.DEFAULT_PRICES['llm']['output_tokens']
        total_cost = input_cost + output_cost
        
        # 创建使用记录
        record = ModelUsageRecord.objects.create(
            provider=provider,
            project_id=project_id,
            user_id=user_id,
            usage_type='llm',
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost=total_cost,
            metadata=metadata or {}
        )
        
        # 更新缓存统计
        self._update_cache_stats(provider.id, user_id, total_cost)
        
        return {
            'record_id': str(record.id),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'cost': float(total_cost),
            'currency': 'USD'
        }
    
    def record_image_generation(
        self,
        provider: ModelProvider,
        project_id: str,
        user_id: int,
        image_count: int = 1,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        记录文生图使用量
        
        Args:
            provider: 模型提供商
            project_id: 项目ID
            user_id: 用户ID
            image_count: 生成图片数量
            metadata: 额外元数据
            
        Returns:
            Dict: 使用记录和成本信息
        """
        from apps.models.models import ModelUsageRecord
        
        # 计算成本
        total_cost = Decimal(image_count) * self.DEFAULT_PRICES['text2image']['per_image']
        
        # 创建使用记录
        record = ModelUsageRecord.objects.create(
            provider=provider,
            project_id=project_id,
            user_id=user_id,
            usage_type='text2image',
            image_count=image_count,
            total_cost=total_cost,
            metadata=metadata or {}
        )
        
        # 更新缓存统计
        self._update_cache_stats(provider.id, user_id, total_cost)
        
        return {
            'record_id': str(record.id),
            'image_count': image_count,
            'cost': float(total_cost),
            'currency': 'USD'
        }
    
    def record_video_generation(
        self,
        provider: ModelProvider,
        project_id: str,
        user_id: int,
        video_count: int = 1,
        duration_seconds: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        记录图生视频使用量
        
        Args:
            provider: 模型提供商
            project_id: 项目ID
            user_id: 用户ID
            video_count: 生成视频数量
            duration_seconds: 视频时长（秒）
            metadata: 额外元数据
            
        Returns:
            Dict: 使用记录和成本信息
        """
        from apps.models.models import ModelUsageRecord
        
        # 计算成本（可以根据时长调整价格）
        base_cost = Decimal(video_count) * self.DEFAULT_PRICES['image2video']['per_video']
        
        # 如果有时长信息，可以按时长计费
        if duration_seconds:
            # 例如：每秒额外收费
            duration_cost = Decimal(duration_seconds) * Decimal('0.01')
            total_cost = base_cost + duration_cost
        else:
            total_cost = base_cost
        
        # 创建使用记录
        record = ModelUsageRecord.objects.create(
            provider=provider,
            project_id=project_id,
            user_id=user_id,
            usage_type='image2video',
            video_count=video_count,
            duration_seconds=duration_seconds,
            total_cost=total_cost,
            metadata=metadata or {}
        )
        
        # 更新缓存统计
        self._update_cache_stats(provider.id, user_id, total_cost)
        
        return {
            'record_id': str(record.id),
            'video_count': video_count,
            'duration_seconds': duration_seconds,
            'cost': float(total_cost),
            'currency': 'USD'
        }
    
    def get_user_statistics(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        获取用户的使用统计
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 统计信息
        """
        from apps.models.models import ModelUsageRecord
        
        # 构建查询
        query = Q(user_id=user_id)
        if start_date:
            query &= Q(created_at__gte=start_date)
        if end_date:
            query &= Q(created_at__lte=end_date)
        
        records = ModelUsageRecord.objects.filter(query)
        
        # 总成本
        total_cost = records.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
        
        # 按类型统计
        llm_stats = records.filter(usage_type='llm').aggregate(
            count=Count('id'),
            input_tokens=Sum('input_tokens'),
            output_tokens=Sum('output_tokens'),
            cost=Sum('total_cost')
        )
        
        image_stats = records.filter(usage_type='text2image').aggregate(
            count=Count('id'),
            images=Sum('image_count'),
            cost=Sum('total_cost')
        )
        
        video_stats = records.filter(usage_type='image2video').aggregate(
            count=Count('id'),
            videos=Sum('video_count'),
            cost=Sum('total_cost')
        )
        
        return {
            'total_cost': float(total_cost),
            'currency': 'USD',
            'period': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            },
            'llm': {
                'requests': llm_stats['count'] or 0,
                'input_tokens': llm_stats['input_tokens'] or 0,
                'output_tokens': llm_stats['output_tokens'] or 0,
                'cost': float(llm_stats['cost'] or 0)
            },
            'text2image': {
                'requests': image_stats['count'] or 0,
                'images': image_stats['images'] or 0,
                'cost': float(image_stats['cost'] or 0)
            },
            'image2video': {
                'requests': video_stats['count'] or 0,
                'videos': video_stats['videos'] or 0,
                'cost': float(video_stats['cost'] or 0)
            }
        }
    
    def get_provider_statistics(
        self,
        provider_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        获取模型提供商的使用统计
        
        Args:
            provider_id: 提供商ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 统计信息
        """
        from apps.models.models import ModelUsageRecord
        
        # 构建查询
        query = Q(provider_id=provider_id)
        if start_date:
            query &= Q(created_at__gte=start_date)
        if end_date:
            query &= Q(created_at__lte=end_date)
        
        records = ModelUsageRecord.objects.filter(query)
        
        # 总统计
        total_stats = records.aggregate(
            total_requests=Count('id'),
            total_cost=Sum('total_cost')
        )
        
        # 按用户统计
        user_stats = records.values('user_id').annotate(
            requests=Count('id'),
            cost=Sum('total_cost')
        ).order_by('-cost')[:10]  # Top 10用户
        
        return {
            'provider_id': provider_id,
            'total_requests': total_stats['total_requests'] or 0,
            'total_cost': float(total_stats['total_cost'] or 0),
            'currency': 'USD',
            'top_users': [
                {
                    'user_id': stat['user_id'],
                    'requests': stat['requests'],
                    'cost': float(stat['cost'])
                }
                for stat in user_stats
            ]
        }
    
    def get_project_cost(self, project_id: str) -> Dict:
        """
        获取项目的总成本
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict: 成本信息
        """
        from apps.models.models import ModelUsageRecord
        
        records = ModelUsageRecord.objects.filter(project_id=project_id)
        
        total_cost = records.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
        
        # 按类型分组
        breakdown = records.values('usage_type').annotate(
            cost=Sum('total_cost')
        )
        
        return {
            'project_id': project_id,
            'total_cost': float(total_cost),
            'currency': 'USD',
            'breakdown': {
                item['usage_type']: float(item['cost'])
                for item in breakdown
            }
        }
    
    def _update_cache_stats(self, provider_id: str, user_id: int, cost: Decimal):
        """更新缓存中的统计数据"""
        # 更新提供商统计
        provider_key = f'cost_stats:provider:{provider_id}'
        provider_stats = cache.get(provider_key, {'requests': 0, 'cost': 0})
        provider_stats['requests'] += 1
        provider_stats['cost'] += float(cost)
        cache.set(provider_key, provider_stats, self.cache_timeout)
        
        # 更新用户统计
        user_key = f'cost_stats:user:{user_id}'
        user_stats = cache.get(user_key, {'requests': 0, 'cost': 0})
        user_stats['requests'] += 1
        user_stats['cost'] += float(cost)
        cache.set(user_key, user_stats, self.cache_timeout)
