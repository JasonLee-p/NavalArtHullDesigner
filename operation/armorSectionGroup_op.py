# -*- coding: utf-8 -*-
"""
定义装甲截面组操作
"""

from .basic_op import Operation, OperationStack


class AddArmorSectionGroupOp(Operation):
    def __init__(self):
        """
        添加装甲截面组操作
        """
        super().__init__()

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        self.execute()


class DelArmorSectionGroupOp(Operation):
    def __init__(self):
        """
        删除装甲截面组操作
        """
        super().__init__()

    def execute(self):
        pass

    def undo(self):
        pass

    def redo(self):
        self.execute()
