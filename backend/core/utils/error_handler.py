"""
统一错误处理工具
提供完善的异常捕获和错误处理机制
"""

import logging
import time
import functools
from typing import Any, Callable, Optional, Type, Tuple
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """可重试的错误"""
    pass


class NonRetryableError(Exception):
    """不可重试的错误"""
    pass


class APIError(Exception):
    """API调用错误"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Any = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class RateLimitError(RetryableError):
    """速率限制错误"""
    pass


class TimeoutError(RetryableError):
    """超时错误"""
    pass


class NetworkError(RetryableError):
    """网络错误"""
    pass


def retry_on_error(
    max_retries: int = 3,
    retry_delay: float = 2.0,
    backoff_factor: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (RetryableError, ConnectionError, TimeoutError),
    logger_name: Optional[str] = None,
):
    """
    错误重试装饰器
    
    Args:
        max_retries: 最大重试次数
        retry_delay: 初始重试延迟（秒）
        backoff_factor: 指数退避系数
        retry_on: 需要重试的异常类型
        logger_name: 日志记录器名称
    
    Example:
        @retry_on_error(max_retries=3, retry_delay=1.0)
        def call_api():
            # API调用代码
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logging.getLogger(logger_name or func.__module__)
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = retry_delay * (backoff_factor ** attempt)
                        _logger.warning(
                            f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}. "
                            f"将在 {delay:.1f} 秒后重试..."
                        )
                        time.sleep(delay)
                    else:
                        _logger.error(
                            f"{func.__name__} 在 {max_retries + 1} 次尝试后仍然失败: {str(e)}"
                        )
                except Exception as e:
                    # 不可重试的错误直接抛出
                    _logger.error(f"{func.__name__} 遇到不可重试的错误: {str(e)}", exc_info=True)
                    raise
            
            # 所有重试都失败了
            raise last_exception
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    default_return: Any = None,
    log_errors: bool = True,
    logger_name: Optional[str] = None,
) -> Any:
    """
    安全执行函数，捕获所有异常
    
    Args:
        func: 要执行的函数
        default_return: 发生错误时的默认返回值
        log_errors: 是否记录错误日志
        logger_name: 日志记录器名称
    
    Returns:
        函数执行结果或默认返回值
    
    Example:
        result = safe_execute(lambda: risky_operation(), default_return={})
    """
    _logger = logging.getLogger(logger_name or __name__)
    
    try:
        return func()
    except Exception as e:
        if log_errors:
            _logger.error(f"执行 {func.__name__} 时发生错误: {str(e)}", exc_info=True)
        return default_return


def handle_llm_errors(func: Callable) -> Callable:
    """
    LLM调用错误处理装饰器
    专门处理LLM API调用中的各种错误
    
    Example:
        @handle_llm_errors
        def call_openai_api():
            # OpenAI API调用
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        # OpenAI特定错误
        except Exception as e:
            error_msg = str(e).lower()
            
            # 速率限制错误
            if 'rate limit' in error_msg or 'quota' in error_msg:
                logger.warning(f"LLM API速率限制: {str(e)}")
                raise RateLimitError(f"API速率限制，请稍后重试: {str(e)}")
            
            # 超时错误
            elif 'timeout' in error_msg or 'timed out' in error_msg:
                logger.warning(f"LLM API超时: {str(e)}")
                raise TimeoutError(f"API调用超时: {str(e)}")
            
            # 网络错误
            elif 'connection' in error_msg or 'network' in error_msg:
                logger.warning(f"LLM API网络错误: {str(e)}")
                raise NetworkError(f"网络连接失败: {str(e)}")
            
            # 认证错误（不可重试）
            elif 'authentication' in error_msg or 'api key' in error_msg or 'unauthorized' in error_msg:
                logger.error(f"LLM API认证失败: {str(e)}")
                raise NonRetryableError(f"API认证失败，请检查API密钥: {str(e)}")
            
            # 参数错误（不可重试）
            elif 'invalid' in error_msg or 'bad request' in error_msg:
                logger.error(f"LLM API参数错误: {str(e)}")
                raise NonRetryableError(f"API参数错误: {str(e)}")
            
            # 其他错误
            else:
                logger.error(f"LLM API未知错误: {str(e)}", exc_info=True)
                raise APIError(f"API调用失败: {str(e)}")
    
    return wrapper


def validate_and_execute(
    validator_func: Callable,
    executor_func: Callable,
    error_message: str = "操作失败",
) -> Any:
    """
    先验证后执行的模式
    
    Args:
        validator_func: 验证函数
        executor_func: 执行函数
        error_message: 错误消息
    
    Returns:
        执行结果
    
    Raises:
        ValidationError: 验证失败
    
    Example:
        result = validate_and_execute(
            lambda: validate_input(data),
            lambda: process_data(data),
            error_message="数据处理失败"
        )
    """
    try:
        # 先验证
        validator_func()
        
        # 再执行
        return executor_func()
    
    except ValidationError:
        # 验证错误直接抛出
        raise
    
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}", exc_info=True)
        raise


class ErrorContext:
    """
    错误上下文管理器
    用于捕获和记录特定代码块的错误
    
    Example:
        with ErrorContext("处理用户请求", raise_on_error=False):
            # 可能出错的代码
            risky_operation()
    """
    
    def __init__(
        self,
        operation_name: str,
        raise_on_error: bool = True,
        log_level: str = "error",
        logger_name: Optional[str] = None,
    ):
        self.operation_name = operation_name
        self.raise_on_error = raise_on_error
        self.log_level = log_level
        self.logger = logging.getLogger(logger_name or __name__)
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            
            # 记录错误
            log_func = getattr(self.logger, self.log_level)
            log_func(
                f"{self.operation_name} 失败: {str(exc_val)}",
                exc_info=(exc_type, exc_val, exc_tb)
            )
            
            # 决定是否抑制异常
            return not self.raise_on_error
        
        return False


def format_error_response(error: Exception, include_traceback: bool = False) -> dict:
    """
    格式化错误响应
    
    Args:
        error: 异常对象
        include_traceback: 是否包含堆栈跟踪
    
    Returns:
        格式化的错误字典
    """
    import traceback
    
    response = {
        'success': False,
        'error': str(error),
        'error_type': type(error).__name__,
    }
    
    # 添加特定错误的额外信息
    if isinstance(error, APIError):
        response['status_code'] = error.status_code
        response['response_data'] = error.response_data
    
    if isinstance(error, ValidationError):
        response['validation_errors'] = error.message_dict if hasattr(error, 'message_dict') else str(error)
    
    # 添加堆栈跟踪（仅用于调试）
    if include_traceback:
        response['traceback'] = traceback.format_exc()
    
    return response
