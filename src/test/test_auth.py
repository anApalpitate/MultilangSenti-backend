import pytest
import requests

from config import get_config

config = get_config()
BASE_URL = f"http://{config.HOST}:{config.PORT}"
print("BASE_URL:", BASE_URL)


@pytest.fixture(scope="module")
def test_user():
    return {
        "username": "testuser_live",
        "password": "Test1234!"
    }


@pytest.fixture(scope="module")
def token(test_user):
    # 注册用户（可能已存在）
    res = requests.post(f"{BASE_URL}/auth/register", json=test_user)

    if res.status_code not in [200, 400]:
        print("用户已存在，无需注册")

    # 登录获取 token
    res = requests.post(f"{BASE_URL}/auth/login", data=test_user)
    assert res.status_code == 200
    return res.json()["access_token"]


def test_get_me(token):
    print("token:", token)
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "testuser_live"
