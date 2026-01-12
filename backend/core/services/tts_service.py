"""
AI 配音服务（Text-to-Speech）
支持多个真实 TTS 提供商：阿里云、Azure、讯飞
"""

import os
import json
import logging
import requests
import hashlib
import time
import base64
import hmac
from pathlib import Path
from typing import Dict, Optional, List
from urllib.parse import urlencode
from django.conf import settings

logger = logging.getLogger(__name__)


class TTSProvider:
    """TTS 提供商基类"""
    
    def generate_speech(
        self,
        text: str,
        voice: str,
        output_path: str,
        **kwargs
    ) -> str:
        """
        生成语音
        
        Args:
            text: 要转换的文本
            voice: 音色ID
            output_path: 输出文件路径
            **kwargs: 其他参数
            
        Returns:
            str: 生成的音频文件路径
        """
        raise NotImplementedError


class AliyunTTSProvider(TTSProvider):
    """阿里云 TTS 服务"""
    
    def __init__(self, app_key: str, access_key_id: str, access_key_secret: str):
        self.app_key = app_key
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.api_url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts"
    
    def generate_speech(
        self,
        text: str,
        voice: str = "xiaoyun",  # 默认音色
        output_path: str = None,
        speech_rate: int = 0,  # 语速 -500~500
        pitch_rate: int = 0,   # 音调 -500~500
        volume: int = 50,      # 音量 0~100
        sample_rate: int = 16000,  # 采样率
        format: str = "mp3"    # 格式: wav, mp3
    ) -> str:
        """
        使用阿里云 TTS 生成语音
        文档: https://help.aliyun.com/document_detail/84435.html
        """
        try:
            # 构建请求参数
            params = {
                'appkey': self.app_key,
                'token': self._get_token(),
                'text': text,
                'voice': voice,
                'format': format,
                'sample_rate': sample_rate,
                'volume': volume,
                'speech_rate': speech_rate,
                'pitch_rate': pitch_rate
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=60
            )
            
            if response.status_code == 200:
                # 检查响应头
                content_type = response.headers.get('Content-Type', '')
                
                if 'audio' in content_type:
                    # 保存音频文件
                    if not output_path:
                        output_path = os.path.join(
                            settings.MEDIA_ROOT,
                            'tts',
                            f'tts_{int(time.time())}_{hashlib.md5(text.encode()).hexdigest()[:8]}.{format}'
                        )
                    
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    logger.info(f"阿里云 TTS 生成成功: {output_path}")
                    return output_path
                else:
                    # 错误响应
                    error_data = response.json()
                    raise Exception(f"阿里云 TTS 错误: {error_data}")
            else:
                raise Exception(f"阿里云 TTS 请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"阿里云 TTS 生成失败: {str(e)}")
            raise
    
    def _get_token(self) -> str:
        """
        获取访问令牌
        文档: https://help.aliyun.com/document_detail/72153.html
        """
        token_url = "https://nls-meta.cn-shanghai.aliyuncs.com/token"
        
        params = {
            'AccessKeyId': self.access_key_id,
            'Action': 'CreateToken',
            'Version': '2019-02-28',
            'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            'Format': 'JSON',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'SignatureNonce': str(int(time.time() * 1000))
        }
        
        # 签名
        signature = self._sign_request(params)
        params['Signature'] = signature
        
        response = requests.get(token_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data['Token']['Id']
        else:
            raise Exception(f"获取阿里云 Token 失败: {response.text}")
    
    def _sign_request(self, params: Dict) -> str:
        """生成请求签名"""
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        string_to_sign = f"GET&%2F&{urlencode({'': query_string})[1:]}"
        
        h = hmac.new(
            (self.access_key_secret + '&').encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        )
        
        return base64.b64encode(h.digest()).decode('utf-8')


class AzureTTSProvider(TTSProvider):
    """Azure TTS 服务"""
    
    def __init__(self, subscription_key: str, region: str = "eastasia"):
        self.subscription_key = subscription_key
        self.region = region
        self.token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        self.tts_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    def generate_speech(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",  # 默认音色
        output_path: str = None,
        speech_rate: str = "0%",  # 语速 -50% ~ +100%
        pitch: str = "0%",        # 音调
        volume: str = "0%",       # 音量
        format: str = "audio-16khz-128kbitrate-mono-mp3"
    ) -> str:
        """
        使用 Azure TTS 生成语音
        文档: https://docs.microsoft.com/azure/cognitive-services/speech-service/
        """
        try:
            # 获取访问令牌
            token = self._get_token()
            
            # 构建 SSML
            ssml = f"""
            <speak version='1.0' xml:lang='zh-CN'>
                <voice xml:lang='zh-CN' name='{voice}'>
                    <prosody rate='{speech_rate}' pitch='{pitch}' volume='{volume}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # 发送请求
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': format,
                'User-Agent': 'AI-Story-TTS'
            }
            
            response = requests.post(
                self.tts_url,
                headers=headers,
                data=ssml.encode('utf-8'),
                timeout=60
            )
            
            if response.status_code == 200:
                # 保存音频文件
                if not output_path:
                    ext = 'mp3' if 'mp3' in format else 'wav'
                    output_path = os.path.join(
                        settings.MEDIA_ROOT,
                        'tts',
                        f'tts_{int(time.time())}_{hashlib.md5(text.encode()).hexdigest()[:8]}.{ext}'
                    )
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Azure TTS 生成成功: {output_path}")
                return output_path
            else:
                raise Exception(f"Azure TTS 请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Azure TTS 生成失败: {str(e)}")
            raise
    
    def _get_token(self) -> str:
        """获取访问令牌"""
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        
        response = requests.post(self.token_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"获取 Azure Token 失败: {response.text}")


class XunfeiTTSProvider(TTSProvider):
    """讯飞 TTS 服务"""
    
    def __init__(self, app_id: str, api_key: str, api_secret: str):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = "wss://tts-api.xfyun.cn/v2/tts"
    
    def generate_speech(
        self,
        text: str,
        voice: str = "xiaoyan",  # 默认音色
        output_path: str = None,
        speed: int = 50,   # 语速 0~100
        pitch: int = 50,   # 音调 0~100
        volume: int = 50,  # 音量 0~100
        format: str = "mp3"
    ) -> str:
        """
        使用讯飞 TTS 生成语音
        文档: https://www.xfyun.cn/doc/tts/online_tts/API.html
        """
        try:
            import websocket
            import ssl
            
            # 构建认证 URL
            auth_url = self._create_auth_url()
            
            # 准备参数
            params = {
                "common": {
                    "app_id": self.app_id
                },
                "business": {
                    "vcn": voice,
                    "speed": speed,
                    "pitch": pitch,
                    "volume": volume,
                    "aue": "lame" if format == "mp3" else "raw",
                    "tte": "UTF8"
                },
                "data": {
                    "status": 2,
                    "text": base64.b64encode(text.encode('utf-8')).decode('utf-8')
                }
            }
            
            # 准备输出文件
            if not output_path:
                output_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'tts',
                    f'tts_{int(time.time())}_{hashlib.md5(text.encode()).hexdigest()[:8]}.{format}'
                )
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 音频数据缓冲
            audio_data = bytearray()
            
            def on_message(ws, message):
                data = json.loads(message)
                code = data.get('code')
                
                if code != 0:
                    raise Exception(f"讯飞 TTS 错误: {data.get('message')}")
                
                # 获取音频数据
                audio = data.get('data', {}).get('audio')
                if audio:
                    audio_data.extend(base64.b64decode(audio))
                
                # 检查是否完成
                if data.get('data', {}).get('status') == 2:
                    ws.close()
            
            def on_error(ws, error):
                logger.error(f"讯飞 TTS WebSocket 错误: {error}")
            
            def on_open(ws):
                ws.send(json.dumps(params))
            
            # 创建 WebSocket 连接
            ws = websocket.WebSocketApp(
                auth_url,
                on_message=on_message,
                on_error=on_error,
                on_open=on_open
            )
            
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # 保存音频文件
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"讯飞 TTS 生成成功: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"讯飞 TTS 生成失败: {str(e)}")
            raise
    
    def _create_auth_url(self) -> str:
        """创建认证 URL"""
        from urllib.parse import urlencode, quote
        from datetime import datetime
        
        # 生成时间戳
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接签名原文
        signature_origin = f"host: tts-api.xfyun.cn\ndate: {date}\nGET /v2/tts HTTP/1.1"
        
        # 进行 HMAC-SHA256 加密
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        # 构建认证参数
        authorization = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        
        # 构建 URL
        params = {
            'authorization': base64.b64encode(authorization.encode('utf-8')).decode('utf-8'),
            'date': date,
            'host': 'tts-api.xfyun.cn'
        }
        
        return f"{self.api_url}?{urlencode(params)}"


class TTSService:
    """TTS 服务管理器"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """初始化 TTS 提供商"""
        # 阿里云
        if hasattr(settings, 'ALIYUN_TTS_CONFIG'):
            config = settings.ALIYUN_TTS_CONFIG
            self.providers['aliyun'] = AliyunTTSProvider(
                app_key=config['app_key'],
                access_key_id=config['access_key_id'],
                access_key_secret=config['access_key_secret']
            )
        
        # Azure
        if hasattr(settings, 'AZURE_TTS_CONFIG'):
            config = settings.AZURE_TTS_CONFIG
            self.providers['azure'] = AzureTTSProvider(
                subscription_key=config['subscription_key'],
                region=config.get('region', 'eastasia')
            )
        
        # 讯飞
        if hasattr(settings, 'XUNFEI_TTS_CONFIG'):
            config = settings.XUNFEI_TTS_CONFIG
            self.providers['xunfei'] = XunfeiTTSProvider(
                app_id=config['app_id'],
                api_key=config['api_key'],
                api_secret=config['api_secret']
            )
    
    def generate_speech(
        self,
        text: str,
        provider: str = 'aliyun',
        voice: str = None,
        output_path: str = None,
        **kwargs
    ) -> str:
        """
        生成语音
        
        Args:
            text: 文本内容
            provider: 提供商 (aliyun/azure/xunfei)
            voice: 音色
            output_path: 输出路径
            **kwargs: 其他参数
            
        Returns:
            str: 音频文件路径
        """
        if provider not in self.providers:
            raise ValueError(f"不支持的 TTS 提供商: {provider}")
        
        return self.providers[provider].generate_speech(
            text=text,
            voice=voice,
            output_path=output_path,
            **kwargs
        )
    
    def get_available_voices(self, provider: str = 'aliyun') -> List[Dict]:
        """
        获取可用音色列表
        
        Returns:
            List[Dict]: 音色列表
        """
        # 阿里云音色
        aliyun_voices = [
            {'id': 'xiaoyun', 'name': '小云', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'xiaogang', 'name': '小刚', 'gender': 'male', 'language': 'zh-CN'},
            {'id': 'ruoxi', 'name': '若兮', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'siqi', 'name': '思琪', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'sijia', 'name': '思佳', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'aiqi', 'name': '艾琪', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'aijia', 'name': '艾佳', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'aicheng', 'name': '艾诚', 'gender': 'male', 'language': 'zh-CN'},
        ]
        
        # Azure 音色
        azure_voices = [
            {'id': 'zh-CN-XiaoxiaoNeural', 'name': '晓晓', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'zh-CN-YunxiNeural', 'name': '云希', 'gender': 'male', 'language': 'zh-CN'},
            {'id': 'zh-CN-YunyangNeural', 'name': '云扬', 'gender': 'male', 'language': 'zh-CN'},
            {'id': 'zh-CN-XiaochenNeural', 'name': '晓辰', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'zh-CN-XiaohanNeural', 'name': '晓涵', 'gender': 'female', 'language': 'zh-CN'},
        ]
        
        # 讯飞音色
        xunfei_voices = [
            {'id': 'xiaoyan', 'name': '小燕', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'aisjiuxu', 'name': '许久', 'gender': 'male', 'language': 'zh-CN'},
            {'id': 'aisxping', 'name': '小萍', 'gender': 'female', 'language': 'zh-CN'},
            {'id': 'aisjinger', 'name': '小婧', 'gender': 'female', 'language': 'zh-CN'},
        ]
        
        voices_map = {
            'aliyun': aliyun_voices,
            'azure': azure_voices,
            'xunfei': xunfei_voices
        }
        
        return voices_map.get(provider, [])
