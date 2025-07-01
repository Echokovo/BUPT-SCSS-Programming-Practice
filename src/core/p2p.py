import socket
import threading
import json
import logging
import base64
import tempfile
from src.models.message import Message
from src.utils.logger import setup_logger
from src.utils.steganography import embed_message, extract_message

# P2PManager 负责点对点消息的发送与接收、加密解密、对等方管理等。
class P2PManager:
    def __init__(self, crypto_manager):
        self.logger = setup_logger(__name__)
        self.crypto = crypto_manager
        self.peers = {}  # email: (ip, port)
        self.message_queue = []  # 收到的消息队列
        self.listening = False
        self.listener_thread = None

    def start_listener(self, port=0):
        """
        启动P2P监听线程，监听指定端口的TCP连接。
        :param port: 监听端口，0为自动分配
        :return: 实际绑定端口
        """
        if self.listening:
            return

        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind(('0.0.0.0', port))
        self.listener_socket.listen(5)

        # 获取实际绑定的端口
        _, actual_port = self.listener_socket.getsockname()

        self.listening = True
        self.listener_thread = threading.Thread(target=self._listen_for_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()

        self.logger.info(f"P2P listener started on port {actual_port}")
        return actual_port

    def _listen_for_messages(self):
        """
        循环监听传入的TCP连接，每个连接新开线程处理。
        """
        while self.listening:
            try:
                conn, addr = self.listener_socket.accept()
                threading.Thread(target=self._handle_connection, args=(conn, addr)).start()
            except Exception as e:
                self.logger.error(f"Error accepting connection: {e}")

    def _handle_connection(self, conn, addr):   
        try:
            data = conn.recv(4096)
            if data:
                message_dict = json.loads(data.decode('utf-8'))
                message = Message.from_dict(message_dict)
                # 隐写消息自动提取
                if message.type == "steg_picture":
                    img_data = base64.b64decode(message.content)
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        steg_img_path = tmp.name
                        tmp.write(img_data)
                    # 你需要约定最大提取长度或在消息结构中传递
                    extracted = extract_message(steg_img_path, length=128)  # 128为最大字符数示例
                    message.content = extracted
                else:
                    # 普通消息解密
                    encrypted_content = message.message['content']
                    try:
                        decrypted_content = self.crypto.decrypt_message(encrypted_content)
                        message.message['content'] = decrypted_content
                    except Exception as e:
                        self.logger.error(f"Decrypt message error: {e}")
                        message.message['content'] = "[解密失败]"
                self.message_queue.append(message)
                self.logger.info(f"Received message from {message.sender}")
        except Exception as e:
            self.logger.error(f"Error handling connection: {e}")
        finally:
            conn.close()

    def send_message(self, receiver_email, message_dict, receiver_public_key, use_steganography=False):
        """
        发送消息给指定对等方，先加密 message['content'] 字段。
        :param receiver_email: 对方邮箱
        :param message_dict: 消息字典（需符合 Message.to_dict 格式）
        :param receiver_public_key: 对方公钥
        :param use_steganography: 是否使用隐写术
        :return: 统一响应结构
        """
        if receiver_email not in self.peers:
            return {"status": 404, "message": "Peer not found"}

        ip, port = self.peers[receiver_email]

        try:
            original_content = message_dict['message']['content']
            encrypted_content = self.crypto.encrypt_message(
                original_content,
                receiver_public_key
            )
            if use_steganography:
                # 隐写消息，需有一张模板图片路径 message_dict['steg_img_template']
                steg_img_template = message_dict.get('steg_img_template')
                if not steg_img_template:
                    return {"status": 400, "message": "缺少隐写模板图片路径"}
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_out:
                    embed_message(steg_img_template, encrypted_content, tmp_out.name)
                    with open(tmp_out.name, 'rb') as f:
                        img_bytes = f.read()
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                # 组装隐写消息结构
                steg_message = {
                    'type': 'steg_picture',
                    'sender': message_dict.get('sender'),
                    'receiver': message_dict.get('receiver'),
                    'content': b64_img,
                    'timestamp': message_dict.get('timestamp'),
                }
                send_data = steg_message
            else:
                message_dict['message']['content'] = encrypted_content
                send_data = message_dict
        except Exception as e:
            self.logger.error(f"Encrypt/embed message error: {e}")
            return {"status": 500, "message": "消息加密或隐写失败"}

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip, port))
                s.sendall(json.dumps(send_data).encode('utf-8'))
            self.logger.info(f"Message sent to {receiver_email}")
            return {"status": 200, "message": "Message sent successfully"}
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return {"status": 500, "message": str(e)}

    def add_peer(self, email, ip, port):
        """
        添加对等方信息（手动维护，适合本地测试）
        :param email: 对方邮箱
        :param ip: 对方IP
        :param port: 对方端口
        """
        self.peers[email] = (ip, port)
        self.logger.info(f"Added peer {email} at {ip}:{port}")

    def stop(self):
        """
        停止监听线程，关闭 socket
        """
        self.listening = False
        if hasattr(self, 'listener_socket'):
            self.listener_socket.close()
        if self.listener_thread:
            self.listener_thread.join()
        self.logger.info("P2P listener stopped")