"""
项目管理自定义异常
职责: 定义业务逻辑异常，提供结构化错误信息
"""

from rest_framework.exceptions import APIException
from rest_framework import status
from .constants import ErrorCode, ErrorMessage


class ProjectBaseException(APIException):
    """项目管理基础异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ErrorCode.SYSTEM_ERROR
    default_detail = ErrorMessage.SYSTEM_ERROR

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if status_code is not None:
            self.status_code = status_code
        
        super().__init__(detail={"error": detail, "code": code})


class ProjectNotFoundException(ProjectBaseException):
    """项目不存在异常"""
    default_code = ErrorCode.PROJECT_NOT_FOUND
    default_detail = ErrorMessage.PROJECT_NOT_FOUND


class ProjectInvalidStatusException(ProjectBaseException):
    """项目状态无效异常"""
    default_code = ErrorCode.PROJECT_INVALID_STATUS
    
    def __init__(self, message=None, **kwargs):
        super().__init__(detail=message or self.default_detail, **kwargs)


class ProjectNotResumableException(ProjectBaseException):
    """项目不可恢复异常"""
    default_code = ErrorCode.PROJECT_NOT_RESUMABLE
    default_detail = ErrorMessage.PROJECT_ONLY_PAUSED_CAN_RESUME


class ProjectNotPausableException(ProjectBaseException):
    """项目不可暂停异常"""
    default_code = ErrorCode.PROJECT_NOT_PAUSABLE
    default_detail = ErrorMessage.PROJECT_ONLY_PROCESSING_CAN_PAUSE


class StageNotFoundException(ProjectBaseException):
    """阶段不存在异常"""
    default_code = ErrorCode.STAGE_NOT_FOUND
    
    def __init__(self, stage_name=None, **kwargs):
        detail = ErrorMessage.STAGE_NOT_FOUND.format(stage_name=stage_name) if stage_name else "阶段不存在"
        super().__init__(detail=detail, **kwargs)


class StageMaxRetriesExceededException(ProjectBaseException):
    """阶段超过最大重试次数异常"""
    default_code = ErrorCode.STAGE_MAX_RETRIES_EXCEEDED
    
    def __init__(self, stage_name=None, max_retries=3, **kwargs):
        detail = ErrorMessage.STAGE_MAX_RETRIES.format(
            stage_name=stage_name, 
            max_retries=max_retries
        ) if stage_name else "阶段已达到最大重试次数"
        super().__init__(detail=detail, **kwargs)


class TaskStartFailedException(ProjectBaseException):
    """任务启动失败异常"""
    default_code = ErrorCode.TASK_START_FAILED
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(self, error=None, **kwargs):
        detail = ErrorMessage.TASK_START_FAILED.format(error=error) if error else "任务启动失败"
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, **kwargs)


class DatabaseException(ProjectBaseException):
    """数据库操作异常"""
    default_code = ErrorCode.DATABASE_ERROR
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(self, error=None, **kwargs):
        detail = ErrorMessage.DATABASE_ERROR.format(error=error) if error else "数据库操作失败"
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, **kwargs)
