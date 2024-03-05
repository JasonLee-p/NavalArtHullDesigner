# -*- coding: utf-8 -*-
"""
读取配置文件信息，保存配置信息
"""

import ujson
from path_vars import *


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


class ConfigHandler:
    DEFAULT_CONFIG = {
        "Config": {
            "Language": "Chinese",
            "Sensitivity": {
                "缩放": 50,
                "旋转": 50,
                "平移": 50
            },
            "FramePosition": {
                "User": "bottom",
                "Edit": "right",
                "Structure": "left"
            },
            "CheckUpdate": True,
            "Guided": False,
            "ExitAfterClosingEditor": False
        },
        "Theme": {
            "ThemeName": "Night",
            "GUITHeme": {
                "BG_COLOR0": "#222324",
                "BG_COLOR1": "#333434",
                "BG_COLOR2": "#555657",
                "BG_COLOR3": "#666789",
                "FG_COLOR0": "#f0f0f0",
                "FG_COLOR1": "#ffaaaa",
                "GRAY": "#707070"
            },
            "GLTheme": {
                "背景": (0.1, 0.1, 0.1, 1),
                "主光源": [(0.4, 0.4, 0.4, 1.0), (0.55, 0.55, 0.55, 1.0), (0.45, 0.47, 0.47, 1.0)],
                "辅助光": [(0.3, 0.3, 0.3, 1.0), (0.3, 0.3, 0.3, 1.0), (0.3, 0.3, 0.3, 1.0)],
                "选择框": [(1, 1, 1, 1)],
                "被选中": [(0.0, 0.7, 0.7, 1)],
                "橙色": [(1, 0.9, 0.5, 1.0)],
                "节点": [(0.0, 0.8, 0.8, 1)],
                "线框": [(0.7, 0.7, 0.7, 0.6), (0.2, 0.25, 0.3, 0.6), (0.2, 0.25, 0.3, 0.5), (0,)],
                "水线": [(0.0, 0.7, 0.7, 0.6), (0.3, 0.4, 0.5, 0.6), (0.2, 0.25, 0.3, 0.2), (50,)],
                "钢铁": [(0.4, 0.4, 0.4, 1.0)],
                "半透明": [(1, 1, 1, 0.15)],
                "甲板": [(0.46, 0.43, 0.39, 1.0), (0.15, 0.17, 0.17, 1.0), (0, 0, 0, 0.2), (0,)],
                "海面": [(0.3, 0.6, 0.7, 0.7)],
                "海底": [(0.09, 0.08, 0.05, 1)],
                "光源": [(1.0, 1.0, 1.0, 1.0)]
            }
        },
        "Projects": {
            # "KMS Hindenburg": "C:\/Users\/dlzx\/AppData\/LocalLow\/RZEntertainment\/NavalArt\/HullProjects\/KMS Hindenburg.naprj"
        },
        # "ProjectsFolder": f"C:\/Users\/dlzx\/AppData\/LocalLow\/RZEntertainment\/NavalArt\/HullProjects"
        "ProjectsFolder": os.path.join(NA_ROOT_PATH, 'HullProjects')
    }

    def __init__(self):
        self.__config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    self.__config = ujson.load(f)
                    # 和默认配置合并，递归地检查每一层字典的键，优先使用用户配置
                    dict_changed = merge_dict(self.__config, self.DEFAULT_CONFIG)
                    if dict_changed:
                        self.save_config()
            except ValueError and KeyError:
                self.__config = self.DEFAULT_CONFIG
                self.save_config()
        else:
            self.__config = self.DEFAULT_CONFIG
            self.save_config()

    def save_config(self):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            ujson.dump(self.__config, f, ensure_ascii=False, indent=2)

    def get_config(self, key: str):
        if key in self.__config:
            return self.__config[key]
        elif key in self.__config["Config"]:
            return self.__config["Config"][key]
        elif key in self.__config["Theme"]:
            return self.__config["Theme"][key]
        elif key in self.__config["Theme"]["GUITHeme"]:
            return self.__config["Theme"]["GUITHeme"][key]
        elif key in self.__config["THeme"]["GLTheme"]:
            return self.__config["Theme"]["GLTheme"][key]

    def set_config(self, key: str, value):
        """
        只修改内存中的配置，不保存到文件
        :param key: 配置键
        :param value: 配置值
        """
        if key in self.__config:
            self.__config[key] = value
        elif key in self.__config["Config"]:
            self.__config["Config"][key] = value
        elif key in self.__config["Theme"]:
            self.__config["Theme"][key] = value
        elif key in self.__config["Theme"]["GUITHeme"]:
            self.__config["Theme"]["GUITHeme"][key] = value
        elif key in self.__config["THeme"]["GLTheme"]:
            self.__config["Theme"]["GLTheme"][key] = value
        return value
