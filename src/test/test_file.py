import os

import pytest
import requests

from config import get_config

config = get_config()
BASE_URL = f"http://{config.HOST}:{config.PORT}"
AUTH_URL = f"{BASE_URL}/auth"
FILE_URL = f"{BASE_URL}/file"

# 本地测试文件目录（调整为实际路径）
TEST_FILES_DIR = os.path.join(os.getcwd(), "./test/files")
TEST_FILES = [
    "file1.txt",
    "file2.jpg",
    "file3.pdf",
    "file4.png",
    "file5.md"
]

created_users = []
created_files = []


# -------------------- 工具函数 --------------------
def register_user(username, password="test123456", role="user"):
    payload = {"username": username, "password": password, "role": role}
    res = requests.post(f"{AUTH_URL}/register", json=payload)
    if res.status_code == 200:
        created_users.append(username)
    return res


def login_user(username, password="test123456"):
    payload = {"username": username, "password": password}
    res = requests.post(f"{AUTH_URL}/login", data=payload)
    return res


def get_token(username, password="test123456"):
    res = login_user(username, password)
    if res.status_code == 200:
        return res.json()["access_token"]
    print(res.json())
    return None


def upload_file(token, filepath, category="test_files"):
    headers = {"Authorization": f"Bearer {token}"}
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        files = {
            "file": (filename, f),
            "category": (None, category)
        }
        res = requests.post(f"{FILE_URL}/upload", files=files, headers=headers)
    if res.status_code == 200:
        file_id = res.json().get("id")
        owner = res.json().get("owner_id")
        created_files.append((file_id, owner))
    return res


def delete_file(token, file_id):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.delete(f"{FILE_URL}/{file_id}", headers=headers)
    if res.status_code == 200:
        # 删除成功，从记录中清理
        global created_files
        created_files = [f for f in created_files if f[0] != file_id]
    return res


def get_user_by_name(username, token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{AUTH_URL}/user", params={"username": username}, headers=headers)
    return res


def delete_user(token, user_id):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{AUTH_URL}/delete/{user_id}", headers=headers)


# -------------------- 测试用例 --------------------

@pytest.fixture(scope="module")
def test_user_token():
    """
    注册并登录测试用户，重复测试时保证同一个用户存在
    """
    username = "test_file_user"
    # 先尝试注册，失败可能是已经存在，忽略
    register_user(username)
    token = get_token(username)
    assert token is not None, "登录失败，无法获得token"
    yield token


@pytest.fixture(scope="module", autouse=True)
def cleanup(test_user_token):
    """
    测试结束后清理环境
    """
    yield

    admin_username = "test_file"
    admin_password = "cleanup123456"
    # 创建admin，尝试注册失败忽略
    register_user(admin_username, admin_password, role="admin")
    admin_token = get_token(admin_username, admin_password)

    assert admin_token is not None, "清理时无法获取admin token"

    # 获取所有测试用户（created_users中）
    for username in list(created_users):
        res = get_user_by_name(username, admin_token)
        if res.status_code != 200:
            continue
        user_id = res.json()["id"]
        delete_user(admin_token, user_id)


# -------------------- 实际测试 --------------------
def test_upload_single_file(test_user_token):
    """
    单文件上传测试（上传 file1.txt）
    """
    token = test_user_token
    filename = TEST_FILES[0]
    filepath = os.path.join(TEST_FILES_DIR, filename)
    assert os.path.isfile(filepath), f"测试文件不存在: {filepath}"

    res = upload_file(token, filepath)
    print(res.json())
    assert res.status_code == 200, "单文件上传失败"
    data = res.json()
    assert data["filename"] == filename
    assert "id" in data
    assert "owner_id" in data


def test_upload_all_files(test_user_token):
    """
    测试上传五个文件
    """
    token = test_user_token
    for filename in TEST_FILES:
        filepath = os.path.join(TEST_FILES_DIR, filename)
        assert os.path.isfile(filepath), f"测试文件不存在: {filepath}"
        res = upload_file(token, filepath)
        assert res.status_code == 200, f"上传失败: {filename}"
        data = res.json()
        assert data["filename"] == filename
        assert "id" in data
        assert "owner_id" in data


def test_upload_no_file(test_user_token):
    """
    上传接口传空文件，应该报400
    """
    token = test_user_token
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("", b""), "category": (None, "test_files")}
    res = requests.post(f"{FILE_URL}/upload", files=files, headers=headers)
    assert res.status_code == 400


def test_delete_file(test_user_token):
    """
    上传后删除文件，检查是否成功
    """
    token = test_user_token
    # 上传第一个文件
    filepath = os.path.join(TEST_FILES_DIR, TEST_FILES[0])
    res = upload_file(token, filepath)
    assert res.status_code == 200
    file_id = res.json()["id"]

    # 删除
    del_res = delete_file(token, file_id)
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "删除成功"

    # 再删除一次，应该返回404
    del_res_2 = delete_file(token, file_id)
    assert del_res_2.status_code == 404


def test_delete_file_no_auth():
    """
    未登录删除文件，应拒绝访问（401）
    """
    # 试删一个任意ID
    res = requests.delete(f"{FILE_URL}/1")
    assert res.status_code == 401
