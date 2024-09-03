# -*- coding: utf-8 -*-
"""
各类按钮
"""
from .other_widgets import *
from ..basic_data import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def _set_buttons(
        buttons, sizes, font=YAHEI[10], border=0, bd_color=FG_COLOR0,
        bd_radius: Union[int, Tuple[int, int, int, int]] = 7, padding=0,
        bg: Union[str, ThemeColor, tuple] = (BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3),
        fg=FG_COLOR0
):
    """
    设置按钮样式
    :param buttons: 按钮列表
    :param sizes:
    :param font: QFont对象
    :param border: 边框宽度
    :param bd_color: 边框颜色
    :param bd_radius: 边框圆角
    :param padding: 内边距
    :param bg: 按钮背景颜色
    :param fg: 按钮字体颜色
    :return:
    """
    buttons = list(buttons)
    if isinstance(bd_radius, int):
        bd_radius = (bd_radius, bd_radius, bd_radius, bd_radius)
    if type(sizes[0]) in [int, None]:
        sizes = [sizes] * len(buttons)
    if border != 0:
        border_text = f"{border}px solid {bd_color}"
    else:
        border_text = "none"
    if isinstance(padding, int):
        padding = (padding, padding, padding, padding)
    if isinstance(bg, (str, ThemeColor)):
        bg = (bg, bg, bg, bg)
    if isinstance(fg, (str, ThemeColor)):
        fg = (fg, fg, fg, fg)
    for button in buttons:
        if sizes[buttons.index(button)][0] is None:
            # 宽度拉伸
            button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            button.setFixedHeight(sizes[buttons.index(button)][1])
        elif sizes[buttons.index(button)][1] is None:
            # 高度拉伸
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
            button.setFixedWidth(sizes[buttons.index(button)][0])
        else:
            button.setFixedSize(*sizes[buttons.index(button)])
        button.setFont(font)
        button.setStyleSheet(f"""
            QPushButton{{
                background-color:{bg[0]};
                color:{fg[0]};
                border-top-left-radius: {bd_radius[0]}px;
                border-top-right-radius: {bd_radius[1]}px;
                border-bottom-right-radius: {bd_radius[2]}px;
                border-bottom-left-radius: {bd_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
            QPushButton:hover{{
                background-color:{bg[1]};
                color:{fg[1]};
                border-top-left-radius: {bd_radius[0]}px;
                border-top-right-radius: {bd_radius[1]}px;
                border-bottom-right-radius: {bd_radius[2]}px;
                border-bottom-left-radius: {bd_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
            QPushButton::pressed{{
                background-color:{bg[2]};
                color:{fg[2]};
                border-top-left-radius: {bd_radius[0]}px;
                border-top-right-radius: {bd_radius[1]}px;
                border-bottom-right-radius: {bd_radius[2]}px;
                border-bottom-left-radius: {bd_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
            QPushButton::focus{{
                background-color:{bg[3]};
                color:{fg[3]};
                border-top-left-radius: {bd_radius[0]}px;
                border-top-right-radius: {bd_radius[1]}px;
                border-bottom-right-radius: {bd_radius[2]}px;
                border-bottom-left-radius: {bd_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
        """)


