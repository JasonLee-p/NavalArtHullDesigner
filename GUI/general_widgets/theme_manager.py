# -*- coding: utf-8 -*-
"""
Runtime theme state and persistence helpers.
"""
from copy import deepcopy
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from config_handler import ConfigHandler


class ThemeManager(QObject):
    """
    Holds the active theme and emits a signal when it changes.

    This class does not apply styles to widgets by itself. Custom widgets should
    connect to themeChanged and rebuild their own stylesheets from current.
    """
    themeChanged = pyqtSignal(str, dict)

    def __init__(self, config_handler: Optional[ConfigHandler] = None):
        super().__init__()
        self.config_handler = config_handler or ConfigHandler()
        self._theme_name = self._read_theme_name()
        self._theme = self.config_handler.get_theme_definition(self._theme_name)

    @property
    def name(self) -> str:
        return self._theme_name

    @property
    def current(self) -> dict:
        return deepcopy(self._theme)

    @property
    def ui(self) -> dict:
        return deepcopy(self._theme.get("ui", {}))

    @property
    def render(self) -> dict:
        return deepcopy(self._theme.get("render", {}))

    def color(self, key: str, default=None):
        return self._theme.get("ui", {}).get(key, default)

    def render_color(self, key: str, default=None):
        return self._theme.get("render", {}).get(key, default)

    def list_themes(self) -> list[str]:
        theme_config = self.config_handler.get_config("Theme") or {}
        names = []
        presets = theme_config.get("ThemePresets", {})
        custom_themes = theme_config.get("CustomThemes", {})
        if isinstance(presets, dict):
            names.extend(presets.keys())
        if isinstance(custom_themes, dict):
            names.extend(name for name in custom_themes.keys() if name not in names)
        return names

    def reload(self, emit_signal: bool = True) -> dict:
        self._theme_name = self._read_theme_name()
        self._theme = self.config_handler.get_theme_definition(self._theme_name)
        if emit_signal:
            self.themeChanged.emit(self._theme_name, self.current)
        return self.current

    def set_theme(self, theme_name: str, emit_signal: bool = True) -> dict:
        self._theme = self.config_handler.set_active_theme(theme_name)
        self._theme_name = theme_name
        if emit_signal:
            self.themeChanged.emit(self._theme_name, self.current)
        return self.current

    def save_custom_theme(self, theme_name: str, theme_definition: dict, activate: bool = True,
                          emit_signal: bool = True) -> dict:
        saved_theme = self.config_handler.save_custom_theme(theme_name, theme_definition, activate)
        if activate:
            self._theme_name = theme_name
            self._theme = self.config_handler.get_theme_definition(theme_name)
            if emit_signal:
                self.themeChanged.emit(self._theme_name, self.current)
        return deepcopy(saved_theme)

    def delete_custom_theme(self, theme_name: str, emit_signal: bool = True):
        was_active = theme_name == self._theme_name
        self.config_handler.delete_custom_theme(theme_name)
        if was_active:
            self.reload(emit_signal=emit_signal)

    def _read_theme_name(self) -> str:
        theme_config = self.config_handler.get_config("Theme") or {}
        return theme_config.get("ThemeName", "Night")


_theme_manager: Optional[ThemeManager] = None


def get_theme_manager(config_handler: Optional[ConfigHandler] = None) -> ThemeManager:
    """
    Return the process-wide theme manager.
    """
    global _theme_manager
    if _theme_manager is None or config_handler is not None:
        _theme_manager = ThemeManager(config_handler)
    return _theme_manager

