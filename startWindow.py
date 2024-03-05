# -*- coding: utf-8 -*-
"""

"""

from GUI import *
from PyQt5.QtCore import Qt
from funcs_utils import open_url


class _MyLabel(QLabel):
    def __init__(self, text, font=YAHEI[9], color=FG_COLOR0, side=Qt.AlignLeft | Qt.AlignVCenter):
        super().__init__(text)
        self.setFont(font)
        self.setStyleSheet(f"color:{color};")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAlignment(side)


def _set_buttons(
        _buttons, sizes, font=YAHEI[9], border=0, border_color=FG_COLOR0,
        border_radius=10, padding=0, bg=(BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3),
        fg=FG_COLOR0
):
    """
    设置按钮样式
    :param _buttons: 按钮列表
    :param sizes:
    :param font: QFont对象
    :param border: 边框宽度
    :param border_color: 边框颜色
    :param border_radius: 边框圆角
    :param padding: 内边距
    :param bg: 按钮背景颜色
    :param fg: 按钮字体颜色
    :return:
    """
    _buttons = list(_buttons)
    if isinstance(border_radius, int):
        border_radius = (border_radius, border_radius, border_radius, border_radius)
    if type(sizes[0]) in [int, None]:
        sizes = [sizes] * len(_buttons)
    if border != 0:
        border_text = f"{border}px solid {border_color}"
    else:
        border_text = "none"
    if isinstance(padding, int):
        padding = (padding, padding, padding, padding)
    if isinstance(bg, ThemeColor) or isinstance(bg, str):
        bg = (bg, bg, bg, bg)
    if isinstance(fg, ThemeColor) or isinstance(fg, str):
        fg = (fg, fg, fg, fg)
    for button in _buttons:
        if sizes[_buttons.index(button)][0] is None:
            # 宽度拉伸
            button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            button.setFixedHeight(sizes[_buttons.index(button)][1])
        elif sizes[_buttons.index(button)][1] is None:
            # 高度拉伸
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
            button.setFixedWidth(sizes[_buttons.index(button)][0])
        else:
            button.setFixedSize(*sizes[_buttons.index(button)])
        button.setFont(font)
        button.setStyleSheet(f"""
            QPushButton{{
                background-color:{bg[0]};
                color:{fg[0]};
                border-top-left-radius: {border_radius[0]}px;
                border-top-right-radius: {border_radius[1]}px;
                border-bottom-right-radius: {border_radius[2]}px;
                border-bottom-left-radius: {border_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
            QPushButton:hover{{
                background-color:{bg[1]};
                color:{fg[1]};
                border-top-left-radius: {border_radius[0]}px;
                border-top-right-radius: {border_radius[1]}px;
                border-bottom-right-radius: {border_radius[2]}px;
                border-bottom-left-radius: {border_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
            QPushButton::pressed{{
                background-color:{bg[2]};
                color:{fg[2]};
                border-top-left-radius: {border_radius[0]}px;
                border-top-right-radius: {border_radius[1]}px;
                border-bottom-right-radius: {border_radius[2]}px;
                border-bottom-left-radius: {border_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
            QPushButton::focus{{
                background-color:{bg[3]};
                color:{fg[3]};
                border-top-left-radius: {border_radius[0]}px;
                border-top-right-radius: {border_radius[1]}px;
                border-bottom-right-radius: {border_radius[2]}px;
                border-bottom-left-radius: {border_radius[3]}px;
                border: {border_text};
                padding: {padding[0]}px {padding[1]}px {padding[2]}px {padding[3]}px;
            }}
        """)


def _create_rounded_thumbnail(image_path, width, height, corner_radius):
    if isinstance(image_path, str):
        original_image = QPixmap(image_path).scaled(width, height, Qt.KeepAspectRatio)
    else:  # 是QPixmap对象
        original_image = image_path.scaled(width, height, Qt.KeepAspectRatio)
    rounded_thumbnail = QPixmap(width, height)
    rounded_thumbnail.fill(Qt.transparent)  # 设置背景透明
    painter = QPainter(rounded_thumbnail)
    painter.setRenderHint(QPainter.Antialiasing)
    # 创建一个椭圆路径来表示圆角
    path = QPainterPath()
    path.addRoundedRect(0, 0, width, height, corner_radius, corner_radius)
    painter.setClipPath(path)  # 设置剪裁路径
    # 在剪裁后的区域内绘制原始图像
    painter.drawPixmap(0, 0, original_image)
    painter.end()  # 结束绘制
    return rounded_thumbnail


