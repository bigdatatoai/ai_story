"""
缓存工具类
职责: 提供统一的缓存操作接口
"""

from django.core.cache import cache
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    # 缓存键前缀
    PREFIX_MODEL_PROVIDER = 'model_provider'
    PREFIX_PROJECT_STAGES = 'project_stages'
    PREFIX_STORYBOARD_COUNT = 'storyboard_count'
    PREFIX_CAMERA_MOVEMENT = 'camera_movement'
    
    # 缓存过期时间（秒）
    TIMEOUT_SHORT = 300  # 5分钟
    TIMEOUT_MEDIUM = 1800  # 30分钟
    TIMEOUT_LONG = 3600  # 1小时
    TIMEOUT_DAY = 86400  # 24小时
    
    @classmethod
    def get_model_provider_name(cls, provider_id):
        """获取模型提供商名称（带缓存）"""
        cache_key = f'{cls.PREFIX_MODEL_PROVIDER}_name_{provider_id}'
        name = cache.get(cache_key)
        
        if name is None:
            try:
                from apps.models.models import ModelProvider
                provider = ModelProvider.objects.filter(id=provider_id).first()
                name = provider.name if provider else None
                cache.set(cache_key, name, cls.TIMEOUT_LONG)
            except Exception as e:
                logger.warning(f"查询模型提供商名称失败: {str(e)}")
                name = None
        
        return name
    
    @classmethod
    def get_project_stages_count(cls, project_id):
        """获取项目阶段数量（带缓存）"""
        cache_key = f'{cls.PREFIX_PROJECT_STAGES}_count_{project_id}'
        count = cache.get(cache_key)
        
        if count is None:
            try:
                from apps.projects.models import ProjectStage
                count = ProjectStage.objects.filter(project_id=project_id).count()
                cache.set(cache_key, count, cls.TIMEOUT_SHORT)
            except Exception as e:
                logger.warning(f"查询项目阶段数量失败: {str(e)}")
                count = 0
        
        return count
    
    @classmethod
    def clear_project_cache(cls, project_id):
        """清除项目相关缓存"""
        cache.delete(f'{cls.PREFIX_PROJECT_STAGES}_count_{project_id}')
        cache.delete(f'{cls.PREFIX_PROJECT_STAGES}_completed_{project_id}')
        logger.info(f"已清除项目缓存: {project_id}")
    
    @classmethod
    def clear_storyboard_cache(cls, storyboard_id):
        """清除分镜相关缓存"""
        cache.delete(f'{cls.PREFIX_STORYBOARD_COUNT}_images_{storyboard_id}')
        cache.delete(f'{cls.PREFIX_STORYBOARD_COUNT}_videos_{storyboard_id}')
        logger.info(f"已清除分镜缓存: {storyboard_id}")
    
    @classmethod
    def clear_all_cache(cls):
        """清除所有缓存"""
        cache.clear()
        logger.warning("已清除所有缓存")


def cache_result(timeout=CacheManager.TIMEOUT_MEDIUM, key_prefix=''):
    """
    缓存装饰器
    
    Args:
        timeout: 缓存过期时间（秒）
        key_prefix: 缓存键前缀
    
    Usage:
        @cache_result(timeout=300, key_prefix='user_profile')
        def get_user_profile(user_id):
            return User.objects.get(id=user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存键
            cache_key = f'{key_prefix}_{func.__name__}'
            if args:
                cache_key += f'_{"_".join(str(arg) for arg in args)}'
            if kwargs:
                cache_key += f'_{"_".join(f"{k}_{v}" for k, v in sorted(kwargs.items()))}'
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"缓存设置: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_pattern):
    """
    清除匹配模式的缓存
    
    Args:
        key_pattern: 缓存键模式（支持通配符）
    """
    try:
        # Django默认缓存不支持模式匹配删除
        # 需要使用Redis等支持的缓存后端
        from django.core.cache import caches
        redis_cache = caches['default']
        
        if hasattr(redis_cache, 'delete_pattern'):
            deleted = redis_cache.delete_pattern(key_pattern)
            logger.info(f"清除缓存: {key_pattern}, 删除数量: {deleted}")
        else:
            logger.warning(f"当前缓存后端不支持模式删除: {key_pattern}")
    
    except Exception as e:
        logger.error(f"清除缓存失败: {str(e)}")
