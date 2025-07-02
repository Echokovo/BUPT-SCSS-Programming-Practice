import os
import logging
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from src.utils.logger import setup_logger
from config import CRYPTO_CONFIG

# CryptoManager 负责生成/加载RSA密钥对，消息加密/解密，公钥序列化等。
class CryptoManager:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.private_key = None
        self.public_key = None
        self._setup_keys()

    def _setup_keys(self):
        """设置或加载密钥对"""
        key_dir = CRYPTO_CONFIG['key_dir']
        key_file = os.path.join(key_dir, CRYPTO_CONFIG['key_file'])

        # 创建目录如果不存在
        Path(key_dir).mkdir(parents=True, exist_ok=True)

        if os.path.exists(key_file):
            self._load_keys(key_file)
        else:
            self._generate_keys(key_file)

    def _generate_keys(self, key_file):
        """生成新的RSA密钥对并保存到文件"""
        self.logger.info("Generating new RSA key pair")
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=CRYPTO_CONFIG['key_size'],
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

        # 保存私钥
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open(key_file, 'wb') as f:
            f.write(pem)

        self.logger.info(f"Private key saved to {key_file}")

    def _load_keys(self, key_file):
        """从文件加载密钥"""
        self.logger.info(f"Loading private key from {key_file}")
        with open(key_file, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        self.public_key = self.private_key.public_key()

    def encrypt_message(self, message, public_key_pem):
        """
        使用对方公钥加密消息（RSA），适合加密短消息或对称密钥
        :param message: 明文字符串
        :param public_key_pem: 对方公钥PEM字符串
        :return: base64编码的密文字符串
        """
        from base64 import b64encode
        # 加载对方公钥
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        # 加密
        ciphertext = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return b64encode(ciphertext).decode('utf-8')

    def decrypt_message(self, encrypted_message):
        """
        使用本地私钥解密消息（RSA）
        :param encrypted_message: base64编码的密文字符串
        :return: 明文字符串
        """
        from base64 import b64decode
        ciphertext = b64decode(encrypted_message.encode('utf-8'))
        plaintext = self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode('utf-8')

    @property
    def public_key_pem(self):
        """获取PEM格式的公钥字符串，便于网络传输"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')