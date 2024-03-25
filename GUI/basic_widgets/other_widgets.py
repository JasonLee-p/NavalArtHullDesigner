# -*- coding: utf-8 -*-
"""
其他小部件
"""
from typing import Union, Tuple, Type

from ..basic_data import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QSlider, QSplitter, QScrollArea, QFrame, QLabel, QLineEdit, QProgressBar, QWidget, \
    QHBoxLayout, QSizePolicy
from PyQt5.QtGui import *


class HorSpliter(QFrame):
    def __init__(self, parent=None, height=2):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.setStyleSheet(f"background-color: {BG_COLOR0};")


class VerSpliter(QFrame):
    def __init__(self, parent=None, width=1):
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setStyleSheet(f"background-color: {BG_COLOR0};")


class TextLabel(QLabel):
    def __init__(self, parent, text, font=YAHEI[10], color=FG_COLOR0, align=Qt.AlignLeft):
        super().__init__(parent=parent, text=text)
        self.text = text
        self.setFont(font)
        self.setStyleSheet(f"background-color: rgba(0, 0, 0, 0); color: {color};")
        self.setAlignment(align)

    def set_text(self, text, color: str = None):
        self.text = text
        if color:
            self.setStyleSheet(f"color:{color};")
        self.setText(text)


class ColoredTextLabel(QLabel):
    def __init__(self, parent, text, font=YAHEI[10], color=FG_COLOR0, bg=BG_COLOR0, bd_radius=5, bd=0, bd_color=GRAY,
                 align=Qt.AlignCenter, padding=6):
        super().__init__(parent=parent, text=text)
        self.text = text
        self.setFont(font)
        self.setStyleSheet(f"""
            QLabel{{
                background-color: {bg}; color: {color}; 
                border: {bd}px solid {bd_color}; 
                border-radius: {bd_radius}px;
                padding-top: {padding}px;
                padding-bottom: {padding}px;
                padding-left: {padding + 5}px;
                padding-right: {padding + 5}px;
            }}
        """)
        self.setAlignment(align)


class IconLabel(QLabel):
    def __init__(self, parent, ico_bytes, title, height):
        super().__init__(parent)
        ico = QIcon()
        icon = QPixmap()
        icon_image = QImage.fromData(QByteArray(ico_bytes))
        icon.convertFromImage(icon_image)
        ico.addPixmap(icon, QIcon.Normal, QIcon.Off)
        self.setPixmap(ico.pixmap(QSize(26, 26)))
        self.setFixedSize(55, height)
        self.setAlignment(Qt.AlignCenter)
        self.setToolTip(title) if title else None
        self.setToolTipDuration(5000)


class BorderRadiusImage(QLabel):
    def __init__(self, parent, img_bytes: bytes, img_size: Union[int, Tuple[int, int]], bd_radius: int = 0,
                 tool_tip=None):
        super().__init__(parent)
        # 处理参数
        if isinstance(img_size, int):
            self.width, self.height = img_size, img_size
        else:
            self.width, self.height = img_size[0], img_size[1]
        self.img_bytes = img_bytes
        self.bd_radius = bd_radius
        image = QImage.fromData(QByteArray(self.img_bytes))
        img = QPixmap()
        img.convertFromImage(image)
        img.scaled(self.width, self.height, Qt.KeepAspectRatio)
        rounded_img = QPixmap()
        rounded_img.scaled(self.width, self.height, Qt.KeepAspectRatio)
        rounded_img.fill(Qt.transparent)
        painter = QPainter()
        painter.begin(rounded_img)
        painter.setRenderHint(QPainter.Antialiasing)
        # 创建一个椭圆路径来表示圆角
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, self.bd_radius, self.bd_radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, img)
        painter.end()
        self.setPixmap(rounded_img)
        self.setStyleSheet(
            f"background-color: rgba(0, 0, 0, 0);"
            f"border-radius: {self.bd_radius}px;"
        )
        self.setFixedSize(self.width, self.height)
        if tool_tip:
            self.setToolTip(tool_tip)
            self.setToolTipDuration(5000)


class ProgressBar(QProgressBar):
    ...


