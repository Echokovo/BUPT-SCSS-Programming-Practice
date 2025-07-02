# Contact 模型：用于存储联系人信息（用户名、在线状态、公钥、P2P信息），支持序列化/反序列化。

class Contact:
    def __init__(self, user_id, flag=False, online=False, public_key=None, ip=None, port=None):
        """
        :param user_id: 联系人用户名
        :param flag: 好友状态位（True/False）
        :param online: 在线状态（True/False）
        :param public_key: 联系人公钥
        :param ip: P2P连接IP地址
        :param port: P2P连接端口
        """
        self.user_id = user_id
        self.flag = flag
        self.online = online
        self.public_key = public_key
        self.ip = ip
        self.port = port

    def to_dict(self):
        """
        转为字典，便于网络传输和存储
        :return: dict
        """
        return {
            "user_id": self.user_id,
            "flag": self.flag,
            "online": self.online,
            "public_key": self.public_key,
            "ip": self.ip,
            "port": self.port
        }

    @classmethod
    def from_dict(cls, data):
        """
        从字典创建 Contact 对象
        :param data: dict
        :return: Contact
        """
        return cls(
            user_id=data.get('user_id'),
            flag=data.get('flag', False),
            online=data.get('online', False),
            public_key=data.get('public_key'),
            ip=data.get('ip'),
            port=data.get('port')
        )

    def __str__(self):
        return f"{self.user_id} - {'Friend' if self.flag else 'Not Friend'} - {'Online' if self.online else 'Offline'} - IP:{self.ip}:{self.port}"