import os
from pathlib import Path

# 配置管理：集中管理服务器地址、端口、密钥路径、日志格式等全局配置。

BASE_DIR = Path(__file__).parent.parent  # 项目根目录

# 服务器配置：用于与后端服务器通信的地址、端口、API路径、超时时间
SERVER_CONFIG = {
    'host': 'your_server_address.com',  # 服务器地址（需替换为实际地址）
    'port': 8000,                      # 服务器端口
    'api_base': '/api/v1',             # API 路径前缀
    'timeout': 10                      # 请求超时时间（秒）
}

# 本地Web服务器配置：本地 Flask Web 服务监听的地址和端口（供前端访问）
WEB_SERVER_CONFIG = {
    'host': 'localhost',  # 本地监听地址
    'port': 5000         # 本地监听端口
}

# 加密配置：密钥长度、密钥存储目录和文件名
CRYPTO_CONFIG = {
    'key_size': 2048,  # RSA 密钥长度（位）
    'key_dir': os.path.join(BASE_DIR, 'keys'),  # 密钥存储目录
    'key_file': 'private_key.pem'               # 私钥文件名
}

# 日志配置：日志等级、格式、日志文件路径
LOG_CONFIG = {
    'level': 'INFO',  # 日志等级（DEBUG/INFO/WARNING/ERROR）
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    'file': os.path.join(BASE_DIR, 'logs', 'client.log')  # 日志文件路径
}

# 数据存储配置：本地消息、联系人等数据的存储路径
DATA_CONFIG = {
    'message_dir': os.path.join(BASE_DIR, 'data', 'messages'),        # 消息存储目录
    'contacts_file': os.path.join(BASE_DIR, 'data', 'contacts.json')  # 联系人信息文件
}