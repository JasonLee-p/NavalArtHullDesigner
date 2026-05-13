# -*- coding: utf-8 -*-
"""Tests for path helper functions."""
from pathlib import Path

import pytest

from path_lib import increment_path


def test_increment_path_returns_original_when_path_does_not_exist(tmp_path):
    """A non-existing path should not be renamed."""
    target = tmp_path / "design.naprj"

    assert increment_path(target) == str(target)


def test_increment_path_appends_counter_when_path_exists(tmp_path):
    """An existing path should be converted to the first available numbered path."""
    target = tmp_path / "design.naprj"
    target.write_text("existing", encoding="utf-8")

    assert increment_path(target) == str(tmp_path / "design_0000.naprj")


def test_increment_path_skips_existing_numbered_paths(tmp_path):
    """Numbered paths that already exist should be skipped."""
    target = tmp_path / "design.naprj"
    target.write_text("existing", encoding="utf-8")
    (tmp_path / "design_0000.naprj").write_text("existing", encoding="utf-8")

    assert increment_path(target) == str(tmp_path / "design_0001.naprj")
