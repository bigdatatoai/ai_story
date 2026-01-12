"""
WebSocket协作消费者
实现实时故事协作编辑功能
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger('ai_story.websocket')


class StoryCollaborationConsumer(AsyncWebsocketConsumer):
    """故事协作WebSocket消费者"""
    
    async def connect(self):
        """建立WebSocket连接"""
        self.story_id = self.scope['url_route']['kwargs']['story_id']
        self.room_group_name = f'story_{self.story_id}'
        self.user = self.scope.get('user')
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 通知其他用户有新用户加入
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else '访客',
            }
        )
        
        logger.info(f"用户 {self.user.username if self.user.is_authenticated else '访客'} 加入故事 {self.story_id}")
    
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        # 通知其他用户有用户离开
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else '访客',
            }
        )
        
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"用户 {self.user.username if self.user.is_authenticated else '访客'} 离开故事 {self.story_id}")
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'edit':
                await self.handle_edit(data)
            elif action == 'cursor_move':
                await self.handle_cursor_move(data)
            elif action == 'comment':
                await self.handle_comment(data)
            elif action == 'lock_section':
                await self.handle_lock_section(data)
            elif action == 'unlock_section':
                await self.handle_unlock_section(data)
            else:
                logger.warning(f"未知的操作类型: {action}")
        
        except json.JSONDecodeError:
            logger.error("无效的JSON数据")
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
    
    async def handle_edit(self, data):
        """处理编辑操作"""
        content = data.get('content')
        position = data.get('position')
        edit_type = data.get('edit_type', 'insert')  # insert/delete/replace
        
        # 广播编辑操作给其他用户
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'story_edit',
                'user_id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else '访客',
                'content': content,
                'position': position,
                'edit_type': edit_type,
            }
        )
        
        # 保存到数据库（异步）
        await self.save_edit_to_db(content, position, edit_type)
    
    async def handle_cursor_move(self, data):
        """处理光标移动"""
        position = data.get('position')
        
        # 广播光标位置
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_update',
                'user_id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else '访客',
                'position': position,
            }
        )
    
    async def handle_comment(self, data):
        """处理评论"""
        comment_text = data.get('text')
        position = data.get('position')
        
        # 广播评论
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_comment',
                'user_id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else '访客',
                'text': comment_text,
                'position': position,
            }
        )
    
    async def handle_lock_section(self, data):
        """处理段落锁定"""
        section_id = data.get('section_id')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'section_locked',
                'user_id': str(self.user.id) if self.user.is_authenticated else 'anonymous',
                'username': self.user.username if self.user.is_authenticated else '访客',
                'section_id': section_id,
            }
        )
    
    async def handle_unlock_section(self, data):
        """处理段落解锁"""
        section_id = data.get('section_id')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'section_unlocked',
                'section_id': section_id,
            }
        )
    
    # 以下是接收组消息的处理方法
    
    async def user_joined(self, event):
        """用户加入通知"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def user_left(self, event):
        """用户离开通知"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def story_edit(self, event):
        """故事编辑通知"""
        # 不发送给自己
        if event['user_id'] == str(self.user.id if self.user.is_authenticated else 'anonymous'):
            return
        
        await self.send(text_data=json.dumps({
            'type': 'edit',
            'user_id': event['user_id'],
            'username': event['username'],
            'content': event['content'],
            'position': event['position'],
            'edit_type': event['edit_type'],
        }))
    
    async def cursor_update(self, event):
        """光标更新通知"""
        # 不发送给自己
        if event['user_id'] == str(self.user.id if self.user.is_authenticated else 'anonymous'):
            return
        
        await self.send(text_data=json.dumps({
            'type': 'cursor_move',
            'user_id': event['user_id'],
            'username': event['username'],
            'position': event['position'],
        }))
    
    async def new_comment(self, event):
        """新评论通知"""
        await self.send(text_data=json.dumps({
            'type': 'comment',
            'user_id': event['user_id'],
            'username': event['username'],
            'text': event['text'],
            'position': event['position'],
        }))
    
    async def section_locked(self, event):
        """段落锁定通知"""
        await self.send(text_data=json.dumps({
            'type': 'section_locked',
            'user_id': event['user_id'],
            'username': event['username'],
            'section_id': event['section_id'],
        }))
    
    async def section_unlocked(self, event):
        """段落解锁通知"""
        await self.send(text_data=json.dumps({
            'type': 'section_unlocked',
            'section_id': event['section_id'],
        }))
    
    @database_sync_to_async
    def save_edit_to_db(self, content, position, edit_type):
        """保存编辑到数据库"""
        from apps.content.models.story_models import Story
        
        try:
            story = Story.objects.get(id=self.story_id)
            # 这里可以实现更复杂的版本控制逻辑
            # 简化版：直接更新内容
            story.content = content
            story.save()
        except Story.DoesNotExist:
            logger.error(f"故事 {self.story_id} 不存在")
        except Exception as e:
            logger.error(f"保存编辑失败: {str(e)}")
