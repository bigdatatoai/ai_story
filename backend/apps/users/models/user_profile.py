"""
用户配置和偏好设置模型
"""

from django.db import models
from django.contrib.auth import get_user_model
from apps.users.permissions import UserRole
import uuid

User = get_user_model()


class UserProfile(models.Model):
    """用户配置"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 角色和权限
    role = models.CharField(
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.REGULAR,
        verbose_name='用户角色'
    )
    
    # 账户状态
    is_verified = models.BooleanField(default=False, verbose_name='是否已验证')
    is_banned = models.BooleanField(default=False, verbose_name='是否被封禁')
    ban_reason = models.TextField(blank=True, verbose_name='封禁原因')
    
    # 订阅信息
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('free', '免费版'),
            ('basic', '基础版'),
            ('premium', '高级版'),
            ('enterprise', '企业版'),
        ],
        default='free',
        verbose_name='订阅类型'
    )
    subscription_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='订阅过期时间')
    
    # 使用统计
    total_stories_generated = models.IntegerField(default=0, verbose_name='总生成故事数')
    total_words_generated = models.IntegerField(default=0, verbose_name='总生成字数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class UserPreferences(models.Model):
    """用户偏好设置"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # 界面偏好
    theme = models.CharField(
        max_length=20,
        choices=[('light', '浅色'), ('dark', '深色'), ('auto', '自动')],
        default='auto',
        verbose_name='主题'
    )
    font_size = models.IntegerField(default=16, verbose_name='字体大小')
    font_family = models.CharField(max_length=50, default='default', verbose_name='字体')
    
    # 生成偏好
    default_age_group = models.CharField(max_length=20, default='elementary', verbose_name='默认年龄段')
    default_genre = models.CharField(max_length=50, default='fairy_tale', verbose_name='默认题材')
    default_style = models.CharField(max_length=50, default='warm_healing', verbose_name='默认风格')
    default_word_count = models.IntegerField(default=800, verbose_name='默认字数')
    
    # 通知偏好
    email_notifications = models.BooleanField(default=True, verbose_name='邮件通知')
    push_notifications = models.BooleanField(default=True, verbose_name='推送通知')
    notify_on_generation_complete = models.BooleanField(default=True, verbose_name='生成完成通知')
    notify_on_review_result = models.BooleanField(default=True, verbose_name='审核结果通知')
    
    # 隐私偏好
    public_profile = models.BooleanField(default=False, verbose_name='公开个人资料')
    allow_story_sharing = models.BooleanField(default=True, verbose_name='允许故事分享')
    
    # 其他设置
    auto_save_drafts = models.BooleanField(default=True, verbose_name='自动保存草稿')
    enable_offline_mode = models.BooleanField(default=True, verbose_name='启用离线模式')
    
    # 自定义配置(JSON)
    custom_settings = models.JSONField(default=dict, blank=True, verbose_name='自定义设置')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = '用户偏好'
        verbose_name_plural = '用户偏好'
    
    def __str__(self):
        return f"{self.user.username} - 偏好设置"


class UserActivity(models.Model):
    """用户活动记录"""
    
    ACTIVITY_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('generate_story', '生成故事'),
        ('edit_story', '编辑故事'),
        ('export_story', '导出故事'),
        ('share_story', '分享故事'),
        ('create_template', '创建模板'),
        ('create_character', '创建角色'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, verbose_name='活动类型')
    description = models.TextField(blank=True, verbose_name='描述')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='元数据')
    
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = '用户活动'
        verbose_name_plural = '用户活动'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class DeviceInfo(models.Model):
    """用户设备信息（用于多设备同步）"""
    
    DEVICE_TYPES = [
        ('web', 'Web浏览器'),
        ('mobile', '移动设备'),
        ('tablet', '平板'),
        ('desktop', '桌面应用'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    
    device_id = models.CharField(max_length=255, unique=True, verbose_name='设备ID')
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, verbose_name='设备类型')
    device_name = models.CharField(max_length=100, verbose_name='设备名称')
    
    # 设备信息
    os = models.CharField(max_length=50, blank=True, verbose_name='操作系统')
    browser = models.CharField(max_length=50, blank=True, verbose_name='浏览器')
    
    # 同步状态
    last_sync_at = models.DateTimeField(null=True, blank=True, verbose_name='最后同步时间')
    sync_token = models.CharField(max_length=255, blank=True, verbose_name='同步令牌')
    
    # 推送令牌
    push_token = models.CharField(max_length=255, blank=True, verbose_name='推送令牌')
    
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'device_info'
        verbose_name = '设备信息'
        verbose_name_plural = '设备信息'
        ordering = ['-last_sync_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name}"


class AuditLog(models.Model):
    """审计日志"""
    
    LOG_LEVELS = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 操作信息
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=100, verbose_name='操作')
    resource_type = models.CharField(max_length=50, verbose_name='资源类型')
    resource_id = models.CharField(max_length=100, blank=True, verbose_name='资源ID')
    
    # 日志详情
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info', verbose_name='级别')
    message = models.TextField(verbose_name='消息')
    details = models.JSONField(default=dict, blank=True, verbose_name='详情')
    
    # 请求信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    request_id = models.CharField(max_length=100, blank=True, verbose_name='请求ID')
    
    # 结果
    success = models.BooleanField(default=True, verbose_name='是否成功')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.created_at}"
