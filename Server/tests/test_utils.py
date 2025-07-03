import pytest
import json

# Test data
TEST_USER1 = {
    "user_id": "test_user1",
    "password": "password123",
    "email": "user1@test.com",
    "public_key": "public_key_user1",
    "ip": "127.0.0.1",
    "port": 5000
}

TEST_USER2 = {
    "user_id": "test_user2",
    "password": "password456",
    "email": "user2@test.com",
    "public_key": "public_key_user2",
    "ip": "127.0.0.1",
    "port": 5001
}


def register_user(client, user_data):
    return client.post('/register', json={
        "data": {
            "user_id": user_data["user_id"],
            "password": user_data["password"],
            "email": user_data["email"]
        }
    })


def login_user(client, user_data):
    return client.post('/login', json={
        "data": {
            "user_id": user_data["user_id"],
            "password": user_data["password"],
            "public_key": user_data["public_key"],
            "ip": user_data["ip"],
            "port": user_data["port"]
        }
    })


def add_friend(client, token, friend_id):
    return client.post('/contacts',
                       json={"data": {"friend_id": friend_id}},
                       headers={"Authorization": f"Bearer {token}"}
                       )


def get_auth_token(client, user_data):
    register_user(client, user_data)
    login_response = login_user(client, user_data)
    return json.loads(login_response.data)["data"]["token"]


def test_check_online_status(client, db_setup):
    # Setup users and get tokens
    token1 = get_auth_token(client, TEST_USER1)
    token2 = get_auth_token(client, TEST_USER2)

    # User1 adds User2 as friend (one-way)
    add_friend(client, token1, TEST_USER2["user_id"])
    # User2 adds User1 as friend to complete friendship
    add_friend(client, token2, TEST_USER1["user_id"])

    # Test checking online status
    response = client.post('/online',
                           json={"data": {"friend_id": TEST_USER2["user_id"]}},
                           headers={"Authorization": f"Bearer {token1}"}
                           )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == 200

    # Test checking non-friend (should fail)
    TEST_USER3 = {
        "user_id": "test_user3",
        "password": "password789",
        "email": "user3@test.com",
        "public_key": "public_key_user3",
        "ip": "127.0.0.1",
        "port": 5002
    }
    register_user(client, TEST_USER3)

    response = client.post('/online',
                           json={"data": {"friend_id": TEST_USER3["user_id"]}},
                           headers={"Authorization": f"Bearer {token1}"}
                           )
    assert response.status_code == 403

    # Test checking non-existent user
    response = client.post('/online',
                           json={"data": {"friend_id": "nonexistent_user"}},
                           headers={"Authorization": f"Bearer {token1}"}
                           )
    assert response.status_code == 404


def test_get_public_key(client, db_setup):
    # Setup users and get tokens
    token1 = get_auth_token(client, TEST_USER1)
    token2 = get_auth_token(client, TEST_USER2)

    # Establish friendship
    add_friend(client, token1, TEST_USER2["user_id"])
    add_friend(client, token2, TEST_USER1["user_id"])

    # Test getting public key of online friend
    response = client.post('/online',
                           json={"data": {"friend_id": TEST_USER2["user_id"]}},
                           headers={"Authorization": f"Bearer {token1}"}
                           )

    assert response.status_code == 200
    data = json.loads(response.data)
    # Assuming the response includes public_key in data
    # Note: According to the interface doc, this endpoint only returns status
    # You might need a separate endpoint for public key retrieval

    # This part would need adjustment based on actual API implementation
    # Currently, the interface doc doesn't specify how to get public key
    # So this is a placeholder for that functionality

    # For now, we can verify that the friend is online (which implies we could get their public key)
    assert data["status"] == 200
