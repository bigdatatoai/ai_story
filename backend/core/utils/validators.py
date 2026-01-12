"""
输入验证工具
提供统一的输入验证和清洗功能
"""

import re
import logging
from typing import Any, Dict, Optional, List
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class InputValidator:
    """输入验证器"""
    
    # 危险字符模式
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS脚本
        r'javascript:',  # JavaScript协议
        r'on\w+\s*=',  # 事件处理器
        r'eval\s*\(',  # eval函数
        r'exec\s*\(',  # exec函数
    ]
    
    @classmethod
    def validate_text_input(
        cls,
        text: str,
        field_name: str = "输入",
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        allow_empty: bool = False,
        strip_html: bool = True,
    ) -> str:
        """
        验证文本输入
        
        Args:
            text: 输入文本
            field_name: 字段名称（用于错误提示）
            min_length: 最小长度
            max_length: 最大长度
            allow_empty: 是否允许空值
            strip_html: 是否移除HTML标签
            
        Returns:
            清洗后的文本
            
        Raises:
            ValidationError: 验证失败
        """
        # 类型检查
        if not isinstance(text, str):
            raise ValidationError(f"{field_name}必须是字符串类型")
        
        # 去除首尾空白
        text = text.strip()
        
        # 空值检查
        if not text:
            if allow_empty:
                return text
            raise ValidationError(f"{field_name}不能为空")
        
        # 长度检查
        if min_length is not None and len(text) < min_length:
            raise ValidationError(f"{field_name}长度不能少于{min_length}个字符")
        
        if max_length is not None and len(text) > max_length:
            raise ValidationError(f"{field_name}长度不能超过{max_length}个字符")
        
        # 危险字符检查
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"检测到危险字符: {field_name}")
                raise ValidationError(f"{field_name}包含不允许的内容")
        
        # HTML标签清理
        if strip_html:
            text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    @classmethod
    def validate_json_data(
        cls,
        data: Dict[str, Any],
        required_fields: Optional[List[str]] = None,
        field_name: str = "数据"
    ) -> Dict[str, Any]:
        """
        验证JSON数据
        
        Args:
            data: JSON数据
            required_fields: 必需字段列表
            field_name: 字段名称
            
        Returns:
            验证后的数据
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(data, dict):
            raise ValidationError(f"{field_name}必须是字典类型")
        
        # 检查必需字段
        if required_fields:
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                raise ValidationError(
                    f"{field_name}缺少必需字段: {', '.join(missing_fields)}"
                )
        
        return data
    
    @classmethod
    def validate_number(
        cls,
        value: Any,
        field_name: str = "数值",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_negative: bool = True,
    ) -> float:
        """
        验证数值输入
        
        Args:
            value: 输入值
            field_name: 字段名称
            min_value: 最小值
            max_value: 最大值
            allow_negative: 是否允许负数
            
        Returns:
            验证后的数值
            
        Raises:
            ValidationError: 验证失败
        """
        try:
            num = float(value)
        except (TypeError, ValueError):
            raise ValidationError(f"{field_name}必须是有效的数值")
        
        if not allow_negative and num < 0:
            raise ValidationError(f"{field_name}不能为负数")
        
        if min_value is not None and num < min_value:
            raise ValidationError(f"{field_name}不能小于{min_value}")
        
        if max_value is not None and num > max_value:
            raise ValidationError(f"{field_name}不能大于{max_value}")
        
        return num
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        清理文件名，移除危险字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 移除路径分隔符和特殊字符
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # 移除控制字符
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
        # 限制长度
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or 'unnamed'
    
    @classmethod
    def validate_stage_input(
        cls,
        stage_type: str,
        input_data: Dict[str, Any],
        config: Any = None
    ) -> Dict[str, Any]:
        """
        验证阶段输入数据
        
        Args:
            stage_type: 阶段类型
            input_data: 输入数据
            config: 配置对象（可选）
            
        Returns:
            验证后的数据
            
        Raises:
            ValidationError: 验证失败
        """
        validated_data = {}
        
        # 根据阶段类型验证不同字段
        if stage_type == 'rewrite':
            # 文案改写阶段
            if 'original_topic' in input_data:
                validated_data['original_topic'] = cls.validate_text_input(
                    input_data['original_topic'],
                    field_name="原始文案",
                    min_length=config.get_min_input_length('rewrite') if config else 10,
                    max_length=config.get_max_input_length('rewrite') if config else 10000,
                )
        
        elif stage_type == 'storyboard':
            # 分镜生成阶段
            if 'rewritten_text' in input_data:
                validated_data['rewritten_text'] = cls.validate_text_input(
                    input_data['rewritten_text'],
                    field_name="改写后文案",
                    min_length=config.get_min_input_length('storyboard') if config else 50,
                    max_length=config.get_max_input_length('storyboard') if config else 5000,
                )
        
        elif stage_type == 'camera_movement':
            # 运镜生成阶段
            if 'storyboard_text' in input_data:
                validated_data['storyboard_text'] = cls.validate_text_input(
                    input_data['storyboard_text'],
                    field_name="分镜文本",
                    min_length=config.get_min_input_length('camera_movement') if config else 50,
                    max_length=config.get_max_input_length('camera_movement') if config else 8000,
                )
        
        # 复制其他字段
        for key, value in input_data.items():
            if key not in validated_data:
                validated_data[key] = value
        
        return validated_data


# 导出验证器实例
input_validator = InputValidator()
