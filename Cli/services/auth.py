from config import SERVER_CONFIG
from schemas.auth import BaseResponse
from services.serverAPI import serverAPI
from services.clientAPI import ClientAPI
_client_api = None
def register_service(user_id, password, email):
    response = serverAPI.register(user_id, password, email)
    return BaseResponse(**response).model_dump(), response['status']

def login_service(user_id, password):
    """需要实现"""
    global _client_api
    if _client_api is None:
        _client_api = ClientAPI()
        _client_api.start()  # 启动监听线程
    public_key = _client_api.get_public_key_bytes().decode('utf-8')
    ip, port = _client_api.host, _client_api.port

    response = serverAPI.login(user_id, password, public_key, ip, port)
    return BaseResponse(**response).model_dump(), response['status']

def logout_service(user_id):
    pass