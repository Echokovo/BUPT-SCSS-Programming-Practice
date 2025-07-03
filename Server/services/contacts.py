from schemas.contacts import BaseResponse
from services.serverAPI import serverAPI

def get_contacts_service():
    response = serverAPI.get_contacts()
    return BaseResponse(**response).model_dump(), response['status']

def add_friend_service(friend_id):
    response = serverAPI.add_friend(friend_id)
    return BaseResponse(**response).model_dump(), response['status']

def agree_service(user_id):
    """未实现"""
    pass

def delete_friend_service(friend_id):
    response = serverAPI.delete_friend(friend_id)
    return BaseResponse(**response).model_dump(), response['status']