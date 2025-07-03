from schemas.utils import BaseResponse
from services.serverAPI import serverAPI

def online_service(friend_id):
    response = serverAPI.get_online_status(friend_id)
    return BaseResponse(**response).model_dump(), response['status']