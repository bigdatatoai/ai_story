"""
统一响应格式
职责: 标准化API响应结构
"""

from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data=None, message="操作成功", code=200, status_code=status.HTTP_200_OK):
        """成功响应"""
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'success': True
        }, status=status_code)
    
    @staticmethod
    def error(message="操作失败", code=400, data=None, status_code=status.HTTP_400_BAD_REQUEST):
        """错误响应"""
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'success': False
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="创建成功", code=201):
        """创建成功响应"""
        return APIResponse.success(data, message, code, status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(message="删除成功", code=204):
        """无内容响应"""
        return Response({
            'code': code,
            'message': message,
            'success': True
        }, status=status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def bad_request(message="请求参数错误", data=None):
        """请求参数错误"""
        return APIResponse.error(message, 400, data, status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def unauthorized(message="未授权访问", data=None):
        """未授权"""
        return APIResponse.error(message, 401, data, status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="禁止访问", data=None):
        """禁止访问"""
        return APIResponse.error(message, 403, data, status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message="资源不存在", data=None):
        """资源不存在"""
        return APIResponse.error(message, 404, data, status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def server_error(message="服务器内部错误", data=None):
        """服务器错误"""
        return APIResponse.error(message, 500, data, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def paginated(data, total, page, page_size, message="查询成功"):
        """分页响应"""
        return APIResponse.success({
            'items': data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }, message)
