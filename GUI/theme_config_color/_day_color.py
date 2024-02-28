from PyQt5.QtGui import *


class ThemeColor:
    def __init__(self, color: str):
        self.color = color

    def __str__(self):
        return self.color

    def __repr__(self):
        return self.color

    @property
    def rgb(self):
        if self.color[0] == '#':
            return int(self.color[1:3], 16), int(self.color[3:5], 16), int(self.color[5:7], 16)
        else:
            # 是一个颜色名，例如：'red'
            return QColor(self.color).getRgb()[:3]


THEME: str = 'day'
BG_COLOR0 = ThemeColor('#fffff0')
BG_COLOR1 = ThemeColor('#f5f5dC')
BG_COLOR2 = ThemeColor('#ddddc6')
BG_COLOR3 = ThemeColor('#d2c08c')
FG_COLOR0 = ThemeColor('#101010')
FG_COLOR1 = ThemeColor('#b22222')
GRAY = ThemeColor('#bcb9b0')

GLTheme = {
    "背景": (0.9, 0.95, 1.0, 1.0),
    "主光源": [(0.75, 0.75, 0.75, 1.0), (0.75, 0.75, 0.75, 1.0), (0.58, 0.58, 0.5, 1.0)],
    "辅助光": [(0.2, 0.2, 0.2, 1.0), (0.1, 0.1, 0.1, 1.0), (0.2, 0.2, 0.2, 1.0)],
    "选择框": [(0, 0, 0, 0.95)],
    "被选中": [(0.0, 0.6, 0.6, 1)],
    "橙色": [(1.0, 0.3, 0.0, 1)],
    "节点": [(0.0, 0.4, 1.0, 1)],
    "线框": [(0, 0, 0, 0.8)],
    "水线": [(0.0, 1.0, 1.0, 0.6)],
    "钢铁": [(0.24, 0.24, 0.24, 1.0)],
    "半透明": [(0.2, 0.2, 0.2, 0.1)],
    "甲板": [(0.6, 0.56, 0.52, 1.0), (0.2, 0.2, 0.16, 1.0), (0.03, 0.025, 0.02, 0.2), (0,)],
    "海面": [(0.0, 0.2, 0.3, 0.3)],
    "海底": [(0.18, 0.16, 0.1, 0.9)],
    "光源": [(1.0, 1.0, 1.0, 1.0)]
}
