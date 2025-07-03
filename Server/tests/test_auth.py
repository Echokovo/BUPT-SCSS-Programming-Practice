import json

def test_register_success(client):
    # 测试成功注册
    response = client.post(
        '/register',
        json={
            "data": {
                "user_id": "test_user",
                "password": "test_password",
                "email": "test@example.com"
            }
        }
    )
    assert response.status_code == 200

def test_register_existing_user(client):
    # 测试注册已存在的用户
    # 先注册用户
    client.post(
        '/register',
        json={
            "data": {
                "user_id": "existing_user",
                "password": "password",
                "email": "existing@example.com"
            }
        }
    )
    # 再次注册相同用户
    response = client.post(
        '/register',
        json={
            "data": {
                "user_id": "existing_user",
                "password": "password",
                "email": "existing@example.com"
            }
        }
    )
    assert response.status_code == 409

def test_register_invalid_params(client):
    # 测试注册时缺少必要参数
    response = client.post(
        '/register',
        json={
            "data": {
                "user_id": "test_user",
                "password": "test_password"
                # 缺少email
            }
        }
    )
    assert response.status_code == 400

def test_login_success(client):
    # 测试成功登录
    # 先注册用户
    client.post(
        '/register',
        json={
            "data": {
                "user_id": "login_user",
                "password": "login_password",
                "email": "login@example.com"
            }
        }
    )
    # 登录用户
    response = client.post(
        '/login',
        json={
            "data": {
                "user_id": "login_user",
                "password": "login_password",
                "public_key": "test_public_key",
                "ip": "127.0.0.1",
                "port": 12345
            }
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data['data']

def test_login_nonexistent_user(client):
    # 测试登录不存在的用户
    response = client.post(
        '/login',
        json={
            "data": {
                "user_id": "nonexistent_user",
                "password": "password",
                "public_key": "test_public_key",
                "ip": "127.0.0.1",
                "port": 12345
            }
        }
    )
    assert response.status_code == 404

def test_login_wrong_password(client):
    # 测试登录密码错误
    # 先注册用户
    client.post(
        '/register',
        json={
            "data": {
                "user_id": "wrong_password_user",
                "password": "correct_password",
                "email": "wrong@example.com"
            }
        }
    )
    # 使用错误密码登录
    response = client.post(
        '/login',
        json={
            "data": {
                "user_id": "wrong_password_user",
                "password": "wrong_password",
                "public_key": "test_public_key",
                "ip": "127.0.0.1",
                "port": 12345
            }
        }
    )
    assert response.status_code == 401

def test_login_invalid_params(client):
    # 测试登录时缺少必要参数
    response = client.post(
        '/login',
        json={
            "data": {
                "user_id": "test_user",
                "password": "test_password"
                # 缺少public_key, ip, port
            }
        }
    )
    assert response.status_code == 400

from models.online import Online

def test_login_existing_user(client):
    """测试已登录用户再次登录返回409状态码"""
    # 注册新用户
    client.post(
        '/register',
        json={
            "data": {
                "user_id": "existing_user",
                "password": "test_password",
                "email": "existing@example.com"
            }
        }
    )

    # 第一次登录 - 正常登录
    first_login = client.post(
        '/login',
        json={
            "data": {
                "user_id": "existing_user",
                "password": "test_password",
                "public_key": "pub_key_1",
                "ip": "192.168.1.1",
                "port": 8080
            }
        }
    )
    assert first_login.status_code == 200

    # 验证用户已记录到Online表
    with client.application.app_context():
        online_user = Online.get_user("existing_user")
        assert online_user is not None
        assert online_user.public_key == "pub_key_1"
        assert online_user.ip == "192.168.1.1"
        assert online_user.port == 8080

    # 同一用户再次登录 - 应返回409
    second_login = client.post(
        '/login',
        json={
            "data": {
                "user_id": "existing_user",
                "password": "test_password",
                "public_key": "pub_key_2",  # 尝试使用不同的公钥
                "ip": "192.168.1.2",
                "port": 8081
            }
        }
    )
    assert second_login.status_code == 409

    # 验证Online表中数据未被覆盖
    with client.application.app_context():
        online_user = Online.get_user("existing_user")
        assert online_user.public_key == "pub_key_1"  # 确保数据未被新登录覆盖
        assert online_user.ip == "192.168.1.1"
        assert online_user.port == 8080