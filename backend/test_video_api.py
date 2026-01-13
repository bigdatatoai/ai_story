"""
测试视频创建API
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.content.models import Video
from apps.content.serializers.video_serializers import VideoCreateSerializer

User = get_user_model()

def test_video_create_serializer():
    """测试视频创建序列化器"""
    print("=" * 60)
    print("测试视频创建序列化器")
    print("=" * 60)
    
    # 获取或创建测试用户
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ 创建测试用户: {user.username}")
    else:
        print(f"✓ 使用现有测试用户: {user.username}")
    
    # 测试数据（模拟前端发送的数据）
    test_data = {
        'type': 'drama',
        'theme': '都市爱情故事',
        'episode_count': 3,
        'duration_per_episode': 60,
        'visual_style': 'realistic'
    }
    
    print(f"\n前端发送的数据:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # 创建序列化器实例
    serializer = VideoCreateSerializer(data=test_data)
    
    # 验证数据
    if serializer.is_valid():
        print("\n✓ 数据验证通过")
        print(f"\n验证后的数据:")
        for key, value in serializer.validated_data.items():
            print(f"  {key}: {value}")
        
        # 保存到数据库
        video = serializer.save(user=user)
        print(f"\n✓ 视频创建成功!")
        print(f"  ID: {video.id}")
        print(f"  标题: {video.title}")
        print(f"  生成类型: {video.generation_type}")
        print(f"  提示词: {video.prompt}")
        print(f"  配置: {video.generation_config}")
        print(f"  状态: {video.status}")
        
        return True
    else:
        print("\n✗ 数据验证失败:")
        for field, errors in serializer.errors.items():
            print(f"  {field}: {errors}")
        return False

def test_different_types():
    """测试不同的视频类型"""
    print("\n" + "=" * 60)
    print("测试不同的视频类型")
    print("=" * 60)
    
    user = User.objects.get(username='testuser')
    
    test_cases = [
        {
            'name': '动漫制作',
            'data': {
                'type': 'anime',
                'theme': '热血少年冒险',
                'episode_count': 12,
                'duration_per_episode': 24,
                'visual_style': 'anime'
            }
        },
        {
            'name': '漫画制作',
            'data': {
                'type': 'comic',
                'theme': '都市奇幻',
                'episode_count': 1,
                'visual_style': 'comic'
            }
        },
        {
            'name': '文本转视频',
            'data': {
                'type': 'text_to_video',
                'theme': '科技未来',
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        serializer = VideoCreateSerializer(data=test_case['data'])
        
        if serializer.is_valid():
            video = serializer.save(user=user)
            print(f"  ✓ 成功 - ID: {video.id}, 类型: {video.generation_type}")
        else:
            print(f"  ✗ 失败 - 错误: {serializer.errors}")

def cleanup():
    """清理测试数据"""
    print("\n" + "=" * 60)
    print("清理测试数据")
    print("=" * 60)
    
    count = Video.objects.filter(user__username='testuser').count()
    if count > 0:
        Video.objects.filter(user__username='testuser').delete()
        print(f"✓ 删除了 {count} 条测试视频记录")
    else:
        print("✓ 没有需要清理的数据")

if __name__ == '__main__':
    try:
        # 运行测试
        success = test_video_create_serializer()
        
        if success:
            test_different_types()
        
        # 询问是否清理
        print("\n" + "=" * 60)
        response = input("是否清理测试数据? (y/n): ")
        if response.lower() == 'y':
            cleanup()
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
