import requests
from config import SERVER_CONFIG
from models.friends import friends


class ServerAPI:
    """
    负责与后端服务器进行 HTTP 通信，封装所有C/S接口。
    所有请求体均为 {"data": {...}}，所有响应体均为 {"status": int, "message": str, "data": {}}。
    支持token认证机制。
    """

    def __init__(self):
        # 构建基础 URL
        self.base_url = f"http://{SERVER_CONFIG['host']}{SERVER_CONFIG['api_base']}"
        self.timeout = SERVER_CONFIG['timeout']
        self.user_id = None
        self.token = None  # 存储登录后的token
        # SERVER_CONFIG的配置在config.py

    def _post(self, path, data, use_token=True):
        """
        发送 POST 请求，自动封装 data 字段，处理异常和日志。
        :param path: 接口路径
        :param data: 业务数据 dict
        :param use_token: 是否使用token认证
        :return: 统一格式响应 dict
        """
        url = f"{self.base_url}{path}"
        headers = {}
        if use_token and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        response = requests.post(url, json={"data": data}, headers=headers, timeout=self.timeout)
        print(response)
        return response.json()

    def _get(self, path, use_token=True):
        """
        发送 GET 请求，处理异常和日志。
        :param path: 接口路径
        :param use_token: 是否使用token认证
        :return: 统一格式响应 dict
        """
        url = f"{self.base_url}{path}"
        headers = {}
        if use_token and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        response = requests.get(url, headers=headers, timeout=self.timeout)
        return response.json()

    def _delete(self, path, data, use_token=True):
        """
        发送 DELETE 请求，自动封装 data 字段，处理异常和日志。
        :param path: 接口路径
        :param data: 业务数据 dict
        :param use_token: 是否使用token认证
        :return: 统一格式响应 dict
        """
        url = f"{self.base_url}{path}"
        headers = {}
        if use_token and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        response = requests.delete(url, json={"data": data}, headers=headers, timeout=self.timeout)
        return response.json()

    # ================== 业务接口 ==================

    def register(self, user_id, password, email):
        data = {
            "user_id": user_id,
            "password": password,
            "email": email
        }
        response = self._post("/register", data, use_token=False)
        return response

    def login(self, user_id, password, public_key, ip, port):
        data = {
            "user_id": user_id,
            "password": password,
            "public_key": public_key,
            "ip": ip,
            "port": port
        }
        response = self._post("/login", data, use_token=False)
        print(response)
        if response.get('status') == 200:
            self.user_id = data['user_id']
            self.token = response.get('data', {}).get('token')
        return response

    def get_contacts(self):
        response = self._get("/contacts")
        print(response)
        return response

    def add_friend(self, friend_id):
        data = {
            "friend_id": friend_id
        }
        response = self._post("/contacts", data)
        print(response)
        return response

    def delete_friend(self, friend_id):
        data = {
            "friend_id": friend_id
        }
        response = self._delete("/contacts", data)
        print(response)
        return response

    def get_online_status(self, friend_id):
        data = {
            "friend_id": friend_id
        }
        response = self._post("/online", data)
        print(response)
        return response

    def get_public_key(self, friend_id):
        data = {
            "friend_id": friend_id
        }
        response = self._post("/public_key", data)
        friends.create_friend(
            friend_id=response['data']['friend_id'],
            public_key=response['data']['public_key'],
            ip=response['data']['ip'],
            port=response['data']['port']
        )
        print(response)
        return response

    def heartbeat(self):
        response = self._get("/heartbeat")
        print(response)
        return response

serverAPI = ServerAPI()