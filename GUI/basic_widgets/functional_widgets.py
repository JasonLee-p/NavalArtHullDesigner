# -*- coding: utf-8 -*-
"""
有特定功能的中型部件
"""
from abc import abstractmethod

from ..basic_data import *
from .line_edit import NumberEdit, TextEdit
from .buttons import _set_buttons
from .other_widgets import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class HSLColorPicker(QWidget):
    def __init__(self):
        self.current_color = QColor.fromHsl(180, 255, 127)
        self.updating = False
        self.align = Qt.AlignRight | Qt.AlignTop
        self.align_center = Qt.AlignRight | Qt.AlignVCenter
        super().__init__()
        self.layout = QVBoxLayout()
        self.HSL_layout = QGridLayout()
        self.layoutContentMargins = (4, 4, 4, 4)
        self.layoutVerticalSpacing = 4
        self.layoutHorizontalSpacing = 16
        self.sliderHei = 25
        self.hue_slider = ColorSlider(ColorSlider.H, self.sliderHei)
        self.hue_label = TextLabel(None, "色相:")
        self.saturation_slider = ColorSlider(ColorSlider.S, self.sliderHei)
        self.saturation_label = TextLabel(None, "饱和:")
        self.lightness_slider = ColorSlider(ColorSlider.L, self.sliderHei)
        self.brightness_label = TextLabel(None, "明度:")
        self.hue_slider.init_slider(self.hue_slider, self.saturation_slider, self.lightness_slider)
        self.saturation_slider.init_slider(self.hue_slider, self.saturation_slider, self.lightness_slider)
        self.lightness_slider.init_slider(self.hue_slider, self.saturation_slider, self.lightness_slider)
        self.color_preview = QLabel()
        # 下方RBG色值显示
        self.message_layout = QHBoxLayout()
        self.RGB_layout = QGridLayout()
        self.labelR = TextLabel(None, "R:", color="#FFCCCC")
        self.labelG = TextLabel(None, "G:", color="#CCFFCC")
        self.labelB = TextLabel(None, "B:", color="#CCCCFF")
        self.labelR_value = NumberEdit(None, self, num_range=(0, 255), size=(49, 24))
        self.labelG_value = NumberEdit(None, self, num_range=(0, 255), size=(49, 24))
        self.labelB_value = NumberEdit(None, self, num_range=(0, 255), size=(49, 24))
        self.init_ui()

    def init_ui(self):
        self.init_HSL()
        self.initMessage()
        self.setLayout(self.layout)
        self.layout.setAlignment(self.align)

    # noinspection PyUnresolvedReferences
    def init_HSL(self):
        self.HSL_layout.setContentsMargins(1, 1, 1, 1)
        self.HSL_layout.setSpacing(1)
        self.HSL_layout.setContentsMargins(*self.layoutContentMargins)
        self.HSL_layout.setVerticalSpacing(self.layoutVerticalSpacing)
        self.HSL_layout.setHorizontalSpacing(self.layoutHorizontalSpacing)
        self.HSL_layout.setAlignment(self.align)
        color_preview_r = 3 * self.sliderHei + 2 * self.layoutVerticalSpacing - 8
        self.color_preview.setFixedSize(color_preview_r, color_preview_r)
        self.update_color()

        self.hue_slider.valueChanged.connect(self.update_color)
        self.saturation_slider.valueChanged.connect(self.update_color)
        self.lightness_slider.valueChanged.connect(self.update_color)

        self.HSL_layout.addWidget(self.hue_label, 0, 0, self.align_center)
        self.HSL_layout.addWidget(self.hue_slider, 0, 1, self.align_center)
        self.HSL_layout.addWidget(self.saturation_label, 1, 0, self.align_center)
        self.HSL_layout.addWidget(self.saturation_slider, 1, 1, self.align_center)
        self.HSL_layout.addWidget(self.brightness_label, 2, 0, self.align_center)
        self.HSL_layout.addWidget(self.lightness_slider, 2, 1, self.align_center)
        self.HSL_layout.addWidget(self.color_preview, 0, 2, 3, 1, self.align_center)
        self.layout.addLayout(self.HSL_layout)

    def initMessage(self):
        self.message_layout.setAlignment(self.align)
        self.message_layout.setContentsMargins(1, 1, 1, 1)
        self.RGB_layout.setAlignment(self.align)
        self.RGB_layout.setContentsMargins(7, 1, 7, 1)
        self.RGB_layout.setVerticalSpacing(4)
        self.RGB_layout.setHorizontalSpacing(8)
        self.RGB_layout.setAlignment(self.align)

        self.RGB_layout.addWidget(self.labelR, 0, 0, self.align_center)
        self.RGB_layout.addWidget(self.labelR_value, 0, 1, self.align_center)
        self.RGB_layout.addWidget(self.labelG, 1, 0, self.align_center)
        self.RGB_layout.addWidget(self.labelG_value, 1, 1, self.align_center)
        self.RGB_layout.addWidget(self.labelB, 2, 0, self.align_center)
        self.RGB_layout.addWidget(self.labelB_value, 2, 1, self.align_center)

        # 绑定到输入事件
        self.labelR_value.textChanged.connect(self.update_rgb_color)
        self.labelG_value.textChanged.connect(self.update_rgb_color)
        self.labelB_value.textChanged.connect(self.update_rgb_color)

        self.message_layout.addLayout(self.RGB_layout)
        self.layout.addLayout(self.message_layout)

    def mousePressEvent(self, event):
        # 鼠标在控件外的时候，取色
        if event.button() == Qt.LeftButton:
            if not self.rect().contains(event.__pos()):
                # 获取鼠标位置的颜色
                _pos = event.globalPos()
                _color = QColor.fromRgb(
                    QPixmap.grabWindow(QApplication.desktop().winId()).toImage().pixel(_pos))
                self.current_color = _color
                # 移动滑动条
                _h = self.current_color.hue()
                _s = self.current_color.saturation()
                _l = self.current_color.lightness()
                self.hue_slider.setValue(_h)
                self.saturation_slider.setValue(_s)
                self.lightness_slider.setValue(_l)
                # 更新RGB值
                self.labelR_value.setText(str(self.current_color.red()))
                self.labelG_value.setText(str(self.current_color.green()))
                self.labelB_value.setText(str(self.current_color.blue()))

    def update_color(self):
        if self.updating:
            return
        self.updating = True

        self.current_color = QColor.fromHsl(
            self.hue_slider.value(),
            self.saturation_slider.value(),
            self.lightness_slider.value()
        )
        # 更新滑动条颜色
        self.hue_slider.update()
        self.saturation_slider.update()
        self.lightness_slider.update()
        # 更新RGB值
        self.labelR_value.setText(str(self.current_color.red()))
        self.labelG_value.setText(str(self.current_color.green()))
        self.labelB_value.setText(str(self.current_color.blue()))
        self.update_color_preview()
        self.updating = False

    def update_rgb_color(self):
        if self.updating:
            return
        self.updating = True
        try:
            r = int(self.labelR_value.text())
            g = int(self.labelG_value.text())
            b = int(self.labelB_value.text())
        except ValueError:
            return
        self.current_color = QColor(r, g, b)
        # 移动滑动条
        _h = self.current_color.hue()
        _s = self.current_color.saturation()
        _l = self.current_color.lightness()
        _hsl_color = QColor.fromHsl(_h, _s, _l)
        self.hue_slider.setValue(_h)
        self.saturation_slider.setValue(_s)
        self.lightness_slider.setValue(_l)
        self.update_color_preview()
        self.updating = False

    def update_color_preview(self):
        self.color_preview.setStyleSheet(f"""QLabel{{
            border-radius: 10px;
            background-color: {self.current_color.name()};
            border: 0px solid {BG_COLOR1};
        }}""")