class TextEdit(QLineEdit):
    def __init__(self, text, parent, tool_tip: str = None, font=YAHEI[10], bg="transparent", padding=3):
        super().__init__(text, parent)
        self.setFont(font)
        side_padding = padding + 5
        self.setStyleSheet(f"""
            QLineEdit{{
                background-color: {bg};
                color: {FG_COLOR0}; 
                border: 1px solid {FG_COLOR0}; 
                border-radius: 5px;
                padding-top: {padding}px;
                padding-bottom: {padding}px;
                padding-left: {side_padding}px;
                padding-right: {side_padding}px;
            }}
            QLineEdit:hover{{
                background-color: {BG_COLOR2}; 
                color: {FG_COLOR0}; 
                border: 1px solid {FG_COLOR0}; 
                border-radius: 5px;
                padding-top: {padding}px;
                padding-bottom: {padding}px;
                padding-left: {side_padding}px;
                padding-right: {side_padding}px;
            }}
            QLineEdit::disabled{{
                background-color: {BG_COLOR1}; 
                color: {GRAY};
                border: 1px solid {GRAY};
                border-radius: 5px;
                padding-top: {padding}px;
                padding-bottom: {padding}px;
                padding-left: {side_padding}px;
                padding-right: {side_padding}px;
            }}
            QLineEdit::focus{{
                background-color: {BG_COLOR2}; 
                color: {FG_COLOR0}; 
                border: 1px solid {FG_COLOR0}; 
                border-radius: 5px;
                padding-top: {padding}px;
                padding-bottom: {padding}px;
                padding-left: {side_padding}px;
                padding-right: {side_padding}px;
            }}  
        """)
        if tool_tip:
            self.setToolTip(tool_tip)
            self.setToolTipDuration(5000)


class NumberEdit(TextEdit):
    value_changed = pyqtSignal(float)

    def __init__(
            self, parent, root_parent,
            size: Union[Tuple[int, int], Tuple[int, None], Tuple[None, int], None] = (68, 24),
            num_type: Union[Type[int], Type[float]] = int,
            num_range: tuple = (-100000, 100000),
            rounding: int = 0,
            default_value: int = 0,
            step: Union[int, float] = int(1),
            font=YAHEI[10],
            bg="transparent",
            tool_tip: str = None,
            padding=3
    ):
        super().__init__(str(default_value), parent, tool_tip, font, bg, padding)
        self.root_parent = root_parent
        self.num_type = num_type
        self.num_range = num_range
        self.rounding = None if self.num_type == int else rounding
        self.default_value = default_value
        self.current_value = round(self.num_type(default_value), self.rounding) if self.rounding else int(default_value)
        self.step = step
        # 设置属性
        if size:
            if size[0]:
                self.setFixedWidth(size[0])
            if size[1]:
                self.setFixedHeight(size[1])
        self.setAlignment(Qt.AlignCenter)
        if self.num_type == int:
            self.setValidator(QIntValidator(self.num_range[0], self.num_range[1]))
        elif self.num_type == float:
            self.setValidator(QDoubleValidator(self.num_range[0], self.num_range[1], self.rounding))
        # 解绑滚轮事件，将来绑定到父控件上。这样做能够让控件在unfocus状态也能够响应滚轮事件进行值修改；
        self.wheelEvent = lambda event: None
        # 绑定值改变事件
        self.textChanging = False  # 防止递归
        self.textChanged.connect(self.text_changed)

    def text_changed(self):
        if self.textChanging:
            return
        self.textChanging = True
        if self.text() != "":
            if self.text()[0] == "0" and len(self.text()) > 1:
                self.setText(self.text()[1:])
            try:
                if self.num_range[0] <= self.num_type(self.text()) <= self.num_range[1]:
                    self.current_value = round(self.num_type(self.text()), self.rounding) if self.rounding else int(
                        self.text())
            except ValueError:
                pass
        else:
            self.current_value = 0
        self.setText(str(self.current_value))
        self.value_changed.emit(self.current_value)
        self.root_parent.update()
        self.textChanging = False


