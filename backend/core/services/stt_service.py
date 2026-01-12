"""
语音识别服务（Speech-to-Text）
用于自动生成字幕
支持：阿里云、Azure、讯飞
"""

import os
import json
import logging
import requests
import base64
import hashlib
import hmac
import time
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class STTProvider:
    """STT 提供商基类"""
    
    def transcribe(
        self,
        audio_path: str,
        language: str = 'zh-CN',
        **kwargs
    ) -> Dict:
        """
        语音识别
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码
            **kwargs: 其他参数
            
        Returns:
            Dict: 识别结果，包含文本和时间戳
        """
        raise NotImplementedError


class AliyunSTTProvider(STTProvider):
    """阿里云语音识别"""
    
    def __init__(self, app_key: str, access_key_id: str, access_key_secret: str):
        self.app_key = app_key
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.api_url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr"
    
    def transcribe(
        self,
        audio_path: str,
        language: str = 'zh-CN',
        enable_punctuation: bool = True,
        enable_inverse_text_normalization: bool = True
    ) -> Dict:
        """
        阿里云语音识别
        文档: https://help.aliyun.com/document_detail/90727.html
        """
        try:
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # 获取 Token
            token = self._get_token()
            
            # 构建请求
            params = {
                'appkey': self.app_key,
                'token': token,
                'format': 'pcm',  # 或 wav, mp3
                'sample_rate': 16000,
                'enable_punctuation_prediction': enable_punctuation,
                'enable_inverse_text_normalization': enable_inverse_text_normalization
            }
            
            headers = {
                'Content-Type': 'application/octet-stream'
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                params=params,
                headers=headers,
                data=audio_data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 解析结果
                text = result.get('result', '')
                
                return {
                    'text': text,
                    'segments': self._parse_segments(result),
                    'confidence': result.get('confidence', 0),
                    'provider': 'aliyun'
                }
            else:
                raise Exception(f"阿里云 STT 请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"阿里云 STT 识别失败: {str(e)}")
            raise
    
    def _get_token(self) -> str:
        """获取访问令牌"""
        from urllib.parse import urlencode
        
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
        from urllib.parse import urlencode, quote
        
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        string_to_sign = f"GET&%2F&{quote(query_string, safe='')}"
        
        h = hmac.new(
            (self.access_key_secret + '&').encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        )
        
        return base64.b64encode(h.digest()).decode('utf-8')
    
    def _parse_segments(self, result: Dict) -> List[Dict]:
        """解析时间戳片段"""
        segments = []
        
        # 阿里云返回的详细结果
        if 'flash_result' in result:
            flash_result = result['flash_result']
            sentences = flash_result.get('sentences', [])
            
            for sentence in sentences:
                segments.append({
                    'text': sentence.get('text', ''),
                    'start': sentence.get('begin_time', 0) / 1000,  # 转换为秒
                    'end': sentence.get('end_time', 0) / 1000,
                    'confidence': sentence.get('confidence', 0)
                })
        
        return segments


class AzureSTTProvider(STTProvider):
    """Azure 语音识别"""
    
    def __init__(self, subscription_key: str, region: str = "eastasia"):
        self.subscription_key = subscription_key
        self.region = region
        self.api_url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    def transcribe(
        self,
        audio_path: str,
        language: str = 'zh-CN',
        detailed: bool = True
    ) -> Dict:
        """
        Azure 语音识别
        文档: https://docs.microsoft.com/azure/cognitive-services/speech-service/
        """
        try:
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # 构建请求
            params = {
                'language': language,
                'format': 'detailed' if detailed else 'simple'
            }
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
                'Accept': 'application/json'
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                params=params,
                headers=headers,
                data=audio_data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 解析结果
                if detailed:
                    best_result = result.get('NBest', [{}])[0]
                    text = best_result.get('Display', '')
                    confidence = best_result.get('Confidence', 0)
                    segments = self._parse_azure_segments(best_result)
                else:
                    text = result.get('DisplayText', '')
                    confidence = 0
                    segments = []
                
                return {
                    'text': text,
                    'segments': segments,
                    'confidence': confidence,
                    'provider': 'azure'
                }
            else:
                raise Exception(f"Azure STT 请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Azure STT 识别失败: {str(e)}")
            raise
    
    def _parse_azure_segments(self, result: Dict) -> List[Dict]:
        """解析 Azure 时间戳片段"""
        segments = []
        
        words = result.get('Words', [])
        
        for word in words:
            segments.append({
                'text': word.get('Word', ''),
                'start': word.get('Offset', 0) / 10000000,  # 转换为秒
                'end': (word.get('Offset', 0) + word.get('Duration', 0)) / 10000000,
                'confidence': word.get('Confidence', 0)
            })
        
        return segments


class XunfeiSTTProvider(STTProvider):
    """讯飞语音识别"""
    
    def __init__(self, app_id: str, api_key: str, api_secret: str):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = "wss://iat-api.xfyun.cn/v2/iat"
    
    def transcribe(
        self,
        audio_path: str,
        language: str = 'zh_cn',
        enable_punctuation: bool = True
    ) -> Dict:
        """
        讯飞语音识别
        文档: https://www.xfyun.cn/doc/asr/voicedictation/API.html
        """
        try:
            import websocket
            import ssl
            
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # 构建认证 URL
            auth_url = self._create_auth_url()
            
            # 结果缓存
            result_text = []
            result_segments = []
            
            def on_message(ws, message):
                data = json.loads(message)
                code = data.get('code')
                
                if code != 0:
                    raise Exception(f"讯飞 STT 错误: {data.get('message')}")
                
                # 解析识别结果
                result = data.get('data', {}).get('result', {})
                ws_list = result.get('ws', [])
                
                for ws_item in ws_list:
                    for cw in ws_item.get('cw', []):
                        word = cw.get('w', '')
                        result_text.append(word)
                        
                        # 添加时间戳
                        result_segments.append({
                            'text': word,
                            'start': ws_item.get('bg', 0) / 1000,
                            'end': ws_item.get('ed', 0) / 1000,
                            'confidence': 0
                        })
                
                # 检查是否完成
                if data.get('data', {}).get('status') == 2:
                    ws.close()
            
            def on_error(ws, error):
                logger.error(f"讯飞 STT WebSocket 错误: {error}")
            
            def on_open(ws):
                # 分块发送音频数据
                chunk_size = 1280  # 每次发送 1280 字节
                status = 0  # 0: 首帧, 1: 中间帧, 2: 尾帧
                
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i + chunk_size]
                    
                    if i + chunk_size >= len(audio_data):
                        status = 2  # 最后一帧
                    elif i == 0:
                        status = 0  # 第一帧
                    else:
                        status = 1  # 中间帧
                    
                    params = {
                        "common": {
                            "app_id": self.app_id
                        },
                        "business": {
                            "language": language,
                            "domain": "iat",
                            "accent": "mandarin",
                            "vad_eos": 10000,
                            "dwa": "wpgs" if enable_punctuation else ""
                        },
                        "data": {
                            "status": status,
                            "format": "audio/L16;rate=16000",
                            "encoding": "raw",
                            "audio": base64.b64encode(chunk).decode('utf-8')
                        }
                    }
                    
                    ws.send(json.dumps(params))
                    time.sleep(0.04)  # 控制发送速率
            
            # 创建 WebSocket 连接
            ws = websocket.WebSocketApp(
                auth_url,
                on_message=on_message,
                on_error=on_error,
                on_open=on_open
            )
            
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            return {
                'text': ''.join(result_text),
                'segments': result_segments,
                'confidence': 0,
                'provider': 'xunfei'
            }
            
        except Exception as e:
            logger.error(f"讯飞 STT 识别失败: {str(e)}")
            raise
    
    def _create_auth_url(self) -> str:
        """创建认证 URL"""
        from urllib.parse import urlencode
        from datetime import datetime
        
        # 生成时间戳
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接签名原文
        signature_origin = f"host: iat-api.xfyun.cn\ndate: {date}\nGET /v2/iat HTTP/1.1"
        
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
            'host': 'iat-api.xfyun.cn'
        }
        
        return f"{self.api_url}?{urlencode(params)}"


