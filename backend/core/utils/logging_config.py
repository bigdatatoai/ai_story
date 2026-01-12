"""
日志配置工具
提供统一的日志配置和管理
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


class LoggerConfig:
    """日志配置类"""
    
    # 日志级别映射
    LEVEL_MAP = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    
    # 日志格式
    DETAILED_FORMAT = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s'
    )
    
    SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    
    JSON_FORMAT = (
        '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", '
        '"file": "%(filename)s", "line": %(lineno)d, "function": "%(funcName)s", '
        '"message": "%(message)s"}'
    )
    
    @classmethod
    def setup_logger(
        cls,
        name: str,
        level: str = 'INFO',
        log_file: Optional[str] = None,
        console_output: bool = True,
        detailed: bool = False,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ) -> logging.Logger:
        """
        配置并返回日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            log_file: 日志文件路径
            console_output: 是否输出到控制台
            detailed: 是否使用详细格式
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的备份文件数量
        
        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(cls.LEVEL_MAP.get(level.upper(), logging.INFO))
        
        # 清除已有的处理器
        logger.handlers.clear()
        
        # 选择格式
        formatter = logging.Formatter(
            cls.DETAILED_FORMAT if detailed else cls.SIMPLE_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 文件处理器（带轮转）
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @classmethod
    def setup_app_loggers(cls, base_log_dir: str = 'logs'):
        """
        配置应用的所有日志记录器
        
        Args:
            base_log_dir: 日志基础目录
        """
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # 确保日志目录存在
        Path(base_log_dir).mkdir(parents=True, exist_ok=True)
        
        # 主应用日志
        cls.setup_logger(
            'ai_story',
            level=log_level,
            log_file=os.path.join(base_log_dir, 'app.log'),
            console_output=True,
            detailed=True,
        )
        
        # LLM调用日志
        cls.setup_logger(
            'ai_story.llm',
            level=log_level,
            log_file=os.path.join(base_log_dir, 'llm.log'),
            console_output=False,
            detailed=True,
        )
        
        # API请求日志
        cls.setup_logger(
            'ai_story.api',
            level=log_level,
            log_file=os.path.join(base_log_dir, 'api.log'),
            console_output=False,
            detailed=True,
        )
        
        # 错误日志
        cls.setup_logger(
            'ai_story.error',
            level='ERROR',
            log_file=os.path.join(base_log_dir, 'error.log'),
            console_output=True,
            detailed=True,
        )
        
        # Celery任务日志
        cls.setup_logger(
            'ai_story.celery',
            level=log_level,
            log_file=os.path.join(base_log_dir, 'celery.log'),
            console_output=False,
            detailed=True,
        )
        
        # 性能日志
        cls.setup_logger(
            'ai_story.performance',
            level='INFO',
            log_file=os.path.join(base_log_dir, 'performance.log'),
            console_output=False,
            detailed=False,
        )


class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, logger_name: str = 'ai_story.performance'):
        self.logger = logging.getLogger(logger_name)
    
    def log_api_call(
        self,
        endpoint: str,
        method: str,
        duration: float,
        status_code: int,
        user_id: Optional[str] = None,
    ):
        """
        记录API调用性能
        
        Args:
            endpoint: API端点
            method: HTTP方法
            duration: 请求耗时（秒）
            status_code: 响应状态码
            user_id: 用户ID
        """
        self.logger.info(
            f"API调用 - {method} {endpoint} - "
            f"耗时: {duration:.3f}s - 状态: {status_code} - 用户: {user_id or 'N/A'}"
        )
    
    def log_llm_call(
        self,
        model: str,
        stage_type: str,
        duration: float,
        tokens_used: Optional[int] = None,
        success: bool = True,
    ):
        """
        记录LLM调用性能
        
        Args:
            model: 模型名称
            stage_type: 阶段类型
            duration: 调用耗时（秒）
            tokens_used: 使用的token数
            success: 是否成功
        """
        status = "成功" if success else "失败"
        tokens_info = f"- Tokens: {tokens_used}" if tokens_used else ""
        
        self.logger.info(
            f"LLM调用 - 模型: {model} - 阶段: {stage_type} - "
            f"耗时: {duration:.3f}s - 状态: {status} {tokens_info}"
        )
    
    def log_task_execution(
        self,
        task_name: str,
        duration: float,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """
        记录任务执行性能
        
        Args:
            task_name: 任务名称
            duration: 执行耗时（秒）
            success: 是否成功
            error: 错误信息
        """
        status = "成功" if success else "失败"
        error_info = f"- 错误: {error}" if error else ""
        
        self.logger.info(
            f"任务执行 - {task_name} - "
            f"耗时: {duration:.3f}s - 状态: {status} {error_info}"
        )


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
    
    def log_event(
        self,
        event_type: str,
        level: str = 'INFO',
        **kwargs
    ):
        """
        记录结构化事件
        
        Args:
            event_type: 事件类型
            level: 日志级别
            **kwargs: 事件数据
        """
        import json
        
        event_data = {
            'event_type': event_type,
            **kwargs
        }
        
        message = json.dumps(event_data, ensure_ascii=False)
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
    def log_llm_request(
        self,
        stage_type: str,
        model: str,
        prompt_length: int,
        **kwargs
    ):
        """记录LLM请求"""
        self.log_event(
            'llm_request',
            level='INFO',
            stage_type=stage_type,
            model=model,
            prompt_length=prompt_length,
            **kwargs
        )
    
    def log_llm_response(
        self,
        stage_type: str,
        model: str,
        response_length: int,
        tokens_used: Optional[int] = None,
        duration: Optional[float] = None,
        **kwargs
    ):
        """记录LLM响应"""
        self.log_event(
            'llm_response',
            level='INFO',
            stage_type=stage_type,
            model=model,
            response_length=response_length,
            tokens_used=tokens_used,
            duration=duration,
            **kwargs
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        **kwargs
    ):
        """记录错误"""
        self.log_event(
            'error',
            level='ERROR',
            error_type=error_type,
            error_message=error_message,
            **kwargs
        )


# 创建全局日志记录器实例
performance_logger = PerformanceLogger()
