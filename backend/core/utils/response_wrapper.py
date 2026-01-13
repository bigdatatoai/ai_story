"""
统一响应格式包装器
确保所有API返回格式一致
"""

from rest_framework.response import Response
from rest_framework import status
from typing import Any, Optional, Dict


class ErrorCode:
    """统一错误码定义"""
    
    # 通用错误 (1000-1999)
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    INVALID_PARAMS = 1001
    MISSING_PARAMS = 1002
    INVALID_REQUEST = 1003
    
    # 认证授权错误 (2000-2999)
    UNAUTHORIZED = 2000
    TOKEN_EXPIRED = 2001
    TOKEN_INVALID = 2002
    PERMISSION_DENIED = 2003
    
    # 业务错误 (3000-3999)
    RESOURCE_NOT_FOUND = 3000
    RESOURCE_ALREADY_EXISTS = 3001
    OPERATION_FAILED = 3002
    
    # 故事生成错误 (4000-4999)
    STORY_GENERATION_FAILED = 4000
    STORY_QUALITY_LOW = 4001
    STORY_NOT_FOUND = 4002
    
    # 视频生成错误 (5000-5999)
    VIDEO_GENERATION_FAILED = 5000
    VIDEO_NOT_FOUND = 5001
    VIDEO_PROCESSING = 5002
    
    # 速率限制错误 (6000-6999)
    RATE_LIMIT_EXCEEDED = 6000
    DUPLICATE_REQUEST = 6001
    
    # 系统错误 (9000-9999)
    INTERNAL_ERROR = 9000
    SERVICE_UNAVAILABLE = 9001
    DATABASE_ERROR = 9002


class ErrorMessage:
    """错误消息映射"""
    
    MESSAGES = {
        ErrorCode.SUCCESS: '成功',
        ErrorCode.UNKNOWN_ERROR: '未知错误',
        ErrorCode.INVALID_PARAMS: '参数格式错误',
        ErrorCode.MISSING_PARAMS: '缺少必填参数',
        ErrorCode.INVALID_REQUEST: '无效的请求',
        
        ErrorCode.UNAUTHORIZED: '未授权，请先登录',
        ErrorCode.TOKEN_EXPIRED: 'Token已过期',
        ErrorCode.TOKEN_INVALID: 'Token无效',
        ErrorCode.PERMISSION_DENIED: '权限不足',
        
        ErrorCode.RESOURCE_NOT_FOUND: '资源不存在',
        ErrorCode.RESOURCE_ALREADY_EXISTS: '资源已存在',
        ErrorCode.OPERATION_FAILED: '操作失败',
        
        ErrorCode.STORY_GENERATION_FAILED: '故事生成失败',
        ErrorCode.STORY_QUALITY_LOW: '故事质量不达标',
        ErrorCode.STORY_NOT_FOUND: '故事不存在',
        
        ErrorCode.VIDEO_GENERATION_FAILED: '视频生成失败',
        ErrorCode.VIDEO_NOT_FOUND: '视频不存在',
        ErrorCode.VIDEO_PROCESSING: '视频正在处理中',
        
        ErrorCode.RATE_LIMIT_EXCEEDED: '请求过于频繁，请稍后再试',
        ErrorCode.DUPLICATE_REQUEST: '检测到重复请求',
        
        ErrorCode.INTERNAL_ERROR: '服务器内部错误',
        ErrorCode.SERVICE_UNAVAILABLE: '服务暂时不可用',
        ErrorCode.DATABASE_ERROR: '数据库错误',
    }
    
    @classmethod
    def get(cls, code: int, default: str = '未知错误') -> str:
        return cls.MESSAGES.get(code, default)


