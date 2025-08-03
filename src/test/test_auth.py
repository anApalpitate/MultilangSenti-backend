# import pytest
# import requests
#
# from config import get_config
#
# config = get_config()
# BASE_URL = f"http://{config.HOST}:{config.PORT}/auth"
# created_users = []
#
#
# # ---------- 工具函数 ----------
# def register_user(username, password="test123456", role="user"):
#     payload = {"username": username, "password": password, "role": role}
#     res = requests.post(f"{BASE_URL}/register", json=payload)
#     if res.status_code == 200:
#         created_users.append(username)
#     return res
#
#
# def login_user(username, password="test123456"):
#     payload = {"username": username, "password": password}
#     return requests.post(f"{BASE_URL}/login", data=payload)
#
#
# def get_me(token):
#     headers = {"Authorization": f"Bearer {token}"}
#     return requests.get(f"{BASE_URL}/me", headers=headers)
#
#
# def delete_user(user_id, token):
#     headers = {"Authorization": f"Bearer {token}"}
#     return requests.delete(f"{BASE_URL}/delete/{user_id}", headers=headers)
#
#
# def get_user_by_id(user_id, token):
#     headers = {"Authorization": f"Bearer {token}"}
#     return requests.get(f"{BASE_URL}/user/{user_id}", headers=headers)
#
#
# def get_user_by_name(username, token):
#     headers = {"Authorization": f"Bearer {token}"}
#     return requests.get(f"{BASE_URL}/user", params={"username": username}, headers=headers)
#
#
# # ---------- 测试固定数据 ----------
# @pytest.fixture(scope="module")
# def test_user():
#     username = "test_user_001"
#     register_user(username)
#     yield username
#
#
# @pytest.fixture(scope="module")
# def admin_user():
#     username = "test_auth"
#     password = "adminpass"
#     register_user(username, password, role="admin")
#     yield username
#
#
# @pytest.fixture(scope="module")
# def admin_token(admin_user):
#     res = login_user(admin_user, "adminpass")
#     return res.json()["access_token"]
#
#
# # ---------- 清理已注册用户 ----------
# @pytest.fixture(scope="module", autouse=True)
# def cleanup(admin_token):
#     yield
#     for username in created_users:
#         res = get_user_by_name(username, admin_token)
#         if res.status_code != 200:
#             continue
#         user_id = res.json()["id"]
#         delete_user(user_id, admin_token)
#
#
# # ---------- 测试接口逻辑 ----------
# def test_register_success():
#     """测试正常注册"""
#     res = register_user("test_register_success")
#     print(res.json())
#     assert res.status_code == 200
#     assert res.json()["username"] == "test_register_success"
#
#
# def test_register_duplicate():
#     """测试重复注册"""
#     register_user("test_dup")
#     res = register_user("test_dup")
#     assert res.status_code == 400
#     assert res.json()["detail"] == "用户名已被注册"
#
#
# def test_login_success(test_user):
#     """测试正常登录"""
#     res = login_user(test_user)
#     assert res.status_code == 200
#     assert "access_token" in res.json()
#
#
# def test_login_fail():
#     """测试使用未注册用户登录"""
#     res = login_user("nonexistent")
#     assert res.status_code == 401
#     assert res.json()["detail"] == "请先注册"
#
#
# def test_get_me_success(test_user):
#     """测试获取当前用户信息"""
#     token = login_user(test_user).json()["access_token"]
#     res = get_me(token)
#     assert res.status_code == 200
#     assert res.json()["username"] == test_user
#
#
# def test_delete_user_by_admin(admin_token):
#     """测试管理员删除一个新用户"""
#     username = "user_to_delete"
#     register_user(username)
#     res = login_user(username)
#     user_token = res.json()["access_token"]
#     user_info = get_me(user_token).json()
#     user_id = user_info["id"]
#     del_res = delete_user(user_id, admin_token)
#     assert del_res.status_code == 200
#     assert "删除id为" in del_res.json()["message"]
#
#
# def test_delete_self_fail(admin_token):
#     """测试管理员删除自己失败"""
#     admin_info = get_me(admin_token).json()
#     admin_id = admin_info["id"]
#     del_res = delete_user(admin_id, admin_token)
#     assert del_res.status_code == 403
#     assert "不能删除自己" in del_res.json()["detail"]
#
#
# def test_get_user_by_id_success(admin_token):
#     """测试通过 ID 获取用户信息"""
#     username = "get_user_test"
#     register_user(username)
#     res = login_user(username)
#     token = res.json()["access_token"]
#     user_id = get_me(token).json()["id"]
#     res = get_user_by_id(user_id, admin_token)
#     assert res.status_code == 200
#     assert res.json()["username"] == username
#
#
# def test_get_user_by_name_success(admin_token):
#     """测试通过用户名获取用户信息"""
#     username = "get_user_by_name_test"
#     register_user(username)
#     res = get_user_by_name(username, admin_token)
#     assert res.status_code == 200
#     assert res.json()["username"] == username
