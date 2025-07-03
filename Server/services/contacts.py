from schemas.contacts import BaseResponse
from models.contacts import Contacts
from models.users import User

def get_contacts_service(user_id):
    result = dict()
    datas = list()
    friends = set()
    friend_requests = set()
    if User.get_user(user_id) is not None:
        contacts = Contacts.get_all_contacts(user_id)
        for contact in contacts:
            if contact.user_A == user_id:
                other_user_id = contact.user_B
                if Contacts.check_contact(other_user_id, user_id):
                    friends.add(other_user_id)
                else:
                    continue
            else:
                other_user_id = contact.user_A
                if Contacts.check_contact(other_user_id, user_id):
                    friends.add(other_user_id)
                else:
                    friend_requests.add(other_user_id)
        for user in friends:
            data = {
                'user_id': user,
                'flag': True
            }
            datas.append(data)
        for user in friend_requests:
            data = {
                'user_id': user,
                'flag': False
            }
            datas.append(data)
        result['status'] = 200
        result['message'] = 'success'
        result['data'] = datas
    else:
        result['status'] = 404
        result['message'] = 'User does not exist'
    return BaseResponse(**result).model_dump(), result['status']

def add_friend_service(user_id, friend_id):
    result = dict()
    if User.get_user(user_id) is not None:
        if not Contacts.check_contact(user_id, friend_id):
            Contacts.add_contact(user_id, friend_id)
            result['status'] = 200
            result['message'] = 'success'
        else:
            result['status'] = 409
            result['message'] = 'Contact already exists'
    else:
        result['status'] = 404
        result['message'] = 'User does not exist'

    return BaseResponse(**result).model_dump(), result['status']

def delete_friend_service(user_id, friend_id):
    result = dict()
    if User.get_user(user_id) is not None:
        if Contacts.check_contact(user_id, friend_id):
            Contacts.delete_contact(user_id, friend_id)
            result['status'] = 200
            result['message'] = 'success'
        else:
            result['status'] = 409
            result['message'] = 'Friend does not exist'
    else:
        result['status'] = 404
        result['message'] = 'User does not exist'

    return BaseResponse(**result).model_dump(), result['status']