class _BasicDialog(QDialog):
    def __init__(self, parent=None, border_radius: Union[int, Tuple[int, int, int, int]] = 10,
                 title=None, size=QSize(400, 300), center_layout=None,
                 resizable=False, hide_top=False, hide_bottom=False, ensure_bt_fill=False):
        self.close_bg = QIcon(QPixmap.fromImage(CLOSE_IMAGE))
        self._parent = parent
        self._generate_self_parent = False
        if not parent:
            # 此时没有其他控件，但是如果直接显示会导致圆角黑边，所以需要设置一个背景色
            self._parent = QWidget()
            # 设置透明
            self._parent.setAttribute(Qt.WA_TranslucentBackground)
            self._parent.setWindowFlags(Qt.FramelessWindowHint)
            self._parent.setFixedSize(WIN_WID, WIN_HEI)
            self._parent.move((WIN_WID - self._parent.width()) // 2, 3 * (WIN_HEI - self._parent.height()) // 7)
            self._parent.show()
            self._generate_self_parent = True
        super().__init__(parent=self._parent)
        self.hide()
        self.setWindowTitle(title)
        self.title = title
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(size)
        self.topH = 35
        self.TitleFont = YAHEI[10]
        self.ContentFont = YAHEI[15]
        # 设置边框阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setBlurRadius(15)
        self.setGraphicsEffect(self.shadow)
        if isinstance(border_radius, int):
            border_command = f"border-radius:{border_radius}px;"
        elif isinstance(border_radius, tuple):
            border_command = f"""
            border-top-left-radius:{border_radius[0]}px;
            border-top-right-radius:{border_radius[1]}px;
            border-bottom-left-radius:{border_radius[2]}px;
            border-bottom-right-radius:{border_radius[3]}px;
            """
        else:
            border_command = f"border-radius:10px;"
        self.setStyleSheet(f"""
            QDialog{{
                background-color:{BG_COLOR1};
                {border_command}
            }}
        """)
        # 设置主题
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        if not hide_top:
            # 顶部栏
            self.top_layout = QHBoxLayout()
            self.close_button = QPushButton()
            self.__add_top_bar()
            # 分割线
            spl = QFrame(self, frameShape=QFrame.HLine, frameShadow=QFrame.Sunken)
            spl.setStyleSheet(f"background-color:{BG_COLOR0};")
            self.main_layout.addWidget(spl, alignment=Qt.AlignTop)
        # 主体-----------------------------------------------------------------------------------------------
        self._center_layout = center_layout
        self.__init_center_layout()
        self.main_layout.addStretch(1)
        if not hide_bottom:
            if not hide_top:
                # 分割线
                spl2 = QFrame(self, frameShape=QFrame.HLine, frameShadow=QFrame.Sunken)
                spl2.setStyleSheet(f"background-color:{BG_COLOR0};")
                self.main_layout.addWidget(spl2, alignment=Qt.AlignTop)
            # 底部（按钮）
            self.bottom_layout = QHBoxLayout()
            if not ensure_bt_fill:
                self.cancel_button = QPushButton('取消')
            self.ensure_button = QPushButton('确定')
            self.__add_bottom_bar(ensure_bt_fill)
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
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)  # 设置窗口无边框
            self.setMouseTracking(True)  # 设置widget鼠标跟踪
            self.resize_flag = False  # 用于判断是否拉伸窗口
            self.resize_dir = None  # 用于判断拉伸窗口的方向
            self.resize_area = 5  # 用于判断鼠标是否在边缘区域
            self.resize_min_size = QSize(200, 200)
            self.resize_max_size = QSize(WIN_WID, WIN_HEI)

    def ensure(self):
        self.close()

    def close(self):
        super().close()
        if self._generate_self_parent:
            self._parent.close()

    def __add_top_bar(self):
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
        cb_size = (self.topH + 10, self.topH)
        self.close_button.setIcon(self.close_bg)
        self.close_button.setFocusPolicy(Qt.NoFocus)
        _set_buttons([self.close_button], sizes=cb_size, border=0, bg=(BG_COLOR1, "#F76677", "#F76677", "#F76677"))
        self.close_button.clicked.connect(self.close)
        self.top_layout.addWidget(self.close_button, alignment=Qt.AlignRight)

    def __init_center_layout(self):
        self.main_layout.addLayout(self._center_layout, stretch=1)

    def __add_bottom_bar(self, ensure_bt_fill):
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(0)
        self.main_layout.addLayout(self.bottom_layout)
        self.bottom_layout.addStretch(1)
        if not ensure_bt_fill:
            self.bottom_layout.addWidget(self.cancel_button)
            self.bottom_layout.addWidget(self.ensure_button)
            _set_buttons([self.cancel_button], sizes=(80, 30), border=0, border_radius=10,
                         bg=(BG_COLOR1, "#F76677", "#F76677", BG_COLOR2))
            _set_buttons([self.ensure_button], sizes=(80, 30), border=0, border_radius=10,
                         bg=(BG_COLOR1, "#6DDF6D", "#6DDF6D", BG_COLOR2))
            self.cancel_button.clicked.connect(self.close)
            self.ensure_button.clicked.connect(self.ensure)
            self.ensure_button.setFocus()
        else:
            self.bottom_layout.addWidget(self.ensure_button)
            _set_buttons([self.ensure_button], sizes=(300, 35), border=0, border_radius=(0, 0, 15, 15),
                         bg=(BG_COLOR2, "#6DDF6D", "#6DDF6D", BG_COLOR2))
            self.ensure_button.setFocusPolicy(Qt.NoFocus)
            self.ensure_button.clicked.connect(self.ensure)

    def mousePressEvent(self, event):
        # 鼠标按下时，记录当前位置，若在标题栏内且非最大化，则允许拖动
        if event.button() == Qt.LeftButton and event.x() < self.topH and self.isMaximized() is False:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
        elif event.button() == Qt.LeftButton and self.resizable:
            self.resize_flag = True
            self.m_Position = event.globalPos()
            _pos = event.pos()
            # 判断鼠标所在的位置是否为边缘
            if _pos.x() < self.resize_area:
                self.drag[0] = True
            if _pos.x() > self.width() - self.resize_area:
                self.drag[1] = True
            if _pos.x() < self.resize_area:
                self.drag[2] = True
            if _pos.x() > self.height() - self.resize_area:
                self.drag[3] = True
            # 判断鼠标所在的位置是否为角落
            if _pos.x() < self.resize_area and _pos.x() < self.resize_area:
                self.resize_dir = 'lt'
            elif _pos.x() < self.resize_area and _pos.x() > self.height() - self.resize_area:
                self.resize_dir = 'lb'
            elif _pos.x() > self.width() - self.resize_area and _pos.x() < self.resize_area:
                self.resize_dir = 'rt'
            elif _pos.x() > self.width() - self.resize_area and _pos.x() > self.height() - self.resize_area:
                self.resize_dir = 'rb'
            event.accept()
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        # 拖动窗口时，鼠标释放后停止拖动
        self.m_flag = False if self.m_flag else self.m_flag
        if self.resizable:
            self.resize_flag = False if self.resize_flag else self.resize_flag
            self.drag = [False, False, False, False]
            self.resize_dir = None

    def mouseMoveEvent(self, QMouseEvent):
        # 当鼠标在标题栏按下且非最大化时，移动窗口
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)
            QMouseEvent.accept()
        if self.resizable:
            # 检查是否需要改变鼠标样式
            _pos = QMouseEvent.pos()
            if _pos.x() < self.resize_area:
                self.setCursor(Qt.SizeHorCursor)
            elif _pos.x() > self.width() - self.resize_area:
                self.setCursor(Qt.SizeHorCursor)
            elif _pos.x() < self.resize_area:
                self.setCursor(Qt.SizeVerCursor)
            elif _pos.x() > self.height() - self.resize_area:
                self.setCursor(Qt.SizeVerCursor)
            elif _pos.x() < self.resize_area and _pos.x() < self.resize_area:
                self.setCursor(Qt.SizeFDiagCursor)
            elif _pos.x() < self.resize_area and _pos.x() > self.height() - self.resize_area:
                self.setCursor(Qt.SizeBDiagCursor)
            elif _pos.x() > self.width() - self.resize_area and _pos.x() < self.resize_area:
                self.setCursor(Qt.SizeBDiagCursor)
            elif _pos.x() > self.width() - self.resize_area and _pos.x() > self.height() - self.resize_area:
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            # 检查是否需要拉伸窗口
            if self.resize_flag:
                _pos = QMouseEvent.pos()
                _dx = QMouseEvent.globalPos().x() - self.m_Position.x()
                _dy = QMouseEvent.globalPos().x() - self.m_Position.x()
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
                self.m_Position = QMouseEvent.globalPos()
                QMouseEvent.accept()

    def _animate(self):
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        self.show()
        animation.start()


