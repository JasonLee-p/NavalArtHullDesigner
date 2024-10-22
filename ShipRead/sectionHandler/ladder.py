"""
工程文件组件：直梯
"""
from typing import List, Literal
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QVector3D
from .baseComponent import PrjComponent
from main_logger import Log


class Ladder(PrjComponent):
    """
    直梯
    """
    TAG = "Ladder"

    def getCopy(self):
        ladder = Ladder(self.hullProject, self.name, self.shape)
        ladder.Pos = self.Pos
        ladder.Rot = self.Rot
        ladder.Col = self.Col
        ladder.length = self.length
        ladder.width = self.width
        ladder.interval = self.interval
        ladder.material_width = self.material_width
        return ladder

    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, name, shape: Literal["cylinder", "box"]):
        self.hullProject = prj
        self.name = name
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Rot: List[float] = [0, 0, 0]
        self.Col: QColor = QColor(128, 128, 129)  # 颜色
        self.length = 3  # 梯子整体长度
        self.width = 0.5  # 梯子整体宽度
        self.interval = 0.5  # 梯子间隔
        # 梯子材料属性
        self.shape = shape  # 梯子材料形状
        self.material_width = 0.1
        super().__init__("PosShow")
        self.setPaintItem("default")
        self.setPos(self.Pos)
        self.setRot(self.Rot)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._ladder_tab.widget)

    def to_dict(self):
        if isinstance(self.Rot, QVector3D):
            self.Rot = [self.Rot.x(), self.Rot.y(), self.Rot.z()]
            Log().warning(self.TAG, f"{self.name} 函数to_dict：Rot 的类型为 QVector3D，已转换为 List[float]")
        return {
            "name": f"{self.name}",
            "pos": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "length": self.length,
            "width": self.width,
            "interval": self.interval,
            "shape": self.shape,
            "material_width": self.material_width
        }

    def delete(self):
        super().delete()
        try:
            Ladder.idMap.pop(self.getId())
        except KeyError:
            Log().warning(self.TAG, f"{self.name} 不在 Ladder.idMap 中")
