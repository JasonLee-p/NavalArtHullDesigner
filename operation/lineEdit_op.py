# -*- coding: utf-8 -*-
"""
LineEdit中的输入操作
注意，通常值修改伴随着绘制对象和其他控件内容的变化，因此这里的操作不仅仅是修改值，还需要修改绘制对象
"""

from .basic_op import Operation, OperationStack


class _LineEditValueChangeOp(Operation):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.old_value = text_edit.text()
        self.new_value = None

    def execute(self):
        self.text_edit.setText(self.new_value)

    def undo(self):
        self.text_edit.setText(self.old_value)

    def redo(self):
        self.text_edit.setText(self.new_value)

