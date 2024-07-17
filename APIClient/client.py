"""
和服务器通信
"""
import requests
from APIClient.email_utils import *
from main_logger import Log

_TAG = "APIClient"


def request_url(url, data=None):
    if data is None:
        response = requests.get(url)
    else:
        response = requests.post(url, json=data)
    return response.json()


class APIClient:
    def __init__(self):
        self.base_url = "http://"
        self._register_url = f"{self.base_url}/user/register"
        self._login_url = f"{self.base_url}/user/login"
        self._logout_url = f"{self.base_url}/user/logout"
        self._currentUser_url = f"{self.base_url}/user/user"

    def register_request(self, username, email, password):
        # 检查邮箱是否合法
        if not is_valid_email(email):
            return "邮箱格式不正确"
        elif not verify_email_smtp(email):
            return "邮箱不存在"
        # 检查用户名格式
        if username.strip() == "":
            return "用户名不能为空"
        elif len(username) < 3:
            return "用户名长度不能小于3"
        # 检查密码
        if password.strip() == "":
            return "密码不能为空"
        elif len(password) < 6:
            return "密码长度不能小于6"

        data = {
            'username': username,
            'email': email,
            'password': password
        }
        response = request_url(self._register_url, data)
        # 如果用户名或邮箱已存在
        if "error" in response:
            return response["error"]
        return response["message"]

    def _register_request(self, username, email, password):
        data = {
            'username': username,
            'email': email,
            'password': password
        }
        response = requests.post(self._register_url, json=data)
        return response.json()

    def _login_request(self, email, password):
        data = {
            'email': email,
            'password': password
        }
        response = requests.post(self._login_url, json=data)
        return response.json()

    def _logout_request(self):
        response = requests.post(self._logout_url)
        return response.json()

    def _currentUser_request(self):
        response = requests.get(self._currentUser_url)
        return response.json()
