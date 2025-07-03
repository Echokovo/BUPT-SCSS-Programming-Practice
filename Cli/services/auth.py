from config import SERVER_CONFIG
from schemas.auth import BaseResponse
from services.serverAPI import serverAPI

def register_service(user_id, password, email):
    response = serverAPI.register(user_id, password, email)
    return BaseResponse(**response).model_dump(), response['status']

def login_service(user_id, password):
    """需要实现"""
    port = SERVER_CONFIG['port']
    response = serverAPI.login(user_id, password, public_key, ip, port)
    return BaseResponse(**response).model_dump(), response['status']

def logout_service():
    return None, 200