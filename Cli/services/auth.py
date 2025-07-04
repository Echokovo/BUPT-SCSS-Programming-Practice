from config import SERVER_CONFIG
from schemas.auth import BaseResponse
from services.serverAPI import serverAPI
from services.clientAPI import ClientAPI, get_client_api


def register_service(user_id, password, email):
    response = serverAPI.register(user_id, password, email)
    return BaseResponse(**response).model_dump(), response['status']

def login_service(user_id, password):
    client_api = get_client_api() # 启动监听线程
    public_key = client_api.get_public_key_bytes().decode('utf-8')
    ip, port = client_api.host, client_api.port

    response = serverAPI.login(user_id, password, public_key, ip, port)
    return BaseResponse(**response).model_dump(), response['status']

def logout_service():
    return {},200