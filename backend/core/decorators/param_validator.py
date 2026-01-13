"""
参数校验装饰器
提供便捷的API参数验证功能
"""

import functools
from typing import Dict, Any, List, Optional, Callable
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

from core.utils.response_wrapper import APIResponse, ErrorCode
from core.utils.validators import input_validator


def validate_params(**validators):
    """
    参数校验装饰器
    
    用法:
        @validate_params(
            topic={'required': True, 'type': str, 'min_length': 2, 'max_length': 100},
            word_count={'type': int, 'min_value': 100, 'max_value': 5000, 'default': 800},
            age_group={'type': str, 'choices': ['preschool', 'elementary', 'middle_school']}
        )
        def my_view(request):
            # request.validated_data 包含验证后的参数
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            validated_data = {}
            errors = {}
            
            for param_name, rules in validators.items():
                try:
                    # 获取参数值
                    value = request.data.get(param_name)
                    
                    # 检查必填
                    if rules.get('required', False) and value is None:
                        errors[param_name] = f'{param_name} 是必填参数'
                        continue
                    
                    # 使用默认值
                    if value is None and 'default' in rules:
                        value = rules['default']
                    
                    # 如果值为None且非必填，跳过后续验证
                    if value is None:
                        validated_data[param_name] = None
                        continue
                    
                    # 类型验证
                    expected_type = rules.get('type')
                    if expected_type:
                        if expected_type == int:
                            try:
                                value = int(value)
                            except (TypeError, ValueError):
                                errors[param_name] = f'{param_name} 必须是整数'
                                continue
                        elif expected_type == float:
                            try:
                                value = float(value)
                            except (TypeError, ValueError):
                                errors[param_name] = f'{param_name} 必须是数值'
                                continue
                        elif expected_type == str:
                            if not isinstance(value, str):
                                errors[param_name] = f'{param_name} 必须是字符串'
                                continue
                        elif expected_type == list:
                            if not isinstance(value, list):
                                errors[param_name] = f'{param_name} 必须是列表'
                                continue
                        elif expected_type == dict:
                            if not isinstance(value, dict):
                                errors[param_name] = f'{param_name} 必须是字典'
                                continue
                    
                    # 字符串长度验证
                    if isinstance(value, str):
                        min_length = rules.get('min_length')
                        max_length = rules.get('max_length')
                        
                        if min_length and len(value) < min_length:
                            errors[param_name] = f'{param_name} 长度不能少于 {min_length} 个字符'
                            continue
                        
                        if max_length and len(value) > max_length:
                            errors[param_name] = f'{param_name} 长度不能超过 {max_length} 个字符'
                            continue
                    
                    # 数值范围验证
                    if isinstance(value, (int, float)):
                        min_value = rules.get('min_value')
                        max_value = rules.get('max_value')
                        
                        if min_value is not None and value < min_value:
                            errors[param_name] = f'{param_name} 不能小于 {min_value}'
                            continue
                        
                        if max_value is not None and value > max_value:
                            errors[param_name] = f'{param_name} 不能大于 {max_value}'
                            continue
                    
                    # 选项验证
                    choices = rules.get('choices')
                    if choices and value not in choices:
                        errors[param_name] = f'{param_name} 必须是以下值之一: {", ".join(map(str, choices))}'
                        continue
                    
                    # 列表长度验证
                    if isinstance(value, list):
                        min_items = rules.get('min_items')
                        max_items = rules.get('max_items')
                        
                        if min_items and len(value) < min_items:
                            errors[param_name] = f'{param_name} 至少需要 {min_items} 个元素'
                            continue
                        
                        if max_items and len(value) > max_items:
                            errors[param_name] = f'{param_name} 最多允许 {max_items} 个元素'
                            continue
                    
                    # 自定义验证函数
                    custom_validator = rules.get('validator')
                    if custom_validator and callable(custom_validator):
                        try:
                            value = custom_validator(value)
                        except Exception as e:
                            errors[param_name] = str(e)
                            continue
                    
                    validated_data[param_name] = value
                    
                except Exception as e:
                    errors[param_name] = str(e)
            
            # 如果有验证错误，返回错误响应
            if errors:
                return APIResponse.bad_request(
                    message='参数验证失败',
                    code=ErrorCode.INVALID_PARAMS,
                    data={'errors': errors}
                )
            
            # 将验证后的数据附加到request对象
            request.validated_data = validated_data
            
            # 调用原函数
            return func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_fields(*fields):
    """
    简化的必填字段验证装饰器
    
    用法:
        @require_fields('topic', 'age_group')
        def my_view(request):
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            missing_fields = []
            
            for field in fields:
                if field not in request.data or request.data.get(field) is None:
                    missing_fields.append(field)
            
            if missing_fields:
                return APIResponse.bad_request(
                    message=f'缺少必填参数: {", ".join(missing_fields)}',
                    code=ErrorCode.MISSING_PARAMS,
                    data={'missing_fields': missing_fields}
                )
            
            return func(self, request, *args, **kwargs)
        
        return wrapper
    return decorator


def validate_request_data(schema: Dict[str, Any]):
    """
    基于schema验证请求数据
    
    用法:
        @validate_request_data({
            'type': 'object',
            'properties': {
                'topic': {'type': 'string', 'minLength': 2, 'maxLength': 100},
                'word_count': {'type': 'integer', 'minimum': 100, 'maximum': 5000}
            },
            'required': ['topic']
        })
        def my_view(request):
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                # 这里可以集成 jsonschema 库进行更复杂的验证
                # 简化实现：只检查必填字段
                required_fields = schema.get('required', [])
                missing_fields = [f for f in required_fields if f not in request.data]
                
                if missing_fields:
                    return APIResponse.bad_request(
                        message=f'缺少必填参数: {", ".join(missing_fields)}',
                        code=ErrorCode.MISSING_PARAMS,
                        data={'missing_fields': missing_fields}
                    )
                
                return func(self, request, *args, **kwargs)
                
            except Exception as e:
                return APIResponse.bad_request(
                    message=f'参数验证失败: {str(e)}',
                    code=ErrorCode.INVALID_PARAMS
                )
        
        return wrapper
    return decorator