class Slider(QSlider):
    value_changed = pyqtSignal(int)

    def __init__(self, parent, orientation, range_, step, init_value=0):
        super().__init__(orientation, parent)
        self.setRange(range_[0], range_[1])
        self.setValue(init_value)
        self.setSingleStep(step)
        self.setPageStep(0)
        self.setToolTip(str(init_value))
        self.setToolTipDuration(3000)
        self.barWidth = 12
        self.bdr = 6
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background-color: {BG_COLOR0};
                height: {self.barWidth}px;
                border-radius: {self.bdr}px;
            }}
            QSlider::handle:horizontal {{
                background-color: {FG_COLOR1};
                width: 12px;
                height: 20px;
                border-radius: {self.bdr}px;
            }}
            QSlider::add-page:horizontal {{
                background-color: {BG_COLOR2};
                height: {self.barWidth}px;
                border-radius: {self.bdr}px;
            }}
            QSlider::sub-page:horizontal {{
                background-color: {BG_COLOR3};
                height: {self.barWidth}px;
                border-radius: {self.bdr}px;
            }}
            QSlider::groove:vertical {{
                background-color: {BG_COLOR0};
                width: {self.barWidth}px;
                border-radius: {self.bdr}px;
            }}
            QSlider::handle:vertical {{
                background-color: {FG_COLOR1};
                width: 20px;
                height: 12px;
                border-radius: {self.bdr}px;
            }}
            QSlider::add-page:vertical {{
                background-color: {BG_COLOR3};
                width: {self.barWidth}px;
                border-radius: {self.bdr}px;
            }}
            QSlider::sub-page:vertical {{
                background-color: {BG_COLOR2};
                width: {self.barWidth}px;
                border-radius: {self.bdr}px;
            }}
        """)

    def mousePressEvent(self, event):
        # 将颜色直接设置到鼠标点击的位置
        if event.button() == Qt.LeftButton:
            if self.orientation() == Qt.Horizontal:
                value = int(event.x() / self.width() * self.maximum())
            else:
                value = int(event.y() / self.height() * self.maximum())
                value = self.maximum() - value
            self.setValue(value)
            self.value_changed.emit(value)
            self.setToolTip(str(value))
            self.update()

    def mouseMoveEvent(self, event):
        # 将颜色直接设置到鼠标点击的位置
        if event.buttons() == Qt.LeftButton:
            if self.orientation() == Qt.Horizontal:
                value = int(event.x() / self.width() * self.maximum())
            else:
                value = int(event.y() / self.height() * self.maximum())
                value = self.maximum() - value
            self.setValue(value)
            self.value_changed.emit(value)
            self.setToolTip(str(value))
            self.update()


class ColorSlider(QSlider):
    H = "h"
    S = "s"
    L = "l"

    def __init__(self, _type, height=20):
        super().__init__(Qt.Horizontal)
        # 设置track不可见
        self.hei = height
        self.hue_slider = None
        self.saturation_slider = None
        self.lightness_slider = None
        self.type = _type

    def init_slider(self, hue_slider, saturation_slider, lightness):
        self.hue_slider = hue_slider
        self.saturation_slider = saturation_slider
        self.lightness_slider = lightness
        if self.type == ColorSlider.H:
            self.setRange(0, 359)
            self.setValue(180)
        elif self.type == ColorSlider.S:
            self.setRange(0, 255)
            self.setValue(0)
        elif self.type == ColorSlider.L:
            self.setRange(0, 255)
            self.setValue(127)
        self.setFixedSize(400, self.hei)

    def mousePressEvent(self, event):
        # 将颜色直接设置到鼠标点击的位置
        if event.button() == Qt.LeftButton:
            value = int(event.x() / self.width() * self.maximum())
            self.setValue(value)
            self.update()

    def mouseMoveEvent(self, event):
        # 将颜色直接设置到鼠标点击的位置
        if event.buttons() == Qt.LeftButton:
            value = int(event.x() / self.width() * self.maximum())
            self.setValue(value)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = QRect(0, 5, self.width(), self.hei - 10)
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        if self.type == ColorSlider.H:
            for i in range(0, 360):
                gradient.setColorAt(i / 360, QColor.fromHsl(i, 255, 127))
        elif self.type == ColorSlider.S:
            l_color = QColor.fromHsl(self.hue_slider.value(), 0, self.lightness_slider.value())
            r_color = QColor.fromHsl(self.hue_slider.value(), 255, self.lightness_slider.value())
            gradient.setColorAt(0, l_color)
            gradient.setColorAt(1, r_color)
        elif self.type == ColorSlider.L:
            for i in range(0, 256):
                gradient.setColorAt(i / 255, QColor.fromHsl(self.hue_slider.value(), self.saturation_slider.value(), i))
        painter.fillRect(rect, gradient)
        # 绘制游标
        pos_x = int(self.value() / self.maximum() * self.width())
        # 半透明矩形
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 127))
        painter.drawRect(pos_x - 5, 5, 10, self.hei - 10)
        # 绘制游标上的三角形（FG_COLOR0）
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(str(FG_COLOR0)))
        # noinspection PyArgumentList
        painter.drawPolygon(QPolygon([
            QPoint(pos_x - 5, 0),
            QPoint(pos_x + 5, 0),
            QPoint(pos_x, 5),
        ]))


class Splitter(QSplitter):
    def __init__(self, orientation):
        super().__init__(orientation)
        self.setMouseTracking(True)
        self.setObjectName("splitter")
        self.setChildrenCollapsible(False)
        self.setContentsMargins(0, 0, 0, 0)
        self.setHandleWidth(1)
        self.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {BG_COLOR0};
                color: {FG_COLOR0};
                width: 1px;
            }}
            QSplitter::handle:horizontal {{
                background-color: {BG_COLOR0};
                color: {FG_COLOR0};
                width: 1px;
            }}
            QSplitter::handle:vertical {{
                background-color: {BG_COLOR0};
                color: {FG_COLOR0};
                width: 1px;
            }}
            QSplitter::handle:hover {{
                background-color: {BG_COLOR2};
                color: {FG_COLOR0};
                width: 1px;
            }}
            QSplitter::handle:pressed {{
                background-color: {BG_COLOR3};
                color: {FG_COLOR0};
                width: 1px;
            }}
        """)

    def createHandle(self):
        handle = super().createHandle()
        handle.setMouseTracking(True)
        return handle

    def addWidget(self, widget):
        widget.setMinimumSize(40, 40)
        super().addWidget(widget)

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)


