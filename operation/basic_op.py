# -*- coding: utf-8 -*-
"""
操作类的基类
"""
from abc import abstractmethod
from typing import List, Union, Optional

from PyQt5.QtCore import QMutex


class Operation:
    def __init__(self):
        """
        操作栈中的操作基类
        在state_history.py中，
        """
        self.name = f"未命名操作 {self.__class__.__name__}"
        pass

    @abstractmethod
    def execute(self):
        """
        执行操作，由operation_stack调用，请勿直接调用
        要执行操作，请通过operation_stack.execute()调用栈中的操作
        """
        pass

    @abstractmethod
    def undo(self):
        """
        和正操作相反的操作，由operation_stack调用，请勿直接调用
        :return:
        """
        pass

    @abstractmethod
    def redo(self):
        """
        重做操作，由operation_stack调用，请勿直接调用
        :return:
        """
        self.execute()


class OperationStack:
    operationMutex = QMutex()

    def __init__(self, main_editor, max_length: int = 10000):
        """
        在编辑器对象中初始化，而不是在操作对象中初始化
        管理操作，以撤回和重做
        :param main_editor: 父窗口
        :param max_length: 栈的最大长度，从配置文件中读取
        """
        self.main_editor = main_editor
        # 初始化一个定长的状态栈
        self.max_length = max_length if max_length > 0 else 10000
        self.stateStack: List[Union[Operation, None]] = [None] * self.max_length
        self.current_index = None

    def init_stack(self):
        """
        初始化状态
        :return:
        """
        self.stateStack[0] = Operation()
        self.current_index = 0  # 当前状态的索引

    def execute(self, operation: Operation):
        """
        调用该函数以执行命令，执行完命令后，命令会被添加到栈中。
        :param operation:
        :return:
        """
        if self.current_index is None:
            raise Exception("OperationStack not initialized, please call init_stack() first")
        self.operationMutex.lock()
        operation.execute()
        if self.current_index == self.max_length - 1:
            self.stateStack = self.stateStack[1:] + [operation]
            self.main_editor.show_statu_("操作栈已满", "warning")
        else:
            self.current_index += 1
            self.stateStack[self.current_index] = operation
            self.main_editor.show_statu_(f"{operation.name}\t{self.current_index + 1}", "process")
        self.main_editor.gl_widget.paintGL_outside()
        self.operationMutex.unlock()

    def undo(self):
        """
        撤回
        """
        self.operationMutex.lock()
        if self.current_index > 0:
            try:
                self.stateStack[self.current_index].undo()
            except Exception as e:
                self.main_editor.show_statu_(f"无效的撤回操作：{e}", "warning")
            self.main_editor.show_statu_(
                f"Ctrl+Z 撤回 {self.stateStack[self.current_index].name}\t{self.current_index}", "process")
            self.current_index -= 1
        else:
            self.main_editor.show_statu_("Ctrl+Z 没有更多的历史记录", "warning")
            ...
        self.main_editor.gl_widget.paintGL_outside()
        self.operationMutex.unlock()

    def redo(self):
        """
        重做命令
        """
        self.operationMutex.lock()
        if self.current_index is not None and self.stateStack[self.current_index + 1] is not None:
            self.current_index += 1
            try:
                self.stateStack[self.current_index].redo()
            except Exception as e:
                self.main_editor.show_statu_(f"无效的重做操作：{e}", "warning")
            self.main_editor.show_statu_(
                f"Ctrl+Shift+Z 重做 {self.stateStack[self.current_index].name}\t{self.current_index + 1}",
                "process")
        else:
            self.main_editor.show_statu_("Ctrl+Shift+Z 没有更多的历史记录", "warning")
        self.main_editor.gl_widget.paintGL_outside()
        self.operationMutex.unlock()

    def update_size(self, size: int):
        if size < 5 or size > 2 ** 16:
            raise ValueError("Size should be in [5, 2^16]")
        if size < self.max_length:
            self.stateStack = self.stateStack[self.max_length - size:]
            self.max_length = size
        else:
            self.stateStack = [None] * (size - self.max_length) + self.stateStack
            self.max_length = size
        self.current_index = size - 1

    def clear(self, length: Optional[int] = None):
        self.operationMutex.lock()
        if length is None:
            self.stateStack = [None] * self.max_length
            self.init_stack()
            self.main_editor.show_statu_("操作栈已清空", "warning")
            self.main_editor.gl_widget.paintGL_outside()
        else:
            # 清空撤回栈的前length个操作（操作依次前移）
            for i in range(self.current_index - length + 1):
                self.stateStack[i] = self.stateStack[i + length]
            self.current_index = self.current_index - length
            for i in range(length):
                self.stateStack[self.current_index + i + 1] = None
            self.main_editor.show_statu_(f"撤回栈已清空 {length} 个操作", "warning")
        self.operationMutex.unlock()
