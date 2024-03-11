# -*- coding: utf-8 -*-
"""
定义船体截面组操作
"""

from .basic_op import Operation, OperationStack


class AddHullSectionOp(Operation):
    def __init__(self):
        """
        添加船体截面组操作
        """
        super().__init__()

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        self.execute()


class DelHullSectionOp(Operation):
    def __init__(self):
        """
        删除船体截面组操作
        """
        super().__init__()

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        self.execute()
