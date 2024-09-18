# -*- coding: utf-8 -*-
"""
定义一些常用的布局
"""
from abc import abstractmethod
from typing import Literal, Optional, List, Dict

from .buttons import *


from utils.funcs_utils import color_print, operationMutexLock
from utils.const import CONST


def get_distance(pos1: QPoint, pos2: QPoint) -> float:
    """
    计算两个点之间的距离
    :param pos1:
    :param pos2:
    :return:
    """
    return ((pos1.x() - pos2.x()) ** 2 + (pos1.y() - pos2.y()) ** 2) ** 0.5


class TabButton(Button):
    def __init__(self, tab: '_MutiDirectionTab', image: QImage, tool_tip, bd_radius=7):
        """
        可拖动的按钮
        :param tab: 所属的Tab
        :param image:
        :param tool_tip:
        :param bd_radius:
        :return:
        """
        super().__init__(None, tool_tip, 0, BG_COLOR1, bd_radius, bg=(BG_COLOR1, BG_COLOR3, GRAY, BG_COLOR3),
                         size=28)
        # 状态
        self.click_pos = None
        # 处理参数
        if isinstance(bd_radius, int):
            bd_radius = [bd_radius] * 4
        # 设置样式
        self.setIcon(QIcon(QPixmap(image)))
        self.setFocusPolicy(Qt.NoFocus)
        self.setFlat(True)
        self.tab: _MutiDirectionTab = tab
        self.bd_radius = bd_radius
        # 阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setBlurRadius(20)
        # 临时按钮，用于拖动显示
        self._temp_button = Button(None, None, 0, BG_COLOR1, bd_radius,
                                   bg=(GRAY, BG_COLOR3, GRAY, BG_COLOR3), size=28, alpha=0.6)
        self.init_temp_button()
        self._temp_button.setIcon(QIcon(QPixmap(image)))

    def init_temp_button(self):
        self._temp_button.setVisible(False)
        self._temp_button.setWindowFlags(Qt.FramelessWindowHint)
        self._temp_button.setAttribute(Qt.WA_TranslucentBackground)
        self._temp_button.setFocusPolicy(Qt.NoFocus)
        self._temp_button.setFlat(True)
        self._temp_button.setGraphicsEffect(self.shadow)

    def mousePressEvent(self, event):
        """
        先改变状态，变为可拖动状态，不立即开始拖动状态，在主控件中判断：当有一定距离后再开始拖动。
        然后将可拖动tab的信息传递给全局.
        注意，当鼠标按下按钮，只有按钮的 mousePressEvent 会被调用。
        :param event:
        :return:
        """
        super().mousePressEvent(event)
        self.click_pos = event.globalPos()
        _MutiDirectionTab._MutiDirectionTab__draggable_tab = self.tab

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)  # 将事件传递给父控件
        if get_distance(self.click_pos, event.globalPos()) < 25:
            tabFrame = self.tab.main_widget_with_multidir.TabWidgetMap[self.tab.direction]
            tabFrame.change_tab(self.tab)
            if hasattr(self, 'func_'):
                self.func_()

    def start_dragging(self):
        """ 开始拖动，修改状态量 """
        self._temp_button.setVisible(True)

    def move_temp_bt(self, pos):
        """ 移动临时按钮 """
        self._temp_button.move(pos)

    def end_dragging(self):
        """ 结束拖动，修改状态量 """
        self.click_pos = None
        self._temp_button.setVisible(False)
        self._temp_button.move(self.mapToGlobal(QPoint(0, 0)))
        QCoreApplication.processEvents()  # noqa  # 刷新界面


class ButtonGroup:
    def __init__(self, buttons: List[QPushButton] = None, default_index: int = 0):
        """
        按钮组，只能有一个按钮被选中
        :param buttons:
        :param default_index:
        """
        self.operationMutex = QMutex()
        if buttons:
            self.buttons = buttons
            for button in buttons:
                button.setFocusPolicy(Qt.NoFocus)
                button.setCheckable(True)
                button.setChecked(False)
                button.clicked.connect(lambda: self.button_clicked(button))
            buttons[default_index].setChecked(True)
            self.current = buttons[default_index]
        else:
            self.buttons = []
            self.current = None

    def __str__(self):
        return f"ButtonGroup: {len(self.buttons)} buttons, current: {self.current}"

    @operationMutexLock
    def button_clicked(self, button: QPushButton):
        """
        按钮被点击时，更新当前按钮
        :param button:
        :return:
        """

        if button not in self.buttons:
            color_print(f"[WARNING] Clicked Button {button} not in <{self}>.", "red")
            return False
        if self.current is not None:
            self.current.setChecked(False)
        self.current = button
        self.current.setChecked(True)

    @operationMutexLock
    def add(self, button: QPushButton, setChecked=True):
        """
        添加按钮
        :param button: QPushButton
        :param setChecked: 是否激活
        :return:
        """
        button.setCheckable(True)
        button.setFocusPolicy(Qt.NoFocus)
        button.func_ = lambda: self.button_clicked(button)
        button.clicked.connect(button.func_)
        if button in self.buttons:
            color_print(f"[WARNING] Added Button {button} already in <{self}>.", "red")
            return False
        self.buttons.append(button)
        if setChecked:
            if self.current:
                self.current.setChecked(False)
            self.current = button
            self.current.setChecked(True)

    @operationMutexLock
    def remove(self, button: QPushButton):
        """
        移除按钮
        :param button:
        :return:
        """
        # 处理异常传入
        if button not in self.buttons:
            color_print(f"[WARNING] Removed Button {button} not in <{self}>.", "red")
            return False
        # 移除按钮
        self.buttons.remove(button)
        if hasattr(button, 'func_'):
            button.clicked.disconnect(button.func_)
        button.setChecked(False)
        if self.current == button:
            if self.buttons:
                self.current = self.buttons[-1]
                self.current.setChecked(True)
                self.current.update()
            else:
                self.current = None

    def clear(self):
        """
        清空
        """
        for button in self.buttons:
            button.setChecked(False)
            if hasattr(button, 'func_'):
                button.clicked.disconnect(button.func_)
        self.buttons.clear()
        self.current = None


