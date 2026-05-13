# -*- coding: utf-8 -*-
"""
寻找游戏目录，如果找不到就返回桌面位置
不可在此导入Log模块，会造成循环导入，引发ImportError
"""
import os
import sys
from pathlib import Path

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), 'Desktop')
CURRENT_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = os.path.join(CURRENT_PATH, 'plugin_config.json')
WINDOWS_USERS_PATH = 'C:\\Users'


def increment_path(path):
    """
    若输入文件路径已存在, 为了避免覆盖, 自动在后面累加数字返回一个可用的路径
    例如输入 './img.jpg' 已存在, 则返回 './img_0000.jpg'
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        return str(path)

    suffix = path.suffix
    stem = path.stem
    for n in range(0, 9999):
        new_path = path.with_name(f"{stem}_{n:04d}{suffix}")
        if not new_path.exists():
            return str(new_path)
    raise FileExistsError(f"No available incremented path for {path}")


def _iter_windows_users():
    """
    遍历 Windows 用户目录。
    在非 Windows 环境或 C:\\Users 不存在时返回空列表，避免导入模块时崩溃。
    """
    if os.name != 'nt' or not os.path.isdir(WINDOWS_USERS_PATH):
        return []
    return os.listdir(WINDOWS_USERS_PATH)


def __find_ptb_path():
    # 将PTB_path初始化为桌面位置
    PTB_path = DESKTOP_PATH
    # 从C盘开始寻找：
    # 优先在用户目录下寻找，先遍历所有账户名：
    for user in _iter_windows_users():
        # 找到AppData/LocalLow/茕海开发组/工艺战舰Alpha
        if os.path.isdir(os.path.join(WINDOWS_USERS_PATH, user, 'AppData', 'LocalLow', '茕海开发组', '工艺战舰Alpha')):
            PTB_path = os.path.join(WINDOWS_USERS_PATH, user, 'AppData', 'LocalLow', '茕海开发组', '工艺战舰Alpha')
            break
    # 如果在用户目录下没有找到，就返回桌面位置
    return PTB_path


def __find_na_ship_path():
    # 将NA_path初始化为桌面位置
    NA_path = DESKTOP_PATH
    # 从C盘开始寻找：
    # 优先在用户目录下寻找，先遍历所有账户名：
    for user in _iter_windows_users():
        # 找到AppData/LocalLow/RZEntertainment/NavalArt/ShipSaves
        if os.path.isdir(os.path.join(
                WINDOWS_USERS_PATH, user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt', 'ShipSaves')):
            NA_path = os.path.join(
                WINDOWS_USERS_PATH, user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt', 'ShipSaves')
            break
    # 如果在用户目录下没有找到，就返回桌面位置
    return NA_path


def __find_na_root_path():
    # 将NA_path初始化为桌面位置
    NA_path = DESKTOP_PATH
    # 从C盘开始寻找：
    # 优先在用户目录下寻找，先遍历所有账户名：
    for user in _iter_windows_users():
        # 找到AppData/LocalLow/RZEntertainment/NavalArt
        if os.path.isdir(os.path.join(
                WINDOWS_USERS_PATH, user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt')):
            NA_path = os.path.join(
                WINDOWS_USERS_PATH, user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt')
            break
    # 如果在用户目录下没有找到，就返回桌面位置
    return NA_path


# DESKTOP_PATH = os.path.join(os.path.expanduser("~"), 'Desktop')
PTB_PATH = __find_ptb_path()
NA_SHIP_PATH = __find_na_ship_path()
NA_ROOT_PATH = __find_na_root_path()
