"""
缓存管理工具
提供LLM响应缓存功能，减少重复API调用
"""

import hashlib
import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, prefix: str = 'llm:response:', ttl: int = 86400):
        """
        初始化缓存管理器
        
        Args:
            prefix: 缓存键前缀
            ttl: 缓存过期时间（秒），默认24小时
        """
        self.prefix = prefix
        self.ttl = ttl
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            缓存键
        """
        # 将参数序列化为JSON字符串
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        
        # 使用MD5生成哈希
        key_hash = hashlib.md5(key_string.encode('utf-8')).hexdigest()
        
        return f"{self.prefix}{key_hash}"
    
    def get(self, *args, **kwargs) -> Optional[Any]:
        """
        从缓存获取数据
        
        Args:
            *args: 用于生成缓存键的参数
            **kwargs: 用于生成缓存键的参数
        
        Returns:
            缓存的数据，如果不存在则返回None
        """
        cache_key = self._generate_cache_key(*args, **kwargs)
        
        try:
            data = cache.get(cache_key)
            if data is not None:
                logger.debug(f"缓存命中: {cache_key}")
            return data
        except Exception as e:
            logger.error(f"缓存读取失败: {str(e)}")
            return None
    
    def set(self, data: Any, *args, **kwargs) -> bool:
        """
        设置缓存数据
        
        Args:
            data: 要缓存的数据
            *args: 用于生成缓存键的参数
            **kwargs: 用于生成缓存键的参数
        
        Returns:
            是否成功设置缓存
        """
        cache_key = self._generate_cache_key(*args, **kwargs)
        
        try:
            cache.set(cache_key, data, self.ttl)
            logger.debug(f"缓存设置成功: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"缓存设置失败: {str(e)}")
            return False
    
    def delete(self, *args, **kwargs) -> bool:
        """
        删除缓存数据
        
        Args:
            *args: 用于生成缓存键的参数
            **kwargs: 用于生成缓存键的参数
        
        Returns:
            是否成功删除缓存
        """
        cache_key = self._generate_cache_key(*args, **kwargs)
        
        try:
            cache.delete(cache_key)
            logger.debug(f"缓存删除成功: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"缓存删除失败: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str = None) -> bool:
        """
        清除匹配模式的缓存
        
        Args:
            pattern: 缓存键模式，默认清除所有带前缀的缓存
        
        Returns:
            是否成功清除
        """
        try:
            if pattern is None:
                pattern = f"{self.prefix}*"
            
            # 注意：这个功能依赖于缓存后端的实现
            # Redis支持，但Memcached可能不支持
            cache.delete_pattern(pattern)
            logger.info(f"缓存清除成功: {pattern}")
            return True
        except AttributeError:
            logger.warning("当前缓存后端不支持模式删除")
            return False
        except Exception as e:
            logger.error(f"缓存清除失败: {str(e)}")
            return False


def cached_llm_response(
    cache_manager: CacheManager = None,
    ttl: Optional[int] = None,
    key_params: Optional[list] = None,
):
    """
    LLM响应缓存装饰器
    
    Args:
        cache_manager: 缓存管理器实例
        ttl: 缓存过期时间（秒）
        key_params: 用于生成缓存键的参数名列表
    
    Example:
        @cached_llm_response(ttl=3600, key_params=['prompt', 'model'])
        def call_llm(prompt, model='gpt-3.5-turbo', temperature=0.7):
            # LLM调用代码
            return response
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 使用默认缓存管理器
            _cache_manager = cache_manager or CacheManager()
            
            # 如果指定了TTL，更新缓存管理器的TTL
            if ttl is not None:
                _cache_manager.ttl = ttl
            
            # 提取用于缓存键的参数
            if key_params:
                cache_kwargs = {k: kwargs.get(k) for k in key_params if k in kwargs}
            else:
                cache_kwargs = kwargs
            
            # 尝试从缓存获取
            cached_result = _cache_manager.get(*args, **cache_kwargs)
            if cached_result is not None:
                logger.info(f"使用缓存的LLM响应: {func.__name__}")
                return cached_result
            
            # 缓存未命中，调用原函数
            logger.info(f"缓存未命中，调用LLM: {func.__name__}")
            result = func(*args, **kwargs)
            
            # 保存到缓存
            _cache_manager.set(result, *args, **cache_kwargs)
            
            return result
        
        return wrapper
    return decorator


class LLMCacheManager(CacheManager):
    """
    LLM专用缓存管理器
    提供更智能的缓存策略
    """
    
    def __init__(self, prefix: str = 'llm:response:', ttl: int = 86400):
        super().__init__(prefix, ttl)
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
        }
    
    def get_with_stats(self, *args, **kwargs) -> Optional[Any]:
        """
        获取缓存并更新统计信息
        """
        data = self.get(*args, **kwargs)
        
        if data is not None:
            self.stats['hits'] += 1
        else:
            self.stats['misses'] += 1
        
        return data
    
    def set_with_stats(self, data: Any, *args, **kwargs) -> bool:
        """
        设置缓存并更新统计信息
        """
        success = self.set(data, *args, **kwargs)
        
        if success:
            self.stats['sets'] += 1
        
        return success
    
    def get_cache_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            包含命中率等统计信息的字典
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.2f}%",
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
        }
    
    def cache_llm_response(
        self,
        stage_type: str,
        prompt: str,
        model: str,
        response: Any,
        **params
    ) -> bool:
        """
        缓存LLM响应
        
        Args:
            stage_type: 阶段类型
            prompt: 提示词
            model: 模型名称
            response: LLM响应
            **params: 其他参数（如temperature, max_tokens等）
        
        Returns:
            是否成功缓存
        """
        return self.set_with_stats(
            response,
            stage_type=stage_type,
            prompt=prompt,
            model=model,
            **params
        )
    
    def get_llm_response(
        self,
        stage_type: str,
        prompt: str,
        model: str,
        **params
    ) -> Optional[Any]:
        """
        获取缓存的LLM响应
        
        Args:
            stage_type: 阶段类型
            prompt: 提示词
            model: 模型名称
            **params: 其他参数
        
        Returns:
            缓存的响应，如果不存在则返回None
        """
        return self.get_with_stats(
            stage_type=stage_type,
            prompt=prompt,
            model=model,
            **params
        )


# 创建全局缓存管理器实例
llm_cache = LLMCacheManager()
