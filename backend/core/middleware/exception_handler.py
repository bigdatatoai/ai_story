"""
全局异常处理中间件
职责: 捕获并统一处理所有异常
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import APIException, ValidationError
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from core.response import APIResponse
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    
    # 先调用DRF默认的异常处理器
    response = drf_exception_handler(exc, context)
    
    # 记录异常日志
    request = context.get('request')
    view = context.get('view')
    
    log_message = f"异常: {exc.__class__.__name__} - {str(exc)}"
    if request:
        log_message += f" | 路径: {request.path} | 方法: {request.method}"
    if view:
        log_message += f" | 视图: {view.__class__.__name__}"
    
    # DRF已处理的异常
    if response is not None:
        logger.warning(log_message)
        
        # 统一响应格式
        error_data = {
            'code': response.status_code,
            'message': _get_error_message(exc, response.data),
            'data': response.data if isinstance(response.data, dict) else {'detail': response.data},
            'success': False
        }
        response.data = error_data
        return response
    
    # 处理Django原生异常
    if isinstance(exc, Http404) or isinstance(exc, ObjectDoesNotExist):
        logger.warning(log_message)
        return APIResponse.not_found(message=str(exc) or "资源不存在")
    
    if isinstance(exc, PermissionDenied):
        logger.warning(log_message)
        return APIResponse.forbidden(message=str(exc) or "权限不足")
    
    # 处理未捕获的异常
    logger.error(log_message, exc_info=True)
    
    # 生产环境隐藏详细错误信息
    from django.conf import settings
    if settings.DEBUG:
        error_message = f"{exc.__class__.__name__}: {str(exc)}"
    else:
        error_message = "服务器内部错误，请稍后重试"
    
    return APIResponse.server_error(message=error_message)


def _get_error_message(exc, data):
    """提取错误消息"""
    if isinstance(exc, ValidationError):
        if isinstance(data, dict):
            # 提取第一个字段的错误信息
            for field, errors in data.items():
                if isinstance(errors, list) and errors:
                    return f"{field}: {errors[0]}"
                return str(errors)
        elif isinstance(data, list) and data:
            return str(data[0])
    
    return str(exc) or "请求处理失败"


class ExceptionLoggingMiddleware:
    """异常日志中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """处理视图中未捕获的异常"""
        logger.error(
            f"未捕获异常: {exception.__class__.__name__} - {str(exception)} | "
            f"路径: {request.path} | 方法: {request.method}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
            }
        )
        return None
