from config import CLIENT_CONFIG
from schemas.auth import BaseResponse
from services.online import Heartbeat
from services.serverAPI import serverAPI
from services.clientAPI import get_client_api, ClientAPI


def register_service(user_id, password, email):
    response = serverAPI.register(user_id, password, email)
    return BaseResponse(**response).model_dump(), response['status']

def login_service(user_id, password):
    private_key, public_key = ClientAPI.generate_key_pair()
    response = serverAPI.login(user_id, password, public_key, CLIENT_CONFIG['ip'], CLIENT_CONFIG['port'])
    if response['status'] == 200:
        p2p_client = get_client_api(
            host=CLIENT_CONFIG['ip'],
            port=CLIENT_CONFIG['port'],
            user_id=user_id,
            public_key=public_key,
            private_key=private_key
        )
        heartbeat = Heartbeat()
    return BaseResponse(**response).model_dump(), response['status']

def logout_service():
    return {},200