"""
初始化模型提供商数据
运行方式: python manage.py shell < scripts/init_models.py
"""

from apps.models.models import ModelProvider

# 清空现有数据（可选）
# ModelProvider.objects.all().delete()

# 创建 LLM 模型提供商
llm_providers = [
    {
        'name': 'OpenAI GPT-4',
        'provider_type': 'llm',
        'model_name': 'gpt-4',
        'api_key': 'your-openai-api-key',
        'api_base': 'https://api.openai.com/v1',
        'executor_class': 'OpenAIExecutor',
        'priority': 1,
        'is_active': True,
        'config': {
            'temperature': 0.7,
            'max_tokens': 2000
        }
    },
    {
        'name': 'OpenAI GPT-3.5',
        'provider_type': 'llm',
        'model_name': 'gpt-3.5-turbo',
        'api_key': 'your-openai-api-key',
        'api_base': 'https://api.openai.com/v1',
        'executor_class': 'OpenAIExecutor',
        'priority': 2,
        'is_active': True,
        'config': {
            'temperature': 0.7,
            'max_tokens': 2000
        }
    },
    {
        'name': '通义千问',
        'provider_type': 'llm',
        'model_name': 'qwen-max',
        'api_key': 'your-dashscope-api-key',
        'api_base': 'https://dashscope.aliyuncs.com/api/v1',
        'executor_class': 'DashScopeExecutor',
        'priority': 3,
        'is_active': False,
        'config': {
            'temperature': 0.7
        }
    }
]

# 创建文生图模型提供商
text2image_providers = [
    {
        'name': 'Stable Diffusion XL',
        'provider_type': 'text2image',
        'model_name': 'stabilityai/stable-diffusion-xl-base-1.0',
        'api_key': '',
        'api_base': 'http://localhost:7860',
        'executor_class': 'StableDiffusionExecutor',
        'priority': 1,
        'is_active': True,
        'config': {
            'steps': 30,
            'guidance_scale': 7.5,
            'width': 1024,
            'height': 1024
        }
    },
    {
        'name': 'DALL-E 3',
        'provider_type': 'text2image',
        'model_name': 'dall-e-3',
        'api_key': 'your-openai-api-key',
        'api_base': 'https://api.openai.com/v1',
        'executor_class': 'DallEExecutor',
        'priority': 2,
        'is_active': False,
        'config': {
            'size': '1024x1024',
            'quality': 'standard'
        }
    }
]

# 创建图生视频模型提供商
image2video_providers = [
    {
        'name': 'Stable Video Diffusion',
        'provider_type': 'image2video',
        'model_name': 'stabilityai/stable-video-diffusion-img2vid-xt',
        'api_key': '',
        'api_base': 'http://localhost:7861',
        'executor_class': 'SVDExecutor',
        'priority': 1,
        'is_active': True,
        'config': {
            'num_frames': 25,
            'fps': 6,
            'motion_bucket_id': 127
        }
    },
    {
        'name': 'Runway Gen-2',
        'provider_type': 'image2video',
        'model_name': 'gen2',
        'api_key': 'your-runway-api-key',
        'api_base': 'https://api.runwayml.com/v1',
        'executor_class': 'RunwayExecutor',
        'priority': 2,
        'is_active': False,
        'config': {
            'duration': 4,
            'resolution': '1280x768'
        }
    }
]

# 批量创建
all_providers = llm_providers + text2image_providers + image2video_providers

created_count = 0
for provider_data in all_providers:
    provider, created = ModelProvider.objects.get_or_create(
        name=provider_data['name'],
        defaults=provider_data
    )
    if created:
        created_count += 1
        print(f"✓ 创建模型提供商: {provider.name}")
    else:
        print(f"- 模型提供商已存在: {provider.name}")

print(f"\n完成！共创建 {created_count} 个模型提供商")
print(f"总计: {ModelProvider.objects.count()} 个模型提供商")
