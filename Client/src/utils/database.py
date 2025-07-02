#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyDB数据库管理器：用于管理客户端本地数据存储
"""

import os
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from src.utils.logger import setup_logger
from config import DATA_CONFIG

class DatabaseManager:
    """
    TinyDB数据库管理器
    管理Friends和Messages两个表
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.db_path = os.path.join(DATA_CONFIG['database_dir'], 'client.db')
        
        try:
            # 确保数据目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # 初始化数据库，使用缓存中间件提高性能
            self.db = TinyDB(self.db_path, storage=CachingMiddleware(JSONStorage))
            
            # 获取表引用
            self.friends_table = self.db.table('friends')
            self.messages_table = self.db.table('messages')
            
            self.logger.info(f"TinyDB initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
        self.logger.info("Database connection closed")
    
    # ================== Friends表操作 ==================
    
    def add_friend(self, friend_data):
        """
        添加好友到Friends表
        :param friend_data: 好友数据字典，包含user_id, flag, online, public_key, ip, port
        :return: 插入的文档ID
        """
        try:
            # 验证必需字段
            if 'user_id' not in friend_data:
                raise ValueError("friend_data must contain 'user_id' field")
            
            Friend = Query()
            # 检查是否已存在
            existing = self.friends_table.get(Friend.user_id == friend_data['user_id'])
            if existing:
                # 更新现有记录
                self.friends_table.update(friend_data, Friend.user_id == friend_data['user_id'])
                self.logger.info(f"Updated friend: {friend_data['user_id']}")
                return existing.doc_id
            else:
                # 插入新记录
                doc_id = self.friends_table.insert(friend_data)
                self.logger.info(f"Added friend: {friend_data['user_id']}")
                return doc_id
        except Exception as e:
            self.logger.error(f"添加好友失败: {e}")
            raise
    
    def get_friend(self, user_id):
        """
        获取好友信息
        :param user_id: 用户ID
        :return: 好友数据字典或None
        """
        Friend = Query()
        result = self.friends_table.get(Friend.user_id == user_id)
        return result
    
    def get_all_friends(self):
        """
        获取所有好友
        :return: 好友列表
        """
        return self.friends_table.all()
    
    def update_friend(self, user_id, update_data):
        """
        更新好友信息
        :param user_id: 用户ID
        :param update_data: 要更新的数据字典
        :return: 是否更新成功
        """
        Friend = Query()
        result = self.friends_table.update(update_data, Friend.user_id == user_id)
        if result:
            self.logger.info(f"Updated friend: {user_id}")
        return len(result) > 0
    
    def delete_friend(self, user_id):
        """
        删除好友
        :param user_id: 用户ID
        :return: 是否删除成功
        """
        Friend = Query()
        result = self.friends_table.remove(Friend.user_id == user_id)
        if result:
            self.logger.info(f"Deleted friend: {user_id}")
        return len(result) > 0
    
    def update_friend_status(self, user_id, online):
        """
        更新好友在线状态
        :param user_id: 用户ID
        :param online: 在线状态
        """
        self.update_friend(user_id, {'online': online})
    
    def update_friend_p2p_info(self, user_id, ip, port):
        """
        更新好友P2P信息
        :param user_id: 用户ID
        :param ip: IP地址
        :param port: 端口
        """
        self.update_friend(user_id, {'ip': ip, 'port': port})
    
    def update_friend_public_key(self, user_id, public_key):
        """
        更新好友公钥
        :param user_id: 用户ID
        :param public_key: 公钥
        """
        self.update_friend(user_id, {'public_key': public_key})
    
    # ================== Messages表操作 ==================
    
    def add_message(self, message_data):
        """
        添加消息到Messages表
        :param message_data: 消息数据字典，包含timestamp, sender_id, receiver_id, message
        :return: 插入的文档ID
        """
        try:
            # 验证必需字段
            required_fields = ['timestamp', 'sender_id', 'receiver_id', 'content']
            for field in required_fields:
                if field not in message_data:
                    raise ValueError(f"message_data must contain '{field}' field")
            
            doc_id = self.messages_table.insert(message_data)
            self.logger.info(f"Added message from {message_data['sender_id']} to {message_data['receiver_id']}")
            return doc_id
        except Exception as e:
            self.logger.error(f"添加消息失败: {e}")
            raise
    
    def get_messages(self, sender_id=None, receiver_id=None, limit=None):
        """
        获取消息
        :param sender_id: 发送者ID（可选）
        :param receiver_id: 接收者ID（可选）
        :param limit: 限制返回数量（可选）
        :return: 消息列表
        """
        Message = Query()
        query = None
        
        if sender_id and receiver_id:
            query = (Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)
        elif sender_id:
            query = Message.sender_id == sender_id
        elif receiver_id:
            query = Message.receiver_id == receiver_id
        else:
            # 获取所有消息
            messages = self.messages_table.all()
            if limit:
                messages = messages[-limit:]
            return messages
        
        messages = self.messages_table.search(query)
        if limit:
            messages = messages[-limit:]
        return messages
    
    def get_chat_history(self, user1_id, user2_id, limit=None):
        """
        获取两个用户之间的聊天历史
        :param user1_id: 用户1 ID
        :param user2_id: 用户2 ID
        :param limit: 限制返回数量（可选）
        :return: 消息列表
        """
        Message = Query()
        # 查询两个方向的消息
        messages = self.messages_table.search(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        )
        
        # 按时间戳排序
        messages.sort(key=lambda x: x['timestamp'])
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def delete_messages(self, sender_id=None, receiver_id=None):
        """
        删除消息
        :param sender_id: 发送者ID（可选）
        :param receiver_id: 接收者ID（可选）
        :return: 删除的消息数量
        """
        Message = Query()
        query = None
        
        if sender_id and receiver_id:
            query = (Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)
        elif sender_id:
            query = Message.sender_id == sender_id
        elif receiver_id:
            query = Message.receiver_id == receiver_id
        else:
            return 0
        
        result = self.messages_table.remove(query)
        deleted_count = len(result)
        self.logger.info(f"Deleted {deleted_count} messages")
        return deleted_count
    
    # ================== 数据库维护 ==================
    
    def clear_all_data(self):
        """清空所有数据"""
        self.friends_table.truncate()
        self.messages_table.truncate()
        self.logger.info("All data cleared")
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        return {
            'friends_count': len(self.friends_table),
            'messages_count': len(self.messages_table),
            'database_path': self.db_path
        }
    
    def backup_database(self, backup_path):
        """
        备份数据库
        :param backup_path: 备份文件路径
        """
        import shutil
        shutil.copy2(self.db_path, backup_path)
        self.logger.info(f"Database backed up to {backup_path}")
    
    def restore_database(self, backup_path):
        """
        从备份恢复数据库
        :param backup_path: 备份文件路径
        """
        import shutil
        self.close()
        shutil.copy2(backup_path, self.db_path)
        # 重新初始化
        self.__init__()
        self.logger.info(f"Database restored from {backup_path}") 