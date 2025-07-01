import requests
import logging
from src.utils.logger import setup_logger
from config import SERVER_CONFIG

class ServerAPI:
    """
    负责与后端服务器进行 HTTP 通信，封装所有前后端接口。
    所有请求体均为 {"data": {...}}，所有响应体均为 {"status": int, "message": str, "data": {}}。
    """
    def __init__(self):
        self.logger = setup_logger(__name__)
        # 构建基础 URL
        self.base_url = f"http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}{SERVER_CONFIG['api_base']}"
        self.timeout = SERVER_CONFIG['timeout']
        #SERVER_CONFIG的配置在config.py

    def _post(self, path, data):
        """
        发送 POST 请求，自动封装 data 字段，处理异常和日志。
        :param path: 接口路径
        :param data: 业务数据 dict
        :return: 统一格式响应 dict
        """
        url = f"{self.base_url}{path}"
        try:
            response = requests.post(url, json={"data": data}, timeout=self.timeout)
            return self._format_response(response)
        except Exception as e:
            self.logger.error(f"POST {path} error: {e}")
            return {"status": 500, "message": str(e), "data": {}}

    def _get(self, path):
        """
        发送 GET 请求，处理异常和日志。
        :param path: 接口路径
        :return: 统一格式响应 dict
        """
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, timeout=self.timeout)
            return self._format_response(response)
        except Exception as e:
            self.logger.error(f"GET {path} error: {e}")
            return {"status": 500, "message": str(e), "data": {}}

    def _delete(self, path, data):
        """
        发送 DELETE 请求，自动封装 data 字段，处理异常和日志。
        :param path: 接口路径
        :param data: 业务数据 dict
        :return: 统一格式响应 dict
        """
        url = f"{self.base_url}{path}"
        try:
            response = requests.delete(url, json={"data": data}, timeout=self.timeout)
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

    def register(self, username, email, password):
        """
        用户注册
        :param username: 用户名
        :param email: 邮箱
        :param password: 密码
        :return: 统一格式响应 dict
        """
        data = {"username": username, "email": email, "password": password}
        return self._post("/register", data)

    def login(self, email, password, public_key):
        """
        用户登录
        :param email: 邮箱
        :param password: 密码
        :param public_key: 公钥
        :return: 统一格式响应 dict
        """
        data = {"email": email, "password": password, "public_key": public_key}
        return self._post("/login", data)

    def add_contact(self, email):
        """
        添加好友
        :param email: 好友邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/contacts", data)

    def delete_contact(self, email):
        """
        删除好友
        :param email: 好友邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._delete("/contacts", data)

    def get_contacts(self):
        """
        获取通讯录
        :return: 统一格式响应 dict
        """
        return self._get("/contacts")

    def get_history(self, email):
        """
        获取聊天历史
        :param email: 对方邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/history", data)

    def send_message(self, message_dict):
        """
        发送消息
        :param message_dict: 消息结构体 dict
        :return: 统一格式响应 dict
        """
        return self._post("/chat", message_dict)

    def get_online_status(self, email):
        """
        检查用户在线状态
        :param email: 目标邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/user/status", data)

    def get_public_key(self, email):
        """
        获取用户公钥
        :param email: 目标邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/user/public_key", data)

    def check_user_exists(self, email):
        """
        验证用户是否存在
        :param email: 目标邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/user/exists", data)

    def heartbeat(self, email):
        """
        发送心跳包，告诉服务器用户还在线
        :param email: 用户邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/heartbeat", data)

    def register_p2p(self, email, ip, port):
        """
        注册 P2P 节点
        :param email: 目标邮箱
        :param ip: 节点 IP
        :param port: 节点端口
        :return: 统一格式响应 dict
        """
        data = {"email": email, "ip": ip, "port": port}
        return self._post("/user/register_p2p", data)

    def get_peer(self, email):
        """
        获取 P2P 节点
        :param email: 目标邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/user/get_peer", data)

    def apply_friend(self, email):
        """
        申请好友
        :param email: 好友邮箱
        :return: 统一格式响应 dict
        """
        data = {"email": email}
        return self._post("/friend/apply", data)

    def get_friend_requests(self):
        """
        获取好友申请
        :return: 统一格式响应 dict
        """
        return self._get("/friend/requests")

    def handle_friend_request(self, email, accept=True):
        """
        处理好友申请
        :param email: 好友邮箱
        :param accept: 是否接受
        :return: 统一格式响应 dict
        """
        data = {"email": email, "accept": accept}
        return self._post("/friend/handle", data)