# -*- coding: utf-8 -*-
"""
GUI基础参数
"""
import ctypes
from base64 import b64decode

import ujson
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from path_vars import DESKTOP_PATH, CONFIG_PATH

try:
    YAHEI = [QFont("Microsoft YaHei", size) for size in range(0, 101)]
    HEI = [QFont("SimHei", size) if size else None for size in range(0, 101)]
    # 加粗
    BOLD_YAHEI = [QFont("Microsoft YaHei", size, weight=QFont.Bold) for size in range(0, 101)]
    BOLD_HEI = [QFont("SimHei", size, weight=QFont.Bold) for size in range(0, 101)]
    # 斜体
    ITALIC_YAHEI = [QFont("Microsoft YaHei", size, italic=True) for size in range(0, 101)]
    ITALIC_HEI = [QFont("SimHei", size, italic=True) for size in range(0, 101)]
    # 加粗斜体
    BOLD_ITALIC_YAHEI = [QFont("Microsoft YaHei", size, weight=QFont.Bold, italic=True) for size in range(0, 101)]
    BOLD_ITALIC_HEI = [QFont("SimHei", size, weight=QFont.Bold, italic=True) for size in range(0, 101)]
except Exception as e:
    print(e)

# 主要颜色
try:
    from config_read import ConfigHandler
    configHandler = ConfigHandler()
    theme_details = configHandler.get_config("Theme")
    Theme = theme_details["Theme"]["ThemeName"]
except (FileNotFoundError, KeyError, AttributeError):
    Theme = 'Night'
    theme_details = ConfigHandler.DEFAULT_CONFIG["Theme"]

# 其他基础色
WHITE = '#FFFFFF'
BLACK = '#000000'
RED = '#FF0000'
GREEN = '#00FF00'
BLUE = '#0000FF'
YELLOW = '#FFFF00'
ORANGE = '#FFA500'
PURPLE = '#800080'
PINK = '#FFC0CB'
BROWN = '#A52A2A'
CYAN = '#00FFFF'
GOLD = '#FFD700'
LIGHTER_RED = '#F76677'
LIGHTER_GREEN = '#6DDF6D'
LIGHTER_BLUE = '#6D9DDF'
DARKER_RED = '#C00010'
DARKER_GREEN = '#00C000'
DARKER_BLUE = '#0010C0'

# 根据主题选择颜色，图片
if Theme == 'Light' or Theme == 'Day':
    # noinspection PyProtectedMember
    from .theme_config_color._day_color import *
    # noinspection PyProtectedMember
    from .UI_design.ImgPng_day import (
        _close, _add, _choose, _minimize, _maximize, _normal, _ICO, _settings,
        _structure, _layer, _elements, _user, _edit, _tip, _indicator, _folder
    )
elif Theme == 'Dark' or Theme == 'Night':
    # noinspection PyProtectedMember
    from .theme_config_color._night_color import *
    # noinspection PyProtectedMember
    from .UI_design.ImgPng_night import (
        _close, _add, _choose, _minimize, _maximize, _normal, _ICO, _settings,
        _structure, _layer, _elements, _user, _edit, _tip, _indicator, _folder
    )
elif Theme == 'Custom':
    # noinspection PyUnboundLocalVariable
    BG_COLOR0 = theme_details["Theme"]["GUITHeme"]["BG_COLOR0"]
    BG_COLOR1 = theme_details["Theme"]["GUITHeme"]["BG_COLOR1"]
    BG_COLOR2 = theme_details["Theme"]["GUITHeme"]["BG_COLOR2"]
    BG_COLOR3 = theme_details["Theme"]["GUITHeme"]["BG_COLOR3"]
    FG_COLOR0 = theme_details["Theme"]["GUITHeme"]["FG_COLOR0"]
    FG_COLOR1 = theme_details["Theme"]["GUITHeme"]["FG_COLOR1"]
    GRAY = theme_details["Theme"]["GUITHeme"]["GRAY"]
    GLTheme = theme_details["Theme"]["GLTheme"]
    # noinspection PyProtectedMember
    from .UI_design.ImgPng_night import (
        _close, _add, _choose, _minimize, _maximize, _normal, _ICO, _settings,
        _structure, _layer, _elements, _user, _edit, _tip, _indicator, _folder
    )

_all_imgs = [_close, _add, _choose, _minimize, _maximize, _normal, _ICO, _settings,
             _structure, _layer, _elements, _user, _edit, _tip, _indicator, _folder]

# 图标
BYTES_CLOSE = b64decode(_close)
BYTES_ADD = b64decode(_add)
BYTES_CHOOSE = b64decode(_choose)
BYTES_MINIMIZE = b64decode(_minimize)
BYTES_MAXIMIZE = b64decode(_maximize)
BYTES_NORMAL = b64decode(_normal)
BYTES_ICO = b64decode(_ICO)
BYTES_SETTINGS = b64decode(_settings)
BYTES_STRUCTURE = b64decode(_structure)
BYTES_LAYER = b64decode(_layer)
BYTES_ELEMENTS = b64decode(_elements)
BYTES_USER = b64decode(_user)
BYTES_EDIT = b64decode(_edit)
BYTES_TIP = b64decode(_tip)
BYTES_INDICATOR = b64decode(_indicator)
BYTES_FOLDER = b64decode(_folder)

CLOSE_IMAGE = QImage.fromData(QByteArray(BYTES_CLOSE))
ADD_IMAGE = QImage.fromData(QByteArray(BYTES_ADD))
CHOOSE_IMAGE = QImage.fromData(QByteArray(BYTES_CHOOSE))
MINIMIZE_IMAGE = QImage.fromData(QByteArray(BYTES_MINIMIZE))
MAXIMIZE_IMAGE = QImage.fromData(QByteArray(BYTES_MAXIMIZE))
NORMAL_IMAGE = QImage.fromData(QByteArray(BYTES_NORMAL))
ICO_IMAGE = QImage.fromData(QByteArray(BYTES_ICO))
SETTINGS_IMAGE = QImage.fromData(QByteArray(BYTES_SETTINGS))
STRUCTURE_IMAGE = QImage.fromData(QByteArray(BYTES_STRUCTURE))
LAYER_IMAGE = QImage.fromData(QByteArray(BYTES_LAYER))
ELEMENTS_IMAGE = QImage.fromData(QByteArray(BYTES_ELEMENTS))
USER_IMAGE = QImage.fromData(QByteArray(BYTES_USER))
EDIT_IMAGE = QImage.fromData(QByteArray(BYTES_EDIT))
TIP_IMAGE = QImage.fromData(QByteArray(BYTES_TIP))
INDICATOR_IMAGE = QImage.fromData(QByteArray(BYTES_INDICATOR))
FOLDER_IMAGE = QImage.fromData(QByteArray(BYTES_FOLDER))

ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 设置高分辨率
SCALE_FACTOR = ctypes.windll.shcore.GetScaleFactorForDevice(0)  # 获取缩放比例
user32 = ctypes.windll.user32
WIN_WID = user32.GetSystemMetrics(0)  # 获取分辨率
WIN_HEI = user32.GetSystemMetrics(1)  # 获取分辨率
