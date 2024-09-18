# -*- coding: utf-8 -*-
"""
GUI基础参数，包括字体加载器，颜色配置，图片处理等
由于颜色和图标被动态加载，一些变量名例如 BG_COLOR0，BYTES_USER，USER_IMAGE 等是动态生成的，其他模块会在静态检查时报错，但是运行时不会有问题
"""
import ctypes
from base64 import b64decode
import importlib
from typing import List, Optional

from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 静态导入需要的模块
import general_widgets.theme_config_color._day_color as _day_color
import general_widgets.theme_config_color._night_color as _night_color
import GUI.UI_design.ImgPng_day as _ImgPng_day
import GUI.UI_design.ImgPng_night as _ImgPng_night


class LazyFontLoader:
    """
    惰性加载字体，根据字体大小加载字体对象
    惰性加载可以减少内存占用，只有在需要时才加载字体对象
    """
    def __init__(self, font_family, bold=False, italic=False):
        self.font_family = font_family
        self.weight = QFont.Bold if bold else QFont.Normal
        self.italic = italic
        self._cache: List[Optional[QFont]] = [None] * 101  # 预留101个位置，用于存储字体对象

    def _load_font(self, font_size: int):
        """加载字体并存入缓存"""
        font = QFont(self.font_family, font_size, weight=self.weight, italic=self.italic)
        self._cache[font_size] = font
        return font

    def __getitem__(self, size):
        """
        通过索引访问字体，懒加载字体
        如果缓存中已经存在，则直接返回，否则懒加载
        """
        if self._cache[size] is None:
            return self._load_font(size)

        return self._cache[size]


def load_module(module_path):
    """使用 importlib 动态加载模块"""
    return importlib.import_module(module_path)


def process_images(img_module):
    """处理图片，生成 BYTES_... 和 ..._IMAGE 变量，直接加载到全局命名空间"""
    for attr_name in dir(img_module):
        # print(attr_name)
        # 筛选以 "_" 开头的变量
        if not attr_name.startswith('__') and attr_name.startswith('_'):
            # 获取变量的 base64 编码数据
            base64_data = getattr(img_module, attr_name)
            # 生成对应的 BYTES_... 变量名称
            bytes_var_name = f'BYTES{attr_name.upper()}'
            # 对 base64 数据解码为 bytes
            byte_data = b64decode(base64_data)
            # 将 BYTES_... 变量添加到全局命名空间
            globals()[bytes_var_name] = byte_data
            # 生成对应的 ..._IMAGE 变量名称
            image_var_name = f'{attr_name[1:].upper()}_IMAGE'
            # 将 bytes 转换为 QImage
            qimage = QImage.fromData(QByteArray(byte_data))  # noqa
            # 将 ..._IMAGE 变量添加到全局命名空间
            globals()[image_var_name] = qimage


def load_colors(color_module, _theme_details=None):
    """处理颜色配置，生成颜色变量"""
    if _theme_details:
        # 处理自定义主题的颜色
        themeColor = getattr(color_module, 'ThemeColor')
        globals()['BG_COLOR0'] = themeColor(_theme_details["GUITHeme"]["BG_COLOR0"])
        globals()['BG_COLOR1'] = themeColor(_theme_details["GUITHeme"]["BG_COLOR1"])
        globals()['BG_COLOR2'] = themeColor(_theme_details["GUITHeme"]["BG_COLOR2"])
        globals()['BG_COLOR3'] = themeColor(_theme_details["GUITHeme"]["BG_COLOR3"])
        globals()['FG_COLOR0'] = themeColor(_theme_details["GUITHeme"]["FG_COLOR0"])
        globals()['FG_COLOR1'] = themeColor(_theme_details["GUITHeme"]["FG_COLOR1"])
        globals()['GRAY'] = themeColor(_theme_details["GUITHeme"]["GRAY"])
        globals()['GLTheme'] = themeColor(_theme_details["GLTheme"])
    else:
        # 处理默认主题的颜色
        globals()['BG_COLOR0'] = getattr(color_module, 'BG_COLOR0')
        globals()['BG_COLOR1'] = getattr(color_module, 'BG_COLOR1')
        globals()['BG_COLOR2'] = getattr(color_module, 'BG_COLOR2')
        globals()['BG_COLOR3'] = getattr(color_module, 'BG_COLOR3')
        globals()['FG_COLOR0'] = getattr(color_module, 'FG_COLOR0')
        globals()['FG_COLOR1'] = getattr(color_module, 'FG_COLOR1')
        globals()['GRAY'] = getattr(color_module, 'GRAY')
        globals()['GLTheme'] = getattr(color_module, 'GLTheme')


