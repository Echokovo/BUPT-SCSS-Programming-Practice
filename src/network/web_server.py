from flask import Flask, request, jsonify
import threading
import logging
from src.utils.logger import setup_logger
from config import WEB_SERVER_CONFIG

class WebServer:
    """
    本地 Web 服务，负责为前端页面或本地应用提供 RESTful API。
    路由与接口文档保持一致，所有请求体和响应体格式严格统一。
    """
    def __init__(self, client):
        self.logger = setup_logger(__name__)
        self.client = client  # SecureChatClient 实例，负责核心业务逻辑
        self.app = Flask(__name__)
        self._setup_routes()
        self.server_thread = None

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
                data.get('username'),
                data.get('email'),
                data.get('password')
            )
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/login', methods=['POST'])
        def login():
            """用户登录接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.login(
                data.get('email'),
                data.get('password')
            )
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/contacts', methods=['GET'])
        def get_contacts():
            """获取通讯录接口"""
            if not self.client.user_email:
                return self._response(401, "Not logged in")
            contacts = [c.to_dict() for c in self.client.contacts]
            return self._response(200, "Success", {"contacts": contacts})

        @self.app.route('/contacts', methods=['POST'])
        def add_contact():
            """添加好友接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.add_contact(data.get('email'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/contacts', methods=['DELETE'])
        def delete_contact():
            """删除好友接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.delete_contact(data.get('email'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/history', methods=['POST'])
        def get_history():
            """获取聊天历史接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.get_history(data.get('email'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/chat', methods=['POST'])
        def send_message():
            """发送消息接口"""
            if not self.client.user_email:
                return self._response(401, "Not logged in")
            
            req = request.get_json(force=True)
            data = req.get('data', {})
            
            # 从消息结构中提取信息
            receiver = data.get('receiver')
            message_content = data.get('message', {}).get('content')
            message_type = data.get('message', {}).get('type', 'text')
            use_steganography = data.get('use_steganography', False)
            steg_img_template = data.get('steg_img_template')
            
            if not receiver or not message_content:
                return self._response(400, "缺少接收者或消息内容")
            
            # 调用客户端的发送消息方法（包含P2P逻辑）
            resp = self.client.send_message(receiver, message_content, message_type, use_steganography, steg_img_template)
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/user/status', methods=['POST'])
        def user_status():
            """检查用户在线状态接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.get_online_status(data.get('email'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/user/public_key', methods=['POST'])
        def user_public_key():
            """获取用户公钥接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.get_public_key(data.get('email'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/user/exists', methods=['POST'])
        def user_exists():
            """验证用户存在接口"""
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.server_api.check_user_exists(data.get('email'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/user/info', methods=['GET'])
        def get_user_info():
            """获取当前用户信息接口"""
            if not self.client.user_email:
                return self._response(401, "Not logged in")
            return self._response(200, "Success", {
                "email": self.client.user_email,
                "public_key": self.client.crypto.public_key_pem
            })

        @self.app.route('/search', methods=['POST'])
        def search_user():
            """搜索用户接口"""
            if not self.client.user_email:
                return self._response(401, "Not logged in")
            
            req = request.get_json(force=True)
            data = req.get('data', {})
            resp = self.client.search_user(data.get('email'))
            return self._response(resp.get('status'), resp.get('message'), resp.get('data'))

        @self.app.route('/messages', methods=['GET'])
        def get_messages():
            """获取P2P接收到的消息接口"""
            if not self.client.user_email:
                return self._response(401, "Not logged in")
            
            # 返回消息队列中的消息并清空队列
            messages = [m.to_dict() for m in self.client.p2p_manager.message_queue]
            self.client.p2p_manager.message_queue = []
            return self._response(200, "Success", {"messages": messages})

        @self.app.route('/logout', methods=['POST'])
        def logout():
            """用户登出接口"""
            if not self.client.user_email:
                return self._response(401, "Not logged in")
            
            # 停止心跳
            self.client.is_running = False
            self.client.user_email = None
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
        停止 Web 服务器（Flask 开发服务器无优雅关闭方式，实际部署建议用 gunicorn/uwsgi 等）。
        """
        self.logger.info("Web server stopped")