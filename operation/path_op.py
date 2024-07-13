"""
关于路径的操作
"""
from .basic_op import Operation


class ChangeModelPathOperation(Operation):
    def __init__(self, modelItem, newPath, formerPath):
        """
        修改模型路径操作
        :param modelItem: 模型对象
        :param newPath: 新路径
        :param formerPath: 旧路径
        """
        super().__init__()
        self.name = f"修改模型路径 {modelItem.name}"
        self.modelItem = modelItem
        self.newPath = newPath
        self.formerPath = formerPath

    def execute(self):
        self.modelItem.changePath(self.newPath)  # changePath函数内已经通知gl_widget更新

    def undo(self):
        self.modelItem.changePath(self.formerPath)  # changePath函数内已经通知gl_widget更新

    def redo(self):
        self.execute()
