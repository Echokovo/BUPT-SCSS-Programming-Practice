from flask import Flask, request, jsonify
import threading
import logging
import jwt
import time
from src.utils.logger import setup_logger
from config import WEB_SERVER_CONFIG, JWT_CONFIG

class WebServer:
    """
    本地 Web 服务，负责为前端页面或本地应用提供 RESTful API。
    路由与接口文档保持一致，所有请求体和响应体格式严格统一。
    支持token验证机制。
    """
    def __init__(self, client):
        self.logger = setup_logger(__name__)
        self.client = client  # SecureChatClient 实例，负责核心业务逻辑
        self.app = Flask(__name__)
        self.secret_key = JWT_CONFIG['secret_key']  # 从配置文件读取JWT密钥
        self._setup_routes()
        self.server_thread = None

    def _verify_token(self, token):
        """
        验证token是否有效
        :param token: JWT token字符串
        :return: (is_valid, user_id) 元组
        """
        try:
            # 移除Bearer前缀
            if token.startswith('Bearer '):
                token = token[7:]
            
            # 验证token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            exp = payload.get('exp', 0)
            
            # 检查是否过期
            if exp < time.time():
                return False, None
                
            return True, user_id
        except jwt.InvalidTokenError:
            return False, None

    def _get_token_from_request(self):
        """
        从请求头中获取token
        :return: token字符串或None
        """
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None

    def _require_auth(self, f):
        """
        装饰器：要求token认证
        """
        def decorated_function(*args, **kwargs):
            token = self._get_token_from_request()
            if not token:
                return self._response(401, "Missing Authorization header")
            
            is_valid, user_id = self._verify_token(token)
            if not is_valid:
                return self._response(401, "Invalid or expired token")
            
            # 验证token中的用户ID与客户端当前用户ID一致
            if user_id != self.client.user_id:
                return self._response(401, "Token user mismatch")
            
            return f(*args, **kwargs)
        return decorated_function

    def _response(self, status, message="", data=None):
        """
        统一响应格式，便于前端处理。
        :param status: 状态码
        :param message: 信息
        :param data: 数据 dict
        :return: Flask Response
        """
        return jsonify({
            "status": status,
            "message": message,
            "data": data if data is not None else {}
        })

    def _setup_routes(self):
        """
        设置所有 RESTful 路由，严格按照接口文档实现。
        """
        @self.app.route('/register', methods=['POST'])
        def register():
            """用户注册接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.register(
                data.get('user_id'),
                data.get('password'),
                data.get('email')
            )
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/login', methods=['POST'])
        def login():
            """用户登录接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.login(
                data.get('user_id'),
                data.get('password')
            )
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/contacts', methods=['GET'])
        @self._require_auth
        def get_contacts():
            """获取通讯录接口"""
            contacts = [c.to_dict() for c in self.client.contacts]
            return self._response(200, "Success", {"contacts": contacts})

        @self.app.route('/contacts', methods=['POST'])
        @self._require_auth
        def add_contact():
            """添加好友接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.add_contact(data.get('friend_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/contacts', methods=['DELETE'])
        @self._require_auth
        def delete_contact():
            """删除好友接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.delete_contact(data.get('friend_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/history', methods=['POST'])
        @self._require_auth
        def get_history():
            """获取聊天历史接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.get_history(data.get('friend_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/chat', methods=['POST'])
        @self._require_auth
        def send_message():
            """发送消息接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            
            # 从消息结构中提取信息
            friend_id = data.get('friend_id')
            message_content = data.get('message', {}).get('content')
            message_type = data.get('message', {}).get('type', 'text')
            use_steganography = data.get('use_steganography', False)
            steg_img_template = data.get('steg_img_template')
            
            if not friend_id or not message_content:
                return self._response(400, "缺少接收者或消息内容")
            
            # 调用客户端的发送消息方法（包含P2P逻辑）
            resp = self.client.send_message(friend_id, message_content, message_type, use_steganography, steg_img_template)
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/online', methods=['POST'])
        @self._require_auth
        def user_status():
            """检查用户在线状态接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.get_online_status(data.get('friend_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/public_key', methods=['POST'])
        @self._require_auth
        def user_public_key():
            """获取用户公钥接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.get_public_key(data.get('friend_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/user/exists', methods=['POST'])
        def user_exists():
            """验证用户存在接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.check_user_exists(data.get('user_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/user/info', methods=['GET'])
        @self._require_auth
        def get_user_info():
            """获取当前用户信息接口"""
            return self._response(200, "Success", {
                "user_id": self.client.user_id,
                "public_key": self.client.crypto.public_key_pem
            })

        @self.app.route('/search', methods=['POST'])
        @self._require_auth
        def search_user():
            """搜索用户接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.search_user(data.get('user_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/friend/apply', methods=['POST'])
        @self._require_auth
        def apply_friend():
            """申请好友接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.apply_friend(data.get('friend_id'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/friend/requests', methods=['GET'])
        @self._require_auth
        def get_friend_requests():
            """获取好友申请接口"""
            resp = self.client.get_friend_requests()
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/friend/handle', methods=['POST'])
        @self._require_auth
        def handle_friend_request():
            """处理好友申请接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            friend_id = data.get('friend_id')
            accept = data.get('accept', True)
            resp = self.client.handle_friend_request(friend_id, accept)
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/local/history', methods=['POST'])
        @self._require_auth
        def get_local_history():
            """获取本地聊天历史接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            friend_id = data.get('friend_id')
            limit = data.get('limit', 50)  # 默认返回50条
            messages = self.client.get_local_history(friend_id, limit)
            return self._response(200, "Success", {
                "length": len(messages),
                "messages": messages
            })

        @self.app.route('/messages', methods=['GET'])
        @self._require_auth
        def get_messages():
            """获取P2P接收到的消息接口"""
            # 返回消息队列中的消息并清空队列
            messages = [m.to_dict() for m in self.client.p2p_manager.message_queue]
            self.client.p2p_manager.message_queue = []
            return self._response(200, "Success", {"messages": messages})

        @self.app.route('/logout', methods=['POST'])
        @self._require_auth
        def logout():
            """用户登出接口"""
            # 停止心跳
            self.client.is_running = False
            self.client.user_id = None
            self.client.server_api.token = None  # 清除token
            return self._response(200, "Logout successful")

    def start(self):
        """
        启动 Web 服务器，采用多线程方式运行 Flask。
        """
        self.server_thread = threading.Thread(
            target=self.app.run,
            kwargs={
                'host': WEB_SERVER_CONFIG['host'],
                'port': WEB_SERVER_CONFIG['port'],
                'debug': False,
                'use_reloader': False
            }
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        self.logger.info(f"Web server started on {WEB_SERVER_CONFIG['host']}:{WEB_SERVER_CONFIG['port']}")

    def stop(self):
        """
        停止 Web 服务器
        """
        if self.server_thread and self.server_thread.is_alive():
            self.logger.info("Stopping web server...")
            # Flask 没有优雅的停止方法，这里只是标记线程停止
            self.server_thread.join(timeout=5)