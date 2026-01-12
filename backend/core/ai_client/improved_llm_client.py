"""
改进的LLM客户端
集成配置管理、错误处理、缓存、日志等功能
"""

import time
import logging
from typing import Any, Dict, Generator, Optional, List
from config.llm_config import llm_config
from core.utils.validators import input_validator
from core.utils.error_handler import (
    retry_on_error,
    handle_llm_errors,
    RateLimitError,
    TimeoutError,
    NetworkError,
)
from core.utils.cache_manager import llm_cache
from core.utils.logging_config import performance_logger, StructuredLogger

logger = logging.getLogger('ai_story.llm')
structured_logger = StructuredLogger('ai_story.llm')


class ImprovedLLMClient:
    """
    改进的LLM客户端
    
    特性:
    - 配置化参数管理
    - 完善的错误处理和重试机制
    - LLM响应缓存
    - 详细的日志记录
    - 输入验证
    - 性能监控
    """
    
    def __init__(
        self,
        provider: str = 'openai',
        model: str = None,
        api_key: str = None,
        api_base: str = None,
    ):
        """
        初始化LLM客户端
        
        Args:
            provider: LLM提供商 (openai/anthropic/google)
            model: 模型名称
            api_key: API密钥
            api_base: API基础URL
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        
        # 初始化提供商客户端
        self._init_provider_client()
    
    def _init_provider_client(self):
        """初始化提供商特定的客户端"""
        if self.provider == 'openai':
            import openai
            if self.api_key:
                openai.api_key = self.api_key
            if self.api_base:
                openai.api_base = self.api_base
            self.client = openai
        
        elif self.provider == 'anthropic':
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        
        elif self.provider == 'google':
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.client = genai
        
        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")
    
    @retry_on_error(
        max_retries=llm_config.MAX_RETRIES,
        retry_delay=llm_config.RETRY_DELAY,
        backoff_factor=llm_config.BACKOFF_FACTOR,
        retry_on=(RateLimitError, TimeoutError, NetworkError),
    )
    @handle_llm_errors
    def generate(
        self,
        prompt: str,
        stage_type: str = 'rewrite',
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        use_cache: bool = None,
        **kwargs
    ) -> str:
        """
        生成文本（非流式）
        
        Args:
            prompt: 用户提示词
            stage_type: 阶段类型（用于获取配置）
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数
            use_cache: 是否使用缓存
            **kwargs: 其他参数
        
        Returns:
            生成的文本
        
        Raises:
            ValidationError: 输入验证失败
            APIError: API调用失败
        """
        start_time = time.time()
        
        # 输入验证
        validated_prompt = input_validator.validate_text_input(
            prompt,
            field_name="提示词",
            min_length=llm_config.get_min_input_length(stage_type),
            max_length=llm_config.get_max_input_length(stage_type),
        )
        
        # 获取配置参数
        temperature = temperature or llm_config.get_temperature(stage_type)
        max_tokens = max_tokens or llm_config.get_max_tokens(stage_type)
        top_p = top_p or llm_config.get_top_p(stage_type)
        use_cache = use_cache if use_cache is not None else llm_config.ENABLE_CACHE
        
        # 记录请求日志
        structured_logger.log_llm_request(
            stage_type=stage_type,
            model=self.model,
            prompt_length=len(validated_prompt),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # 尝试从缓存获取
        if use_cache:
            cached_response = llm_cache.get_llm_response(
                stage_type=stage_type,
                prompt=validated_prompt,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            if cached_response:
                logger.info(f"使用缓存的LLM响应 - 阶段: {stage_type}")
                duration = time.time() - start_time
                performance_logger.log_llm_call(
                    model=self.model,
                    stage_type=stage_type,
                    duration=duration,
                    success=True,
                )
                return cached_response
        
        # 调用LLM API
        try:
            response_text = self._call_provider_api(
                prompt=validated_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            )
            
            # 缓存响应
            if use_cache:
                llm_cache.cache_llm_response(
                    stage_type=stage_type,
                    prompt=validated_prompt,
                    model=self.model,
                    response=response_text,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            
            # 记录性能
            duration = time.time() - start_time
            performance_logger.log_llm_call(
                model=self.model,
                stage_type=stage_type,
                duration=duration,
                success=True,
            )
            
            # 记录响应日志
            structured_logger.log_llm_response(
                stage_type=stage_type,
                model=self.model,
                response_length=len(response_text),
                duration=duration,
            )
            
            return response_text
        
        except Exception as e:
            duration = time.time() - start_time
            performance_logger.log_llm_call(
                model=self.model,
                stage_type=stage_type,
                duration=duration,
                success=False,
            )
            
            structured_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                stage_type=stage_type,
                model=self.model,
            )
            
            raise
    
    def generate_stream(
        self,
        prompt: str,
        stage_type: str = 'rewrite',
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        生成文本（流式）
        
        Args:
            prompt: 用户提示词
            stage_type: 阶段类型
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数
            **kwargs: 其他参数
        
        Yields:
            包含生成内容的字典
        """
        start_time = time.time()
        
        # 输入验证
        validated_prompt = input_validator.validate_text_input(
            prompt,
            field_name="提示词",
            min_length=llm_config.get_min_input_length(stage_type),
            max_length=llm_config.get_max_input_length(stage_type),
        )
        
        # 获取配置参数
        temperature = temperature or llm_config.get_temperature(stage_type)
        max_tokens = max_tokens or llm_config.get_max_tokens(stage_type)
        top_p = top_p or llm_config.get_top_p(stage_type)
        
        # 记录请求
        structured_logger.log_llm_request(
            stage_type=stage_type,
            model=self.model,
            prompt_length=len(validated_prompt),
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
        
        try:
            # 调用流式API
            full_response = ""
            for chunk in self._call_provider_stream_api(
                prompt=validated_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            ):
                full_response += chunk.get('content', '')
                yield chunk
            
            # 记录性能
            duration = time.time() - start_time
            performance_logger.log_llm_call(
                model=self.model,
                stage_type=stage_type,
                duration=duration,
                success=True,
            )
            
            # 记录响应
            structured_logger.log_llm_response(
                stage_type=stage_type,
                model=self.model,
                response_length=len(full_response),
                duration=duration,
                streaming=True,
            )
        
        except Exception as e:
            duration = time.time() - start_time
            performance_logger.log_llm_call(
                model=self.model,
                stage_type=stage_type,
                duration=duration,
                success=False,
            )
            
            structured_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                stage_type=stage_type,
                model=self.model,
            )
            
            raise
    
    def _call_provider_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **params
    ) -> str:
        """
        调用提供商API（非流式）
        
        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            **params: API参数
        
        Returns:
            生成的文本
        """
        if self.provider == 'openai':
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                **params
            )
            
            return response.choices[0].message.content
        
        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                **params
            )
            
            return response.content[0].text
        
        elif self.provider == 'google':
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            
            return response.text
        
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")
    
    def _call_provider_stream_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **params
    ) -> Generator[Dict[str, Any], None, None]:
        """
        调用提供商API（流式）
        
        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            **params: API参数
        
        Yields:
            包含生成内容的字典
        """
        if self.provider == 'openai':
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            stream = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                stream=True,
                **params
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.get('content'):
                    yield {
                        'type': 'token',
                        'content': chunk.choices[0].delta.content
                    }
        
        elif self.provider == 'anthropic':
            with self.client.messages.stream(
                model=self.model,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                **params
            ) as stream:
                for text in stream.text_stream:
                    yield {
                        'type': 'token',
                        'content': text
                    }
        
        else:
            raise ValueError(f"流式模式不支持提供商: {self.provider}")
