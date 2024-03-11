# -*- coding: utf-8 -*-
"""
着色器代码
"""
import os
from path_vars import CURRENT_PATH


__vs_file_dir = os.path.join(CURRENT_PATH, "shaders", "VERTEX_SHADER.glsl")
__fs_file_dir = os.path.join(CURRENT_PATH, "shaders", "FRAGMENT_SHADER.glsl")

with open(__vs_file_dir, "r", encoding="utf-8") as f:
    VERTEX_SHADER = f.read()

with open(__fs_file_dir, "r", encoding="utf-8") as f:
    FRAGMENT_SHADER = f.read()
