"""
项目管理常量定义
职责: 集中管理项目状态、错误码等常量
"""

from enum import Enum


class ProjectStatus:
    """项目状态常量"""
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

    CHOICES = [
        (DRAFT, '草稿'),
        (PROCESSING, '处理中'),
        (COMPLETED, '已完成'),
        (FAILED, '失败'),
        (PAUSED, '已暂停'),
    ]

    # 可恢复的状态集合
    RESUMABLE_STATUSES = {PAUSED}
    
    # 可暂停的状态集合
    PAUSABLE_STATUSES = {PROCESSING}
    
    # 可执行阶段的状态集合
    EXECUTABLE_STATUSES = {DRAFT, PROCESSING, PAUSED}


class StageStatus:
    """阶段状态常量"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    CHOICES = [
        (PENDING, '待处理'),
        (PROCESSING, '处理中'),
        (COMPLETED, '已完成'),
        (FAILED, '失败'),
    ]

    # 可恢复执行的阶段状态
    RESUMABLE_STATUSES = {PENDING, FAILED}


class StageType:
    """阶段类型常量"""
    REWRITE = "rewrite"
    STORYBOARD = "storyboard"
    IMAGE_GENERATION = "image_generation"
    CAMERA_MOVEMENT = "camera_movement"
    VIDEO_GENERATION = "video_generation"

    CHOICES = [
        (REWRITE, '文案改写'),
        (STORYBOARD, '分镜生成'),
        (IMAGE_GENERATION, '文生图'),
        (CAMERA_MOVEMENT, '运镜生成'),
        (VIDEO_GENERATION, '图生视频'),
    ]

    # LLM类阶段
    LLM_STAGES = {REWRITE, STORYBOARD, CAMERA_MOVEMENT}
    
    # 阶段执行顺序
    EXECUTION_ORDER = [
        REWRITE,
        STORYBOARD,
        IMAGE_GENERATION,
        CAMERA_MOVEMENT,
        VIDEO_GENERATION,
    ]


class ErrorCode:
    """错误码定义"""
    # 项目相关错误 (1xxx)
    PROJECT_NOT_FOUND = 1001
    PROJECT_INVALID_STATUS = 1002
    PROJECT_NOT_RESUMABLE = 1003
    PROJECT_NOT_PAUSABLE = 1004
    PROJECT_NOT_EXPORTABLE = 1005
    
    # 阶段相关错误 (2xxx)
    STAGE_NOT_FOUND = 2001
    STAGE_INVALID_STATUS = 2002
    STAGE_MAX_RETRIES_EXCEEDED = 2003
    STAGE_ALREADY_PROCESSING = 2004
    STAGE_NO_RESUMABLE = 2005
    
    # 任务相关错误 (3xxx)
    TASK_START_FAILED = 3001
    TASK_CANCEL_FAILED = 3002
    TASK_NOT_FOUND = 3003
    
    # 数据相关错误 (4xxx)
    DATA_VALIDATION_FAILED = 4001
    DATA_MISSING_REQUIRED = 4002
    
    # 系统错误 (5xxx)
    SYSTEM_ERROR = 5000
    DATABASE_ERROR = 5001
    TRANSACTION_FAILED = 5002


class ErrorMessage:
    """错误消息模板"""
    # 项目相关
    PROJECT_NOT_FOUND = "项目不存在"
    PROJECT_ONLY_PAUSED_CAN_RESUME = "只有暂停的项目才能恢复"
    PROJECT_ONLY_PROCESSING_CAN_PAUSE = "只有处理中的项目才能暂停"
    PROJECT_ONLY_COMPLETED_CAN_EXPORT = "只有完成的项目才能导出"
    PROJECT_ALREADY_COMPLETED = "项目已完成，所有阶段已执行完毕"
    
    # 阶段相关
    STAGE_NOT_FOUND = "阶段 {stage_name} 不存在"
    STAGE_MAX_RETRIES = "阶段 {stage_name} 已达到最大重试次数 ({max_retries})"
    STAGE_ALREADY_PROCESSING = "阶段 {stage_name} 正在处理中"
    STAGE_UNKNOWN_TYPE = "未知阶段类型: {stage_name}"
    
    # 任务相关
    TASK_START_FAILED = "启动任务失败: {error}"
    TASK_CANCEL_FAILED = "取消任务失败: {error}"
    
    # 系统错误
    SYSTEM_ERROR = "系统错误，请稍后重试"
    DATABASE_ERROR = "数据库操作失败: {error}"
    TRANSACTION_FAILED = "事务执行失败，操作已回滚"