class Button(QPushButton):

    def __init__(
            self, parent,
            tool_tip: str = None,
            bd: Union[int, Tuple[int, int, int, int]] = 0,
            bd_color: Union[str, ThemeColor, Tuple[str, str, str, str]] = FG_COLOR0,
            bd_radius: Union[int, Tuple[int, int, int, int]] = 0,
            padding: Union[int, Tuple[int, int, int, int]] = 0,
            bg: Union[str, ThemeColor, Tuple[str, str, str, str]] = (BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3),
            fg: Union[str, ThemeColor, Tuple[str, str, str, str]] = FG_COLOR0,
            font=YAHEI[6],
            align=Qt.AlignCenter,
            size: Union[int, Tuple[int, int], None] = (60, 26),
            alpha=1.0,
            show_indicator: Union[bool, str] = False,
            focus_policy=None
    ):
        """

        :param parent: 父控件
        :param tool_tip: 提示
        :param bd: 边框宽度
        :param bd_color: 边框颜色
        :param bd_radius: 边框圆角
        :param padding: 内边距
        :param bg: 背景颜色：[正常，悬停，按下，焦点]
        :param fg: 字体颜色：[正常，悬停，按下，焦点]
        :param font: 字体
        :param align: 对齐
        :param size: 大小
        :param alpha: 透明度
        :param show_indicator: 是否显示指示器
        :param focus_policy: 焦点策略
        """
        super().__init__(parent)
        # 处理参数
        if bd != 0:
            bd_text = f"{bd}px solid {bd_color}"
        else:
            bd_text = "none"
        if isinstance(bd_radius, int):
            bd_radius = [bd_radius] * 4
        if isinstance(bg, str):
            r, g, b = ThemeColor(bg).rgb
            bg = f"rgba({r}, {g}, {b}, {alpha})"
            bg = [bg] * 4
        elif isinstance(bg, ThemeColor):
            r, g, b = bg.rgb
            bg = f"rgba({r}, {g}, {b}, {alpha})"
            bg = [bg] * 4
        if isinstance(fg, (str, ThemeColor)):
            fg = [fg] * 4
        if isinstance(padding, int):
            padding = [padding] * 4
        if isinstance(size, int):
            size = (size, size)
        self.align = align  # TODO
        self.setFont(font)
        # 属性
        self.bg = bg
        self.fg = fg
        self.bd_radius = bd_radius
        self.padding = padding
        self._bd_text = bd_text
        self.alpha = alpha
        self.show_indicator = show_indicator
        # 设置样式
        self.set_style()
        if size:
            self.setFixedSize(size[0], size[1])
        if tool_tip:
            self.setToolTip(tool_tip)
            self.setToolTipDuration(5000)
        if focus_policy:
            self.setFocusPolicy(focus_policy)
        else:
            self.setFocusPolicy(Qt.NoFocus)

    def set_style(self):
        indicator_styleSheet = f"""
            QPushButton::menu-indicator{{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 0px;
                height: 0px;
            }}
        """
        if self.show_indicator is False:
            pass
        elif self.show_indicator is True:
            indicator_styleSheet = f"""
            """
        else:
            indicator_styleSheet = f"""
                QPushButton::menu-indicator{{
                    image: url({QPixmap(INDICATOR_IMAGE).toImage()});
                }}
            """
        self.setStyleSheet(f"""
            QPushButton{{
                background-color:{self.bg[0]};
                color:{self.fg[0]};
                border-top-left-radius: {self.bd_radius[0]}px;
                border-top-right-radius: {self.bd_radius[1]}px;
                border-bottom-right-radius: {self.bd_radius[2]}px;
                border-bottom-left-radius: {self.bd_radius[3]}px;
                border: {self._bd_text};
                padding: {self.padding[0]}px {self.padding[1]}px {self.padding[2]}px {self.padding[3]}px;
            }}
            QPushButton:hover{{
                background-color:{self.bg[1]};
                color:{self.fg[1]};
                border-top-left-radius: {self.bd_radius[0]}px;
                border-top-right-radius: {self.bd_radius[1]}px;
                border-bottom-right-radius: {self.bd_radius[2]}px;
                border-bottom-left-radius: {self.bd_radius[3]}px;
                border: {self._bd_text};
                padding: {self.padding[0]}px {self.padding[1]}px {self.padding[2]}px {self.padding[3]}px;
            }}
            QPushButton::pressed{{
                background-color:{self.bg[2]};
                color:{self.fg[2]};
                border-top-left-radius: {self.bd_radius[0]}px;
                border-top-right-radius: {self.bd_radius[1]}px;
                border-bottom-right-radius: {self.bd_radius[2]}px;
                border-bottom-left-radius: {self.bd_radius[3]}px;
                border: {self._bd_text};
                padding: {self.padding[0]}px {self.padding[1]}px {self.padding[2]}px {self.padding[3]}px;
            }}
            QPushButton::focus{{
                background-color:{self.bg[3]};
                color:{self.fg[3]};
                border-top-left-radius: {self.bd_radius[0]}px;
                border-top-right-radius: {self.bd_radius[1]}px;
                border-bottom-right-radius: {self.bd_radius[2]}px;
                border-bottom-left-radius: {self.bd_radius[3]}px;
                border: {self._bd_text};
                padding: {self.padding[0]}px {self.padding[1]}px {self.padding[2]}px {self.padding[3]}px;
            }}
            QPushButton::disabled{{
                background-color:{self.bg[0]};
                color: {GRAY};
                border-top-left-radius: {self.bd_radius[0]}px;
                border-top-right-radius: {self.bd_radius[1]}px;
                border-bottom-right-radius: {self.bd_radius[2]}px;
                border-bottom-left-radius: {self.bd_radius[3]}px;
                border: 1px solid {GRAY};
                padding: {self.padding[0]}px {self.padding[1]}px {self.padding[2]}px {self.padding[3]}px;
            }}
            QPushButton::checked{{
                background-color:{self.bg[2]};
                color:{self.fg[2]};
                border-top-left-radius: {self.bd_radius[0]}px;
                border-top-right-radius: {self.bd_radius[1]}px;
                border-bottom-right-radius: {self.bd_radius[2]}px;
                border-bottom-left-radius: {self.bd_radius[3]}px;
                border: {self._bd_text};
                padding: {self.padding[0]}px {self.padding[1]}px {self.padding[2]}px {self.padding[3]}px;
            }}
            {indicator_styleSheet}
            QToolTip {{
                background-color: {self.bg[0]};
                color: {self.fg[0]};
                border: 1px solid {self.fg[1]};
                border-radius: 4px;
            }}
        """)

    def reset_theme(self, theme_data):
        """
        重置主题
        :param theme_data:
        {
            'THEME': 'day'
            'BG_COLOR0': 'beige'
            'BG_COLOR1': 'ivory'
            'BG_COLOR2': '#f0f0ff'
            'BG_COLOR3': 'tan'
            'FG_COLOR0': 'black'
            'FG_COLOR1': 'firebrick'
            'FG_COLOR2': 'gray'
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
        :return:
        """


