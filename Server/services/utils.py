from schemas.utils import GetStateResponse, GetPublicKeyResponse
from models.users import User
from models.online import Online
from models.contacts import Contacts

def online_service(user_id, friend_id):
    result = dict()
    if User.get_user(friend_id):
        if Contacts.check_relationship(user_id, friend_id):
            if Online.get_state(friend_id):
                result['status'] = 200
                result['message'] = 'success'
            else:
                result['status'] = 199
                result['message'] = 'Friend not online'
        else:
            result['status'] = 403
            result['message'] = 'Relationship does not exist'
    else:
        result['status'] = 404
        result['message'] = 'User does not exist'
    return GetStateResponse(**result)

def public_key_service(user_id, friend_id):
    result = dict()
    if User.get_user(friend_id):
        if Contacts.check_relationship(user_id, friend_id):
            if Online.get_state(friend_id):
                user = Online.get_user(friend_id)
                data = dict()
                data['public_key'] = user.public_key
                data['ip'] = user.ip
                data['port'] = user.port
                result['status'] = 200
                result['message'] = 'success'
                result['data'] = data
            else:
                result['status'] = 199
                result['message'] = 'Friend not online'
        else:
            result['status'] = 403
            result['message'] = 'Relationship does not exist'
    else:
        result['status'] = 404
        result['message'] = 'User does not exist'
    return GetPublicKeyResponse(**result)