# -*- coding: utf-8 -*-
"""
工具函数
"""

import ctypes
import time
from functools import singledispatchmethod, update_wrapper
from typing import Literal

from PyQt5.QtCore import QMutexLocker
from PyQt5.QtWidgets import QMessageBox


def snake_to_camel(snake_str):
    """
    将蛇形命名法字符串转换为大驼峰命名法字符串。

    :param snake_str: 以蛇形命名法表示的字符串
    :return: 以大驼峰命名法表示的字符串
    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


def merge_dict(d1, d2):
    """
    递归地合并两个字典，d2的键值对优先级高
    :param d1:
    :param d2:
    :return: 布尔值，是否有合并的操作
    """
    d1_changed = False
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            d_changed = merge_dict(d1[key], d2[key])
            if d_changed:
                d1_changed = True
        else:
            d1[key] = d2[key]
            d1_changed = True
    return d1_changed


def open_url(url):
    def func(_):
        from PyQt5.QtCore import QUrl
        from PyQt5.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl(url))

    return func


def not_implemented(func):  # pragma: no cover
    """
    装饰器，弹出提示框，提示该功能暂未实现
    :return:
    """

    def wrapper(*args, **kwargs):  # pragma: no cover
        QMessageBox.information(None, "提示", "该功能暂未实现，敬请期待！", QMessageBox.Ok)

    return wrapper


def singleton(cls):
    """
    单例模式装饰器
    :param cls:
    :return:
    """
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


class dispatchmethod(singledispatchmethod):
    """Dispatch a method to different implementations
    depending upon the type of its first argument.
    If there is no argument, use 'object' instead.
    """

    def __init__(self, func):
        super().__init__(func)
        self._cache = {}

    def __get__(self, obj, cls=None):
        def _method(*args, **kwargs):
            # Determine the class of the first argument or fallback to object
            if len(args) > 0:
                class__ = args[0].__class__
            elif len(kwargs) > 0:
                class__ = next(iter(kwargs.values())).__class__
            else:
                class__ = object

            # Check the cache first
            if class__ in self._cache:
                method = self._cache[class__]
            else:
                method = self.dispatcher.dispatch(class__)
                self._cache[class__] = method

            return method.__get__(obj, cls)(*args, **kwargs)

        _method.__isabstractmethod__ = self.__isabstractmethod__
        _method.register = self.register
        update_wrapper(_method, self.func)
        return _method


def empty_func(*args, **kwargs):  # pragma: no cover
    """ 空函数，用于占位 """
    pass


def is_admin():
    """
    判断是否是管理员权限
    :return:
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as _e:
        print(_e)
        return False


def color_print(text, color: Literal["red", "green", "yellow", "blue", "magenta", "cyan", "white"] = "green"):
    """
    输出带颜色的文字
    :param text: 文字
    :param color: 颜色
    :return:
    """
    color_dict = {"red": 31, "green": 32, "yellow": 33, "blue": 34, "magenta": 35, "cyan": 36, "white": 37}
    print(f"\033[{color_dict[color]}m{text}\033[0m")


def time_it(func):
    """
    计算函数运行时间
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"函数{func.__name__}运行时间：{end-start}")
        return result
    return wrapper


def now(fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt, time.localtime())


def operationMutexLock(func):
    """
    用于给类的方法加锁
    类一定要有operationMutex属性
    :param func:
    :return:
    """

    def wrapper(self, *args, **kwargs):
        with QMutexLocker(self.operationMutex):
            return func(self, *args, **kwargs)
    return wrapper


def mutexLock(mutexName):
    """
    用于给类的方法加锁
    :param mutexName: 互斥锁的名称
    :return:
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            with QMutexLocker(getattr(self, mutexName)):
                return func(self, *args, **kwargs)
        return wrapper

    return decorator
