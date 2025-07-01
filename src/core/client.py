import json
import logging
from threading import Thread
from src.network.api import ServerAPI
from src.network.web_server import WebServer
from src.core.p2p import P2PManager
from src.core.crypto import CryptoManager
from src.models.message import Message
from src.models.contact import Contact
from src.utils.logger import setup_logger
import time
import os
import requests
from config import DATA_CONFIG

class SecureChatClient:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.crypto = CryptoManager()
        self.server_api = ServerAPI()
        self.p2p_manager = P2PManager(self.crypto)
        self.web_server = WebServer(self)

        self.user_email = None
        self.contacts = []
        self.is_running = False
        self.heartbeat_thread = None

    def start(self):
        """启动客户端"""
        self.is_running = True
        # 启动本地Web服务器(与前端交互)
        web_thread = Thread(target=self.web_server.start)
        web_thread.daemon = True
        web_thread.start()
        self.logger.info("Secure Chat Client started")

    def register(self, username, email, password):
        """
        注册新用户
        :return: 统一响应结构
        """
        response = self.server_api.register(username, email, password)
        if response.get('status') == 200:
            self.user_email = email
        return response

    def login(self, email, password):
        """
        用户登录
        :return: 统一响应结构
        """
        response = self.server_api.login(email, password, self.crypto.public_key)
        if response.get('status') == 200:
            self.user_email = email
            self._load_contacts()
            self.register_p2p_info()  # 登录后自动注册P2P信息
            self.start_heartbeat()    # 登录后启动心跳
        return response

    def _load_contacts(self):
        """
        加载通讯录，数据通过 data 字段获取
        """
        response = self.server_api.get_contacts()
        if response.get('status') == 200:
            self.contacts = [Contact(**c) for c in response.get('data', {}).get('contacts', [])]

    def search_user(self, email):
        """
        检查某邮箱用户是否存在
        :param email: 目标邮箱
        :return: 统一响应结构
        """
        return self.server_api.check_user_exists(email)

    def add_contact(self, email):
        """
        添加好友
        :param email: 好友邮箱
        :return: 统一响应结构
        """
        return self.server_api.add_contact(email)

    def apply_friend(self, email):
        """
        申请好友
        :param email: 好友邮箱
        :return: 统一响应结构
        """
        return self.server_api.apply_friend(email)

    def get_friend_requests(self):
        """
        获取好友申请
        :return: 统一响应结构
        """
        return self.server_api.get_friend_requests()

    def handle_friend_request(self, email, accept=True):
        """
        处理好友申请
        :param email: 好友邮箱
        :param accept: 是否接受
        :return: 统一响应结构
        """
        return self.server_api.handle_friend_request(email, accept)

    def delete_contact(self, email):
        """
        删除好友
        :param email: 好友邮箱
        :return: 统一响应结构
        """
        return self.server_api.delete_contact(email)

    def get_contacts(self):
        """
        获取通讯录
        :return: 统一响应结构
        """
        return self.server_api.get_contacts()

    def get_history(self, email):
        """
        获取与某用户的聊天历史，并存储为本地 json 文件
        :param email: 对方邮箱
        :return: 统一响应结构
        """
        resp = self.server_api.get_history(email)
        # 存储到本地 json
        if resp.get('status') == 200:
            msg_dir = DATA_CONFIG['message_dir']
            os.makedirs(msg_dir, exist_ok=True)
            file_path = os.path.join(msg_dir, f"{email}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(resp['data'], f, ensure_ascii=False, indent=2)
        return resp

    def get_contact_status(self, email):
        """
        获取联系人在线状态
        """
        return self.server_api.get_online_status(email)

    def get_contact_public_key(self, email):
        """
        获取联系人公钥
        """
        return self.server_api.get_public_key(email)

    def get_public_ip(self):
        """
        获取本机公网IP（通过第三方服务）
        """
        try:
            ip = requests.get('https://api.ipify.org').text
            return ip
        except Exception as e:
            self.logger.error(f"获取公网IP失败: {e}")
            return None

    def register_p2p_info(self):
        """
        登录后自动注册自己的公网IP和P2P监听端口到服务器
        """
        ip = self.get_public_ip()
        port = self.p2p_manager.start_listener()  # 启动监听并获取端口
        if ip and port:
            resp = self.server_api.register_p2p(self.user_email, ip, port)
            self.logger.info(f"注册P2P信息到服务器: {resp}")
        else:
            self.logger.warning("未能注册P2P信息（IP或端口获取失败）")

    def start_heartbeat(self):
        """
        启动心跳线程，定期向服务器发送心跳包
        """
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            return  # 如果心跳线程已经在运行，直接返回
        
        def heartbeat_loop():
            consecutive_failures = 0  # 连续失败计数
            max_failures = 5  # 最大连续失败次数
            
            while self.is_running and self.user_email:
                try:
                    resp = self.server_api.heartbeat(self.user_email)
                    if resp.get('status') == 200:
                        self.logger.debug("心跳发送成功")
                        consecutive_failures = 0  # 重置失败计数
                    else:
                        consecutive_failures += 1
                        self.logger.warning(f"心跳发送失败: {resp}, 连续失败次数: {consecutive_failures}")
                        
                        # 连续失败超过阈值，停止心跳
                        if consecutive_failures >= max_failures:
                            self.logger.error(f"心跳连续失败{max_failures}次，停止心跳")
                            break
                            
                    time.sleep(30)  # 每30秒发送一次心跳
                except Exception as e:
                    consecutive_failures += 1
                    self.logger.error(f"心跳发送异常: {e}, 连续失败次数: {consecutive_failures}")
                    
                    # 连续失败超过阈值，停止心跳
                    if consecutive_failures >= max_failures:
                        self.logger.error(f"心跳连续失败{max_failures}次，停止心跳")
                        break
                        
                    time.sleep(30)  # 异常时也等待30秒再重试
            
            self.logger.info("心跳线程已停止")
        
        self.heartbeat_thread = Thread(target=heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        self.logger.info("心跳线程已启动")

    def send_message(self, receiver_email, message_content, message_type="text", use_steganography=False, steg_img_template=None):
        """
        发送消息，自动获取好友P2P信息，优先尝试P2P，失败则回退到 /chat API
        :param receiver_email: 对方邮箱
        :param message_content: 消息内容
        :param message_type: 消息类型
        :param use_steganography: 是否使用隐写术
        :param steg_img_template: 隐写模板图片路径
        :return: 统一响应结构
        """
        # 获取接收者在线状态
        status_resp = self.get_contact_status(receiver_email)
        if status_resp.get('status') != 200:
            return {"status": 404, "message": "Contact not found or offline", "data": {}}

        # 获取接收者公钥
        key_resp = self.get_contact_public_key(receiver_email)
        if key_resp.get('status') != 200:
            return key_resp
        receiver_public_key = key_resp.get('data', {}).get('public_key')
        if not receiver_public_key:
            return {"status": 404, "message": "Receiver public key not found", "data": {}}

        # 自动获取好友P2P信息并add_peer
        peer_info = self.server_api.get_peer(receiver_email)
        if peer_info.get('status') == 200:
            ip = peer_info['data']['ip']
            port = peer_info['data']['port']
            self.p2p_manager.add_peer(receiver_email, ip, port)

        # 构建消息对象
        message = Message(
            sender=self.user_email,
            receiver=receiver_email,
            content=message_content,
            type=message_type,
            timestamp=int(time.time())
        )
        message_dict = message.to_dict()
        # 隐写时传递模板图片路径
        if use_steganography and steg_img_template:
            message_dict['steg_img_template'] = steg_img_template

        # 优先尝试 P2P 发送
        p2p_result = self.p2p_manager.send_message(
            receiver_email,
            message_dict,
            receiver_public_key,
            use_steganography=use_steganography
        )
        if p2p_result.get('status') == 200:
            return {"status": 200, "message": "P2P消息发送成功", "data": {}}
        else:
            # P2P 失败，回退到 /chat API
            api_result = self.server_api.send_message(message_dict)
            if api_result.get('status') == 200:
                return {"status": 200, "message": "通过服务器转发消息成功", "data": {}}
            else:
                return {"status": 500, "message": "消息发送失败", "data": {}}

    def stop(self):
        """
        停止客户端
        """
        self.is_running = False
        
        # 等待心跳线程结束
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.logger.info("等待心跳线程结束...")
            self.heartbeat_thread.join(timeout=5)  # 最多等待5秒
            if self.heartbeat_thread.is_alive():
                self.logger.warning("心跳线程未能在5秒内结束")
        
        self.web_server.stop()
        self.logger.info("Secure Chat Client stopped")