def get_theme_images(theme, _theme_details=None):
    """根据主题加载图标和颜色配置"""
    custom_theme_details = {  # TODO: 将会从配置文件中读取
        "GUITHeme": {
            "BG_COLOR0": "#FFFFFF",
            "BG_COLOR1": "#F0F0F0",
            "BG_COLOR2": "#E0E0E0",
            "BG_COLOR3": "#D0D0D0",
            "FG_COLOR0": "#000000",
            "FG_COLOR1": "#101010",
            "GRAY": "#808080"
        },
        "GLTheme": "#303030"
    }  # 当 theme == 'Custom' 时提供详细的配置信息
    img_module = None
    color_module = None
    if theme in ['Light', 'Day']:
        img_module = _ImgPng_day
        color_module = _day_color
        load_colors(color_module, _theme_details)
    elif theme in ['Dark', 'Night']:
        img_module = _ImgPng_night
        color_module = _night_color
        load_colors(color_module, _theme_details)
    elif theme == 'Custom':
        img_module = _ImgPng_night
        color_module = _night_color
        load_colors(color_module, custom_theme_details)
    globals()['ThemeColor'] = color_module.ThemeColor
    # 动态处理所有图标，直接加载到全局命名空间
    process_images(img_module)


# 实例化不同类型的字体加载器
try:
    YAHEI = LazyFontLoader("Microsoft YaHei")
    HEI = LazyFontLoader("SimHei")
    # 加粗
    BOLD_YAHEI = LazyFontLoader("Microsoft YaHei", bold=True)
    BOLD_HEI = LazyFontLoader("SimHei", bold=True)
    # 斜体
    ITALIC_YAHEI = LazyFontLoader("Microsoft YaHei", italic=True)
    ITALIC_HEI = LazyFontLoader("SimHei", italic=True)
    # 加粗斜体
    BOLD_ITALIC_YAHEI = LazyFontLoader("Microsoft YaHei", bold=True, italic=True)
    BOLD_ITALIC_HEI = LazyFontLoader("SimHei", bold=True, italic=True)
except Exception as e:
    print(e)

# 主要颜色
try:
    from config_handler import ConfigHandler
    configHandler = ConfigHandler()
    theme_details = configHandler.get_config("Theme")
    ThemeName = theme_details["Theme"]["ThemeName"]
except (FileNotFoundError, KeyError, AttributeError):
    ThemeName = 'Night'
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
LIGHTER_RED = '#F76677'  # 可以被用作警告按钮的颜色
LIGHTER_GREEN = '#6DDF6D'  # 可以被用作确认按钮的颜色
LIGHTER_BLUE = '#6D9DDF'
DARKER_RED = '#C00010'
DARKER_GREEN = '#00C000'
DARKER_BLUE = '#0010C0'

get_theme_images(ThemeName, theme_details)

ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 设置高分辨率
SCALE_FACTOR = ctypes.windll.shcore.GetScaleFactorForDevice(0)  # 获取缩放比例
user32 = ctypes.windll.user32
WIN_WID = user32.GetSystemMetrics(0)  # 获取分辨率
WIN_HEI = user32.GetSystemMetrics(1)  # 获取分辨率
