import flask_bcrypt
from flask_jwt_extended import create_access_token
from schemas.auth import UserLoginResponse, UserRegisterResponse
from models.users import User
from models.online import Online

bcrypt = flask_bcrypt.Bcrypt()

def register_service(user_id, password, email):
    result = dict()
    if User.get_user(user_id) is None:
        result['status'] = 200
        result['message'] = 'success'
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        User.create_user(user_id, password, email)
    else:
        result['status'] = 409
        result['message'] = 'user already exists'
    return UserRegisterResponse(**result).model_dump_json()

def login_service(user_id, password, public_key, ip, port):
    result = dict()
    if User.get_user(user_id) is not None:
        if Online.get_user(user_id) is None:
            if bcrypt.check_password_hash(User.get_password(user_id), password):
                result['status'] = 200
                result['message'] = 'success'
                token = create_access_token(identity=user_id, expires_delta=False)
                result["data"] = {"token": token}
                Online.user_login(
                    user_id=user_id,
                    public_key=public_key,
                    ip=ip,
                    port=port
                )
            else:
                result['status'] = 401
                result['message'] = 'wrong password'
        else:
            result['status'] = 409
            result['message'] = 'user already login'
    else:
        result['status'] = 404
        result['message'] = 'user does not exist'
    return UserLoginResponse(**result).model_dump_json()