class APIResponse:
    """统一API响应包装器"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = '操作成功',
        code: int = ErrorCode.SUCCESS,
        http_status: int = status.HTTP_200_OK,
        **kwargs
    ) -> Response:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 成功消息
            code: 业务状态码
            http_status: HTTP状态码
            **kwargs: 其他额外字段
        
        Returns:
            Response对象
        """
        response_data = {
            'success': True,
            'code': code,
            'message': message,
            'data': data,
        }
        response_data.update(kwargs)
        return Response(response_data, status=http_status)
    
    @staticmethod
    def error(
        message: str = None,
        code: int = ErrorCode.UNKNOWN_ERROR,
        data: Any = None,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        **kwargs
    ) -> Response:
        """
        错误响应
        
        Args:
            message: 错误消息（如果为None，从ErrorMessage获取）
            code: 错误码
            data: 错误详情数据
            http_status: HTTP状态码
            **kwargs: 其他额外字段
        
        Returns:
            Response对象
        """
        if message is None:
            message = ErrorMessage.get(code)
        
        response_data = {
            'success': False,
            'code': code,
            'message': message,
            'error': message,  # 兼容旧格式
        }
        
        if data is not None:
            response_data['data'] = data
        
        response_data.update(kwargs)
        return Response(response_data, status=http_status)
    
    @staticmethod
    def paginated(
        results: list,
        count: int,
        next_url: Optional[str] = None,
        previous_url: Optional[str] = None,
        message: str = '获取成功',
        **kwargs
    ) -> Response:
        """
        分页响应
        
        Args:
            results: 结果列表
            count: 总数
            next_url: 下一页URL
            previous_url: 上一页URL
            message: 消息
            **kwargs: 其他额外字段
        
        Returns:
            Response对象
        """
        return APIResponse.success(
            data={
                'results': results,
                'count': count,
                'next': next_url,
                'previous': previous_url,
            },
            message=message,
            **kwargs
        )
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = '创建成功',
        **kwargs
    ) -> Response:
        """创建成功响应"""
        return APIResponse.success(
            data=data,
            message=message,
            http_status=status.HTTP_201_CREATED,
            **kwargs
        )
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = '更新成功',
        **kwargs
    ) -> Response:
        """更新成功响应"""
        return APIResponse.success(
            data=data,
            message=message,
            **kwargs
        )
    
    @staticmethod
    def deleted(
        message: str = '删除成功',
        **kwargs
    ) -> Response:
        """删除成功响应"""
        return APIResponse.success(
            message=message,
            **kwargs
        )
    
    @staticmethod
    def bad_request(
        message: str = None,
        code: int = ErrorCode.INVALID_PARAMS,
        data: Any = None,
        **kwargs
    ) -> Response:
        """400 错误请求"""
        return APIResponse.error(
            message=message,
            code=code,
            data=data,
            http_status=status.HTTP_400_BAD_REQUEST,
            **kwargs
        )
    
    @staticmethod
    def unauthorized(
        message: str = None,
        code: int = ErrorCode.UNAUTHORIZED,
        **kwargs
    ) -> Response:
        """401 未授权"""
        return APIResponse.error(
            message=message,
            code=code,
            http_status=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )
    
    @staticmethod
    def forbidden(
        message: str = None,
        code: int = ErrorCode.PERMISSION_DENIED,
        **kwargs
    ) -> Response:
        """403 禁止访问"""
        return APIResponse.error(
            message=message,
            code=code,
            http_status=status.HTTP_403_FORBIDDEN,
            **kwargs
        )
    
    @staticmethod
    def not_found(
        message: str = None,
        code: int = ErrorCode.RESOURCE_NOT_FOUND,
        **kwargs
    ) -> Response:
        """404 未找到"""
        return APIResponse.error(
            message=message,
            code=code,
            http_status=status.HTTP_404_NOT_FOUND,
            **kwargs
        )
    
    @staticmethod
    def server_error(
        message: str = None,
        code: int = ErrorCode.INTERNAL_ERROR,
        **kwargs
    ) -> Response:
        """500 服务器错误"""
        return APIResponse.error(
            message=message,
            code=code,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )
    
    @staticmethod
    def rate_limited(
        retry_after: int = 60,
        message: str = None,
        **kwargs
    ) -> Response:
        """429 速率限制"""
        return APIResponse.error(
            message=message,
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            http_status=status.HTTP_429_TOO_MANY_REQUESTS,
            retry_after=retry_after,
            **kwargs
        )
