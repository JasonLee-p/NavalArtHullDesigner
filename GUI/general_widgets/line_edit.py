
from typing import Union, Type, Tuple

from .other_widgets import TextLabel
from ._basic_data import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QLineEdit, QFrame, QGridLayout
from PyQt5.QtGui import *


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
    value_changed = pyqtSignal(float)  # 主动更改内容或滚轮滚动时触发，不会在撤回操作的时候触发  # noqa

    def __init__(
            self, parent, root_parent,
            size: Union[Tuple[int, int], Tuple[int, None], Tuple[None, int], None] = (68, 24),
            num_type: Union[Type[int], Type[float]] = int,
            num_range: tuple = (-100000, 100000),
            rounding: int = 0,
            default_value: Union[int, float] = 0,
            step: Union[int, float] = int(1),
            font=YAHEI[10],
            bg="transparent",
            tool_tip: str = None,
            padding=3
    ):
        """
        数字编辑器
        :param parent: 父对象
        :param root_parent: 根部件，用于刷新
        :param size: 尺寸
        :param num_type: 数字类型
        :param num_range: 数字范围
        :param rounding: 保留小数位数
        :param default_value: 默认值
        :param step: 步长
        :param font: 字体
        :param bg: 背景颜色
        :param tool_tip: 提示
        :param padding: 内边距
        """
        super().__init__(str(default_value), parent, tool_tip, font, bg, padding)
        self.update_mutex = QMutex()
        self.root_parent = root_parent
        self.num_type = num_type
        self.num_range = num_range
        self.rounding = None if self.num_type == int else rounding
        self.default_value = num_type(default_value)
        self.current_value: Union[int, float] = round(self.num_type(default_value), self.rounding) if self.rounding else int(default_value)
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
        # # 绑定值改变事件
        # self.textChanged.connect(self.text_changed)
        # 注意，textChanged信号会被撤回操作触发，所以不要在这里触发value_changed信号

    def setValue(self, value):
        """
        设置值，触发value_changed信号
        """
        if self.rounding:
            self.current_value = round(value, self.rounding)
        elif self.rounding == 0:
            self.current_value = int(value)
        self.setText(str(self.current_value))

    def wheelEvent(self, event):
        """
        滚轮事件，滚动时改变值，然后触发value_changed信号
        """
        self.update_mutex.lock()
        if event.angleDelta().y() > 0:
            self.current_value += self.step
        else:
            self.current_value -= self.step
        self.current_value = round(
            self.current_value, self.rounding
        ) if self.rounding else int(self.text())
        self.setText(str(self.current_value))
        self.value_changed.emit(self.current_value)
        if self.root_parent:
            self.root_parent.update()
        self.update_mutex.unlock()
        # 不传递事件
        event.accept()

    # def text_changed(self):
    #     """
    #     文本改变时触发
    #     """
    #     pass

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.valueSetted(False)
        # # 当按下删除，退格，回车，上下键，tab键时，将值设置为当前值
        # if event.key() in [Qt.Key_Delete, Qt.Key_Backspace, Qt.Key_Return, Qt.Key_Up, Qt.Key_Down, Qt.Key_Tab]:
        #     self.valueSetted(False)

    def inputMethodEvent(self, event):
        """
        输入法事件，当输入法输入时，将值设置为当前值
        """
        super().inputMethodEvent(event)
        self.valueSetted(False)

    # # 当光标离开时，将值设置为当前值
    # def focusOutEvent(self, event):
    #     self.valueSetted()
    #     super().focusOutEvent(event)

    def valueSetted(self, change_ui_value=True):
        """
        将属性值设置为控件显示的值，然后触发value_changed信号
        """
        self.update_mutex.lock()
        if self.text() != "":
            if self.text()[0] == "0" and len(self.text()) > 1 and self.text() != "0.":
                self.setText(self.text()[1:])
            try:
                if self.num_range[0] <= self.num_type(self.text()) <= self.num_range[1]:
                    self.current_value = round(self.num_type(self.text()), self.rounding) if self.rounding else int(
                        self.text())
            except ValueError:
                pass
        else:
            self.current_value = self.num_type(0)
        if change_ui_value:
            self.setText(str(self.current_value))
        self.value_changed.emit(self.current_value)
        if self.root_parent:
            self.root_parent.update()
        self.update_mutex.unlock()

    def clear(self):
        """
        清空输入框，将值设为默认值
        """
        self.setValue(self.default_value)


class PosEditFrame(QFrame):
    def __init__(self, parent, root_parent, size: Tuple[int, int] = (60, 24), spacing=5, font=YAHEI[9], bg="transparent"):
        super().__init__(parent)
        self.root_parent = root_parent
        self.x_input = NumberEdit(self, root_parent, size, float, (-100000, 100000), 4, 0, 0.1, font, bg)
        self.y_input = NumberEdit(self, root_parent, size, float, (-100000, 100000), 4, 0, 0.1, font, bg)
        self.z_input = NumberEdit(self, root_parent, size, float, (-100000, 100000), 4, 0, 0.1, font, bg)

        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setHorizontalSpacing(spacing)
        self.layout.addWidget(TextLabel(None, "X:", font, align=Qt.AlignRight), 0, 0)
        self.layout.addWidget(self.x_input, 0, 1)
        self.layout.addWidget(TextLabel(None, "Y:", font, align=Qt.AlignRight), 0, 2)
        self.layout.addWidget(self.y_input, 0, 3)
        self.layout.addWidget(TextLabel(None, "Z:", font, align=Qt.AlignRight), 0, 4)
        self.layout.addWidget(self.z_input, 0, 5)
        self.setLayout(self.layout)

    def get_pos(self):
        return self.x_input.current_value, self.y_input.current_value, self.z_input.current_value

    def get_x(self):
        return self.x_input.current_value

    def get_y(self):
        return self.y_input.current_value

    def get_z(self):
        return self.z_input.current_value

    def clear(self):
        """
        清空所有输入框，将值设为0
        """
        self.x_input.clear()
        self.y_input.clear()
        self.z_input.clear()
