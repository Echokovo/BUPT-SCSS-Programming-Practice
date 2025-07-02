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
from src.utils.steganography import embed_message, extract_message
from src.utils.database import DatabaseManager
import time
import os
import requests
from config import DATA_CONFIG

class SecureChatClient:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.crypto = CryptoManager()#创建一个CryptoManager对象，用于加密和解密消息
        self.server_api = ServerAPI()#创建一个ServerAPI对象，用于与服务器进行交互
        self.p2p_manager = P2PManager(self.crypto)#创建一个P2PManager对象，用于管理P2P连接
        self.web_server = WebServer(self)#创建一个WebServer对象，用于与前端进行交互
        self.db = DatabaseManager()#创建TinyDB数据库管理器

        self.user_id = None#用户ID
        self.contacts = []#通讯录
        self.is_running = False#是否运行
        self.heartbeat_thread = None#心跳线程

    def start(self):
        """启动客户端"""
        self.is_running = True  # 设置为True，表示客户端正在运行
        # 启动本地Web服务器(与前端交互)
        web_thread = Thread(target=self.web_server.start)#创建一个线程，用于启动本地Web服务器
        web_thread.daemon = True#设置为True，表示线程是守护线程
        web_thread.start()#启动线程
        self.logger.info("Secure Chat Client started")#记录日志，表示客户端已启动

    def register(self, user_id, password, email):
        """
        注册新用户
        :return: 统一响应结构
        """
        response = self.server_api.register(user_id, password, email)
        # 注册成功后不自动登录，需要用户手动登录
        return response

    def login(self, user_id, password):
        """
        用户登录
        :return: 统一响应结构
        """
        public_key = self.crypto.public_key  # 获取本机公钥
        ip = self.get_public_ip()            # 获取公网IP
        port = self.p2p_manager.start_listener()  # 获取P2P监听端口
        response = self.server_api.login(user_id, password, public_key, ip, port)
        if response.get('status') == 200:
            self.user_id = user_id
            if not self._load_contacts_from_db():
                self._load_contacts()
            self.start_heartbeat()
        return response

    def _load_contacts(self):   #加载通讯录
        """
        从服务器加载通讯录并保存到TinyDB
        """
        response = self.server_api.get_contacts()#调用ServerAPI的get_contacts方法，获取通讯录
        if response.get('status') == 200:
            contacts_data = response.get('data', {}).get('contacts', [])
            # 保存到TinyDB
            for contact_data in contacts_data:
                self.db.add_friend(contact_data)
            # 更新内存中的contacts列表
            self._load_contacts_from_db()
            self.logger.info(f"Loaded {len(contacts_data)} contacts from server")

    def _load_contacts_from_db(self):
        """
        从TinyDB加载联系人信息到内存
        """
        try:
            friends_data = self.db.get_all_friends()
            self.contacts = [Contact.from_dict(friend) for friend in friends_data]
            self.logger.info(f"Loaded {len(self.contacts)} contacts from database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load contacts from database: {e}")
        return False

    def search_user(self, user_id):#检查某用户是否存在
        """
        检查某用户是否存在
        :param user_id: 目标用户名
        :return: 统一响应结构
        """
        return self.server_api.check_user_exists(user_id)#调用ServerAPI的check_user_exists方法，检查某用户是否存在

    def add_contact(self, friend_id):#添加好友
        """
        添加好友
        :param friend_id: 好友用户名
        :return: 统一响应结构
        """
        return self.server_api.add_contact(friend_id)#调用ServerAPI的add_contact方法，添加好友

    def apply_friend(self, friend_id):#申请好友
        """
        申请好友
        :param friend_id: 好友用户名
        :return: 统一响应结构
        """
        return self.server_api.apply_friend(friend_id)#调用ServerAPI的apply_friend方法，申请好友

    def get_friend_requests(self):#获取好友申请
        """
        获取好友申请
        :return: 统一响应结构
        """
        return self.server_api.get_friend_requests()#调用ServerAPI的get_friend_requests方法，获取好友申请

    def handle_friend_request(self, friend_id, accept=True):#处理好友申请
        """
        处理好友申请
        :param friend_id: 好友用户名
        :param accept: 是否接受
        :return: 统一响应结构
        """
        return self.server_api.handle_friend_request(friend_id, accept)#调用ServerAPI的handle_friend_request方法，处理好友申请

    def delete_contact(self, friend_id):#删除好友
        """
        删除好友
        :param friend_id: 好友用户名
        :return: 统一响应结构
        """
        return self.server_api.delete_contact(friend_id)#调用ServerAPI的delete_contact方法，删除好友

    def get_contacts(self):#获取通讯录
        """
        获取通讯录
        :return: 统一响应结构
        """
        return self.server_api.get_contacts()#调用ServerAPI的get_contacts方法，获取通讯录

    def get_history(self, friend_id):#获取与某用户的聊天历史，并存储到TinyDB
        """
        获取与某用户的聊天历史，并存储到TinyDB
        :param friend_id: 对方用户名
        :return: 统一响应结构
        """
        resp = self.server_api.get_history(friend_id)#调用ServerAPI的get_history方法，获取与某用户的聊天历史
        # 存储到TinyDB
        if resp.get('status') == 200:
            messages_data = resp.get('data', {}).get('messages', [])
            for message_data in messages_data:
                # 确保消息格式正确
                if 'sender_id' not in message_data and 'sender' in message_data:
                    message_data['sender_id'] = message_data.pop('sender')
                if 'receiver_id' not in message_data and 'receiver' in message_data:
                    message_data['receiver_id'] = message_data.pop('receiver')
                # 存储到TinyDB
                self.db.add_message(message_data)
            self.logger.info(f"Stored {len(messages_data)} messages for {friend_id}")
        return resp

    def get_contact_status(self, friend_id):#获取联系人在线状态
        """
        获取联系人在线状态
        """
        return self.server_api.get_online_status(friend_id)#调用ServerAPI的get_online_status方法，获取联系人在线状态

    def get_contact_public_key(self, friend_id):#获取联系人公钥
        """
        获取联系人公钥
        """
        return self.server_api.get_public_key(friend_id)#调用ServerAPI的get_public_key方法，获取联系人公钥

    def get_local_history(self, friend_id, limit=None):
        """
        从TinyDB获取本地聊天历史
        :param friend_id: 对方用户名
        :param limit: 限制返回数量（可选）
        :return: 消息列表
        """
        return self.db.get_chat_history(self.user_id, friend_id, limit)

    def update_contact_info(self, friend_id, public_key=None, ip=None, port=None):
        """
        更新联系人的P2P信息和公钥
        :param friend_id: 好友用户名
        :param public_key: 公钥
        :param ip: P2P IP地址
        :param port: P2P端口
        """
        update_data = {}
        if public_key:
            update_data['public_key'] = public_key
        if ip:
            update_data['ip'] = ip
        if port:
            update_data['port'] = port
        
        if update_data:
            # 更新TinyDB
            self.db.update_friend(friend_id, update_data)
            # 更新内存中的contacts列表
            self._load_contacts_from_db()
            self.logger.info(f"Updated contact info for {friend_id}")
        else:
            self.logger.warning(f"No data to update for {friend_id}")

    def get_public_ip(self):#获取本机公网IP（通过第三方服务）
        """
        获取本机公网IP（通过第三方服务）
        """
        try:
            ip = requests.get('https://api.ipify.org').text#通过第三方服务获取本机公网IP
            return ip
        except Exception as e:
            self.logger.error(f"获取公网IP失败: {e}")
            return None

    def register_p2p_info(self):#登录后自动注册自己的公网IP和P2P监听端口到服务器
        """
        登录后自动注册自己的公网IP和P2P监听端口到服务器
        """
        ip = self.get_public_ip()#获取本机公网IP
        port = self.p2p_manager.start_listener()  # 启动监听并获取端口
        if ip and port:
            resp = self.server_api.register_p2p(self.user_id, ip, port)#调用ServerAPI的register_p2p方法，注册P2P信息到服务器
            self.logger.info(f"注册P2P信息到服务器: {resp}")
        else:
            self.logger.warning("未能注册P2P信息（IP或端口获取失败）")

    def start_heartbeat(self):#启动心跳线程，定期向服务器发送心跳包
        """
        启动心跳线程，定期向服务器发送心跳包
        """
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():#如果心跳线程已经在运行，直接返回
            return  # 如果心跳线程已经在运行，直接返回
        
        def heartbeat_loop():#心跳线程循环
            consecutive_failures = 0  # 连续失败计数
            max_failures = 5  # 最大连续失败次数
            
            while self.is_running and self.user_id:
                try:
                    resp = self.server_api.heartbeat(self.user_id)#调用ServerAPI的heartbeat方法，发送心跳包
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
        
        self.heartbeat_thread = Thread(target=heartbeat_loop)#创建一个线程，用于启动心跳线程
        self.heartbeat_thread.daemon = True#设置为True，表示线程是守护线程
        self.heartbeat_thread.start()#启动线程
        self.logger.info("心跳线程已启动")

    def send_message(self, receiver_id, message_content, message_type="text", use_steganography=False, steg_img_template=None):
        """
        发送消息，自动获取好友P2P信息，优先尝试P2P，失败则回退到 /chat API
        :param receiver_id: 对方用户名
        :param message_content: 消息内容
        :param message_type: 消息类型
        :param use_steganography: 是否使用隐写术
        :param steg_img_template: 隐写模板图片路径
        :return: 统一响应结构
        """
        # 获取接收者在线状态
        status_resp = self.get_contact_status(receiver_id)
        if status_resp.get('status') != 200:
            return {"status": 404, "message": "Contact not found or offline", "data": {}}

        # 获取接收者公钥
        # 首先从本地contacts中查找
        contact = next((c for c in self.contacts if c.user_id == receiver_id), None)
        if contact and contact.public_key:
            receiver_public_key = contact.public_key
        else:
            # 从服务器获取公钥
            key_resp = self.get_contact_public_key(receiver_id)
        if key_resp.get('status') != 200:
            return key_resp
            receiver_public_key = key_resp.get('data', {}).get('public_key')
            if not receiver_public_key:
                return {"status": 404, "message": "Receiver public key not found", "data": {}}
            # 更新TinyDB中的contact信息
            if contact:
                self.db.update_friend_public_key(receiver_id, receiver_public_key)
            else:
                # 如果contact不存在，创建一个新的
                new_contact_data = {
                    'user_id': receiver_id,
                    'flag': False,  # 默认不是好友
                    'online': False,  # 默认离线
                    'public_key': receiver_public_key,
                    'ip': None,
                    'port': None
                }
                self.db.add_friend(new_contact_data)
            # 更新内存中的contacts列表
            self._load_contacts_from_db()

        # 自动获取好友P2P信息并add_peer
        # 首先从本地contacts中查找
        contact = next((c for c in self.contacts if c.user_id == receiver_id), None)
        if contact and contact.ip and contact.port:
            # 使用本地存储的P2P信息
            self.p2p_manager.add_peer(receiver_id, contact.ip, contact.port)
        else:
            # 从服务器获取P2P信息
            peer_info = self.server_api.get_peer(receiver_id)
            if peer_info.get('status') == 200:
                ip = peer_info['data']['ip']
                port = peer_info['data']['port']
                self.p2p_manager.add_peer(receiver_id, ip, port)
                # 更新TinyDB中的contact信息
                if contact:
                    self.db.update_friend_p2p_info(receiver_id, ip, port)
                else:
                    # 如果contact不存在，创建一个新的
                    new_contact_data = {
                        'user_id': receiver_id,
                        'flag': False,  # 默认不是好友
                        'online': False,  # 默认离线
                        'public_key': None,
                        'ip': ip,
                        'port': port
                    }
                    self.db.add_friend(new_contact_data)
                # 更新内存中的contacts列表
                self._load_contacts_from_db()

        # 构建消息对象
        message = Message(
            sender_id=self.user_id,
            receiver_id=receiver_id,
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
            receiver_id,
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
        self.is_running = False#设置为False，表示客户端已停止
        
        # 等待心跳线程结束
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.logger.info("等待心跳线程结束...") #记录日志，表示正在等待心跳线程结束
            self.heartbeat_thread.join(timeout=5)  # 最多等待5秒
            if self.heartbeat_thread.is_alive():
                self.logger.warning("心跳线程未能在5秒内结束") #记录日志，表示心跳线程未能在5秒内结束
        
        self.web_server.stop()#停止Web服务器
        self.db.close()  # 关闭数据库连接
        self.logger.info("Secure Chat Client stopped")#记录日志，表示客户端已停止