from flask_jwt_extended import create_access_token
from ..schemas.auth import UserRegisterRequest, UserLoginResponse
from ..models.users import User

def register_service(user_id, password, email):
    result = dict()
    if User.check_user(user_id) is None:
        result['status'] = 200
        result['message'] = 'success'
        User.create_user(user_id, password, email)
    else:
        result['status'] = 409
        result['message'] = 'user already exists'
    return UserRegisterRequest(**result)

def login_service(user_id, password, public_key):
    result = dict()
    if User.check_user(user_id) is not None:
        if User.check_password(user_id, password):
            result['status'] = 200
            result['message'] = 'success'
            token = create_access_token(identity=user_id, expires_delta=False)
            result["data"] = {"token": token}
        else:
            result['status'] = 401
            result['message'] = 'wrong password'
    else:
        result['status'] = 404
        result['message'] = 'user does not exist'
    return UserLoginResponse(**result)
