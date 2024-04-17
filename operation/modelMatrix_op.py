"""
物体的位姿操作（模型矩阵操作）
"""
from PyQt5.QtGui import QVector3D

from .basic_op import Operation


class MoveToOperation(Operation):

    def __init__(self, sectionHandler, target_pos: QVector3D = None, edits=None):
        """
        移动到操作
        :param sectionHandler: 被移动的元素
        :param target_pos: 目标位置
        """
        super().__init__()
        self.name = f"移动 {sectionHandler.name} 到 ({round(target_pos.x(), 4)}, {round(target_pos.y())}, {round(target_pos.z())})"
        self.sectionHandler = sectionHandler
        self.target_pos = target_pos if target_pos else sectionHandler.Pos
        self.origin_pos = sectionHandler.Pos
        self.edits = edits

    def execute(self):
        self.sectionHandler.setPos(self.target_pos)

    def undo(self):
        self.sectionHandler.setPos(self.origin_pos)
        self.edits[0].setValue(self.origin_pos.x())
        self.edits[1].setValue(self.origin_pos.y())
        self.edits[2].setValue(self.origin_pos.z())

    def redo(self):
        self.execute()
        self.edits[0].setValue(self.target_pos.x())
        self.edits[1].setValue(self.target_pos.y())
        self.edits[2].setValue(self.target_pos.z())


class MoveOperation(Operation):
    def __init__(self, sectionHandler, move_vec: QVector3D = None, edits=None):
        """
        移动操作
        :param sectionHandler: 被移动的元素
        :param move_vec: 移动向量
        """
        super().__init__()
        self.name = f"移动 {sectionHandler.name} ({round(move_vec.x(), 4)}, {round(move_vec.y())}, {round(move_vec.z())})"
        self.sectionHandler = sectionHandler
        self.move_vec = move_vec if move_vec else QVector3D()
        self.origin_pos = sectionHandler.Pos
        self.edits = edits

    def execute(self):
        self.sectionHandler.addPos(self.move_vec)

    def undo(self):
        self.sectionHandler.setPos(self.origin_pos)
        self.edits[0].setValue(self.origin_pos.x())
        self.edits[1].setValue(self.origin_pos.y())
        self.edits[2].setValue(self.origin_pos.z())

    def redo(self):
        self.execute()
        self.edits[0].setValue(self.sectionHandler.Pos.x())
        self.edits[1].setValue(self.sectionHandler.Pos.y())
        self.edits[2].setValue(self.sectionHandler.Pos.z())


class RotateOperation(Operation):
    def __init__(self, setctionHandler, target_rot: list = None, edits=None):
        """
        旋转操作
        :param setctionHandler: 被旋转的元素
        :param target_rot: 目标旋转角度
        """
        super().__init__()
        self.name = f"旋转 {setctionHandler.name} 到 ({round(target_rot[0], 2)}, {round(target_rot[1], 2)}, {round(target_rot[2], 2)})"
        self.setctionHandler = setctionHandler
        self.target_rot = target_rot if target_rot else setctionHandler.Rot
        self.origin_rot = setctionHandler.Rot
        self.edits = edits

    def execute(self):
        self.setctionHandler.setRot(self.target_rot)

    def undo(self):
        self.setctionHandler.setRot(self.origin_rot)
        self.edits[0].setValue(self.origin_rot[0])
        self.edits[1].setValue(self.origin_rot[1])
        self.edits[2].setValue(self.origin_rot[2])

    def redo(self):
        self.execute()
        self.edits[0].setValue(self.target_rot[0])
        self.edits[1].setValue(self.target_rot[1])
        self.edits[2].setValue(self.target_rot[2])
