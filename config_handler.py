# -*- coding: utf-8 -*-
"""
读取配置文件信息，保存配置信息
"""

import ujson
from utils.funcs_utils import merge_dict
from main_logger import Log
from path_lib import *


class ConfigHandler:
    """
    读取配置文件信息，保存配置信息
    """
    TAG = "CONFIG"
    THEME_SCHEMA_VERSION = 1

    DEFAULT_THEME_PRESETS = {
        "Night": {
            "ui": {
                "bg0": "#222324",
                "bg1": "#333434",
                "bg2": "#555657",
                "bg3": "#666789",
                "fg0": "#f0f0f0",
                "fg1": "#ffaaaa",
                "muted": "#707070",
                "danger": "#F76677",
                "success": "#6DDF6D",
                "accent": "#6D9DDF",
                "danger_strong": "#C00010",
                "link_hover": "#00FFFF",
                "brand_panel_bg": "#889998",
                "color_picker_red_hint": "#FFCCCC",
                "color_picker_green_hint": "#CCFFCC",
                "color_picker_blue_hint": "#CCCCFF"
            },
            "render": {
                "background": [0.1, 0.1, 0.1, 1.0],
                "key_light_ambient": [0.6, 0.6, 0.6],
                "key_light_diffuse": [0.7, 0.7, 0.7],
                "key_light_specular": [0.95, 0.95, 0.95],
                "grid_line": [0.3, 0.8, 1.0, 1.0],
                "selected_overlay": [0.1, 0.9, 1.0, 0.3],
                "mesh_line": [0.0, 0.0, 0.0, 0.2],
                "stretch_arrow": [1.0, 1.0, 0.0],
                "node_marker": [0.15, 0.95, 1.0]
            }
        },
        "Day": {
            "ui": {
                "bg0": "#fffff0",
                "bg1": "#f5f5dc",
                "bg2": "#ddddc6",
                "bg3": "#d2c08c",
                "fg0": "#101010",
                "fg1": "#b22222",
                "muted": "#bcb9b0",
                "danger": "#F76677",
                "success": "#6DDF6D",
                "accent": "#6D9DDF",
                "danger_strong": "#C00010",
                "link_hover": "#00FFFF",
                "brand_panel_bg": "#889998",
                "color_picker_red_hint": "#FFCCCC",
                "color_picker_green_hint": "#CCFFCC",
                "color_picker_blue_hint": "#CCCCFF"
            },
            "render": {
                "background": [0.9, 0.95, 1.0, 1.0],
                "key_light_ambient": [0.6, 0.6, 0.6],
                "key_light_diffuse": [0.7, 0.7, 0.7],
                "key_light_specular": [0.95, 0.95, 0.95],
                "grid_line": [0.3, 0.8, 1.0, 1.0],
                "selected_overlay": [0.1, 0.9, 1.0, 0.3],
                "mesh_line": [0.0, 0.0, 0.0, 0.2],
                "stretch_arrow": [1.0, 1.0, 0.0],
                "node_marker": [0.15, 0.95, 1.0]
            }
        }
    }

    LEGACY_UI_KEY_MAP = {
        "BG_COLOR0": "bg0",
        "BG_COLOR1": "bg1",
        "BG_COLOR2": "bg2",
        "BG_COLOR3": "bg3",
        "FG_COLOR0": "fg0",
        "FG_COLOR1": "fg1",
        "GRAY": "muted",
    }

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
            "ThemeSchemaVersion": THEME_SCHEMA_VERSION,
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
            },
            "ThemePresets": DEFAULT_THEME_PRESETS,
            "CustomThemes": {}
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
                Log().info(self.TAG, "成功加载配置文件")
            except ValueError and KeyError as _:
                self.__config = self.DEFAULT_CONFIG
                self.save_config()
                Log().warning(self.TAG, "配置文件未初始化或损坏，已重置为默认配置")

        else:
            self.__config = self.DEFAULT_CONFIG
            self.save_config()

    def save_config(self):
        """
        保存配置文件
        """
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                ujson.dump(self.__config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            Log().error(self.TAG, f"保存配置文件失败：{e}")

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
                    result = self._get_key__(v, key)
                    if result is not None:
                        return result
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

    @classmethod
    def _merge_theme_definition(cls, theme_definition: dict) -> dict:
        """
        Merge a partial theme definition with Night defaults.
        """
        merged = ujson.loads(ujson.dumps(cls.DEFAULT_THEME_PRESETS["Night"]))
        if not isinstance(theme_definition, dict):
            return merged
        for section in ("ui", "render"):
            if isinstance(theme_definition.get(section), dict):
                merged[section].update(theme_definition[section])
        return merged

    @classmethod
    def _theme_from_legacy_config(cls, theme_config: dict) -> dict:
        """
        Convert legacy GUITHeme values to the functional theme key names.
        """
        if not isinstance(theme_config, dict):
            return cls._merge_theme_definition({})
        theme = cls._merge_theme_definition({})
        legacy_ui = theme_config.get("GUITHeme", {})
        if isinstance(legacy_ui, dict):
            for old_key, new_key in cls.LEGACY_UI_KEY_MAP.items():
                if old_key in legacy_ui:
                    theme["ui"][new_key] = legacy_ui[old_key]
        return theme

    def get_theme_definition(self, theme_name: str = None) -> dict:
        """
        Return a merged theme definition by name.
        Presets and custom themes share one namespace; custom themes win on name collision.
        """
        theme_config = self.__config.setdefault("Theme", {})
        theme_name = theme_name or theme_config.get("ThemeName", "Night")
        presets = theme_config.get("ThemePresets", {})
        custom_themes = theme_config.get("CustomThemes", {})
        if isinstance(custom_themes, dict) and theme_name in custom_themes:
            return self._merge_theme_definition(custom_themes[theme_name])
        if isinstance(presets, dict) and theme_name in presets:
            return self._merge_theme_definition(presets[theme_name])
        return self._theme_from_legacy_config(theme_config)

    def save_custom_theme(self, theme_name: str, theme_definition: dict, activate: bool = True):
        """
        Save a custom theme into the config file.
        The definition may be partial; missing fields are filled from Night defaults when read.
        """
        if not isinstance(theme_name, str) or not theme_name.strip():
            raise ValueError("theme_name must be a non-empty string.")
        theme_name = theme_name.strip()
        theme_config = self.__config.setdefault("Theme", {})
        theme_config["ThemeSchemaVersion"] = self.THEME_SCHEMA_VERSION
        theme_config.setdefault("ThemePresets", self.DEFAULT_THEME_PRESETS)
        custom_themes = theme_config.setdefault("CustomThemes", {})
        custom_themes[theme_name] = self._merge_theme_definition(theme_definition)
        if activate:
            theme_config["ThemeName"] = theme_name
        self.save_config()
        return custom_themes[theme_name]

    def set_active_theme(self, theme_name: str):
        """
        Set the active theme by preset or custom theme name and save the config file.
        """
        theme_config = self.__config.setdefault("Theme", {})
        presets = theme_config.get("ThemePresets", {})
        custom_themes = theme_config.get("CustomThemes", {})
        if theme_name not in presets and theme_name not in custom_themes:
            raise KeyError(f"Theme '{theme_name}' not found.")
        theme_config["ThemeName"] = theme_name
        self.save_config()
        return self.get_theme_definition(theme_name)

    def delete_custom_theme(self, theme_name: str):
        """
        Delete a custom theme and fall back to Night if it was active.
        """
        theme_config = self.__config.setdefault("Theme", {})
        custom_themes = theme_config.setdefault("CustomThemes", {})
        if theme_name not in custom_themes:
            raise KeyError(f"Custom theme '{theme_name}' not found.")
        del custom_themes[theme_name]
        if theme_config.get("ThemeName") == theme_name:
            theme_config["ThemeName"] = "Night"
        self.save_config()

    def add_prj(self, prj_name, prj_path):
        """
        添加项目，保存配置
        """
        # 如果字典里已经有了这个项目，就先删除再添加，若没有则直接添加，保证项目在字典的最后
        self.__config["Projects"].pop(prj_name, None)
        self.__config["Projects"][prj_name] = prj_path
        self.save_config()
        Log().info(self.TAG, f"更新最新项目：{prj_name}")

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
                    if self._set_key__(v, key, value):
                        return True
        return False
