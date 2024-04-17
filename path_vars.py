# -*- coding: utf-8 -*-
"""
寻找游戏目录，如果找不到就返回桌面位置
"""
import os
import sys

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), 'Desktop')
CURRENT_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = os.path.join(CURRENT_PATH, 'plugin_config.json')


def __find_ptb_path():
    # 将PTB_path初始化为桌面位置
    PTB_path = DESKTOP_PATH
    # 从C盘开始寻找：
    # 优先在用户目录下寻找，先遍历所有账户名：
    for user in os.listdir('C:\\Users'):
        # 找到AppData/LocalLow/茕海开发组/工艺战舰Alpha
        if os.path.isdir(os.path.join('C:\\Users', user, 'AppData', 'LocalLow', '茕海开发组', '工艺战舰Alpha')):
            PTB_path = os.path.join('C:\\Users', user, 'AppData', 'LocalLow', '茕海开发组', '工艺战舰Alpha')
            break
    # 如果在用户目录下没有找到，就返回None
    return PTB_path


def __find_na_ship_path():
    # 将PTB_path初始化为桌面位置
    NA_path = DESKTOP_PATH
    # 从C盘开始寻找：
    # 优先在用户目录下寻找，先遍历所有账户名：
    for user in os.listdir('C:\\Users'):
        # 找到AppData/LocalLow/RZEntertainment/NavalArt/ShipSaves
        if os.path.isdir(os.path.join(
                'C:\\Users', user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt', 'ShipSaves')):
            NA_path = os.path.join(
                'C:\\Users', user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt', 'ShipSaves')
            break
    # 如果在用户目录下没有找到，就返回None
    return NA_path


def __find_na_root_path():
    # 将NA_path初始化为桌面位置
    NA_path = DESKTOP_PATH
    # 从C盘开始寻找：
    # 优先在用户目录下寻找，先遍历所有账户名：
    for user in os.listdir('C:\\Users'):
        # 找到AppData/LocalLow/RZEntertainment/NavalArt/ShipSaves
        if os.path.isdir(os.path.join(
                'C:\\Users', user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt')):
            NA_path = os.path.join(
                'C:\\Users', user, 'AppData', 'LocalLow', 'RZEntertainment', 'NavalArt')
            break
    # 如果在用户目录下没有找到，就返回桌面位置
    return NA_path


DESKTOP_PATH = os.path.join(os.path.expanduser("~"), 'Desktop')
PTB_PATH = __find_ptb_path()
NA_SHIP_PATH = __find_na_ship_path()
NA_ROOT_PATH = __find_na_root_path()

print(f"""
初始化路径：
\tDESKTOP_PATH: {DESKTOP_PATH}
\tPTB_PATH: {PTB_PATH}
\tNA_SHIP_PATH: {NA_SHIP_PATH}
\tNA_ROOT_PATH: {NA_ROOT_PATH}
\tCONFIG_PATH: {CONFIG_PATH}
\tCURRENT_PATH: {CURRENT_PATH}
""")
