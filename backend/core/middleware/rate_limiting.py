"""
API速率限制中间件
防止接口被恶意刷新和过载
"""

import time
import hashlib
import logging
from typing import Optional, Callable
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('ai_story.api')


class RateLimitMiddleware:
    """速率限制中间件"""
    
    # 默认速率限制配置
    DEFAULT_LIMITS = {
        'default': {'requests': 60, 'window': 60},  # 每分钟60次
        'story_generation': {'requests': 10, 'window': 60},  # 每分钟10次
        'story_export': {'requests': 20, 'window': 60},  # 每分钟20次
    }
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.enabled = getattr(settings, 'RATE_LIMIT_ENABLED', True)
    
    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)
        
        # 检查速率限制
        rate_limit_result = self.check_rate_limit(request)
        
        if not rate_limit_result['allowed']:
            return JsonResponse({
                'success': False,
                'error': '请求过于频繁，请稍后再试',
                'error_code': 'RATE_LIMIT_EXCEEDED',
                'retry_after': rate_limit_result['retry_after'],
                'limit': rate_limit_result['limit'],
                'remaining': 0,
            }, status=429)
        
        # 继续处理请求
        response = self.get_response(request)
        
        # 添加速率限制头部
        response['X-RateLimit-Limit'] = rate_limit_result['limit']
        response['X-RateLimit-Remaining'] = rate_limit_result['remaining']
        response['X-RateLimit-Reset'] = rate_limit_result['reset_time']
        
        return response
    
    def check_rate_limit(self, request) -> dict:
        """
        检查速率限制
        
        Returns:
            dict: {
                'allowed': bool,
                'limit': int,
                'remaining': int,
                'reset_time': int,
                'retry_after': int
            }
        """
        # 获取限制配置
        limit_config = self.get_limit_config(request)
        
        # 生成限制键
        limit_key = self.generate_limit_key(request, limit_config['name'])
        
        # 获取当前计数
        current_count = cache.get(limit_key, 0)
        
        # 检查是否超限
        allowed = current_count < limit_config['requests']
        
        if allowed:
            # 增加计数
            if current_count == 0:
                # 首次请求，设置过期时间
                cache.set(limit_key, 1, limit_config['window'])
            else:
                # 增加计数
                cache.incr(limit_key)
            
            current_count += 1
        
        # 计算剩余次数和重置时间
        remaining = max(0, limit_config['requests'] - current_count)
        ttl = cache.ttl(limit_key) or limit_config['window']
        reset_time = int(time.time()) + ttl
        retry_after = ttl if not allowed else 0
        
        return {
            'allowed': allowed,
            'limit': limit_config['requests'],
            'remaining': remaining,
            'reset_time': reset_time,
            'retry_after': retry_after,
        }
    
    def get_limit_config(self, request) -> dict:
        """获取请求的限制配置"""
        path = request.path
        
        # 根据路径确定限制类型
        if '/execute_stage/' in path or '/generate' in path:
            limit_type = 'story_generation'
        elif '/export' in path:
            limit_type = 'story_export'
        else:
            limit_type = 'default'
        
        config = self.DEFAULT_LIMITS.get(limit_type, self.DEFAULT_LIMITS['default'])
        
        return {
            'name': limit_type,
            **config
        }
    
    def generate_limit_key(self, request, limit_type: str) -> str:
        """生成限制键"""
        # 获取用户标识
        if request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            # 使用IP地址
            ip = self.get_client_ip(request)
            identifier = f"ip:{ip}"
        
        # 生成键
        key = f"rate_limit:{limit_type}:{identifier}"
        return key
    
    def get_client_ip(self, request) -> str:
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestIdempotencyMiddleware:
    """请求幂等性中间件"""
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.enabled = getattr(settings, 'IDEMPOTENCY_ENABLED', True)
        self.cache_ttl = 3600  # 1小时
    
    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)
        
        # 只处理POST/PUT/PATCH请求
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return self.get_response(request)
        
        # 获取幂等性键
        idempotency_key = request.headers.get('X-Idempotency-Key')
        
        if not idempotency_key:
            # 没有幂等性键，正常处理
            return self.get_response(request)
        
        # 检查是否已处理过
        cache_key = f"idempotency:{idempotency_key}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info(f"返回缓存的幂等性响应: {idempotency_key}")
            return JsonResponse(cached_response)
        
        # 处理请求
        response = self.get_response(request)
        
        # 缓存响应（仅缓存成功的响应）
        if response.status_code < 400:
            try:
                import json
                response_data = json.loads(response.content)
                cache.set(cache_key, response_data, self.cache_ttl)
            except Exception as e:
                logger.warning(f"无法缓存幂等性响应: {str(e)}")
        
        return response


def rate_limit_decorator(
    requests: int = 60,
    window: int = 60,
    key_func: Optional[Callable] = None
):
    """
    速率限制装饰器
    
    Args:
        requests: 时间窗口内允许的请求数
        window: 时间窗口（秒）
        key_func: 自定义键生成函数
    
    Example:
        @rate_limit_decorator(requests=10, window=60)
        def my_view(request):
            pass
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            # 生成限制键
            if key_func:
                limit_key = key_func(request)
            else:
                # 默认使用用户ID或IP
                if request.user.is_authenticated:
                    identifier = f"user:{request.user.id}"
                else:
                    ip = request.META.get('REMOTE_ADDR')
                    identifier = f"ip:{ip}"
                
                limit_key = f"rate_limit:{func.__name__}:{identifier}"
            
            # 检查限制
            current_count = cache.get(limit_key, 0)
            
            if current_count >= requests:
                ttl = cache.ttl(limit_key) or window
                return JsonResponse({
                    'success': False,
                    'error': '请求过于频繁，请稍后再试',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': ttl,
                }, status=429)
            
            # 增加计数
            if current_count == 0:
                cache.set(limit_key, 1, window)
            else:
                cache.incr(limit_key)
            
            # 执行函数
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


class RequestDeduplicationMiddleware:
    """请求去重中间件"""
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.enabled = getattr(settings, 'REQUEST_DEDUP_ENABLED', True)
        self.dedup_window = 5  # 5秒内的重复请求会被拒绝
    
    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)
        
        # 只处理POST请求
        if request.method != 'POST':
            return self.get_response(request)
        
        # 生成请求指纹
        fingerprint = self.generate_request_fingerprint(request)
        
        # 检查是否重复
        dedup_key = f"request_dedup:{fingerprint}"
        if cache.get(dedup_key):
            logger.warning(f"检测到重复请求: {fingerprint}")
            return JsonResponse({
                'success': False,
                'error': '检测到重复请求，请勿重复提交',
                'error_code': 'DUPLICATE_REQUEST',
            }, status=409)
        
        # 标记请求
        cache.set(dedup_key, True, self.dedup_window)
        
        # 处理请求
        response = self.get_response(request)
        
        return response
    
    def generate_request_fingerprint(self, request) -> str:
        """生成请求指纹"""
        # 获取用户标识
        if request.user.is_authenticated:
            user_id = str(request.user.id)
        else:
            user_id = request.META.get('REMOTE_ADDR', 'anonymous')
        
        # 获取请求体
        try:
            body = request.body.decode('utf-8')
        except:
            body = ''
        
        # 生成指纹
        fingerprint_data = f"{user_id}:{request.path}:{body}"
        fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
        
        return fingerprint
