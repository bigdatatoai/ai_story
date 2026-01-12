"""
用户权限管理系统
实现基于角色的访问控制(RBAC)
"""

from rest_framework import permissions
from django.contrib.auth.models import Group
from functools import wraps
from django.http import JsonResponse


class UserRole:
    """用户角色定义"""
    ADMIN = 'admin'
    PREMIUM = 'premium'
    REGULAR = 'regular'
    GUEST = 'guest'
    
    CHOICES = [
        (ADMIN, '管理员'),
        (PREMIUM, '高级用户'),
        (REGULAR, '普通用户'),
        (GUEST, '访客'),
    ]
    
    # 角色权限映射
    PERMISSIONS = {
        ADMIN: {
            'can_manage_users': True,
            'can_review_content': True,
            'can_configure_system': True,
            'can_view_analytics': True,
            'can_export_data': True,
            'daily_generation_limit': -1,  # 无限制
            'can_use_premium_features': True,
            'can_batch_generate': True,
            'max_batch_size': 100,
        },
        PREMIUM: {
            'can_manage_users': False,
            'can_review_content': False,
            'can_configure_system': False,
            'can_view_analytics': False,
            'can_export_data': True,
            'daily_generation_limit': 100,
            'can_use_premium_features': True,
            'can_batch_generate': True,
            'max_batch_size': 20,
        },
        REGULAR: {
            'can_manage_users': False,
            'can_review_content': False,
            'can_configure_system': False,
            'can_view_analytics': False,
            'can_export_data': True,
            'daily_generation_limit': 10,
            'can_use_premium_features': False,
            'can_batch_generate': False,
            'max_batch_size': 1,
        },
        GUEST: {
            'can_manage_users': False,
            'can_review_content': False,
            'can_configure_system': False,
            'can_view_analytics': False,
            'can_export_data': False,
            'daily_generation_limit': 3,
            'can_use_premium_features': False,
            'can_batch_generate': False,
            'max_batch_size': 1,
        },
    }


class IsAdminUser(permissions.BasePermission):
    """管理员权限"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == UserRole.ADMIN
        )


class IsPremiumUser(permissions.BasePermission):
    """高级用户权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        return request.user.profile.role in [UserRole.ADMIN, UserRole.PREMIUM]


class CanReviewContent(permissions.BasePermission):
    """内容审核权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        role = request.user.profile.role
        return UserRole.PERMISSIONS.get(role, {}).get('can_review_content', False)


class CanConfigureSystem(permissions.BasePermission):
    """系统配置权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        role = request.user.profile.role
        return UserRole.PERMISSIONS.get(role, {}).get('can_configure_system', False)


def check_permission(permission_name):
    """
    权限检查装饰器
    
    Usage:
        @check_permission('can_batch_generate')
        def my_view(request):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': '请先登录',
                    'error_code': 'AUTHENTICATION_REQUIRED',
                }, status=401)
            
            if not hasattr(request.user, 'profile'):
                return JsonResponse({
                    'success': False,
                    'error': '用户配置不完整',
                    'error_code': 'PROFILE_MISSING',
                }, status=403)
            
            role = request.user.profile.role
            permissions = UserRole.PERMISSIONS.get(role, {})
            
            if not permissions.get(permission_name, False):
                return JsonResponse({
                    'success': False,
                    'error': '权限不足',
                    'error_code': 'PERMISSION_DENIED',
                    'required_permission': permission_name,
                }, status=403)
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def check_daily_limit(user):
    """
    检查用户每日生成限制
    
    Returns:
        dict: {
            'allowed': bool,
            'limit': int,
            'used': int,
            'remaining': int
        }
    """
    from django.core.cache import cache
    from datetime import datetime
    
    if not hasattr(user, 'profile'):
        return {
            'allowed': False,
            'limit': 0,
            'used': 0,
            'remaining': 0,
        }
    
    role = user.profile.role
    limit = UserRole.PERMISSIONS.get(role, {}).get('daily_generation_limit', 0)
    
    # 无限制
    if limit == -1:
        return {
            'allowed': True,
            'limit': -1,
            'used': 0,
            'remaining': -1,
        }
    
    # 获取今日使用次数
    today = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"daily_limit:{user.id}:{today}"
    used = cache.get(cache_key, 0)
    
    remaining = max(0, limit - used)
    allowed = used < limit
    
    return {
        'allowed': allowed,
        'limit': limit,
        'used': used,
        'remaining': remaining,
    }


def increment_daily_usage(user):
    """增加用户每日使用次数"""
    from django.core.cache import cache
    from datetime import datetime, timedelta
    
    today = datetime.now().strftime('%Y-%m-%d')
    cache_key = f"daily_limit:{user.id}:{today}"
    
    # 获取当前计数
    current = cache.get(cache_key, 0)
    
    # 增加计数
    cache.set(cache_key, current + 1, timeout=86400)  # 24小时过期
    
    return current + 1


class DailyLimitPermission(permissions.BasePermission):
    """每日限制权限检查"""
    
    message = '今日生成次数已达上限'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        limit_info = check_daily_limit(request.user)
        
        if not limit_info['allowed']:
            self.message = f"今日生成次数已达上限({limit_info['limit']}次)，请明日再试或升级账户"
            return False
        
        return True


def get_user_permissions(user):
    """
    获取用户所有权限
    
    Returns:
        dict: 用户权限字典
    """
    if not hasattr(user, 'profile'):
        return UserRole.PERMISSIONS.get(UserRole.GUEST, {})
    
    role = user.profile.role
    return UserRole.PERMISSIONS.get(role, UserRole.PERMISSIONS[UserRole.GUEST])


def can_user_perform(user, action):
    """
    检查用户是否可以执行某个操作
    
    Args:
        user: 用户对象
        action: 操作名称
    
    Returns:
        bool: 是否允许
    """
    permissions = get_user_permissions(user)
    return permissions.get(action, False)
