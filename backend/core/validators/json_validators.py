"""
JSON 字段校验器
用于校验 JSONField 的数据结构
"""

from django.core.exceptions import ValidationError


def validate_movement_params(value):
    """
    校验运镜参数 JSON 结构
    
    必须包含字段：
    - speed: 运镜速度
    - duration: 持续时间
    
    Args:
        value: JSONField 的值（dict）
    
    Raises:
        ValidationError: 校验失败
    """
    if not isinstance(value, dict):
        raise ValidationError('运镜参数必须是字典类型')
    
    required_fields = ['speed', 'duration']
    missing_fields = [field for field in required_fields if field not in value]
    
    if missing_fields:
        raise ValidationError(
            f'运镜参数缺少必填字段: {", ".join(missing_fields)}'
        )
    
    # 校验字段类型
    if not isinstance(value.get('speed'), (int, float)):
        raise ValidationError('speed 必须是数字类型')
    
    if not isinstance(value.get('duration'), (int, float)):
        raise ValidationError('duration 必须是数字类型')
    
    # 校验字段范围
    if value['speed'] <= 0:
        raise ValidationError('speed 必须大于 0')
    
    if value['duration'] <= 0:
        raise ValidationError('duration 必须大于 0')


def validate_storyboard_config(value):
    """
    校验分镜配置 JSON 结构
    
    Args:
        value: JSONField 的值（dict）
    
    Raises:
        ValidationError: 校验失败
    """
    if not isinstance(value, dict):
        raise ValidationError('分镜配置必须是字典类型')
    
    # 可以添加更多校验规则
    return value


def validate_generation_config(value):
    """
    校验生成配置 JSON 结构
    
    Args:
        value: JSONField 的值（dict）
    
    Raises:
        ValidationError: 校验失败
    """
    if not isinstance(value, dict):
        raise ValidationError('生成配置必须是字典类型')
    
    return value
