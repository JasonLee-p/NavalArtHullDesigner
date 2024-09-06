# -*- coding: utf-8 -*-
"""
读取配置文件信息，保存配置信息
"""

import ujson
from utils.funcs_utils import merge_dict
from path_lib import *


class ConfigHandler:
    """
    读取配置文件信息，保存配置信息
    """
    DEFAULT_CONFIG = {  # 默认配置
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
            "ExitAfterClosingEditor": False,
            "OperationStackMaxLength": 10000
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
        "FindModelFolder": os.path.join(NA_ROOT_PATH, 'HullProjects'),
        # "ProjectsFolder": f"C:\/Users\/dlzx\/AppData\/LocalLow\/RZEntertainment\/NavalArt\/HullProjects"
        "ProjectsFolder": os.path.join(NA_ROOT_PATH, 'HullProjects'),
        "ModelRenderSetting": {
            "ModelDrawLine": True,
            "ModelLineWith": 0.6,
            "ModelLineColor": [0.0, 0.0, 0.0, 0.2]
        }
    }

    def __init__(self):
        self.__config = {}
        self.load_config()

    def load_config(self):
        """
        寻找配置文件，若不存在则创建默认配置文件
        """
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    self.__config = ujson.load(f)
                    # 和默认配置合并，递归地检查每一层字典的键，优先使用用户配置
                    dict_changed = merge_dict(self.__config, self.DEFAULT_CONFIG)
                    if dict_changed:
                        self.save_config()
            except ValueError and KeyError as _:
                self.__config = self.DEFAULT_CONFIG
                self.save_config()
        else:
            self.__config = self.DEFAULT_CONFIG
            self.save_config()

    def save_config(self):
        """
        保存配置文件
        """
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            ujson.dump(self.__config, f, ensure_ascii=False, indent=2)

    def get_config(self, key: str):
        """
        根据键值获取配置信息
        """
        return self._get_key__(self.__config, key)

    def _get_key__(self, dict_, key):
        """
        递归获取键值，若键值不存在则返回None
        """
        if key in dict_:
            return dict_[key]
        else:
            for k, v in dict_.items():
                if isinstance(v, dict):
                    return self._get_key__(v, key)
        return None

    def set_config(self, key: str, value, new_key=False):
        """
        只修改内存中的配置，不保存到文件
        :param key: 配置键
        :param value: 配置值
        :param new_key: 若配置键不存在，是否创建新键
        """
        if new_key:
            self.__config[key] = value
        else:
            succeed = self._set_key__(self.__config, key, value)
            if not succeed:
                raise KeyError(f"Config key '{key}' not found.")
        return value

    def add_prj(self, prj_name, prj_path):
        """
        添加项目，保存配置
        """
        self.__config["Projects"][prj_name] = prj_path
        self.save_config()

    def _set_key__(self, dict_, key, value):
        """
        递归设置键值，若键值不存在则返回False
        """
        if key in dict_:
            dict_[key] = value
            return True
        else:
            for k, v in dict_.items():
                if isinstance(v, dict):
                    return self._set_key__(v, key, value)
        return False
