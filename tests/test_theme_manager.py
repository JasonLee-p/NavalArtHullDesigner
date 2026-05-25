# -*- coding: utf-8 -*-
"""Tests for runtime theme manager state and signals."""

from config_handler import ConfigHandler
from GUI.general_widgets.theme_manager import ThemeManager


def make_config_handler():
    handler = ConfigHandler.__new__(ConfigHandler)
    handler._ConfigHandler__config = {
        "Theme": {
            "ThemeName": "Night",
            "ThemePresets": ConfigHandler.DEFAULT_THEME_PRESETS,
            "CustomThemes": {},
        }
    }
    handler.save_config = lambda: None
    return handler


def test_theme_manager_loads_active_theme():
    handler = make_config_handler()

    manager = ThemeManager(handler)

    assert manager.name == "Night"
    assert manager.color("bg0") == "#222324"
    assert manager.render_color("background") == [0.1, 0.1, 0.1, 1.0]


def test_theme_manager_set_theme_emits_signal():
    handler = make_config_handler()
    manager = ThemeManager(handler)
    emitted = []
    manager.themeChanged.connect(lambda name, theme: emitted.append((name, theme)))

    theme = manager.set_theme("Day")

    assert manager.name == "Day"
    assert theme["ui"]["bg0"] == "#fffff0"
    assert emitted[-1][0] == "Day"
    assert emitted[-1][1]["ui"]["bg0"] == "#fffff0"


def test_theme_manager_save_custom_theme_activates_and_emits_signal():
    handler = make_config_handler()
    manager = ThemeManager(handler)
    emitted = []
    manager.themeChanged.connect(lambda name, theme: emitted.append((name, theme)))

    saved = manager.save_custom_theme("Harbor", {"ui": {"bg0": "#101820"}})

    assert manager.name == "Harbor"
    assert saved["ui"]["bg0"] == "#101820"
    assert manager.color("bg0") == "#101820"
    assert handler.get_config("ThemeName") == "Harbor"
    assert emitted[-1][0] == "Harbor"


def test_theme_manager_delete_active_custom_theme_falls_back():
    handler = make_config_handler()
    manager = ThemeManager(handler)
    manager.save_custom_theme("Harbor", {"ui": {"bg0": "#101820"}}, emit_signal=False)
    emitted = []
    manager.themeChanged.connect(lambda name, theme: emitted.append((name, theme)))

    manager.delete_custom_theme("Harbor")

    assert manager.name == "Night"
    assert manager.color("bg0") == "#222324"
    assert emitted[-1][0] == "Night"