class StartWindow(_BasicDialog):
    lastEdit_signal = pyqtSignal()
    newPrj_signal = pyqtSignal()
    openPrj_signal = pyqtSignal()
    setting_signal = pyqtSignal()
    help_signal = pyqtSignal()
    about_signal = pyqtSignal()

    def __init__(self, parent=None, title="", size=QSize(1100, 800)):
        # 控件
        self.ICO = QPixmap.fromImage(ICO_IMAGE)
        self.TIP = QPixmap.fromImage(TIP_IMAGE)
        self.ico_lb = QLabel()
        self.tip_lb = QLabel()
        self.center_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.left_widget_main = QWidget()
        self.left_grid_layout = QGridLayout()
        self.title = _MyLabel("欢迎使用 NavalArt 船体编辑器", font=YAHEI[20])
        self.buttons = {
            "上次编辑": QPushButton("上次编辑"),
            "新建工程": QPushButton("新建工程"),
            "打开工程": QPushButton("打开工程"),
            "设置": QPushButton("设置"),
            "帮助": QPushButton("帮助"),
            "关于": QPushButton("关于"),
        }
        self.Hei = size.height()
        self.Wid = size.width()
        self.__set_layout()
        # 颜色动效
        self.ico_color_animation = None
        super().__init__(parent, (10, 10, 116, 116), title, size, self.center_layout, hide_bottom=True)
        self.hide()
        # 图标
        self.ICO = QPixmap.fromImage(ICO_IMAGE)
        self.setWindowIcon(QIcon(self.ICO))
        # 事件绑定
        self.__connect_funcs()
        # 动画
        # 窗口透明度
        self.animation_opacity = QPropertyAnimation(self.parent(), b"windowOpacity")
        self.animation_opacity.setStartValue(0)
        self.animation_opacity.setEndValue(1)
        # 窗口位置（从右下）
        self.animation_geometry = QPropertyAnimation(self, b"geometry")
        self.animation_geometry.setStartValue(QRect(self.x() + 100, self.y() + 100, 0, 0))
        self.animation_geometry.setEndValue(QRect(self.x(), self.y(), self.Wid, self.Hei))
        self.animations = [self.animation_opacity, self.animation_geometry]

    def show(self):
        super().show()
        self.__emergeAnimation()

    def __set_layout(self):
        """
        设置布局
        :return:
        """
        self.center_layout.addWidget(self.title)
        self.title.setAlignment(Qt.AlignCenter)
        self.center_layout.addLayout(self.main_layout)
        self.main_layout.addWidget(self.left_widget, stretch=2, alignment=Qt.AlignTop)
        self.main_layout.addWidget(self.right_widget, stretch=1, alignment=Qt.AlignTop)
        self.left_widget.setLayout(self.left_layout)
        self.right_widget.setLayout(self.right_layout)
        self.left_widget.setFixedHeight(self.Hei - 120)
        self.right_widget.setFixedHeight(self.Hei - 120)
        self.center_layout.setContentsMargins(70, 25, 70, 0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setContentsMargins(5, 10, 5, 0)
        self.right_layout.setContentsMargins(5, 30, 5, 0)
        self.main_layout.setSpacing(30)
        self.left_layout.setSpacing(10)
        self.right_layout.setSpacing(22)
        self.__set_left_layout()
        self.__set_right_layout()

    def __set_left_layout(self):
        """
        设置左侧布局
        :return:
        """
        self.left_layout.setAlignment(Qt.AlignTop)
        # 主要控件
        self.left_layout.addWidget(self.left_widget_main, stretch=1)
        self.__set_left_widget_main()
        # 添加文本
        _text = "   NavalArt 船体编辑器，是一款基于颜色选取的船体编辑器。" \
                "我们深知在 NavalArt 游戏内部编辑船体的痛点，" \
                "因此我们开发了这款船体编辑器，希望能够帮助到大家。\n" \
                "   我们将持续更新，如果您有任何建议，请联系我们："
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        # 设置边距
        text_edit.setFixedHeight(145)
        text_edit.setFrameShape(QFrame.NoFrame)
        text_edit.setFrameShadow(QFrame.Plain)
        text_edit.setLineWidth(0)
        # 设置样式
        cursor = text_edit.textCursor()
        block_format = QTextBlockFormat()
        block_format.setLineHeight(125, QTextBlockFormat.ProportionalHeight)  # 设置行间距
        block_format.setIndent(0)  # 设置首行缩进
        # 应用段落格式到文本游标
        cursor.setBlockFormat(block_format)
        cursor.insertText(_text)
        text_edit.setTextCursor(cursor)
        # 光标不变
        text_edit.setFocusPolicy(Qt.NoFocus)
        # 解绑事件
        text_edit.wheelEvent = lambda event: None
        text_edit.mousePressEvent = lambda event: None
        text_edit.mouseMoveEvent = lambda event: None
        text_edit.mouseReleaseEvent = lambda event: None
        # 取消滚动条
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setStyleSheet(
            f"background-color: {BG_COLOR0};"
            f"color: {GRAY};"
            f"padding-left: 22px;"
            f"padding-right: 22px;"
            f"padding-top: 10px;"
            f"padding-bottom: 5px;"
            f"border-top-left-radius: 0px;"
            f"border-top-right-radius: 0px;"
            f"border-bottom-left-radius: 35px;"
            f"border-bottom-right-radius: 35px;"
        )
        text_edit.setFont(YAHEI[11])
        # 添加布局
        self.left_layout.addWidget(text_edit)
        self.left_layout.addLayout(self.left_grid_layout)
        self.__set_left_down_grid_layout()

    def __set_left_widget_main(self):
        """
        设置左侧主要控件
        :return:
        """
        left_widget_main_layout = QHBoxLayout()
        self.left_widget_main.setLayout(left_widget_main_layout)
        left_widget_main_layout.setContentsMargins(0, 20, 0, 0)
        left_widget_main_layout.setSpacing(10)
        left_widget_main_layout.setAlignment(Qt.AlignCenter)
        #
        main_inner_widget = QWidget()
        main_inner_layout = QVBoxLayout()
        main_inner_layout.setAlignment(Qt.AlignCenter)
        main_inner_layout.setContentsMargins(20, 20, 20, 0)
        main_inner_layout.setSpacing(10)
        main_inner_widget.setLayout(main_inner_layout)
        main_inner_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_inner_widget.setStyleSheet(
            f"background-color: {BG_COLOR0};"
            f"border-top-left-radius: 55px;"
            f"border-top-right-radius: 55px;"
            f"border-bottom-left-radius: 0px;"
            f"border-bottom-right-radius: 0px;"
        )
        left_widget_main_layout.addWidget(main_inner_widget)
        # 赞赏二维码
        # 对二维码圆角化处理
        br_tip = _create_rounded_thumbnail(self.TIP, 300, 300, 45)
        self.tip_lb.setPixmap(br_tip)
        self.tip_lb.setFixedSize(300, 300)
        self.tip_lb.setStyleSheet(
            f"background-color: transparent;"
            f"border-radius: 45px;"
        )
        main_inner_layout.addWidget(self.tip_lb, alignment=Qt.AlignCenter)
        main_inner_layout.addWidget(_MyLabel("赞赏二维码", font=YAHEI[13]), alignment=Qt.AlignCenter)

    def __set_left_down_grid_layout(self):
        email_text = _MyLabel("E-mail：", font=YAHEI[10])
        email_content = _MyLabel("2593292614@qq.com", font=YAHEI[10])
        bilibili_text = _MyLabel("哔哩哔哩：", font=YAHEI[10])
        bilibili_content = _MyLabel("咕咕的园艏", font=YAHEI[10])
        # 添加下划线
        email_content.setFrameShape(QFrame.HLine)
        bilibili_content.setFrameShape(QFrame.HLine)
        # 绑定网页
        email_content.setToolTip("单击打开邮箱")
        bilibili_content.setToolTip("单击打开主页")
        bilibili_url = "https://space.bilibili.com/507183077?spm_id_from=333.1007.0.0"
        email_url = "mailto:2593292614@qq.com"
        email_content.mousePressEvent = open_url(email_url)
        bilibili_content.mousePressEvent = open_url(bilibili_url)
        # 设置样式
        styleSheet = f"""
            color: {GRAY};
            background-color: {BG_COLOR1};
            border-radius: 10px;
        """
        # 设置鼠标悬停样式
        hover_styleSheet = f"""
            color: #00FFFF;
            background-color: {BG_COLOR1};
            border-radius: 10px;
        """
        email_text.setStyleSheet(styleSheet)
        bilibili_text.setStyleSheet(styleSheet)
        email_content.setStyleSheet(styleSheet)
        bilibili_content.setStyleSheet(styleSheet)
        email_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        bilibili_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        email_content.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        bilibili_content.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        email_content.setFixedSize(230, 23)
        bilibili_content.setFixedSize(230, 23)
        email_content.setCursor(Qt.PointingHandCursor)
        bilibili_content.setCursor(Qt.PointingHandCursor)
        email_content.enterEvent = lambda event: email_content.setStyleSheet(hover_styleSheet)
        email_content.leaveEvent = lambda event: email_content.setStyleSheet(styleSheet)
        bilibili_content.enterEvent = lambda event: bilibili_content.setStyleSheet(hover_styleSheet)
        bilibili_content.leaveEvent = lambda event: bilibili_content.setStyleSheet(styleSheet)
        # 添加布局
        self.left_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.left_grid_layout.setSpacing(5)
        self.left_grid_layout.setAlignment(Qt.AlignCenter)
        self.left_grid_layout.addWidget(email_text, 0, 0)
        self.left_grid_layout.addWidget(email_content, 0, 1)
        self.left_grid_layout.addWidget(bilibili_text, 1, 0)
        self.left_grid_layout.addWidget(bilibili_content, 1, 1)

    def __set_right_layout(self):
        """
        设置右侧布局
        :return:
        """
        # 添加图标大图
        self.ico_lb.setPixmap(self.ICO)
        self.ico_lb.setAlignment(Qt.AlignCenter)
        self.ico_lb.setFixedSize(254, 254)
        self.ico_lb.setStyleSheet(f"background-color: #889998;"
                                  f"border-radius: 50px;")
        # 添加布局
        self.right_layout.addWidget(self.ico_lb, alignment=Qt.AlignCenter)
        # 文字
        _font = YAHEI[12]
        for button in self.buttons.values():
            self.right_layout.addWidget(button, alignment=Qt.AlignCenter)
            button.setFont(_font)
            button.setFixedSize(256, 33)
            # 设置左边间隔
            button.setStyleSheet(f"""
                QPushButton{{
                    background-color:{BG_COLOR0};
                    color:{FG_COLOR0};
                    border-radius: 12px;
                    border: 0px;
                }}
                QPushButton:hover{{
                    background-color:{BG_COLOR3};
                    color:{FG_COLOR0};
                    border-radius: 12px;
                    border: 0px;
                }}
                QPushButton:pressed{{
                    background-color:{BG_COLOR1};
                    color:{FG_COLOR0};
                    border-radius: 12px;
                    border: 0px;
                }}
            """)
        self.right_widget.setStyleSheet(f"background-color: {BG_COLOR1};color: {FG_COLOR0};")
        self.right_layout.addStretch(2)

    # noinspection PyUnresolvedReferences
    def __connect_funcs(self):
        """
        连接按键到信号，链接tooltip
        :return:
        """
        self.buttons["上次编辑"].clicked.connect(self.lastEdit_signal.emit)
        self.buttons["新建工程"].clicked.connect(self.newPrj_signal.emit)
        self.buttons["打开工程"].clicked.connect(self.openPrj_signal.emit)
        self.buttons["设置"].clicked.connect(self.setting_signal.emit)
        self.buttons["帮助"].clicked.connect(self.help_signal.emit)
        self.buttons["关于"].clicked.connect(self.about_signal.emit)

        # self.buttons["上次编辑"].setToolTip("打开您上次编辑的项目")
        # self.buttons["新建工程"].setToolTip("新建船体工程")
        # self.buttons["打开工程"].setToolTip("打开您已有的船体工程")
        # self.buttons["设置"].setToolTip("基础操作设置")
        # self.buttons["帮助"].setToolTip("打开新手教程")
        # self.buttons["关于"].setToolTip("了解开发计划、作者信息等")

    def __emergeAnimation(self):
        for a in self.animations:
            a.setDuration(200)
            a.start()

    def __closeAnimation(self):
        self.animation_opacity.setDuration(100)
        self.animation_opacity.setDirection(QAbstractAnimation.Backward)
        self.animation_opacity.start()

    def close(self):
        self.__closeAnimation()
        self.animation_opacity.finished.connect(super().close)