class ScrollArea(QScrollArea):
    def __init__(self, parent, widget, orientation, bd=0, bd_radius=0, bg="transparent", bar_bg=BG_COLOR0):
        self.styleSheet = f"""
                QScrollArea{{
                    background-color: {bg}; color: {FG_COLOR0};
                    border: {bd}px solid {FG_COLOR0}; border-radius: {bd_radius}px;
                }}
                QScrollBar:vertical {{
                    background-color: {bar_bg}; border-radius: 4px; width: 8px; margin: 0px 0px 0px 0px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {BG_COLOR2}; border-radius: 4px; min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {BG_COLOR3}; border-radius: 4px; min-height: 20px;
                }}
                QScrollBar::handle:vertical:pressed {{
                    background-color: {GRAY}; border-radius: 4px; min-height: 20px;
                }}
                QScrollBar::add-line:vertical {{
                    height: 0px; subcontrol-position: bottom; subcontrol-origin: margin;
                }}
                QScrollBar::sub-line:vertical {{
                    height: 0px; subcontrol-position: top; subcontrol-origin: margin;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
                QScrollBar:horizontal {{
                    background-color: {bar_bg}; border-radius: 4px; height: 8px; margin: 0px 0px 0px 0px;
                }}
                QScrollBar::handle:horizontal {{
                    background-color: {BG_COLOR2}; border-radius: 4px; min-width: 20px;
                }}
                QScrollBar::handle:horizontal:hover {{
                    background-color: {BG_COLOR3}; border-radius: 4px; min-width: 20px;
                }}
                QScrollBar::handle:horizontal:pressed {{
                    background-color: {GRAY}; border-radius: 4px; min-width: 20px;
                }}
                QScrollBar::add-line:horizontal {{
                    width: 0px; subcontrol-position: right; subcontrol-origin: margin;
                }}
                QScrollBar::sub-line:horizontal {{
                    width: 0px; subcontrol-position: left; subcontrol-origin: margin;
                }}
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                    background: none;
                }}
            """
        super().__init__(parent)
        self.setWidget(widget)
        self.setWidgetResizable(True)
        if orientation == Qt.Horizontal:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        elif orientation == Qt.Vertical:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet(self.styleSheet)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)

    def wheelEvent(self, event):
        # 绑定滚轮事件：Shift滚轮水平滚动，其他情况垂直滚动
        if event.modifiers() == Qt.ShiftModifier:
            self.horizontalScrollBar().event(event)
        else:
            self.verticalScrollBar().event(event)


class RatioDisplayWidget(QWidget):
    def __init__(self, current_value, max_value, label_text='', unit='M'):
        super().__init__(None)

        self.current_value = current_value
        self.max_value = max_value
        self.unit = unit
        self.label = TextLabel(None, label_text, YAHEI[9], FG_COLOR0 - 50)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, max_value)
        self.progress_bar.setValue(current_value)
        self.progress_bar.setFormat(f"{current_value}/{max_value}{self.unit}")
        self.__init_ui()

    def __init_ui(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.label, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.progress_bar.setFont(YAHEI[9])
        self.progress_bar.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding))
        self.setStyleSheet_(FG_COLOR0 - 50)

    def setStyleSheet_(self, color):
        self.progress_bar.setStyleSheet(f"""
            QProgressBar{{
                border: 1px solid {BG_COLOR0};
                border-radius: 0px;
                text-align: center;
                background-color: {BG_COLOR0};
                color: {color};
            }}
            QProgressBar::chunk{{
                background-color: {BG_COLOR3 - 20};
                border-radius: 0px;
                color: {color};
            }}
        """)

    def set_values(self, current_value: int):
        if current_value > self.max_value and not self.current_value > self.max_value:
            self.setStyleSheet_(FG_COLOR1)
        elif current_value <= self.max_value < self.current_value:
            self.setStyleSheet(FG_COLOR0 - 50)
        self.current_value = current_value
        self.progress_bar.setValue(current_value)
        self.progress_bar.setFormat(f"{current_value}/{self.max_value}{self.unit}")
