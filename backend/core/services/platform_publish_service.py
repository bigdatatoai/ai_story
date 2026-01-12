"""
平台发布服务
支持一键发布到抖音、快手、B站、视频号等平台
使用各平台官方开放 API
"""

import os
import json
import logging
import requests
import hashlib
import time
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class PlatformPublisher:
    """平台发布基类"""
    
    def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        **kwargs
    ) -> Dict:
        """
        发布视频
        
        Args:
            video_path: 视频文件路径
            title: 标题
            description: 描述
            tags: 标签列表
            **kwargs: 其他平台特定参数
            
        Returns:
            Dict: 发布结果
        """
        raise NotImplementedError


class DouyinPublisher(PlatformPublisher):
    """抖音开放平台发布"""
    
    def __init__(self, client_key: str, client_secret: str, access_token: str = None):
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = access_token
        self.api_base = "https://open.douyin.com"
    
    def get_access_token(self, code: str) -> str:
        """
        获取访问令牌
        文档: https://developer.open-douyin.com/docs/resource/zh-CN/dop/develop/openapi/account-permission/get-access-token
        
        Args:
            code: 授权码
            
        Returns:
            str: access_token
        """
        url = f"{self.api_base}/oauth/access_token/"
        
        params = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(url, json=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                self.access_token = data['data']['access_token']
                return self.access_token
            else:
                raise Exception(f"获取 token 失败: {data.get('message')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")
    
    def upload_video(self, video_path: str) -> str:
        """
        上传视频到抖音
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            str: video_id
        """
        if not self.access_token:
            raise Exception("未设置 access_token")
        
        # 1. 初始化上传
        init_url = f"{self.api_base}/api/douyin/v1/video/part/init/"
        
        headers = {
            'access-token': self.access_token
        }
        
        response = requests.post(init_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"初始化上传失败: {response.text}")
        
        data = response.json()
        upload_id = data['data']['upload_id']
        
        # 2. 分片上传视频
        chunk_size = 5 * 1024 * 1024  # 5MB per chunk
        
        with open(video_path, 'rb') as f:
            part_number = 1
            
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                upload_url = f"{self.api_base}/api/douyin/v1/video/part/upload/"
                
                files = {
                    'video': chunk
                }
                
                params = {
                    'upload_id': upload_id,
                    'part_number': part_number
                }
                
                response = requests.post(
                    upload_url,
                    headers=headers,
                    params=params,
                    files=files,
                    timeout=120
                )
                
                if response.status_code != 200:
                    raise Exception(f"上传分片 {part_number} 失败: {response.text}")
                
                part_number += 1
        
        # 3. 完成上传
        complete_url = f"{self.api_base}/api/douyin/v1/video/part/complete/"
        
        params = {
            'upload_id': upload_id
        }
        
        response = requests.post(complete_url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['video']['video_id']
        else:
            raise Exception(f"完成上传失败: {response.text}")
    
    def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        cover_image: str = None,
        **kwargs
    ) -> Dict:
        """
        发布视频到抖音
        
        Args:
            video_path: 视频文件路径
            title: 标题
            description: 描述
            tags: 话题标签
            cover_image: 封面图片路径
            **kwargs: 其他参数
            
        Returns:
            Dict: 发布结果
        """
        try:
            # 1. 上传视频
            logger.info(f"开始上传视频到抖音: {video_path}")
            video_id = self.upload_video(video_path)
            
            # 2. 创建视频
            create_url = f"{self.api_base}/api/douyin/v1/video/create/"
            
            headers = {
                'access-token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            # 构建请求体
            body = {
                'video_id': video_id,
                'text': f"{title}\n{description}",
            }
            
            # 添加话题
            if tags:
                body['micro_app_info'] = {
                    'app_id': '',
                    'title': '',
                    'description': '',
                }
                # 抖音话题格式: #话题名#
                text_with_tags = body['text']
                for tag in tags:
                    text_with_tags += f" #{tag}"
                body['text'] = text_with_tags
            
            # 添加封面
            if cover_image:
                # 需要先上传封面图片
                pass  # 封面上传逻辑
            
            # 发布设置
            body.update({
                'poi_id': kwargs.get('poi_id', ''),  # 地理位置
                'at_users': kwargs.get('at_users', []),  # @用户
            })
            
            response = requests.post(
                create_url,
                headers=headers,
                json=body,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data'):
                    logger.info(f"抖音发布成功: {data['data']}")
                    return {
                        'success': True,
                        'platform': 'douyin',
                        'item_id': data['data'].get('item_id'),
                        'share_url': data['data'].get('share_url'),
                        'message': '发布成功'
                    }
                else:
                    raise Exception(f"发布失败: {data.get('message')}")
            else:
                raise Exception(f"请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"抖音发布失败: {str(e)}")
            return {
                'success': False,
                'platform': 'douyin',
                'error': str(e)
            }


class KuaishouPublisher(PlatformPublisher):
    """快手开放平台发布"""
    
    def __init__(self, app_id: str, app_secret: str, access_token: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.api_base = "https://open.kuaishou.com"
    
    def get_access_token(self, code: str) -> str:
        """
        获取访问令牌
        文档: https://open.kuaishou.com/platform/openApi
        """
        url = f"{self.api_base}/oauth2/access_token"
        
        params = {
            'app_id': self.app_id,
            'app_secret': self.app_secret,
            'grant_type': 'code',
            'code': code
        }
        
        response = requests.post(url, json=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('result') == 1:
                self.access_token = data['access_token']
                return self.access_token
            else:
                raise Exception(f"获取 token 失败: {data.get('error_msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")
    
    def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        **kwargs
    ) -> Dict:
        """
        发布视频到快手
        """
        try:
            if not self.access_token:
                raise Exception("未设置 access_token")
            
            # 1. 上传视频
            upload_url = f"{self.api_base}/rest/openapi/photo/upload"
            
            headers = {
                'access-token': self.access_token
            }
            
            with open(video_path, 'rb') as f:
                files = {
                    'file': f
                }
                
                data = {
                    'caption': f"{title}\n{description}",
                    'tags': ','.join(tags) if tags else ''
                }
                
                response = requests.post(
                    upload_url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300
                )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('result') == 1:
                    logger.info(f"快手发布成功: {result}")
                    return {
                        'success': True,
                        'platform': 'kuaishou',
                        'photo_id': result.get('photo_id'),
                        'message': '发布成功'
                    }
                else:
                    raise Exception(f"发布失败: {result.get('error_msg')}")
            else:
                raise Exception(f"请求失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"快手发布失败: {str(e)}")
            return {
                'success': False,
                'platform': 'kuaishou',
                'error': str(e)
            }


class BilibiliPublisher(PlatformPublisher):
    """B站开放平台发布"""
    
    def __init__(self, access_key: str, access_secret: str):
        self.access_key = access_key
        self.access_secret = access_secret
        self.api_base = "https://member.bilibili.com"
    
    def _sign_request(self, params: Dict) -> str:
        """生成请求签名"""
        sorted_params = sorted(params.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str = query_string + self.access_secret
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def upload_video(self, video_path: str) -> Dict:
        """
        上传视频到 B站
        
        Returns:
            Dict: 上传结果，包含 filename 等信息
        """
        # 1. 获取上传地址
        preupload_url = f"{self.api_base}/x/vu/web/add/v3"
        
        params = {
            'access_key': self.access_key,
            'name': os.path.basename(video_path),
            'size': os.path.getsize(video_path),
            'r': 'upos',
            'profile': 'ugcupos/bup',
            'ssl': '0',
            'version': '2.10.4',
            'build': '2100400',
            'upcdn': 'ws',
            'probe_version': '20211012'
        }
        
        params['sign'] = self._sign_request(params)
        
        response = requests.get(preupload_url, params=params, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"获取上传地址失败: {response.text}")
        
        data = response.json()
        
        if data.get('code') != 0:
            raise Exception(f"获取上传地址失败: {data.get('message')}")
        
        # 2. 上传视频文件
        upload_url = data['data']['endpoint']
        auth = data['data']['auth']
        biz_id = data['data']['biz_id']
        
        with open(video_path, 'rb') as f:
            video_data = f.read()
        
        headers = {
            'X-Upos-Auth': auth
        }
        
        upload_response = requests.put(
            upload_url,
            headers=headers,
            data=video_data,
            timeout=600
        )
        
        if upload_response.status_code != 200:
            raise Exception(f"上传视频失败: {upload_response.text}")
        
        return {
            'filename': data['data']['upos_uri'].split('/')[-1],
            'biz_id': biz_id
        }
    
    def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        category: int = 17,  # 分区ID，17=单机游戏
        cover_image: str = None,
        **kwargs
    ) -> Dict:
        """
        发布视频到 B站
        """
        try:
            # 1. 上传视频
            logger.info(f"开始上传视频到B站: {video_path}")
            upload_result = self.upload_video(video_path)
            
            # 2. 提交稿件
            submit_url = f"{self.api_base}/x/vu/web/add/v3"
            
            params = {
                'access_key': self.access_key,
                'copyright': 1,  # 1=自制，2=转载
                'title': title,
                'tid': category,
                'tag': ','.join(tags) if tags else '',
                'desc': description,
                'cover': cover_image or '',
                'videos': json.dumps([{
                    'filename': upload_result['filename'],
                    'title': title,
                    'desc': ''
                }]),
                'source': '',
                'dynamic': '',
                'interactive': 0,
                'no_reprint': 1,
                'subtitle': {
                    'open': 0,
                    'lan': ''
                }
            }
            
            params['sign'] = self._sign_request(params)
            
            response = requests.post(submit_url, data=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 0:
                    logger.info(f"B站发布成功: {data}")
                    return {
                        'success': True,
                        'platform': 'bilibili',
                        'aid': data['data'].get('aid'),
                        'bvid': data['data'].get('bvid'),
                        'message': '发布成功'
                    }
                else:
                    raise Exception(f"发布失败: {data.get('message')}")
            else:
                raise Exception(f"请求失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"B站发布失败: {str(e)}")
            return {
                'success': False,
                'platform': 'bilibili',
                'error': str(e)
            }


class PlatformPublishService:
    """平台发布服务管理器"""
    
    def __init__(self):
        self.publishers = {}
        self._init_publishers()
    
    def _init_publishers(self):
        """初始化发布器"""
        # 抖音
        if hasattr(settings, 'DOUYIN_CONFIG'):
            config = settings.DOUYIN_CONFIG
            self.publishers['douyin'] = DouyinPublisher(
                client_key=config['client_key'],
                client_secret=config['client_secret'],
                access_token=config.get('access_token')
            )
        
        # 快手
        if hasattr(settings, 'KUAISHOU_CONFIG'):
            config = settings.KUAISHOU_CONFIG
            self.publishers['kuaishou'] = KuaishouPublisher(
                app_id=config['app_id'],
                app_secret=config['app_secret'],
                access_token=config.get('access_token')
            )
        
        # B站
        if hasattr(settings, 'BILIBILI_CONFIG'):
            config = settings.BILIBILI_CONFIG
            self.publishers['bilibili'] = BilibiliPublisher(
                access_key=config['access_key'],
                access_secret=config['access_secret']
            )
    
    def publish_to_platform(
        self,
        platform: str,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        **kwargs
    ) -> Dict:
        """
        发布到指定平台
        
        Args:
            platform: 平台名称 (douyin/kuaishou/bilibili)
            video_path: 视频路径
            title: 标题
            description: 描述
            tags: 标签
            **kwargs: 其他参数
            
        Returns:
            Dict: 发布结果
        """
        if platform not in self.publishers:
            return {
                'success': False,
                'platform': platform,
                'error': f'不支持的平台: {platform}'
            }
        
        return self.publishers[platform].publish(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            **kwargs
        )
    
    def publish_to_multiple_platforms(
        self,
        platforms: List[str],
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        **kwargs
    ) -> Dict[str, Dict]:
        """
        发布到多个平台
        
        Returns:
            Dict[str, Dict]: {平台: 发布结果}
        """
        results = {}
        
        for platform in platforms:
            result = self.publish_to_platform(
                platform=platform,
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                **kwargs
            )
            results[platform] = result
            
            # 添加延迟，避免请求过快
            time.sleep(2)
        
        return results
    
    def get_supported_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return list(self.publishers.keys())
