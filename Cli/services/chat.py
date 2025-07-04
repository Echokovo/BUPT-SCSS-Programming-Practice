from schemas.chat import BaseResponse
from services.clientAPI import _client_api

def chat_service(friend_id, message):
    result = dict()
    if _client_api is None:
        result['status'] = 409
        result['message'] = 'not logged in'

    response = _client_api.send_message(

    )
    return BaseResponse(**result).model_dump(), result['status']

def history_service(friend_id):
    result = dict()
    if _client_api is None:
        result['status'] = 409
        result['message'] = 'not logged in'

    return BaseResponse(**result).model_dump(), result['status']

def decipher_service(timestamp):
    result = dict()
    if _client_api is None:
        result['status'] = 409
        result['message'] = 'not logged in'

    return BaseResponse(**result).model_dump(), result['status']