class STTService:
    """语音识别服务管理器"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """初始化 STT 提供商"""
        # 阿里云
        if hasattr(settings, 'ALIYUN_STT_CONFIG'):
            config = settings.ALIYUN_STT_CONFIG
            self.providers['aliyun'] = AliyunSTTProvider(
                app_key=config['app_key'],
                access_key_id=config['access_key_id'],
                access_key_secret=config['access_key_secret']
            )
        
        # Azure
        if hasattr(settings, 'AZURE_STT_CONFIG'):
            config = settings.AZURE_STT_CONFIG
            self.providers['azure'] = AzureSTTProvider(
                subscription_key=config['subscription_key'],
                region=config.get('region', 'eastasia')
            )
        
        # 讯飞
        if hasattr(settings, 'XUNFEI_STT_CONFIG'):
            config = settings.XUNFEI_STT_CONFIG
            self.providers['xunfei'] = XunfeiSTTProvider(
                app_id=config['app_id'],
                api_key=config['api_key'],
                api_secret=config['api_secret']
            )
    
    def transcribe(
        self,
        audio_path: str,
        provider: str = 'aliyun',
        language: str = 'zh-CN',
        **kwargs
    ) -> Dict:
        """
        语音识别
        
        Args:
            audio_path: 音频文件路径
            provider: 提供商 (aliyun/azure/xunfei)
            language: 语言代码
            **kwargs: 其他参数
            
        Returns:
            Dict: 识别结果
        """
        if provider not in self.providers:
            raise ValueError(f"不支持的 STT 提供商: {provider}")
        
        return self.providers[provider].transcribe(
            audio_path=audio_path,
            language=language,
            **kwargs
        )
    
    def generate_subtitles(
        self,
        audio_path: str,
        provider: str = 'aliyun',
        max_chars_per_line: int = 20,
        max_duration_per_subtitle: float = 5.0
    ) -> List[Dict]:
        """
        生成字幕
        
        Args:
            audio_path: 音频文件路径
            provider: 提供商
            max_chars_per_line: 每行最大字符数
            max_duration_per_subtitle: 每条字幕最大时长(秒)
            
        Returns:
            List[Dict]: 字幕列表 [{"text": "...", "start": 0, "end": 3}, ...]
        """
        # 识别语音
        result = self.transcribe(audio_path, provider=provider)
        
        segments = result.get('segments', [])
        
        if not segments:
            # 如果没有时间戳，使用整段文本
            text = result.get('text', '')
            return self._split_text_to_subtitles(text, max_chars_per_line)
        
        # 合并片段生成字幕
        subtitles = []
        current_subtitle = {'text': '', 'start': 0, 'end': 0}
        
        for segment in segments:
            segment_text = segment['text']
            segment_start = segment['start']
            segment_end = segment['end']
            
            # 如果当前字幕为空，开始新字幕
            if not current_subtitle['text']:
                current_subtitle = {
                    'text': segment_text,
                    'start': segment_start,
                    'end': segment_end
                }
            else:
                # 检查是否需要分割
                new_text = current_subtitle['text'] + segment_text
                duration = segment_end - current_subtitle['start']
                
                if (len(new_text) > max_chars_per_line or 
                    duration > max_duration_per_subtitle):
                    # 保存当前字幕
                    subtitles.append(current_subtitle)
                    
                    # 开始新字幕
                    current_subtitle = {
                        'text': segment_text,
                        'start': segment_start,
                        'end': segment_end
                    }
                else:
                    # 继续累加
                    current_subtitle['text'] = new_text
                    current_subtitle['end'] = segment_end
        
        # 添加最后一条字幕
        if current_subtitle['text']:
            subtitles.append(current_subtitle)
        
        return subtitles
    
    def _split_text_to_subtitles(
        self,
        text: str,
        max_chars_per_line: int = 20
    ) -> List[Dict]:
        """将文本分割为字幕（无时间戳）"""
        subtitles = []
        words = list(text)
        
        for i in range(0, len(words), max_chars_per_line):
            chunk = ''.join(words[i:i + max_chars_per_line])
            subtitles.append({
                'text': chunk,
                'start': i * 0.5,  # 估算时间
                'end': (i + len(chunk)) * 0.5
            })
        
        return subtitles
