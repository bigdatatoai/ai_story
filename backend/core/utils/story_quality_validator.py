"""
故事质量验证工具
提供故事内容的质量检查、一致性验证、安全过滤等功能
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger('ai_story.quality')


@dataclass
class QualityCheckResult:
    """质量检查结果"""
    passed: bool
    score: float  # 0-100分
    issues: List[str]  # 问题列表
    suggestions: List[str]  # 改进建议
    details: Dict[str, Any]  # 详细信息


class StoryQualityValidator:
    """故事质量验证器"""
    
    # 敏感词库（示例，实际应从配置文件或数据库加载）
    SENSITIVE_WORDS = {
        'violence': ['杀', '血', '暴力', '打斗', '武器'],
        'horror': ['恐怖', '鬼', '死亡', '尸体', '惊悚'],
        'adult': ['性', '色情', '裸露'],
        'negative': ['自杀', '绝望', '仇恨'],
    }
    
    # 年龄段敏感词限制
    AGE_RESTRICTIONS = {
        'preschool': ['violence', 'horror', 'adult', 'negative'],
        'elementary': ['horror', 'adult', 'negative'],
        'teenager': ['adult'],
        'adult': [],
    }
    
    @classmethod
    def validate_story(
        cls,
        story_text: str,
        age_group: str = 'elementary',
        expected_word_count: int = None,
        genre: str = None,
        style: str = None,
    ) -> QualityCheckResult:
        """
        综合验证故事质量
        
        Args:
            story_text: 故事文本
            age_group: 目标年龄段
            expected_word_count: 期望字数
            genre: 题材
            style: 风格
        
        Returns:
            质量检查结果
        """
        issues = []
        suggestions = []
        details = {}
        scores = []
        
        # 1. 基础检查
        basic_result = cls._check_basic_quality(story_text)
        scores.append(basic_result['score'])
        issues.extend(basic_result.get('issues', []))
        suggestions.extend(basic_result.get('suggestions', []))
        details['basic'] = basic_result
        
        # 2. 字数检查
        if expected_word_count:
            word_count_result = cls._check_word_count(story_text, expected_word_count)
            scores.append(word_count_result['score'])
            if not word_count_result['passed']:
                issues.append(word_count_result['message'])
                suggestions.append(word_count_result['suggestion'])
            details['word_count'] = word_count_result
        
        # 3. 内容安全检查
        safety_result = cls._check_content_safety(story_text, age_group)
        scores.append(safety_result['score'])
        issues.extend(safety_result.get('issues', []))
        suggestions.extend(safety_result.get('suggestions', []))
        details['safety'] = safety_result
        
        # 4. 结构完整性检查
        structure_result = cls._check_story_structure(story_text)
        scores.append(structure_result['score'])
        issues.extend(structure_result.get('issues', []))
        suggestions.extend(structure_result.get('suggestions', []))
        details['structure'] = structure_result
        
        # 5. 语言质量检查
        language_result = cls._check_language_quality(story_text)
        scores.append(language_result['score'])
        issues.extend(language_result.get('issues', []))
        suggestions.extend(language_result.get('suggestions', []))
        details['language'] = language_result
        
        # 计算总分
        total_score = sum(scores) / len(scores) if scores else 0
        passed = total_score >= 60 and len(issues) == 0
        
        return QualityCheckResult(
            passed=passed,
            score=total_score,
            issues=issues,
            suggestions=suggestions,
            details=details,
        )
    
    @classmethod
    def _check_basic_quality(cls, text: str) -> Dict[str, Any]:
        """基础质量检查"""
        issues = []
        suggestions = []
        score = 100
        
        # 检查是否为空
        if not text or not text.strip():
            return {
                'score': 0,
                'issues': ['故事内容为空'],
                'suggestions': ['请生成有效的故事内容'],
            }
        
        # 检查最小长度
        if len(text) < 50:
            score -= 30
            issues.append('故事过短，内容不够充实')
            suggestions.append('增加故事内容，使其更加完整')
        
        # 检查是否有明显的错误标记
        error_patterns = [
            r'错误',
            r'失败',
            r'\[ERROR\]',
            r'无法生成',
        ]
        for pattern in error_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score -= 50
                issues.append('故事包含错误标记')
                suggestions.append('重新生成故事')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
        }
    
    @classmethod
    def _check_word_count(
        cls,
        text: str,
        expected_count: int,
        tolerance: float = 0.15
    ) -> Dict[str, Any]:
        """
        检查字数是否符合要求
        
        Args:
            text: 文本
            expected_count: 期望字数
            tolerance: 容差比例（默认15%）
        """
        actual_count = len(text)
        min_count = int(expected_count * (1 - tolerance))
        max_count = int(expected_count * (1 + tolerance))
        
        passed = min_count <= actual_count <= max_count
        
        if passed:
            score = 100
            message = f'字数符合要求（{actual_count}字）'
            suggestion = ''
        elif actual_count < min_count:
            score = max(0, 100 - (min_count - actual_count) / expected_count * 100)
            message = f'字数不足（{actual_count}字，期望{expected_count}字）'
            suggestion = f'需要增加约{min_count - actual_count}字'
        else:
            score = max(0, 100 - (actual_count - max_count) / expected_count * 100)
            message = f'字数超出（{actual_count}字，期望{expected_count}字）'
            suggestion = f'需要删减约{actual_count - max_count}字'
        
        return {
            'passed': passed,
            'score': score,
            'actual_count': actual_count,
            'expected_count': expected_count,
            'message': message,
            'suggestion': suggestion,
        }
    
    @classmethod
    def _check_content_safety(cls, text: str, age_group: str) -> Dict[str, Any]:
        """内容安全检查"""
        issues = []
        suggestions = []
        score = 100
        found_sensitive = {}
        
        # 获取该年龄段的限制类别
        restricted_categories = cls.AGE_RESTRICTIONS.get(age_group, [])
        
        # 检查敏感词
        for category in restricted_categories:
            words = cls.SENSITIVE_WORDS.get(category, [])
            found_words = [word for word in words if word in text]
            
            if found_words:
                found_sensitive[category] = found_words
                score -= 20
                issues.append(f'包含不适合{age_group}年龄段的{category}内容')
                suggestions.append(f'移除或替换以下词汇：{", ".join(found_words[:3])}')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'found_sensitive': found_sensitive,
        }
    
    @classmethod
    def _check_story_structure(cls, text: str) -> Dict[str, Any]:
        """检查故事结构完整性"""
        issues = []
        suggestions = []
        score = 100
        
        # 检查是否有开头
        has_opening = cls._has_opening(text)
        if not has_opening:
            score -= 20
            issues.append('缺少明确的故事开头')
            suggestions.append('添加故事背景和角色介绍')
        
        # 检查是否有发展
        has_development = cls._has_development(text)
        if not has_development:
            score -= 30
            issues.append('故事发展不够充分')
            suggestions.append('增加情节发展和冲突')
        
        # 检查是否有结尾
        has_ending = cls._has_ending(text)
        if not has_ending:
            score -= 20
            issues.append('缺少明确的故事结尾')
            suggestions.append('添加故事结局和总结')
        
        # 检查段落分布
        paragraphs = text.split('\n\n')
        if len(paragraphs) < 3:
            score -= 10
            issues.append('段落划分不够清晰')
            suggestions.append('使用段落分隔故事的不同部分')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'has_opening': has_opening,
            'has_development': has_development,
            'has_ending': has_ending,
            'paragraph_count': len(paragraphs),
        }
    
    @classmethod
    def _check_language_quality(cls, text: str) -> Dict[str, Any]:
        """检查语言质量"""
        issues = []
        suggestions = []
        score = 100
        
        # 检查重复内容
        repetition_score = cls._check_repetition(text)
        if repetition_score < 80:
            score -= (100 - repetition_score) * 0.3
            issues.append('存在较多重复内容')
            suggestions.append('减少重复的词汇和句式')
        
        # 检查句子长度分布
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_length = sum(len(s) for s in sentences) / len(sentences)
            
            # 检查是否有过长或过短的句子
            too_long = sum(1 for s in sentences if len(s) > 100)
            too_short = sum(1 for s in sentences if len(s) < 5)
            
            if too_long > len(sentences) * 0.2:
                score -= 10
                issues.append('部分句子过长，影响阅读')
                suggestions.append('将长句拆分为短句')
            
            if too_short > len(sentences) * 0.3:
                score -= 10
                issues.append('部分句子过短，内容不够充实')
                suggestions.append('适当扩展句子内容')
        
        # 检查标点符号使用
        punctuation_score = cls._check_punctuation(text)
        if punctuation_score < 80:
            score -= (100 - punctuation_score) * 0.2
            issues.append('标点符号使用不当')
            suggestions.append('检查标点符号的使用')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'repetition_score': repetition_score,
            'punctuation_score': punctuation_score,
        }
    
    @classmethod
    def _has_opening(cls, text: str) -> bool:
        """检查是否有开头"""
        opening_patterns = [
            r'^(从前|很久以前|在.*的.*|有一个|曾经)',
            r'(介绍|这是|故事开始)',
        ]
        first_paragraph = text.split('\n\n')[0] if '\n\n' in text else text[:200]
        
        for pattern in opening_patterns:
            if re.search(pattern, first_paragraph):
                return True
        return len(first_paragraph) > 50
    
    @classmethod
    def _has_development(cls, text: str) -> bool:
        """检查是否有发展"""
        # 简单检查：文本长度足够，且有多个段落
        paragraphs = text.split('\n\n')
        return len(text) > 200 and len(paragraphs) >= 2
    
    @classmethod
    def _has_ending(cls, text: str) -> bool:
        """检查是否有结尾"""
        ending_patterns = [
            r'(从此|最后|终于|结束|完)',
            r'(幸福|快乐|美好).*生活',
        ]
        last_paragraph = text.split('\n\n')[-1] if '\n\n' in text else text[-200:]
        
        for pattern in ending_patterns:
            if re.search(pattern, last_paragraph):
                return True
        return False
    
    @classmethod
    def _check_repetition(cls, text: str) -> float:
        """检查重复度（返回0-100分）"""
        # 检查词语重复
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        if not words:
            return 100
        
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        
        # 计算重复率
        total_words = len(words)
        repeated_words = sum(count - 1 for count in word_count.values() if count > 1)
        repetition_rate = repeated_words / total_words if total_words > 0 else 0
        
        # 转换为分数（重复率越低分数越高）
        score = max(0, 100 - repetition_rate * 200)
        return score
    
    @classmethod
    def _check_punctuation(cls, text: str) -> float:
        """检查标点符号使用（返回0-100分）"""
        score = 100
        
        # 检查是否缺少标点
        sentences = text.split('。')
        for sentence in sentences:
            if len(sentence) > 50 and '，' not in sentence and '、' not in sentence:
                score -= 5
        
        # 检查标点符号重复
        if re.search(r'[，。！？]{3,}', text):
            score -= 10
        
        return max(0, score)
    
    @classmethod
    def suggest_improvements(
        cls,
        story_text: str,
        quality_result: QualityCheckResult,
    ) -> str:
        """
        基于质量检查结果，生成改进建议提示词
        
        Args:
            story_text: 原始故事
            quality_result: 质量检查结果
        
        Returns:
            改进建议提示词
        """
        if quality_result.passed:
            return ""
        
        improvements = []
        improvements.append("请对以下故事进行改进：\n")
        improvements.append(f"原始故事：\n{story_text}\n")
        improvements.append("\n需要改进的问题：")
        
        for i, issue in enumerate(quality_result.issues, 1):
            improvements.append(f"{i}. {issue}")
        
        improvements.append("\n改进建议：")
        for i, suggestion in enumerate(quality_result.suggestions, 1):
            improvements.append(f"{i}. {suggestion}")
        
        improvements.append("\n请生成改进后的故事，确保：")
        improvements.append("- 解决上述所有问题")
        improvements.append("- 保持故事的核心主题和情节")
        improvements.append("- 提升整体质量和可读性")
        
        return '\n'.join(improvements)


# 导出验证器实例
story_quality_validator = StoryQualityValidator()
