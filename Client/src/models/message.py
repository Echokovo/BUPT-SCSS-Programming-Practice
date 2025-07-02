import json
import time

# Message 模型：用于存储和管理消息结构，支持序列化/反序列化。
class Message:
    def __init__(self, sender_id, receiver_id, content, type="text", timestamp=None):
        """
        :param sender_id: 发送者用户名
        :param receiver_id: 接收者用户名
        :param content: 消息内容
        :param type: 消息类型（如 'text', 'picture'）
        :param timestamp: 消息时间戳（int，Unix时间戳）
        """
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.type = type
        # 统一为 int 类型时间戳
        if timestamp is None:
            self.timestamp = int(time.time())
        elif isinstance(timestamp, str) and timestamp.isdigit():
            self.timestamp = int(timestamp)
        else:
            try:
                self.timestamp = int(timestamp)
            except Exception:
                self.timestamp = int(time.time())

    def to_dict(self):
        """
        转为接口文档要求的消息字典格式
        :return: dict
        """
        return {
            "timestamp": self.timestamp,
            "message": {
                "type": self.type,
                "content": self.content
            },
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id
        }

    @classmethod
    def from_dict(cls, data):
        """
        从字典创建 Message 对象，兼容不同时间戳格式
        :param data: dict
        :return: Message
        """
        return cls(
            sender_id=data.get('sender_id') or data.get('sender'),
            receiver_id=data.get('receiver_id') or data.get('receiver'),
            content=data.get('message', {}).get('content'),
            type=data.get('message', {}).get('type', 'text'),
            timestamp=data.get('timestamp')
        )

    def __str__(self):
        return f"Message from {self.sender_id} to {self.receiver_id}: {str(self.content)[:20]}..."