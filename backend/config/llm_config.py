"""
LLM配置管理
集中管理所有LLM相关的配置参数，避免硬编码
"""

from typing import Dict, Any
import os


class LLMConfig:
    """LLM配置类"""
    
    # ==================== 模型参数配置 ====================
    
    # 各阶段的最大token数
    MAX_TOKENS = {
        'rewrite': int(os.getenv('LLM_REWRITE_MAX_TOKENS', 2000)),
        'storyboard': int(os.getenv('LLM_STORYBOARD_MAX_TOKENS', 4000)),
        'camera_movement': int(os.getenv('LLM_CAMERA_MAX_TOKENS', 3000)),
    }
    
    # 各阶段的温度参数
    TEMPERATURE = {
        'rewrite': float(os.getenv('LLM_REWRITE_TEMPERATURE', 0.7)),
        'storyboard': float(os.getenv('LLM_STORYBOARD_TEMPERATURE', 0.8)),
        'camera_movement': float(os.getenv('LLM_CAMERA_TEMPERATURE', 0.6)),
    }
    
    # 各阶段的top_p参数
    TOP_P = {
        'rewrite': float(os.getenv('LLM_REWRITE_TOP_P', 0.9)),
        'storyboard': float(os.getenv('LLM_STORYBOARD_TOP_P', 0.95)),
        'camera_movement': float(os.getenv('LLM_CAMERA_TOP_P', 0.9)),
    }
    
    # ==================== 重试与超时配置 ====================
    
    # API调用重试次数
    MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', 3))
    
    # API调用超时时间（秒）
    TIMEOUT = int(os.getenv('LLM_TIMEOUT', 60))
    
    # 重试延迟（秒）
    RETRY_DELAY = int(os.getenv('LLM_RETRY_DELAY', 2))
    
    # 指数退避系数
    BACKOFF_FACTOR = float(os.getenv('LLM_BACKOFF_FACTOR', 2.0))
    
    # ==================== 速率限制配置 ====================
    
    # 每分钟最大请求数
    RATE_LIMIT_PER_MINUTE = int(os.getenv('LLM_RATE_LIMIT_PER_MINUTE', 60))
    
    # 每天最大请求数
    RATE_LIMIT_PER_DAY = int(os.getenv('LLM_RATE_LIMIT_PER_DAY', 10000))
    
    # ==================== 缓存配置 ====================
    
    # 是否启用缓存
    ENABLE_CACHE = os.getenv('LLM_ENABLE_CACHE', 'true').lower() == 'true'
    
    # 缓存过期时间（秒）
    CACHE_TTL = int(os.getenv('LLM_CACHE_TTL', 86400))  # 默认24小时
    
    # 缓存键前缀
    CACHE_KEY_PREFIX = os.getenv('LLM_CACHE_KEY_PREFIX', 'llm:response:')
    
    # ==================== 输入验证配置 ====================
    
    # 最大输入长度
    MAX_INPUT_LENGTH = {
        'rewrite': int(os.getenv('LLM_REWRITE_MAX_INPUT', 10000)),
        'storyboard': int(os.getenv('LLM_STORYBOARD_MAX_INPUT', 5000)),
        'camera_movement': int(os.getenv('LLM_CAMERA_MAX_INPUT', 8000)),
    }
    
    # 最小输入长度
    MIN_INPUT_LENGTH = {
        'rewrite': int(os.getenv('LLM_REWRITE_MIN_INPUT', 10)),
        'storyboard': int(os.getenv('LLM_STORYBOARD_MIN_INPUT', 50)),
        'camera_movement': int(os.getenv('LLM_CAMERA_MIN_INPUT', 50)),
    }
    
    # ==================== 日志配置 ====================
    
    # 是否记录详细日志
    VERBOSE_LOGGING = os.getenv('LLM_VERBOSE_LOGGING', 'false').lower() == 'true'
    
    # 是否记录请求/响应内容
    LOG_CONTENT = os.getenv('LLM_LOG_CONTENT', 'false').lower() == 'true'
    
    @classmethod
    def get_max_tokens(cls, stage_type: str) -> int:
        """获取指定阶段的最大token数"""
        return cls.MAX_TOKENS.get(stage_type, 2000)
    
    @classmethod
    def get_temperature(cls, stage_type: str) -> float:
        """获取指定阶段的温度参数"""
        return cls.TEMPERATURE.get(stage_type, 0.7)
    
    @classmethod
    def get_top_p(cls, stage_type: str) -> float:
        """获取指定阶段的top_p参数"""
        return cls.TOP_P.get(stage_type, 0.9)
    
    @classmethod
    def get_max_input_length(cls, stage_type: str) -> int:
        """获取指定阶段的最大输入长度"""
        return cls.MAX_INPUT_LENGTH.get(stage_type, 10000)
    
    @classmethod
    def get_min_input_length(cls, stage_type: str) -> int:
        """获取指定阶段的最小输入长度"""
        return cls.MIN_INPUT_LENGTH.get(stage_type, 10)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """导出所有配置为字典"""
        return {
            'max_tokens': cls.MAX_TOKENS,
            'temperature': cls.TEMPERATURE,
            'top_p': cls.TOP_P,
            'max_retries': cls.MAX_RETRIES,
            'timeout': cls.TIMEOUT,
            'retry_delay': cls.RETRY_DELAY,
            'backoff_factor': cls.BACKOFF_FACTOR,
            'rate_limit_per_minute': cls.RATE_LIMIT_PER_MINUTE,
            'rate_limit_per_day': cls.RATE_LIMIT_PER_DAY,
            'enable_cache': cls.ENABLE_CACHE,
            'cache_ttl': cls.CACHE_TTL,
            'max_input_length': cls.MAX_INPUT_LENGTH,
            'min_input_length': cls.MIN_INPUT_LENGTH,
        }


# 导出配置实例
llm_config = LLMConfig()
