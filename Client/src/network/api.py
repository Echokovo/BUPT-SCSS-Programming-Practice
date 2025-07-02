import requests
import logging
from src.utils.logger import setup_logger
from config import SERVER_CONFIG

class ServerAPI:
    """
    负责与后端服务器进行 HTTP 通信，封装所有C/S接口。
    所有请求体均为 {"data": {...}}，所有响应体均为 {"status": int, "message": str, "data": {}}。
    支持token认证机制。
    """
    def __init__(self):
        self.logger = setup_logger(__name__)
        # 构建基础 URL
        self.base_url = f"http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}{SERVER_CONFIG['api_base']}"
        self.timeout = SERVER_CONFIG['timeout']
        self.token = None  # 存储登录后的token
        #SERVER_CONFIG的配置在config.py

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
        
        try:
            response = requests.post(url, json={"data": data}, headers=headers, timeout=self.timeout)
            
            # 检查token是否过期
            if response.status_code == 401:
                self.logger.warning("Token已过期，清除token")
                self.token = None
                return {"status": 401, "message": "Token已过期，请重新登录", "data": {}}
            
            return self._format_response(response)
        except Exception as e:
            self.logger.error(f"POST {path} error: {e}")
            return {"status": 500, "message": str(e), "data": {}}

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
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            # 检查token是否过期
            if response.status_code == 401:
                self.logger.warning("Token已过期，清除token")
                self.token = None
                return {"status": 401, "message": "Token已过期，请重新登录", "data": {}}
            
            return self._format_response(response)
        except Exception as e:
            self.logger.error(f"GET {path} error: {e}")
            return {"status": 500, "message": str(e), "data": {}}

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
        
        try:
            response = requests.delete(url, json={"data": data}, headers=headers, timeout=self.timeout)
            
            # 检查token是否过期
            if response.status_code == 401:
                self.logger.warning("Token已过期，清除token")
                self.token = None
                return {"status": 401, "message": "Token已过期，请重新登录", "data": {}}
            
            return self._format_response(response)
        except Exception as e:
            self.logger.error(f"DELETE {path} error: {e}")
            return {"status": 500, "message": str(e), "data": {}}

    def _format_response(self, response):
        """
        统一格式化响应，保证所有接口返回结构一致。
        :param response: requests.Response 对象
        :return: dict
        """
        try:
            res = response.json()
            return {
                "status": res.get("status", response.status_code),
                "message": res.get("message", ""),
                "data": res.get("data", {})
            }
        except Exception as e:
            return {"status": 500, "message": f"Invalid response: {e}", "data": {}}

    # ================== 业务接口 ==================

    def register(self, user_id, password, email):
        """
        用户注册
        :param user_id: 用户名
        :param password: 密码
        :param email: 邮箱
        :return: 统一格式响应 dict
        """
        data = {"user_id": user_id, "password": password, "email": email}
        return self._post("/register", data, use_token=False)

    def login(self, user_id, password, public_key, ip, port):
        """
        用户登录
        :param user_id: 用户名
        :param password: 密码
        :param public_key: 公钥
        :param ip: 用户ip
        :param port: 用户监听端口
        :return: 统一格式响应 dict
        """
        data = {
            "user_id": user_id,
            "password": password,
            "public_key": public_key,
            "ip": ip,
            "port": port
        }
        response = self._post("/login", data, use_token=False)
        if response.get('status') == 200:
            self.token = response.get('data', {}).get('token')
        return response

    def add_contact(self, friend_id):
        """
        添加好友
        :param friend_id: 好友用户名
        :return: 统一格式响应 dict
        """
        data = {"friend_id": friend_id}
        return self._post("/contacts", data)

    def delete_contact(self, friend_id):
        """
        删除好友
        :param friend_id: 好友用户名
        :return: 统一格式响应 dict
        """
        data = {"friend_id": friend_id}
        return self._delete("/contacts", data)

    def get_contacts(self):
        """
        获取通讯录
        :return: 统一格式响应 dict
        """
        return self._get("/contacts")

    def get_history(self, friend_id):
        """
        获取聊天历史
        :param friend_id: 对方用户名
        :return: 统一格式响应 dict
        """
        data = {"friend_id": friend_id}
        return self._post("/history", data)

    def send_message(self, message_dict):
        """
        发送消息
        :param message_dict: 消息结构体 dict
        :return: 统一格式响应 dict
        """
        return self._post("/chat", message_dict)

    def get_online_status(self, friend_id):
        """
        检查用户在线状态
        :param friend_id: 目标用户名
        :return: 统一格式响应 dict
        """
        data = {"friend_id": friend_id}
        return self._post("/online", data)

    def get_public_key(self, friend_id):
        """
        获取用户公钥
        :param friend_id: 目标用户名
        :return: 统一格式响应 dict
        """
        data = {"friend_id": friend_id}
        return self._post("/public_key", data)

    def check_user_exists(self, user_id):
        """
        验证用户是否存在
        :param user_id: 目标用户名
        :return: 统一格式响应 dict
        """
        data = {"user_id": user_id}
        return self._post("/user/exists", data)

    def heartbeat(self, user_id):
        """
        发送心跳包，告诉服务器用户还在线
        :param user_id: 用户名
        :return: 统一格式响应 dict
        """
        data = {"user_id": user_id}
        return self._post("/heartbeat", data)

    def register_p2p(self, user_id, ip, port):
        """
        注册 P2P 节点
        :param user_id: 用户名
        :param ip: 节点 IP
        :param port: 节点端口
        :return: 统一格式响应 dict
        """
        data = {"user_id": user_id, "ip": ip, "port": port}
        return self._post("/user/register_p2p", data)

    def get_peer(self, user_id):
        """
        获取 P2P 节点
        :param user_id: 目标用户名
        :return: 统一格式响应 dict
        """
        data = {"user_id": user_id}
        return self._post("/user/get_peer", data)

    def apply_friend(self, friend_id):
        """
        申请好友
        :param friend_id: 好友用户名
        :return: 统一格式响应 dict
        """
        data = {"friend_id": friend_id}
        return self._post("/friend/apply", data)

    def get_friend_requests(self):
        """
        获取好友申请列表
        :return: 统一格式响应 dict
        """
        return self._get("/friend/requests")

    def handle_friend_request(self, friend_id, accept=True):
        """
        处理好友申请
        :param friend_id: 好友用户名
        :param accept: 是否接受
        :return: 统一格式响应 dict
        """
        data = {"friend_id": friend_id, "accept": accept}
        return self._post("/friend/handle", data)