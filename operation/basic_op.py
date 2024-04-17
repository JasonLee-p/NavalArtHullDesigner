# -*- coding: utf-8 -*-
"""
操作类的基类
"""
from abc import abstractmethod
from typing import List, Union

from PyQt5.QtCore import QMutex


class Operation:
    def __init__(self):
        """
        操作栈中的操作基类
        在state_history.py中，
        """
        self.name = '操作'
        pass

    @abstractmethod
    def execute(self):
        """
        执行操作
        """
        pass

    @abstractmethod
    def undo(self):
        """
        和正操作相反的操作
        :return:
        """
        pass

    @abstractmethod
    def redo(self):
        self.execute()


class OperationStack:
    operationMutex = QMutex()

    def __init__(self, main_editor, max_length: int = 10000):
        """
        在编辑器对象中初始化，而不是在操作对象中初始化
        管理操作，以撤回和重做
        :param main_editor: 父三维窗口
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
        执行命令后，保存状态
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
            self.stateStack[self.current_index].undo()
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
            self.stateStack[self.current_index].redo()
            self.main_editor.show_statu_(
                f"Ctrl+Shift+Z 重做 {self.stateStack[self.current_index].name}\t{self.current_index + 1}",
                "process")
        else:
            self.main_editor.show_statu_("Ctrl+Shift+Z 没有更多的历史记录", "warning")
        self.main_editor.gl_widget.paintGL_outside()
        self.operationMutex.unlock()
