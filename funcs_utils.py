# -*- coding: utf-8 -*-
"""
工具函数
"""

import ctypes
from typing import Literal
from PyQt5.QtWidgets import QMessageBox


class CONST:
    # 信息类型
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PROMPT = "prompt"
    QUESTION = "question"

    # 具体方位
    FRONT = "front"
    BACK = "back"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    SAME = "same"

    FRONT_NORMAL = (0., 0., 1.)
    BACK_NORMAL = (0., 0., -1.)
    LEFT_NORMAL = (-1., 0., 0.)
    RIGHT_NORMAL = (1., 0., 0.)
    UP_NORMAL = (0., 1., 0.)
    DOWN_NORMAL = (0., -1., 0.)

    # 方位组合
    FRONT_BACK = "front_back"
    UP_DOWN = "up_down"
    LEFT_RIGHT = "left_right"

    # 八个卦限
    FRONT_UP_LEFT = "front_up_left"
    FRONT_UP_RIGHT = "front_up_right"
    FRONT_DOWN_LEFT = "front_down_left"
    FRONT_DOWN_RIGHT = "front_down_right"
    BACK_UP_LEFT = "back_up_left"
    BACK_UP_RIGHT = "back_up_right"
    BACK_DOWN_LEFT = "back_down_left"
    BACK_DOWN_RIGHT = "back_down_right"

    DIR_INDEX_MAP = {FRONT_BACK: 2, UP_DOWN: 1, LEFT_RIGHT: 0}
    SUBDIR_MAP = {FRONT_BACK: (FRONT, BACK), UP_DOWN: (UP, DOWN), LEFT_RIGHT: (LEFT, RIGHT)}
    DIR_OPPOSITE_MAP = {FRONT: BACK, BACK: FRONT, UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT, SAME: SAME}
    VERTICAL_DIR_MAP = {
        FRONT: (UP, DOWN, LEFT, RIGHT), BACK: (UP, DOWN, LEFT, RIGHT), FRONT_BACK: (UP, DOWN, LEFT, RIGHT),
        UP: (FRONT, BACK, LEFT, RIGHT), DOWN: (FRONT, BACK, LEFT, RIGHT), UP_DOWN: (FRONT, BACK, LEFT, RIGHT),
        LEFT: (FRONT, BACK, UP, DOWN), RIGHT: (FRONT, BACK, UP, DOWN), LEFT_RIGHT: (FRONT, BACK, UP, DOWN)}
    VERTICAL_RAWDIR_MAP = {
        FRONT: (UP_DOWN, LEFT_RIGHT), BACK: (UP_DOWN, LEFT_RIGHT), FRONT_BACK: (UP_DOWN, LEFT_RIGHT),
        UP: (FRONT_BACK, LEFT_RIGHT), DOWN: (FRONT_BACK, LEFT_RIGHT), UP_DOWN: (FRONT_BACK, LEFT_RIGHT),
        LEFT: (FRONT_BACK, UP_DOWN), RIGHT: (FRONT_BACK, UP_DOWN), LEFT_RIGHT: (FRONT_BACK, UP_DOWN)}
    DIR_TO_RAWDIR_MAP = {
        FRONT: FRONT_BACK, BACK: FRONT_BACK, UP: UP_DOWN, DOWN: UP_DOWN, LEFT: LEFT_RIGHT, RIGHT: LEFT_RIGHT}
    # 旋转顺序
    __orders = ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"]
    ROTATE_ORDER = __orders[2]


VECTOR_RELATION_MAP = {
    (0., 0., 1.): {"Larger": CONST.FRONT, "Smaller": CONST.BACK},
    (0., 0., -1.): {"Larger": CONST.BACK, "Smaller": CONST.FRONT},
    (1., 0., 0.): {"Larger": CONST.LEFT, "Smaller": CONST.RIGHT},
    (-1., 0., 0.): {"Larger": CONST.RIGHT, "Smaller": CONST.LEFT},
    (0., 1., 0.): {"Larger": CONST.UP, "Smaller": CONST.DOWN},
    (0., -1., 0.): {"Larger": CONST.DOWN, "Smaller": CONST.UP},
}


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


def not_implemented(func):
    """
    装饰器，弹出提示框，提示该功能暂未实现
    :return:
    """

    def wrapper(*args, **kwargs):
        QMessageBox.information(None, "提示", "该功能暂未实现，敬请期待！", QMessageBox.Ok)

    return wrapper


def empty_func(*args, **kwargs):
    """ 空函数，用于占位 """
    pass


def is_admin():
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


def func_run_time(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"函数{func.__name__}运行时间：{end-start}")
        return result
    return wrapper


def bool_protection(attr_name=None):
    """
    当实例对象有状态布尔属性用来标记是否正在操作时，
    保护其不被多线程同时操作
    :param attr_name:
    :return:
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if attr_name is None:
                attr_name_ = f"__{func.__name__}_bool_protection__"
            else:
                attr_name_ = attr_name
            if not hasattr(self, attr_name_):  # 如果没有该属性，则创建该属性
                setattr(self, attr_name_, False)
            if getattr(self, attr_name_):  # 如果正在操作，则返回
                return
            setattr(self, attr_name_, True)
            result = func(self, *args, **kwargs)
            setattr(self, attr_name_, False)
            return result
        return wrapper
    return decorator

