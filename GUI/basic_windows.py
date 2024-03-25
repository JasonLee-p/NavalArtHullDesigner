# -*- coding: utf-8 -*-
"""
窗口基类
"""

import numpy as np
from .basic_widgets import *


def rotate_object(angle: float, axis: Union[list, tuple, np.ndarray]):
    # 旋转矩阵
    c = np.cos(np.radians(angle))
    s = np.sin(np.radians(angle))
    x, y, z = axis
    rotation_matrix = np.array([
        [c + x ** 2 * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s, 0.0],
        [y * x * (1 - c) + z * s, c + y ** 2 * (1 - c), y * z * (1 - c) - x * s, 0.0],
        [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z ** 2 * (1 - c), 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ])
    return rotation_matrix


class MessageBox(QDialog):
    def __init__(self, message, msg_type):
        super().__init__()
        self.setWindowTitle("错误")
        self.setWindowIcon(QIcon(QPixmap(ICO_IMAGE)))
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setFixedSize(300, 150)
        self.message = message
        self.msg_type = msg_type
        self.init_ui()
        color_print(f"[ERROR] {message}", "red")

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(TextLabel(self, self.message))
        self.main_layout.addWidget(EnsureButton(self))
        self.main_layout.addWidget(CancelButton(self))
        self.show()


class LoadingWindow(Window):
    def __init__(self):
        ...
