import json
import time

# Message 模型：用于存储和管理消息结构，支持序列化/反序列化。
class Message:
    def __init__(self, sender, receiver, content, type="text", timestamp=None):
        """
        :param sender: 发送者邮箱
        :param receiver: 接收者邮箱
        :param content: 消息内容
        :param type: 消息类型（如 'text', 'picture'）
        :param timestamp: 消息时间戳（int，Unix时间戳）
        """
        self.sender = sender
        self.receiver = receiver
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
            "sender": self.sender,
            "receiver": self.receiver
        }

    @classmethod
    def from_dict(cls, data):
        """
        从字典创建 Message 对象，兼容不同时间戳格式
        :param data: dict
        :return: Message
        """
        return cls(
            sender=data.get('sender'),
            receiver=data.get('receiver'),
            content=data.get('message', {}).get('content'),
            type=data.get('message', {}).get('type', 'text'),
            timestamp=data.get('timestamp')
        )

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}: {str(self.content)[:20]}..."