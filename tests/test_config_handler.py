# -*- coding: utf-8 -*-
"""Regression tests for configuration loading and nested key access."""

import pytest

from config_handler import ConfigHandler
from utils.funcs_utils import merge_dict


def test_merge_dict_keeps_existing_user_scalar_values():
    """Default config values should fill missing keys without overwriting user values."""
    user_config = {
        "Config": {
            "Language": "English",
        }
    }
    default_config = {
        "Config": {
            "Language": "Chinese",
            "CheckUpdate": True,
        }
    }

    changed = merge_dict(user_config, default_config)

    assert changed is True
    assert user_config["Config"]["Language"] == "English"
    assert user_config["Config"]["CheckUpdate"] is True


def test_get_config_searches_all_nested_dicts():
    """Nested key lookup should continue after the first nested dictionary misses."""
    handler = ConfigHandler.__new__(ConfigHandler)
    handler._ConfigHandler__config = {
        "Config": {
            "Language": "Chinese",
        },
        "Theme": {
            "ThemeName": "Night",
        },
        "Projects": {
            "Demo": "demo.naprj",
        },
    }

    assert handler.get_config("ThemeName") == "Night"
    assert handler.get_config("Demo") == "demo.naprj"


def test_set_config_searches_all_nested_dicts():
    """Nested key assignment should continue after the first nested dictionary misses."""
    handler = ConfigHandler.__new__(ConfigHandler)
    handler._ConfigHandler__config = {
        "Config": {
            "Language": "Chinese",
        },
        "Theme": {
            "ThemeName": "Night",
        },
    }

    handler.set_config("ThemeName", "Day")

    assert handler._ConfigHandler__config["Theme"]["ThemeName"] == "Day"


def test_get_theme_definition_maps_legacy_gui_theme_keys():
    """Legacy GUITHeme colors should be exposed with functional theme keys."""
    handler = ConfigHandler.__new__(ConfigHandler)
    handler._ConfigHandler__config = {
        "Theme": {
            "ThemeName": "LegacyOnly",
            "GUITHeme": {
                "BG_COLOR0": "#010203",
                "FG_COLOR0": "#aabbcc",
                "GRAY": "#333333",
            },
        }
    }

    theme = handler.get_theme_definition()

    assert theme["ui"]["bg0"] == "#010203"
    assert theme["ui"]["fg0"] == "#aabbcc"
    assert theme["ui"]["muted"] == "#333333"
    assert "grid_line" in theme["render"]


def test_save_custom_theme_merges_defaults_and_activates():
    """Custom themes may be partial and are saved under Theme.CustomThemes."""
    handler = ConfigHandler.__new__(ConfigHandler)
    handler._ConfigHandler__config = {"Theme": {}}
    handler.save_config = lambda: None

    saved = handler.save_custom_theme(
        "Ocean",
        {
            "ui": {"bg0": "#001122", "accent": "#44ccff"},
            "render": {"background": [0.0, 0.05, 0.08, 1.0]},
        },
    )

    theme_config = handler._ConfigHandler__config["Theme"]
    assert theme_config["ThemeName"] == "Ocean"
    assert theme_config["CustomThemes"]["Ocean"] == saved
    assert saved["ui"]["bg0"] == "#001122"
    assert saved["ui"]["accent"] == "#44ccff"
    assert saved["ui"]["fg0"] == "#f0f0f0"
    assert saved["render"]["background"] == [0.0, 0.05, 0.08, 1.0]
    assert saved["render"]["selected_overlay"] == [0.1, 0.9, 1.0, 0.3]


def test_set_active_theme_accepts_preset_and_custom_theme():
    """Active theme can point to a built-in preset or a saved custom theme."""
    handler = ConfigHandler.__new__(ConfigHandler)
    handler._ConfigHandler__config = {
        "Theme": {
            "ThemePresets": ConfigHandler.DEFAULT_THEME_PRESETS,
            "CustomThemes": {"Ocean": {"ui": {"bg0": "#001122"}}},
        }
    }
    handler.save_config = lambda: None

    ocean = handler.set_active_theme("Ocean")
    assert handler._ConfigHandler__config["Theme"]["ThemeName"] == "Ocean"
    assert ocean["ui"]["bg0"] == "#001122"

    day = handler.set_active_theme("Day")
    assert handler._ConfigHandler__config["Theme"]["ThemeName"] == "Day"
    assert day["ui"]["bg0"] == "#fffff0"
