import pytest
import json
from models.users import User

class TestContacts:
    @pytest.fixture(autouse=True)
    def setup(self, client, db_setup):
        self.client = client
        self.db = db_setup
        # 注册测试用户
        self.register_user("test_user", "password123", "test@example.com")
        self.register_user("friend1", "password456", "friend1@example.com")
        self.register_user("friend2", "password789", "friend2@example.com")
        # 登录获取token
        test_user_rep = self.login_user("test_user", "password123")
        friend1_rep = self.login_user("friend1", "password456")
        friend2_rep = self.login_user("friend2", "password789")
        self.test_user_token = test_user_rep.json["data"]["token"]
        self.friend1_token = friend1_rep.json["data"]["token"]
        self.friend2_token = friend2_rep.json["data"]["token"]

    def register_user(self, user_id, password, email):
        return self.client.post(
            "/register",
            json={"data": {"user_id": user_id, "password": password, "email": email}}
        )

    def login_user(self, user_id, password):
        return self.client.post(
            "/login",
            json={"data": {
                "user_id": user_id,
                "password": password,
                "public_key": "test_key",
                "ip": "127.0.0.1",
                "port": 12345
            }}
        )

    def test_get_contacts_empty(self):
        response = self.client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"}
        )
        assert response.status_code == 200
        assert len(response.json["data"]) == 0

    def test_add_friend_success(self):
        # 添加好友
        response = self.client.post(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"},
            json={"data": {"friend_id": "friend1"}}
        )
        assert response.status_code == 200

        # 检查通讯录
        response = self.client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {self.friend1_token}"}
        )
        assert response.status_code == 200
        assert len(response.json["data"]) == 1
        assert response.json["data"][0]["user_id"] == "test_user"
        assert response.json["data"][0]["flag"] == False

    def test_add_friend_already_exists(self):
        # 首次添加
        response = self.client.post(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"},
            json={"data": {"friend_id": "friend1"}}
        )
        assert response.status_code == 200

        # 重复添加
        response = self.client.post(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"},
            json={"data": {"friend_id": "friend1"}}
        )
        assert response.status_code == 409

    def test_delete_friend_success(self):
        # 添加好友
        response = self.client.post(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"},
            json={"data": {"friend_id": "friend1"}}
        )
        assert response.status_code == 200

        # 删除好友
        response = self.client.delete(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"},
            json={"data": {"friend_id": "friend1"}}
        )
        assert response.status_code == 200

        # 检查通讯录
        response = self.client.get(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"}
        )
        assert response.status_code == 200
        assert len(response.json["data"]) == 0

    def test_delete_friend_not_exists(self):
        # 删除不存在的好友
        response = self.client.delete(
            "/contacts",
            headers={"Authorization": f"Bearer {self.test_user_token}"},
            json={"data": {"friend_id": "friend1"}}
        )
        assert response.status_code == 409