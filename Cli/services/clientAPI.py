import socket
import threading
import json
import time
from queue import Queue, Empty
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as sym_padding
from tinydb import TinyDB, Query
import os
from io import BytesIO
from PIL import Image

from config import CLIENT_CONFIG
from models.messages import messages


class ClientAPI:
    """
    A P2P communication service with end-to-end transparent hybrid encryption
    and optional image-based steganography embedding/extraction.

    Each peer_id uses its own TinyDB JSON file to store chat history under
    a 'Messages' table with fields: timestamp, sender_id, receiver_id, message, image_path.

    Incoming messages for 'cipher' are decrypted dicts; for 'steg_image', an image object is delivered.
    Supports extracting stego payload by timestamp.
    """
    def __init__(self, host: str = '0.0.0.0', port: int = 0, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.peers = {}
        self.incoming = Queue()
        self._listener_socket = None
        self._running = False
        self._lock = threading.Lock()
        self._message_dbs = {}          # peer_id -> TinyDB table
        self._private_key = None
        self._public_key = None
        self._session_keys = {}         # peer_id -> AES key
        self._generate_asymmetric_keys()


    def _store_message(self, peer_id: str, sender_id: str, receiver_id: str, message: dict, image_path: str = None):
        messages.insert_message(message)

    # Public API to extract stego payload for a given peer and timestamp
    def _extract_from_image(self, image: Image.Image) -> bytes:
        """
        按像素顺序读取所有 LSB，拼成字节流返回
        """
        pixels = image.load()
        w, h = image.size
        bits = []
        for y in range(h):
            for x in range(w):
                r, g, b = pixels[x, y]
                bits.extend([str(r & 1), str(g & 1), str(b & 1)])
        data = bytearray()
        for i in range(0, len(bits) - 7, 8):
            byte = int(''.join(bits[i:i+8]), 2)
            data.append(byte)
        return bytes(data)

    def extract_stego_by_timestamp(self, peer_id: str, timestamp: str) -> bytes:
        """
        1) 从 TinyDB 拿到记录里的 image_path
        2) 打开图片、用 _extract_from_image 读出所有字节
        3) 前 4 字节解析出实际数据长度 N
        4) 取出第 5..(4+N) 字节块，解密并返回
        """
        result = messages.get_message_by_timestamp(timestamp)
        if not result or not result[0].get('image_path'):
            raise ValueError("No stego image found for given timestamp")
        path = result[0]['image_path']
        img = Image.open(path)
        raw = self._extract_from_image(img)
        length = int.from_bytes(raw[:4], 'big')
        encrypted = raw[4:4+length]
        key = self._session_keys.get(peer_id)
        if not key:
            raise ValueError("Session key not established")
        decrypted = self._decrypt(encrypted, key)
        try:
            return json.loads(decrypted.decode('utf-8'))
        except:
            return decrypted

    def _generate_asymmetric_keys(self):
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self._public_key = self._private_key.public_key()

    def get_public_key_bytes(self) -> bytes:
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def load_peer_public_key(self, peer_id: str, peer_pub_bytes: bytes) -> bytes:
        peer_pub = serialization.load_pem_public_key(peer_pub_bytes, backend=default_backend())
        aes_key = os.urandom(32)
        enc_key = peer_pub.encrypt(
            aes_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        self._session_keys[peer_id] = aes_key
        return enc_key

    def finalize_session_key(self, peer_id: str, encrypted_key: bytes):
        aes_key = self._private_key.decrypt(
            encrypted_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        self._session_keys[peer_id] = aes_key

    def _encrypt(self, data: bytes, key: bytes) -> bytes:
        iv = os.urandom(16)
        padder = sym_padding.PKCS7(128).padder()
        padded = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        ct = cipher.encryptor().update(padded) + cipher.encryptor().finalize()
        return iv + ct

    def _decrypt(self, data: bytes, key: bytes) -> bytes:
        iv, ct = data[:16], data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor().update(ct) + cipher.decryptor().finalize()
        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(dec) + unpadder.finalize()

    def embed_in_image(self, image_path: str, data: bytes, output_path: str):
        """
        1) 在 data 前加 4 字节的长度头（big-endian）
        2) 然后按位嵌入到载体图片的 RGB LSB
        """
        header = len(data).to_bytes(4, 'big')
        full = header + data
        img = Image.open(image_path)
        pixels = img.load()
        bits = ''.join(f"{byte:08b}" for byte in full)
        w, h = img.size
        idx = 0
        for y in range(h):
            for x in range(w):
                if idx >= len(bits):
                    break
                r, g, b = pixels[x, y]
                r = (r & 0xFE) | int(bits[idx]); idx += 1
                if idx < len(bits): g = (g & 0xFE) | int(bits[idx]); idx += 1
                if idx < len(bits): b = (b & 0xFE) | int(bits[idx]); idx += 1
                pixels[x, y] = (r, g, b)
            if idx >= len(bits):
                break
        img.save(output_path)

    def start(self):
        self._running = True
        self._listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener_socket.bind((self.host, self.port))
        self._listener_socket.listen()
        self.host, self.port = self._listener_socket.getsockname()
        threading.Thread(target=self._accept_loop, daemon=True).start()
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def stop(self):
        self._running = False
        if self._listener_socket: self._listener_socket.close()
        with self._lock:
            for sock in self.peers.values(): sock.close()
            self.peers.clear()

    def _accept_loop(self):
        while self._running:
            try:
                conn, addr = self._listener_socket.accept()
                peer_id = f"{addr[0]}:{addr[1]}"
                with self._lock: self.peers[peer_id] = conn
            except OSError:
                break

    def connect(self, peer_host: str, peer_port: int) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer_host, peer_port))
        peer_id = f"{peer_host}:{peer_port}"
        with self._lock: self.peers[peer_id] = sock
        return peer_id

    def send(self, peer_id: str, message: dict, use_steg: bool=False,
             carrier_image: str=None, output_image: str=None):
        key = self._session_keys.get(peer_id)
        if not key: raise ValueError("Session key not established")
        self_id = f"{self.host}:{self.port}"
        # Handle steganographic send
        if use_steg and carrier_image and output_image:
            plaintext_json = json.dumps(message).encode('utf-8')
            ciphertext = self._encrypt(plaintext_json, key)
            self.embed_in_image(carrier_image, ciphertext, output_image)
            ts = self._store_message(peer_id, sender_id=self_id,
                                     receiver_id=peer_id, message=message,
                                     image_path=output_image)
            data_hex = open(output_image, 'rb').read().hex()
            payload = {'type':'steg_image','data':data_hex,'timestamp':ts}
        else:
            ciphertext = self._encrypt(json.dumps(message).encode('utf-8'), key)
            ts = self._store_message(peer_id, sender_id=self_id,
                                     receiver_id=peer_id, message=message)
            payload = {'type':'cipher','data':ciphertext.hex(),'timestamp':ts}
        with self._lock: sock = self.peers.get(peer_id)
        sock.sendall(json.dumps(payload).encode('utf-8')+b"\n")

    def _receive_loop(self):
        while self._running:
            with self._lock: items = list(self.peers.items())
            for peer_id, sock in items:
                try:
                    raw = sock.recv(self.buffer_size)
                    if not raw:
                        with self._lock: self.peers.pop(peer_id,None)
                        continue
                    for line in raw.split(b"\n"):
                        if not line: continue
                        msg = json.loads(line.decode('utf-8'))
                        key = self._session_keys.get(peer_id)
                        if msg['type']=='cipher':
                            ct=bytes.fromhex(msg['data']); pt=self._decrypt(ct,key)
                            try: obj=json.loads(pt.decode())
                            except: obj=None
                            self._store_message(peer_id,peer_id,f"{self.host}:{self.port}",obj)
                            self.incoming.put((peer_id,obj))
                        elif msg['type']=='steg_image':
                            img_bytes=bytes.fromhex(msg['data'])
                            img=Image.open(BytesIO(img_bytes))
                            # Store stego image locally
                            ts = msg.get('timestamp', int(time.time()))
                            fname=f"steg_{peer_id.replace(':','_')}_{ts}.png"
                            img.save(fname)
                            # enqueue with timestamp
                            self.incoming.put((peer_id,{'type':'steg_image','image':img,'timestamp':ts}))
                except: continue
            threading.Event().wait(0.01)

    def get_message(self, timeout:float=None):
        try: return self.incoming.get(timeout=timeout)
        except Empty: return None

_client_api = None

def get_client_api():
    global _client_api
    if _client_api is None:
        # 初始化ClientAPI实例并启动
        _client_api = ClientAPI(host=CLIENT_CONFIG['host'],
                               port=CLIENT_CONFIG['port'])
        _client_api.start()
    return _client_api