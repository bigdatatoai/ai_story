"""
负载均衡服务
职责: 实现多种负载均衡策略选择最优的模型提供商
"""

import random
from typing import List, Optional
from django.core.cache import cache
from apps.models.models import ModelProvider


class LoadBalancer:
    """负载均衡器"""
    
    STRATEGY_ROUND_ROBIN = 'round_robin'
    STRATEGY_RANDOM = 'random'
    STRATEGY_WEIGHTED = 'weighted'
    STRATEGY_LEAST_LOADED = 'least_loaded'
    
    def __init__(self, strategy: str = STRATEGY_WEIGHTED):
        """
        初始化负载均衡器
        
        Args:
            strategy: 负载均衡策略
        """
        self.strategy = strategy
    
    def select_provider(
        self,
        providers: List[ModelProvider],
        cache_key: Optional[str] = None
    ) -> Optional[ModelProvider]:
        """
        根据策略选择一个模型提供商
        
        Args:
            providers: 可用的模型提供商列表
            cache_key: 缓存键（用于轮询策略）
            
        Returns:
            ModelProvider: 选中的模型提供商，如果没有可用的返回None
        """
        if not providers:
            return None
        
        # 过滤出激活的提供商
        active_providers = [p for p in providers if p.is_active]
        
        if not active_providers:
            return None
        
        if len(active_providers) == 1:
            return active_providers[0]
        
        # 根据策略选择
        if self.strategy == self.STRATEGY_ROUND_ROBIN:
            return self._round_robin(active_providers, cache_key)
        elif self.strategy == self.STRATEGY_RANDOM:
            return self._random(active_providers)
        elif self.strategy == self.STRATEGY_WEIGHTED:
            return self._weighted(active_providers)
        elif self.strategy == self.STRATEGY_LEAST_LOADED:
            return self._least_loaded(active_providers)
        else:
            # 默认使用权重策略
            return self._weighted(active_providers)
    
    def _round_robin(
        self,
        providers: List[ModelProvider],
        cache_key: Optional[str]
    ) -> ModelProvider:
        """
        轮询策略
        
        Args:
            providers: 提供商列表
            cache_key: 缓存键
            
        Returns:
            ModelProvider: 选中的提供商
        """
        if not cache_key:
            cache_key = 'load_balancer:round_robin:default'
        
        # 从缓存获取当前索引
        current_index = cache.get(cache_key, 0)
        
        # 选择提供商
        provider = providers[current_index % len(providers)]
        
        # 更新索引
        cache.set(cache_key, (current_index + 1) % len(providers), timeout=3600)
        
        return provider
    
    def _random(self, providers: List[ModelProvider]) -> ModelProvider:
        """
        随机策略
        
        Args:
            providers: 提供商列表
            
        Returns:
            ModelProvider: 随机选中的提供商
        """
        return random.choice(providers)
    
    def _weighted(self, providers: List[ModelProvider]) -> ModelProvider:
        """
        权重随机策略
        
        Args:
            providers: 提供商列表
            
        Returns:
            ModelProvider: 按权重随机选中的提供商
        """
        # 获取所有提供商的权重
        weights = [p.priority for p in providers]
        
        # 如果所有权重都是0，使用均等权重
        if all(w == 0 for w in weights):
            weights = [1] * len(providers)
        
        # 按权重随机选择
        return random.choices(providers, weights=weights, k=1)[0]
    
    def _least_loaded(self, providers: List[ModelProvider]) -> ModelProvider:
        """
        最少负载策略（基于Redis计数器）
        
        Args:
            providers: 提供商列表
            
        Returns:
            ModelProvider: 当前负载最少的提供商
        """
        min_load = float('inf')
        selected_provider = providers[0]
        
        for provider in providers:
            # 从缓存获取当前负载
            load_key = f'load_balancer:load:{provider.id}'
            current_load = cache.get(load_key, 0)
            
            if current_load < min_load:
                min_load = current_load
                selected_provider = provider
        
        # 增加选中提供商的负载计数
        load_key = f'load_balancer:load:{selected_provider.id}'
        cache.incr(load_key)
        cache.expire(load_key, 300)  # 5分钟过期
        
        return selected_provider
    
    def release_provider(self, provider: ModelProvider):
        """
        释放提供商（减少负载计数）
        
        Args:
            provider: 提供商实例
        """
        if self.strategy == self.STRATEGY_LEAST_LOADED:
            load_key = f'load_balancer:load:{provider.id}'
            current_load = cache.get(load_key, 0)
            if current_load > 0:
                cache.decr(load_key)
    
    def get_provider_stats(self, provider: ModelProvider) -> dict:
        """
        获取提供商统计信息
        
        Args:
            provider: 提供商实例
            
        Returns:
            dict: 统计信息
        """
        load_key = f'load_balancer:load:{provider.id}'
        current_load = cache.get(load_key, 0)
        
        return {
            'provider_id': str(provider.id),
            'provider_name': provider.name,
            'current_load': current_load,
            'priority': provider.priority,
            'is_active': provider.is_active
        }