class TextButton(Button):
    def __init__(
            self, parent,
            text: str = '',
            tool_tip: str = None,
            bd: Union[int, Tuple[int, int, int, int]] = 0,
            bd_color: Union[str, ThemeColor, Tuple[str, str, str, str]] = FG_COLOR0,
            bd_radius: Union[int, Tuple[int, int, int, int]] = 0,
            padding: Union[int, Tuple[int, int, int, int]] = 0,
            bg: Union[str, ThemeColor, Tuple[str, str, str, str]] = BG_COLOR0,
            fg: Union[str, ThemeColor, Tuple[str, str, str, str]] = FG_COLOR0,
            font=YAHEI[6],
            align=Qt.AlignCenter,
            size: Union[int, Tuple[int, int]] = (60, 26),
            _set_text: bool = True
    ):
        self.text = text
        # 设置样式
        if _set_text:
            self.setText(text)
        super().__init__(parent, tool_tip, bd, bd_color, bd_radius, padding, bg, fg, font, align, size)


class ImageButton(QPushButton):
    def __init__(self, parent, img_bytes: bytes, img_size: Union[int, Tuple[int, int]], bd_radius: int = 0,
                 bg: Union[ThemeColor, str] = BG_COLOR0, tool_tip=None):
        super().__init__(parent)
        # 处理参数
        if isinstance(img_size, int):
            self.width, self.height = img_size, img_size
        else:
            self.width, self.height = img_size[0], img_size[1]
        self.img_bytes = img_bytes
        self.bd_radius = bd_radius
        self.bg = bg

        img = QPixmap(QImage.fromData(QByteArray(self.img_bytes)))  # noqa
        img.scaled(self.width, self.height, Qt.KeepAspectRatio)
        rounded_img = QPixmap(self.width, self.height)
        rounded_img.fill(Qt.transparent)
        painter = QPainter(rounded_img)
        painter.setRenderHint(QPainter.Antialiasing)
        # 创建一个椭圆路径来表示圆角
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, self.bd_radius, self.bd_radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, img)
        painter.end()
        self.setPixmap(rounded_img)
        self.setStyleSheet(
            f"background-color: {self.bg};"
            f"border-radius: {self.bd_radius}px;"
        )
        self.setFixedSize(self.width, self.height)
        if tool_tip:
            self.setToolTip(tool_tip)
            self.setToolTipDuration(5000)


