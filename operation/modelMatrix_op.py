"""
物体的位姿操作（模型矩阵操作）
"""
from PyQt5.QtGui import QVector3D

from .basic_op import Operation, OperationStack


class MoveToOperation(Operation):

    def __init__(self, sectionHandler, target_pos: QVector3D = None):
        """
        移动到操作
        :param sectionHandler: 被移动的元素
        :param target_pos: 目标位置
        """
        super().__init__()
        self.sectionHandler = sectionHandler
        self.target_pos = target_pos if target_pos else sectionHandler.Pos
        self.origin_pos = sectionHandler.Pos

    def execute(self):
        self.sectionHandler.setPos(self.target_pos)

    def undo(self):
        self.sectionHandler.setPos(self.origin_pos)

    def redo(self):
        self.execute()


class MoveOperation(Operation):
    def __init__(self, sectionHandler, move_vec: QVector3D = None):
        """
        移动操作
        :param sectionHandler: 被移动的元素
        :param move_vec: 移动向量
        """
        super().__init__()
        self.sectionHandler = sectionHandler
        self.move_vec = move_vec if move_vec else QVector3D()
        self.origin_pos = sectionHandler.Pos

    def execute(self):
        self.sectionHandler.addPos(self.move_vec)

    def undo(self):
        self.sectionHandler.setPos(self.origin_pos)

    def redo(self):
        self.execute()


class RotateOperation(Operation):
    def __init__(self, setctionHandler, target_rot: QVector3D = None):
        """
        旋转操作
        :param setctionHandler: 被旋转的元素
        :param target_rot: 目标旋转角度
        """
        super().__init__()
        self.setctionHandler = setctionHandler
        self.target_rot = target_rot if target_rot else setctionHandler.Rot
        self.origin_rot = setctionHandler.Rot

    def execute(self):
        self.setctionHandler.setRot(self.target_rot)

    def undo(self):
        self.setctionHandler.setRot(self.origin_rot)

    def redo(self):
        self.execute()
