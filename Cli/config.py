import socket
def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80)) # 连接到Google DNS
            print(f"Local IP: {s.getsockname()[0]}")
            return s.getsockname()[0] # 获取本地IP
    except Exception:
        return socket.gethostbyname(socket.gethostname())

CLIENT_CONFIG = {
    "host": get_local_ip(),
    "port": 6000
}

SERVER_CONFIG = {
    "host": "localhost:5000",
    "api_base": "",
    "timeout": 10
}