class _MutiDirectionTab(QWidget):
    __draggable_tab: Optional['_MutiDirectionTab'] = None
    __dragging_tab: Optional['_MutiDirectionTab'] = None
    __dragging_button: Optional[TabButton] = None

    def __init__(self, main_widget_with_multidir, init_direction=CONST.RIGHT,
                 name: str = None, tool_tip="", image: QImage = None,
                 fg: Union[ThemeColor, str] = FG_COLOR0,
                 bd_radius: Union[int, Tuple[int, int, int, int]] = 0):
        """
        一个可各个方向拖动的单标签页
        """
        # 处理参数
        if isinstance(bd_radius, int):
            bd_radius = [bd_radius] * 4
        super().__init__(None)
        # self.setMouseTracking(True)
        self.name = name
        self.tool_tip = tool_tip
        self.direction = init_direction  # 当前位置
        self.main_widget_with_multidir = main_widget_with_multidir  # 父窗口
        # 按钮
        self._button = TabButton(self, image=image, tool_tip=name)
        # 设置样式
        self.setStyleSheet(f"""
            QWidget{{
                background-color: rgba(0,0,0,0);
                color: {fg};
                border: 0px solid {fg};
                border-top-left-radius: {bd_radius[0]}px;
                border-top-right-radius: {bd_radius[1]}px;
                border-bottom-right-radius: {bd_radius[2]}px;
                border-bottom-left-radius: {bd_radius[3]}px;
            }}
            QToolTip{{
                background-color: {BG_COLOR1};
                color: {FG_COLOR0};
                border: 1px solid {BG_COLOR2};
                border-radius: 4px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.hide()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._top_widget = QWidget()
        self.title_label = TextLabel(self, name, YAHEI[11], fg)
        self._drag_area = QWidget(self)
        self._main_widget = QFrame(None)
        self.main_layout: Union[
            None, QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout, QFormLayout, QLayout] = None
        self._scroll_area = ScrollArea(self, self._main_widget, None)
        self.top_layout = QHBoxLayout(self._top_widget)
        self.__init_layout()

    def __str__(self):
        return f"Tab: {self.name}"

    def __repr__(self):
        return f"Tab: {self.name}"

    @classmethod
    def _get_drag_result(cls) -> Tuple['_MutiDirectionTab', 'TabButton']:
        """
        :return: dragging_tab, dragging_button
        """
        return cls.__dragging_tab, cls.__dragging_button

    # noinspection PyProtectedMember
    @classmethod
    def _check_draggable(cls, globalPos: QPoint):
        if cls.__dragging_tab:
            return True

        elif cls.__draggable_tab and cls.__draggable_tab._button.click_pos:
            if get_distance(cls.__draggable_tab._button.click_pos, globalPos) > 35:
                cls._start_dragging_button()
                return True
        return False

    @classmethod
    def _start_dragging_button(cls):
        """
        开始拖动，修改状态量
        """
        cls.__dragging_tab = cls.__draggable_tab
        # noinspection PyProtectedMember
        cls.__dragging_button = cls.__draggable_tab._button
        cls.__dragging_button.start_dragging()
        # 禁用刷新
        center_w = cls.__draggable_tab.main_widget_with_multidir.center_widget
        if hasattr(center_w, 'enablePaint'):
            center_w.enablePaint(True)

    @classmethod
    def _end_dragging_button(cls):
        """
        结束拖动，修改状态量
        """
        if cls.__dragging_button:
            cls.__dragging_button.end_dragging()
            cls.__dragging_button = None
        cls.__draggable_tab = None
        cls.__dragging_tab = None

    def __init_layout(self):
        self._layout.setAlignment(Qt.AlignTop)
        self.title_label.setFixedHeight(26)
        self.__init_top_widget()
        self.__init_scroll_area()

    def __init_top_widget(self):
        self._layout.setContentsMargins(10, 5, 10, 10)
        self._layout.setSpacing(0)
        self._layout.addWidget(self._top_widget)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.top_layout.addWidget(self.title_label, Qt.AlignLeft | Qt.AlignVCenter)
        self.top_layout.addWidget(self._drag_area, Qt.AlignRight | Qt.AlignVCenter)
        self._top_widget.setToolTip(self.tool_tip)
        self.__init_drag_area()
        self.init_top_widget()

    @abstractmethod
    def init_top_widget(self):
        """
        客制化添加顶栏控件
        :return:
        """
        ...

    def __init_drag_area(self):
        # 添加拖动条，控制窗口大小
        self._drag_area.setFixedWidth(16777215)
        self._drag_area.setStyleSheet("background-color: rgba(0,0,0,0)")
        self._drag_area.mouseMoveEvent = self._button.mouseMoveEvent
        self._drag_area.mousePressEvent = self._button.mousePressEvent
        self._drag_area.mouseReleaseEvent = self._button.mouseReleaseEvent

    def __init_scroll_area(self):
        self._layout.addWidget(self._scroll_area)
        self._main_widget.setContentsMargins(0, 0, 0, 0)
        self._main_widget.setStyleSheet("background-color: rgba(0,0,0,0)")

    @classmethod
    def _draw_temp_button(cls):
        """
        绘制拖动时的半透明小按钮
        """
        bt = cls.__dragging_button
        if not bt or not bt.click_pos:
            color_print(f"[WARNING] No dragging button or no click pos while drawing", "red")
        # 直接令鼠标位置为按钮中心，不考虑起始位置
        new_pos = QCursor().pos() - QPoint(14, 14)
        bt.move_temp_bt(new_pos)


class MutiDirectionTab(_MutiDirectionTab):
    def __init__(self, main_widget_with_multidir, init_direction=CONST.RIGHT,
                 name: str = None, tool_tip="", image: QImage = None):
        super().__init__(main_widget_with_multidir, init_direction, name, tool_tip, image)

    def set_layout(self, layout: QLayout):
        """
        将布局属性 main_layout 赋值并绑定到私有控件
        :param layout: QLayout
        """
        self.main_layout = layout
        self._main_widget.setLayout(layout)

    def change_layout(self, direction):
        """
        根据方向改变布局
        """
        ...

    @abstractmethod
    def init_top_widget(self):
        ...


class FreeTabFrame(QFrame):
    _StyleSheet = f"""
        QFrame{{
            background-color: rgba(0,0,0,0);
            color: {FG_COLOR0};
            border: 1px solid {BG_COLOR1};
        }}
    """
    _lb = ThemeColor(LIGHTER_BLUE).rgb
    _DraggedInStyleSheet = f"""
        QFrame{{
            background-color: rgba({_lb[0]}, {_lb[1]}, {_lb[2]}, 0.3);
            color: {FG_COLOR0};
            border: 1px solid {LIGHTER_BLUE};
        }}
    """
    ALIGN_MAP = {CONST.LEFT: Qt.AlignLeft | Qt.AlignVCenter, CONST.RIGHT: Qt.AlignRight | Qt.AlignVCenter,
                 CONST.UP: Qt.AlignTop | Qt.AlignHCenter, CONST.DOWN: Qt.AlignBottom | Qt.AlignHCenter}
    LAYOUT_MAP = {CONST.LEFT: QHBoxLayout, CONST.RIGHT: QHBoxLayout, CONST.UP: QVBoxLayout, CONST.DOWN: QVBoxLayout}
    all_tabFrames: List['FreeTabFrame'] = []
    dragged_in_frame: Union['FreeTabFrame', None] = None

    def __init__(self, direction, bt_widget, bt_direction: Literal['left', 'right', 'up', 'down'],
                 multi_direction_tab=None):
        """
        一个内容标签可自由拖动的标签页
        （请不要将QFrame改为QWidget，否则样式会受到影响！）
        :param bt_widget: 装按钮的容器，无需初始化布局
        :param bt_direction: 按钮容器的布局方向，为 CONST.LEFT/RIGHT/UP/DOWN
        :param multi_direction_tab: 所属的 MultiDirTabMainFrame
        """
        self.multi_direction_main_frame: Union[MultiDirTabMainFrame, None] = multi_direction_tab
        self.Direction = direction
        super().__init__(None)
        # 状态变量
        self.dragged_in = False  # 是否被拖入
        self.current_tab = None
        self.all_tabs = []
        # 控件
        self.button_group = ButtonGroup()
        self.bt_widget = bt_widget
        self.bt_direction = bt_direction
        self.bt_widget_layout: QLayout = FreeTabFrame.LAYOUT_MAP[bt_direction](self.bt_widget)
        self.bt_widget_layout.setAlignment(FreeTabFrame.ALIGN_MAP[bt_direction])
        self.bt_widget_layout.setContentsMargins(0, 5, 0, 5)
        self.bt_widget_layout.setSpacing(5)
        # 临时控件，用于拖动时显示
        self._temp_button_frame = QFrame(self.bt_widget)
        self._temp_button_frame.hide()
        self._init_temp_widget()
        # 布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setStyleSheet(FreeTabFrame._StyleSheet)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        FreeTabFrame.all_tabFrames.append(self)

    def __str__(self):
        return f"TabFrame: {self.Direction}: {self.all_tabs}"

    def __repr__(self):
        return f"TabFrame: {self.Direction}: {self.all_tabs}"

    def _init_temp_widget(self):
        self._temp_button_frame.setFixedSize(28, 28)
        self._temp_button_frame.setStyleSheet(f"""
            QFrame{{
                background-color: rgba({self._lb[0]}, {self._lb[1]}, {self._lb[2]}, 0.3);
                color: {FG_COLOR0};
                border: 1px solid {LIGHTER_BLUE};
                border-radius: 0px;
            }}
        """)

    def return_normal_style(self):
        if not self.all_tabs:
            self.setVisible(False)
        self.dragged_in = False
        self._temp_button_frame.hide()
        self.setStyleSheet(self._StyleSheet)

    def dragged_in_style(self):
        if not self.all_tabs:
            self.setVisible(True)
        self.dragged_in = True
        self.bt_widget_layout.addWidget(self._temp_button_frame)
        self._temp_button_frame.show()
        self.setStyleSheet(self._DraggedInStyleSheet)

    # noinspection PyProtectedMember
    def add_tab(self, tab: _MutiDirectionTab):
        """
        添加标签页
        :param tab:
        :return:
        """
        if not self.multi_direction_main_frame:
            return
        tab.direction = self.Direction
        self.bt_widget_layout.addWidget(tab._button)
        self.layout.addWidget(tab)
        if not self.all_tabs:
            tab.show()
            self.current_tab = tab
            self.button_group.add(tab._button)
        else:
            self.button_group.add(tab._button, False)
        self.all_tabs.append(tab)
        tab._button.show()

    # noinspection PyProtectedMember
    def remove_tab(self, tab: _MutiDirectionTab):
        """
        移除标签页
        :param tab:
        :return:
        """
        self.button_group.remove(tab._button)
        tab.direction = None
        self.bt_widget_layout.removeWidget(tab._button)
        self.layout.removeWidget(tab)
        self.all_tabs.remove(tab)
        if self.current_tab == tab:
            if self.all_tabs:
                self.current_tab = self.all_tabs[-1]
                self.current_tab.show()
            else:
                self.current_tab = None
                self.hide()
        tab.hide()
        tab._button.hide()

    def change_tab(self, tab: _MutiDirectionTab):
        """
        切换标签页
        :param tab:
        :return:
        """
        if tab not in self.all_tabs:
            color_print(f"[WARNING] {tab} not in <{self}>.", "red")
            # 到其他FreeTabFrame寻找
            for frame in FreeTabFrame.all_tabFrames:
                if tab in frame.all_tabs:
                    frame.change_tab(tab)
        if self.current_tab:
            self.current_tab.hide()
            # noinspection PyProtectedMember
            self.current_tab._button.setChecked(False)
        self.current_tab = tab
        # noinspection PyProtectedMember
        tab._button.click_pos = None
        tab.show()
        # noinspection PyProtectedMember
        tab._button.setChecked(True)


class MultiDirTabMainFrame(QFrame):
    def __init__(self, center_frame: QWidget):
        """
        一个带有多个可各个方向拖动的标签的窗口；
        下方的标签占据整个窗口宽度
        """
        super().__init__(None)
        self.setMouseTracking(True)
        self.center_widget = center_frame
        # 总布局
        self.layout = QHBoxLayout(self)
        self.spliterL, self.spliterR = VerSpliter(self), VerSpliter(self)
        # Spliter
        self.ver_spliter = Splitter(Qt.Horizontal)  # 垂直分割器，用于分割左右两个TabWidget
        self.hor_spliter = Splitter(Qt.Vertical)  # 水平分割器，用于分割中间的控件和下方的TabWidget
        # 按钮容器
        self.left_bt_layout = QVBoxLayout()  # 左侧按钮容器
        self.left_up_bt_frame = QFrame(self)  # 用于 left_tab_widget 的按钮
        self.left_down_bt_frame = QFrame(self)  # 用于 down_tab_widget 的按钮
        self.right_bt_frame = QFrame(self)  # 用于 right_tab_widget 的按钮
        # TabWidgets
        self.down_tab_frame = FreeTabFrame(CONST.DOWN, self.left_down_bt_frame, CONST.DOWN, self)
        self.left_tab_frame = FreeTabFrame(CONST.LEFT, self.left_up_bt_frame, CONST.UP, self)
        self.right_tab_frame = FreeTabFrame(CONST.RIGHT, self.right_bt_frame, CONST.UP, self)
        self.TabWidgetMap: Dict[Literal['left', 'right', 'down'], FreeTabFrame] = {
            CONST.LEFT: self.left_tab_frame, CONST.RIGHT: self.right_tab_frame,
            CONST.DOWN: self.down_tab_frame
        }
        self.init_ui()

    def init_ui(self):
        self.ver_spliter.addWidget(self.left_tab_frame)
        self.ver_spliter.addWidget(self.center_widget)
        self.ver_spliter.addWidget(self.right_tab_frame)
        self.hor_spliter.addWidget(self.ver_spliter)
        self.hor_spliter.addWidget(self.down_tab_frame)

        self.ver_spliter.setStretchFactor(0, 0)
        self.ver_spliter.setStretchFactor(1, 1)
        self.ver_spliter.setStretchFactor(2, 0)
        self.hor_spliter.setStretchFactor(0, 1)
        self.hor_spliter.setStretchFactor(1, 0)

        self.layout.addLayout(self.left_bt_layout)
        self.layout.addWidget(self.spliterL)
        self.layout.addWidget(self.hor_spliter)
        self.layout.addWidget(self.spliterR)
        self.layout.addWidget(self.right_bt_frame)

        for frm in [self.left_up_bt_frame, self.left_down_bt_frame]:
            frm.mouseMoveEvent = self.mouseMoveEvent
            frm.mousePressEvent = self.mousePressEvent
            frm.mouseReleaseEvent = self.mouseReleaseEvent
        self.left_bt_layout.addWidget(self.left_up_bt_frame, stretch=3)
        self.left_bt_layout.addWidget(self.left_down_bt_frame, stretch=1)

        self.left_up_bt_frame.setFixedWidth(36)
        self.left_down_bt_frame.setFixedWidth(36)
        self.right_bt_frame.setFixedWidth(36)
        self.layout.setSpacing(0)
        self.left_bt_layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.left_bt_layout.setContentsMargins(0, 0, 0, 0)
        self.left_up_bt_frame.setContentsMargins(0, 0, 0, 0)
        self.left_down_bt_frame.setContentsMargins(0, 0, 0, 0)
        self.right_bt_frame.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

    def add_tab(self, tab: _MutiDirectionTab):
        """
        添加标签页
        :param tab:
        :return:
        """
        self.TabWidgetMap[tab.direction].add_tab(tab)

    def __move_tab(self, tab: _MutiDirectionTab, orgin_dir: Literal['left', 'right', 'down'],
                   target_dir: Literal['left', 'right', 'down']):
        """
        移动标签页
        """
        tab.is_operating = False
        self.TabWidgetMap[orgin_dir].remove_tab(tab)
        self.TabWidgetMap[target_dir].add_tab(tab)

    def hide_tabFrame(self, direction: Literal['left', 'right', 'down']):
        ...

    def remove_tab(self, tab: _MutiDirectionTab):
        """
        移除标签页
        :param tab:
        :return:
        """
        self.TabWidgetMap[tab.direction].remove_tab(tab)
        self.update()

    def __update_in_area(self):
        """
        检查鼠标释放时的区域
        """
        tabFrame_default_area = {
            self.left_tab_frame: QRect(0, 0, int(self.width() * 0.25), int(self.height() * 0.75)),
            self.right_tab_frame: QRect(int(self.width() * 0.75), 0, int(self.width() * 0.25),
                                        int(self.height() * 0.75)),
            self.down_tab_frame: QRect(0, int(self.height() * 0.75), self.width(), int(self.height() * 0.25))
        }
        pos = QCursor().pos()
        for tw in (self.left_tab_frame, self.right_tab_frame, self.down_tab_frame):
            btw = tw.bt_widget
            if not tw.all_tabs:
                if tabFrame_default_area[tw].contains(pos - tw.parent().mapToGlobal(QPoint(0, 0))):
                    return tw
            if tw.geometry().contains(pos - tw.parent().mapToGlobal(QPoint(0, 0))):
                return tw
            elif btw.geometry().contains(pos - btw.parent().mapToGlobal(QPoint(0, 0))):
                return tw
        return None

    def __button_move(self):
        FreeTabFrame.dragged_in_frame = self.__update_in_area()
        for tw in [self.left_tab_frame, self.right_tab_frame, self.down_tab_frame]:
            if tw == FreeTabFrame.dragged_in_frame and not tw.dragged_in:
                tw.dragged_in_style()
            elif tw != FreeTabFrame.dragged_in_frame and tw.dragged_in:
                tw.return_normal_style()
        # noinspection PyProtectedMember
        _MutiDirectionTab._draw_temp_button()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        return super().eventFilter(obj, event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() == Qt.LeftButton:
            # noinspection PyProtectedMember
            if _MutiDirectionTab._check_draggable(event.globalPos()):
                self.__button_move()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            # noinspection PyProtectedMember
            tab, bt = _MutiDirectionTab._get_drag_result()
            if bt and FreeTabFrame.dragged_in_frame:
                tar_dir = FreeTabFrame.dragged_in_frame.Direction
                if tab.direction != tar_dir:
                    # tabFrame之间交换tab
                    self.__move_tab(tab, tab.direction, tar_dir)
                # 恢复样式
                tar_tabFrame = self.TabWidgetMap[tar_dir]
                tar_tabFrame.return_normal_style()
            FreeTabFrame.dragged_in_frame = None
            # 启用刷新
            if hasattr(self.center_widget, 'enablePaint'):
                self.center_widget.enablePaint(True)
        # noinspection PyProtectedMember
        _MutiDirectionTab._end_dragging_button()
        self.update()
        QApplication.processEvents()


class TabWidget(QTabWidget):
    def __init__(self, parent, position=QTabWidget.North):
        """
        一个可各个方向拖动的标签页
        """
        super().__init__(parent=parent)
        # 设置标签页
        # self.setDocumentMode(True)
        self.setTabPosition(position)
        self.setMovable(True)
        # 设置标签栏向下对齐
        self.bdr = 15
        self.tab_bdr = 8
        padding = 3
        margin = 3
        min_width_or_height = 22
        radius_pos1 = 'top-left'
        radius_pos2 = 'top-right'
        width_or_height = 'width'
        tab_bottom_side = 'bottom'
        radius_pos3 = 'top-right'
        margin_side = 'right'
        if position == QTabWidget.South:
            radius_pos1 = 'bottom-left'
            radius_pos2 = 'bottom-right'
            tab_bottom_side = 'top'
            radius_pos3 = 'bottom-right'
        elif position == QTabWidget.West:
            radius_pos1 = 'top-left'
            radius_pos2 = 'bottom-left'
            width_or_height = 'height'
            tab_bottom_side = 'right'
            radius_pos3 = 'bottom-left'
            margin_side = 'bottom'
        elif position == QTabWidget.East:
            radius_pos1 = 'top-right'
            radius_pos2 = 'bottom-right'
            width_or_height = 'height'
            tab_bottom_side = 'left'
            radius_pos3 = 'bottom-right'
            margin_side = 'bottom'
        self.setStyleSheet(f"""
            QTabWidget::pane{{
                border: 1px solid transparent;
                border-{radius_pos1}-radius: {self.bdr}px;
                border-{radius_pos2}-radius: {self.bdr}px;
                border-{radius_pos3}-radius: {self.bdr}px;
                background-color: {BG_COLOR1};
            }}
            QTabBar::tab{{
                background-color:{BG_COLOR0};
                color:{FG_COLOR0};
                border-{radius_pos1}-radius: {self.tab_bdr}px;
                border-{radius_pos2}-radius: {self.tab_bdr}px;
                padding: {padding}px;
                margin-{margin_side}: {margin}px;
                min-{width_or_height}: {min_width_or_height}ex;
                border-{tab_bottom_side}:1px solid {BG_COLOR1};
            }}
            QTabBar::tab:selected{{
                background-color:{BG_COLOR3};
                color:{FG_COLOR0};
                border-{radius_pos1}-radius: {self.tab_bdr}px;
                border-{radius_pos2}-radius: {self.tab_bdr}px;
                padding: {padding}px;
                margin-{margin_side}: {margin}px;
                min-{width_or_height}: {min_width_or_height}ex;
                border-{tab_bottom_side}:0px solid {DARKER_RED};
            }}
            QTabBar::tab:hover{{
                background-color:{BG_COLOR2};
                color:{FG_COLOR0};
                border-{radius_pos1}-radius: {self.tab_bdr}px;
                border-{radius_pos2}-radius: {self.tab_bdr}px;
                padding: {padding}px;
                margin-{margin_side}: {margin}px;
                min-{width_or_height}: {min_width_or_height}ex;
                border-{tab_bottom_side}:1px solid {GRAY};
            }}
        """)
        self.setFont(YAHEI[9])

    def addTab(self, widget, a1):
        super().addTab(widget, a1)
        radius_pos1 = 'bottom-left'
        radius_pos2 = 'bottom-right'
        radius_pos3 = 'top-right'
        if self.tabPosition() == QTabWidget.South:
            radius_pos1 = 'top-left'
            radius_pos2 = 'top-right'
            radius_pos3 = 'bottom-right'
        elif self.tabPosition() == QTabWidget.West:
            radius_pos1 = 'top-right'
            radius_pos2 = 'bottom-right'
            radius_pos3 = 'bottom-left'
        elif self.tabPosition() == QTabWidget.East:
            radius_pos1 = 'top-left'
            radius_pos2 = 'bottom-left'
            radius_pos3 = 'bottom-right'
        widget.setStyleSheet(f"""
            QWidget{{
                background-color: {BG_COLOR0};
                color: {FG_COLOR0};
                border-{radius_pos1}-radius: {self.bdr}px;
                border-{radius_pos2}-radius: {self.bdr}px;
                border-{radius_pos3}-radius: {self.bdr}px;
            }}
        """)


class Window(QWidget):
    closed = pyqtSignal()  # noqa

    def __init__(
            self, parent, title: str, ico_bites: bytes, ico_size: int = 22, topH: int = 36, bottomH: int = 36,
            size: Tuple[int, int] = (1000, 618), show_maximize: bool = True, resizable: bool = True,
            font=YAHEI[10], bg: Union[str, ThemeColor] = BG_COLOR1, fg: Union[str, ThemeColor] = FG_COLOR0,
            bd_radius: Union[int, Tuple[int, int, int, int]] = 5,
            ask_if_close=True, transparent=False
    ):
        """
        提供带图标，顶栏，顶栏关闭按钮，底栏的窗口及其布局，
        其他的控件需要自己添加布局
        可以重载 init_top_widget, init_center_widget, init_bottom_widget 来自定义布局
        :param parent:
        :param title:
        :param ico_bites:
        :param ico_size:
        :param topH:
        :param bottomH:
        :param size:
        :param show_maximize:
        :param resizable:
        :param font:
        :param bg:
        :param fg:
        :param bd_radius:
        """
        super().__init__(parent)
        self.hide()
        # 处理参数
        if isinstance(bd_radius, int):
            bd_radius = [bd_radius] * 4
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框
        if transparent:
            self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self._init_size = size
        self.ask_if_close = ask_if_close
        # 基础样式
        self.setFont(font)
        # 设置边框阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setOffset(7)
        self.shadow.setColor(QColor(10, 10, 10, 70))
        self.shadow.setBlurRadius(50)
        self.setGraphicsEffect(self.shadow)
        # 设置非最大化的大小
        self.setFixedSize(QSize(size[0], size[1]))
        self.setMinimumSize(QSize(200, 200))
        self.setMaximumSize(QSize(WIN_WID, WIN_HEI))
        self.bg = bg
        self.fg = fg
        self.topH = topH
        self.bottomH = bottomH
        self.btWid = 60
        self.resizable = resizable
        self.title = title
        self.ico_size = ico_size
        self.bd_radius = bd_radius
        # 初始化控件
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.top_widget = QFrame(self)
        self.center_widget = QFrame(self)
        self.bottom_widget = QFrame(self)
        self.top_layout = QHBoxLayout(self.top_widget)
        self.center_layout = QHBoxLayout(self.center_widget)
        self.bottom_layout = QHBoxLayout(self.bottom_widget)
        # 图标和基础按钮
        self.ico_label = IconLabel(None, ico_bites, self.title, topH)
        self.close_button = CloseButton(None, bd_radius=self.bd_radius)
        self.cancel_button = CancelButton(None, bd_radius=self.bd_radius)
        self.ensure_button = EnsureButton(None, bd_radius=self.bd_radius)
        self.maximize_button = MaximizeButton(None)
        self.minimize_button = MinimizeButton(None)
        # 标题
        self.title_label = TextLabel(None, self.title, YAHEI[11], self.fg)
        # 其他可能用到的控件
        self.status_label = TextLabel(None, "", YAHEI[9], self.fg, align=Qt.AlignLeft | Qt.AlignVCenter)
        self.memory_widget = RatioDisplayWidget(0, 2048, "存储:", "M")
        # 自定义顶栏
        self.customized_top_widget = QWidget(self.top_widget)
        # 顶部拖动区域事件和窗口缩放事件
        self.drag_area = self.init_drag_area()
        # 状态
        self.move_flag = False
        self.resize_flag = False
        self.m_Position = None
        self.resize_dir = None
        self.init_ui()
        if self.resizable:
            self.setMouseTracking(True)
        # 动画
        self.animation = QPropertyAnimation(self, QByteArray(b"windowOpacity"))
        # 显示
        self.animate()
        if show_maximize:
            self.showMaximized()
        else:
            self.show()

    def init_ui(self):
        # 设置窗口阴影
        self.shadow.setOffset(5, 5)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setBlurRadius(25)
        self.setGraphicsEffect(self.shadow)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.top_widget, alignment=Qt.AlignTop)
        self.layout.addWidget(HorSpliter())
        self.layout.addWidget(self.center_widget, stretch=1)
        self.layout.addWidget(HorSpliter())
        self.layout.addWidget(self.bottom_widget, alignment=Qt.AlignBottom)
        for _layout in [self.top_layout, self.center_layout, self.bottom_layout]:
            _layout.setContentsMargins(0, 0, 0, 0)
            _layout.setSpacing(0)
        self.init_top_widget()
        self.init_center_widget()
        self.init_bottom_widget()
        self.bind_bt_funcs()

    def init_drag_area(self):
        # 添加拖动条，控制窗口大小
        drag_widget = QWidget(self)
        # 设置宽度最大化
        drag_widget.setFixedWidth(16777215)
        drag_widget.setStyleSheet("background-color: rgba(0,0,0,0)")
        drag_widget.mouseMoveEvent = self.mouseMoveEvent
        drag_widget.mousePressEvent = self.mousePressEvent
        drag_widget.mouseReleaseEvent = self.mouseReleaseEvent
        return drag_widget

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # 开始拖动窗口
        if event.button() == Qt.LeftButton and self.isMaximized() is False:
            if 5 < event.y() < self.topH:
                self.move_flag = True
                self.m_Position = event.globalPos() - self.pos()
            elif self.resizable:
                if event.y() < 5:
                    self.resize_dir = CONST.LEFT
                    self.resize_flag = True
                elif event.x() > self.height() - 5:
                    self.resize_dir = CONST.DOWN
                    self.resize_flag = True
                elif event.x() > self.width() - 5:
                    self.resize_dir = CONST.RIGHT
                    self.resize_flag = True
                elif event.y() < 5:
                    self.resize_dir = CONST.UP
                    self.resize_flag = True
                if self.resize_flag:
                    self.resize_flag = True
                    self.m_Position = event.globalPos() - self.pos()
                    event.accept()

    def mouseReleaseEvent(self, _):
        super().mouseReleaseEvent(_)
        # 停止拖动窗口
        self.setCursor(Qt.ArrowCursor)
        self.move_flag = False if self.move_flag else self.move_flag
        self.resize_flag = False if self.resize_flag else self.resize_flag
        self.m_Position = None
        self.resize_dir = None

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # 拖动窗口
        if Qt.LeftButton:
            if self.move_flag:
                self.move(event.globalPos() - self.m_Position)
                self.setCursor(Qt.ArrowCursor)
                event.accept()
            elif self.resizable:
                if event.x() < 5:
                    self.setCursor(Qt.SizeHorCursor)
                elif event.x() > self.height() - 5:
                    self.setCursor(Qt.SizeVerCursor)
                elif event.x() > self.width() - 5:
                    self.setCursor(Qt.SizeHorCursor)
                elif event.x() < 5:
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)
                if self.resize_flag:
                    if self.resize_dir == CONST.LEFT:
                        self.setGeometry(event.globalPos().x(), self.y(),
                                         self.width() + self.x() - event.globalPos().x(), self.height())
                    elif self.resize_dir == CONST.RIGHT:
                        self.setGeometry(self.x(), self.y(), event.globalPos().x() - self.x(), self.height())
                    elif self.resize_dir == CONST.UP:
                        self.setGeometry(self.x(), event.globalPos().x(), self.width(),
                                         self.height() + self.y() - event.globalPos().x())
                    elif self.resize_dir == CONST.DOWN:
                        self.setGeometry(self.x(), self.y(), self.width(), event.globalPos().x() - self.y())
                    QCoreApplication.processEvents()  # noqa  # 使窗口立即重绘
                    event.accept()

    def init_top_widget(self):
        self.top_widget.setFixedHeight(self.topH)
        self.customized_top_widget.setFixedHeight(self.topH)
        self.customized_top_widget.setLayout(QHBoxLayout())
        # 控件
        self.top_layout.addWidget(self.ico_label, Qt.AlignLeft | Qt.AlignVCenter)
        self.top_layout.addWidget(self.customized_top_widget, Qt.AlignLeft | Qt.AlignVCenter)
        self.top_layout.addWidget(self.drag_area, Qt.AlignLeft | Qt.AlignVCenter, stretch=1)
        self.top_layout.addWidget(self.title_label, Qt.AlignLeft | Qt.AlignVCenter)

    @abstractmethod
    def init_center_widget(self):
        """
        客制化添加中间控件，需要调用基类的方法
        """
        self.center_widget.setStyleSheet(f"""QWidget{{
            background-color: {self.bg};
            color: {self.fg};
        }}""")

    def init_bottom_widget(self):
        self.bottom_widget.setFixedHeight(self.bottomH)
        # 控件
        self.bottom_layout.addWidget(self.cancel_button, Qt.AlignRight | Qt.AlignVCenter)
        self.bottom_layout.addWidget(self.ensure_button, Qt.AlignRight | Qt.AlignVCenter)

    def bind_bt_funcs(self):
        self.close_button.clicked.connect(self.close)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maximize_button.clicked.connect(self.showMaximized)
        self.ensure_button.clicked.connect(self.ensure)
        self.cancel_button.clicked.connect(self.cancel)

    def ensure(self):
        self.close()

    def cancel(self):
        self.close()

    def close(self):
        if self.ask_if_close:
            reply = QMessageBox.question(self, '确认', '确认退出？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return False
        self.animate(1, 0, 100)
        while self.windowOpacity() > 0:
            QApplication.processEvents()
        self.closed.emit()
        super().close()

    def show_statu_(self, message, message_type: Literal['highlight', 'success', 'process', 'error'] = 'process'):
        color_map = {
            'highlight': 'orange',
            'success': f"{FG_COLOR0}",
            'process': f"{GRAY}",
            'error': f"{LIGHTER_RED}",
            'warning': f"{LIGHTER_RED}"
        }
        self.status_label.setStyleSheet(f"color: {color_map[message_type]};")
        self.status_label.setText(message)
        self.status_label.adjustSize()

    @classmethod
    def show_statu(cls, window: 'Window', message,
                   message_type: Literal['highlight', 'success', 'process', 'error'] = 'process'):
        window.show_statu_(message, message_type)

    def showMaximized(self):
        if self.resizable and not self.isMaximized():
            self.maximize_button.setIcon(QIcon(QPixmap.fromImage(NORMAL_IMAGE)))  # noqa
            super().showMaximized()
        else:
            self.maximize_button.setIcon(QIcon(QPixmap.fromImage(MAXIMIZE_IMAGE)))  # noqa
            super().showNormal()

    def animate(self, start=0, end=1, duration=200):
        self.animation.setDuration(duration)
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()
