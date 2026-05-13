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