class MaximizeButton(Button):
    def __init__(self, parent, size=(55, 36), bd_radius: Union[int, Tuple[int, int, int, int]] = 0):
        super().__init__(parent, None, 0, BG_COLOR0,
                         bd_radius, 0,
                         (BG_COLOR1, GRAY, BG_COLOR1, BG_COLOR1), FG_COLOR0, YAHEI[6], Qt.AlignCenter,
                         size)
        self.setIcon(QIcon(QPixmap(MAXIMIZE_IMAGE)))
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(False)
        # 绑定点击事件
        self.clicked.connect(self.clicked_action)

    def clicked_action(self):
        if self.parent().isMaximized():
            self.setIcon(QIcon(QPixmap(MAXIMIZE_IMAGE)))
        else:
            self.setIcon(QIcon(QPixmap(NORMAL_IMAGE)))


class MinimizeButton(Button):
    def __init__(self, parent, size=(55, 36), bd_radius: Union[int, Tuple[int, int, int, int]] = 0):
        super().__init__(parent, None, 0, BG_COLOR0,
                         bd_radius, 0,
                         (BG_COLOR1, GRAY, BG_COLOR1, BG_COLOR1), FG_COLOR0, YAHEI[10], Qt.AlignCenter,
                         size)
        self.setIcon(QIcon(QPixmap(MINIMIZE_IMAGE)))
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(False)


class CloseButton(Button):
    def __init__(self, parent, size=(55, 36), bd_radius: Union[int, Tuple[int, int, int, int]] = 5):
        if isinstance(bd_radius, int):
            bd_radius = (0, bd_radius, 0, 0)
        else:
            bd_radius = (0, bd_radius[1], 0, 0)
        super().__init__(parent, None, 0, BG_COLOR0,
                         bd_radius, 0,
                         (BG_COLOR1, LIGHTER_RED, BG_COLOR1, BG_COLOR1), FG_COLOR0, YAHEI[10], Qt.AlignCenter, size)
        self.setIcon(QIcon(QPixmap(CLOSE_IMAGE)))
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(False)


class CancelButton(Button):
    def __init__(self, parent, size=(55, 36), bd_radius: Union[int, Tuple[int, int, int, int]] = 5):
        super().__init__(parent, None, 0, BG_COLOR0,
                         bd_radius, 0,
                         (BG_COLOR1, LIGHTER_RED, BG_COLOR1, BG_COLOR1), FG_COLOR0, YAHEI[10], Qt.AlignCenter, size)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(False)


class EnsureButton(Button):
    def __init__(self, parent, size=(55, 36), bd_radius: Union[int, Tuple[int, int, int, int]] = 5):
        super().__init__(parent, None, 0, BG_COLOR0,
                         bd_radius, 0,
                         (BG_COLOR1, LIGHTER_GREEN, BG_COLOR1, BG_COLOR1), FG_COLOR0, YAHEI[10], Qt.AlignCenter,
                         size)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCheckable(False)


