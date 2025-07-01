# Contact 模型：用于存储联系人信息（邮箱、姓名、在线状态），支持序列化/反序列化。

class Contact:
    def __init__(self, email, name, online=False):
        """
        :param email: 联系人邮箱
        :param name: 联系人姓名
        :param online: 在线状态（True/False）
        """
        self.email = email
        self.name = name
        self.online = online

    def to_dict(self):
        """
        转为字典，便于网络传输和存储
        :return: dict
        """
        return {
            "email": self.email,
            "name": self.name,
            "online": self.online
        }

    @classmethod
    def from_dict(cls, data):
        """
        从字典创建 Contact 对象
        :param data: dict
        :return: Contact
        """
        return cls(
            email=data.get('email'),
            name=data.get('name'),
            online=data.get('online', False)
        )

    def __str__(self):
        return f"{self.name} ({self.email}) - {'Online' if self.online else 'Offline'}"