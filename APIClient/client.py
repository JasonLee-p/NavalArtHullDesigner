"""
和服务器通信，目前处于测试阶段
"""
import requests
from APIClient.email_utils import *

_TAG = "APIClient"

TESTING = True


def request_url(url, data=None):
    """
    请求url
    """
    if data is None:
        response = requests.get(url)
    else:
        response = requests.post(url, json=data)
    return response.json()


class APIClient:
    """
    和服务器通信
    """
    def __init__(self):
        self.port_url = "http://127.0.0.1:9284" if TESTING else "http://47.113.220.157:9284"
        self._register_url = f"{self.port_url}/register"
        self._login_url = f"{self.port_url}/login"
        self._logout_url = f"{self.port_url}/logout"
        self._currentUser_url = f"{self.port_url}/user"

    def register_request(self, username, email, password):
        """
        注册
        """
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

    def login_request(self, email, password):
        """
        登录
        """
        data = {
            'email': email,
            'password': password
        }
        response = request_url(self._login_url, data)
        if "error" in response:
            return response["error"]
        return response["message"]

    def logout_request(self):
        """
        退出
        """
        response = request_url(self._logout_url)
        return response["message"]

    def currentUser_request(self):
        """
        获取当前用户信息
        """
        response = requests.get(self._currentUser_url)
        return response.json()


if __name__ == '__main__':
    client = APIClient()
    print(client.register_request("test", "2593292614@qq.com", "password123"))
    print(client.login_request("2593292614@qq.com", "Lzx2003123."))
    print()