class CircleSelectButton(Button):
    def __init__(self, parent, relative_widgets: list, tool_tip, radius, color: str, hover_color: str,
                 check_color: str):
        """

        :param parent:
        :param relative_widgets: 与该按钮绑定的其他按钮
        :param tool_tip:
        :param radius:
        :param color:
        :param check_color:
        """
        super().__init__(parent, tool_tip, 0, FG_COLOR0, radius, 0, (color, hover_color, check_color, check_color),
                         FG_COLOR0, YAHEI[10], Qt.AlignCenter, (radius * 2, radius * 2))
        self.setCheckable(True)
        self.setChecked(False)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setCursor(Qt.PointingHandCursor)
        self.radius = radius
        self.relative_widgets = relative_widgets
        self.bind_relative_widgets()

    def bind_relative_widgets(self):
        for widget in self.relative_widgets:
            widget.clicked.connect(self.clicked)
            widget.setCursor(Qt.PointingHandCursor)


class CircleBtWithTextLabel(QPushButton):
    def __init__(self, parent, text, tool_tip, color, check_color, radius, size=(100, 26), spacing=5):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)
        self.setLayout(self.layout)
        self.text_label = TextLabel(self, text, font=YAHEI[10], color=FG_COLOR0, align=Qt.AlignLeft | Qt.AlignVCenter)
        self.__r_widgets = [self.text_label, self]
        self.circle = CircleSelectButton(self, self._r_widgets, tool_tip, radius, color, color, check_color)
        self.layout.addWidget(self.circle, Qt.AlignLeft | Qt.AlignVCenter)
        self.layout.addWidget(self.text_label, Qt.AlignLeft | Qt.AlignVCenter)
        self.setFixedSize(size[0], size[1])
        self.setFlat(True)


class ImageTextButton(TextButton):
    ImgLeft = "ImgLeft"
    ImgRight = "ImgRight"
    ImgTop = "ImgTop"
    ImgBottom = "ImgBottom"

    def __init__(
            self, parent,
            text: str = '',
            tool_tip: str = None,
            img_bytes: bytes = None,
            img_pos: str = ImgLeft,
            img_size: Union[int, Tuple[int, int]] = 0,
            img_bd_radius: int = 0,
            spacing: int = 10,
            bd: Union[int, Tuple[int, int, int, int]] = 0,
            bd_color: Union[str, ThemeColor, Tuple[str, str, str, str]] = FG_COLOR0,
            bd_radius: Union[int, Tuple[int, int, int, int]] = 0,
            padding: Union[int, Tuple[int, int, int, int]] = 0,
            bg: Union[str, ThemeColor, Tuple[str, str, str, str]] = BG_COLOR0,
            fg: Union[str, ThemeColor, Tuple[str, str, str, str]] = FG_COLOR0,
            font=YAHEI[10],
            align=Qt.AlignCenter,
            size: Union[int, Tuple[int, int]] = (55, 25),
    ):
        """
        四个状态分别为：默认，鼠标悬停，鼠标按下，获得焦点
        :param parent:
        :param text:
        :param img_bytes:
        :param img_pos:
        :param img_size:
        :param img_bd_radius:
        :param bd:
        :param bd_color:
        :param bd_radius:
        :param padding:
        :param bg:
        :param fg:
        :param font:
        """
        self.text_label = TextLabel(None, text, font, fg if isinstance(fg, (str, ThemeColor)) else fg[0], align)
        self.img_label = BorderRadiusImage(None, img_bytes, img_size, img_bd_radius)
        self.layout = QHBoxLayout() if img_pos == self.ImgLeft or img_pos == self.ImgRight else QVBoxLayout()
        self.widgets = [self.img_label, self.text_label] if img_pos in [self.ImgLeft, self.ImgTop] else [
            self.text_label, self.img_label]
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)
        self.layout.addStretch()
        for widget in self.widgets:
            self.layout.addWidget(widget)
        self.layout.addStretch()
        super().__init__(parent, text, tool_tip, bd, bd_color, bd_radius, padding, bg, fg, font, align, size,
                         _set_text=False)
        self.setLayout(self.layout)
        self.layout.setAlignment(align)