class BasicDialog(QDialog):
    def __init__(self, parent=None, border_radius=8, title=None, size=QSize(400, 300), center_layout=None,
                 resizable=False, hide_top=False, hide_bottom=False, ensure_bt_fill=False):
        """
        对话框基类

        :param parent: 父窗口，通常设置为None或者主窗口
        :param border_radius: 边框圆角半径，通常为8（和按钮的圆角半径一致）
        :param title: 标题
        :param size: 窗口大小
        :param center_layout: 中心布局，默认None则为QVBoxLayout
        :param resizable: 是否可缩放
        :param hide_top: 是否隐藏顶部栏
        :param hide_bottom: 是否隐藏底部栏
        :param ensure_bt_fill: 确定按钮是否填充整个底部
        """
        self.close_bg = QIcon(QPixmap.fromImage(CLOSE_IMAGE))
        super().__init__(parent=parent)
        self._emerge_animation()
        # self.hide()
        # 设置窗口属性
        self.setWindowTitle("    " + title if title else "")
        self.title = title
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)  # 设置窗口无边框
        self.setFixedSize(size)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.topH = 36
        self.TitleFont = YAHEI[10]
        self.ContentFont = YAHEI[15]
        # 设置边框阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(5)
        self.shadow.setColor(QColor(10, 10, 10, 65))
        self.shadow.setBlurRadius(45)
        self.setGraphicsEffect(self.shadow)
        # 底色控件，使得窗口不全透明
        self.outer_layout = QVBoxLayout()
        self.outer_widget = QWidget()
        self.outer_layout.addWidget(self.outer_widget)
        self.setLayout(self.outer_layout)
        # 设置样式
        if isinstance(border_radius, int):
            border_style = f"border-radius:{border_radius}px;"
        elif isinstance(border_radius, tuple):
            border_style = f"""
            border-top-left-radius:{border_radius[0]}px;
            border-top-right-radius:{border_radius[1]}px;
            border-bottom-left-radius:{border_radius[2]}px;
            border-bottom-right-radius:{border_radius[3]}px;
            """
        else:
            border_style = f"border-radius:10px;"
        self.outer_widget.setStyleSheet(f"""
            QWidget{{
                background-color:{BG_COLOR1};
                {border_style}
            }}
        """)
        # self.setStyleSheet(f"""
        #     QDialog{{
        #         background-color:{BG_COLOR1};
        #     }}
        #     QLabel{{
        #         background-color:{BG_COLOR1};
        #         color:{FG_COLOR0};
        #     }}
        #     QWidget{{
        #         background-color:{BG_COLOR1};
        #         color:{FG_COLOR0};
        #     }}
        # """)
        # 设置主题
        self.main_layout = QVBoxLayout()
        self.outer_widget.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        if not hide_top:
            # 顶部栏
            self.top_layout = QHBoxLayout()
            self.close_button = QPushButton()
            self.add_top_bar()
            # 分割线
            self.main_layout.addWidget(HorSpliter(), alignment=Qt.AlignTop)
        # 主体-----------------------------------------------------------------------------------------------
        self._center_layout = center_layout if center_layout else QVBoxLayout()
        self.__init_center_layout()
        self.main_layout.addStretch(1)
        if not hide_bottom:
            if not hide_top:
                # 分割线
                self.main_layout.addWidget(HorSpliter(), alignment=Qt.AlignTop)
            # 底部（按钮）
            self.bottom_layout = QHBoxLayout()
            if not ensure_bt_fill:
                self.cancel_button = QPushButton('取消')
            self.ensure_button = QPushButton('确定')
            self.add_bottom_bar(ensure_bt_fill)
        # 移动到屏幕中央
        self.move((WIN_WID - self.width()) // 2, 3 * (WIN_HEI - self.height()) // 7)
        # 给top_layout的区域添加鼠标拖动功能
        self.m_flag = False
        self.m_Position = None
        self.drag = None  # 初始化拖动条
        self.resizable = resizable
        if resizable:
            # 添加缩放功能，当鼠标移动到窗口边缘时，鼠标变成缩放样式
            self.drag = [False, False, False, False]  # 用于判断鼠标是否在窗口边缘
            self.setMouseTracking(True)  # 设置widget鼠标跟踪
            self.resize_flag = False  # 用于判断是否拉伸窗口
            self.resize_dir = None  # 用于判断拉伸窗口的方向
            self.resize_area = 5  # 用于判断鼠标是否在边缘区域
            self.resize_min_size = QSize(200, 200)
            self.resize_max_size = QSize(WIN_WID, WIN_HEI)
        self.init_center_layout()

    @abstractmethod
    def ensure(self):
        self.close()

    def show(self):
        super().show()
        self.close_button.setFocusPolicy(Qt.NoFocus)
        # 置顶
        self.raise_()
        self.activateWindow()

    def close(self):
        if hasattr(self, "Instance"):
            self.Instance = None
        super().close()

    def add_top_bar(self):
        # 布局
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.main_layout.addLayout(self.top_layout)
        self.top_layout.addStretch(1)
        text_label = QLabel(self.title)
        text_label.setFont(self.TitleFont)
        text_label.setStyleSheet(f"color:{FG_COLOR0};")
        self.top_layout.addWidget(text_label, alignment=Qt.AlignCenter)
        self.top_layout.addStretch(1)
        # 按钮
        cb_size = (self.topH + 8, self.topH)
        self.close_button.setIcon(self.close_bg)
        _set_buttons([self.close_button], sizes=cb_size, border=0, bg=(BG_COLOR1, "#F76677", "#F76677", "#F76677"))
        self.close_button.clicked.connect(self.close)
        self.close_button.setFocusPolicy(Qt.NoFocus)
        self.top_layout.addWidget(self.close_button, alignment=Qt.AlignRight)

    def __init_center_layout(self):
        self.main_layout.addLayout(self._center_layout, stretch=1)

    @abstractmethod
    def init_center_layout(self):
        """
        初始化中心布局
        在该函数中调用add_widget()添加控件，该函数会在基类初始化时调用
        无需调用基类的该函数
        :return:
        """
        pass

    def add_widget(self, *args, alignment=Qt.AlignCenter):
        """
        QVBoxLayout或QHBoxLayout的参数：widget, stretch, alignment, *args
        QGridLayout的参数：widget, row, column, rowSpan, columnSpan, alignment, *args
        :param alignment:
        :param args:
        :return:
        """
        self._center_layout.addWidget(*args, alignment=alignment)

    def add_bottom_bar(self, ensure_bt_fill: bool):
        """

        :param ensure_bt_fill: 是否填充整个底部
        :return:
        """
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(0)
        self.main_layout.addLayout(self.bottom_layout)
        self.bottom_layout.addStretch(1)
        if not ensure_bt_fill:
            self.bottom_layout.addWidget(self.cancel_button)
            self.bottom_layout.addWidget(self.ensure_button)
            _set_buttons([self.cancel_button], sizes=(80, 30), border=0, bd_radius=10, font=YAHEI[9],
                         bg=(BG_COLOR1, LIGHTER_RED, LIGHTER_RED, BG_COLOR2))
            _set_buttons([self.ensure_button], sizes=(80, 30), border=0, bd_radius=10, font=YAHEI[9],
                         bg=(BG_COLOR1, LIGHTER_GREEN, LIGHTER_GREEN, BG_COLOR2))
            self.cancel_button.clicked.connect(self.close)
            self.ensure_button.clicked.connect(self.ensure)
            self.cancel_button.setFocusPolicy(Qt.NoFocus)
            self.ensure_button.setFocusPolicy(Qt.NoFocus)
        else:
            self.bottom_layout.addWidget(self.ensure_button)
            _set_buttons([self.ensure_button], sizes=(300, 35), border=0, bd_radius=(0, 0, 15, 15),
                         bg=(BG_COLOR2, LIGHTER_GREEN, LIGHTER_GREEN, BG_COLOR2))
            self.ensure_button.setFocusPolicy(Qt.NoFocus)
            self.ensure_button.clicked.connect(self.ensure)

    def mousePressEvent(self, event):
        # 鼠标按下时，记录当前位置，若在标题栏内且非最大化，则允许拖动
        if event.button() == Qt.LeftButton and event.y() <= self.topH and not self.isMaximized():
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
        elif event.button() == Qt.LeftButton and self.resizable:
            self.resize_flag = True
            self.m_Position = event.globalPos()
            _pos = QPoint(event.x(), event.y())
            # 判断鼠标所在的位置是否为边缘
            if _pos.x() < self.resize_area:
                self.drag[0] = True
            if _pos.x() > self.width() - self.resize_area:
                self.drag[1] = True
            if _pos.y() < self.resize_area:
                self.drag[2] = True
            if _pos.y() > self.height() - self.resize_area:
                self.drag[3] = True
            # 判断鼠标所在的位置是否为角落
            if _pos.x() < self.resize_area and _pos.y() < self.resize_area:
                self.resize_dir = 'lt'
            elif self.resize_area > _pos.y() > self.height() - self.resize_area:
                self.resize_dir = 'lb'
            elif self.width() - self.resize_area < _pos.x() < self.resize_area:
                self.resize_dir = 'rt'
            elif _pos.x() > self.width() - self.resize_area and _pos.y() > self.height() - self.resize_area:
                self.resize_dir = 'rb'
            event.accept()
        # 刷新
        self.update()

    def mouseReleaseEvent(self, _):
        # 拖动窗口时，鼠标释放后停止拖动
        self.m_flag = False if self.m_flag else self.m_flag
        if self.resizable:
            self.resize_flag = False if self.resize_flag else self.resize_flag
            self.drag = [False, False, False, False]
            self.resize_dir = None
        self.update()

    def mouseMoveEvent(self, event):
        # 当鼠标在标题栏按下且非最大化时，移动窗口
        if Qt.LeftButton and self.m_flag:
            target_pos = event.globalPos() - self.m_Position
            # 去除窗口移动到屏幕外的情况
            if target_pos.x() < 0:
                target_pos.setX(0)
            if target_pos.y() < 0:
                target_pos.setY(0)
            self.move(target_pos)
            event.accept()
            # 刷新
            self.update()
        if self.resizable:
            # 检查是否需要改变鼠标样式
            _pos = QPoint(event.x(), event.y())
            if _pos.x() < self.resize_area:
                self.setCursor(Qt.SizeHorCursor)
            elif _pos.x() > self.width() - self.resize_area:
                self.setCursor(Qt.SizeHorCursor)
            elif _pos.y() < self.resize_area:
                self.setCursor(Qt.SizeVerCursor)
            elif _pos.y() > self.height() - self.resize_area:
                self.setCursor(Qt.SizeVerCursor)
            elif _pos.x() < self.resize_area and _pos.y() < self.resize_area:
                self.setCursor(Qt.SizeFDiagCursor)
            elif self.resize_area > _pos.y() > self.height() - self.resize_area:
                self.setCursor(Qt.SizeBDiagCursor)
            elif self.width() - self.resize_area < _pos.x() < self.resize_area:
                self.setCursor(Qt.SizeBDiagCursor)
            elif _pos.x() > self.width() - self.resize_area and _pos.y() > self.height() - self.resize_area:
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            # 检查是否需要拉伸窗口
            if self.resize_flag:
                _pos = event.__pos()
                _dx = event.globalPos().x() - self.m_Position.x()
                _dy = event.globalPos().y() - self.m_Position.y()
                if self.resize_dir == 'lt':
                    self.setGeometry(self.x() + _dx, self.y() + _dy, self.width() - _dx, self.height() - _dy)
                elif self.resize_dir == 'lb':
                    self.setGeometry(self.x() + _dx, self.y(), self.width() - _dx, _dy)
                elif self.resize_dir == 'rt':
                    self.setGeometry(self.x(), self.y() + _dy, self.width() + _dx, self.height() - _dy)
                elif self.resize_dir == 'rb':
                    self.setGeometry(self.x(), self.y(), self.width() + _dx, self.height() + _dy)
                elif self.resize_dir == 't':
                    self.setGeometry(self.x(), self.y() + _dy, self.width(), self.height() - _dy)
                elif self.resize_dir == 'l':
                    self.setGeometry(self.x() + _dx, self.y(), self.width() - _dx, self.height())
                elif self.resize_dir == 'r':
                    self.setGeometry(self.x(), self.y(), self.width() + _dx, self.height())
                elif self.resize_dir == 'b':
                    self.setGeometry(self.x(), self.y(), self.width(), self.height() + _dy)
                self.m_Position = event.globalPos()
                event.accept()
                # 刷新
                self.update()

    def _emerge_animation(self):
        self.animation = QPropertyAnimation(self.parent(), QByteArray(b"windowOpacity"))
        self.animation.setDuration(100)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
