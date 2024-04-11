"""
船体截面组
"""
from typing import List, Union, Literal
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QVector3D
from ShipPaint import HullSectionItem, HullSectionGroupItem
from ShipRead.sectionHandler.baseSH import SectionNodeXY, SectionHandler, SubSectionHandler
from ShipRead.sectionHandler.bridge import Railing, Handrail


class HullSection(SubSectionHandler):
    """
    船体截面
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, z, node_datas, colors):
        self.hullProject = prj
        self._parent = None
        self._frontSection = None
        self._backSection = None
        self.z = z
        self.nodes: List[SectionNodeXY] = []
        self.load_nodes(node_datas, colors)
        self.armor = None
        super().__init__()
        for node in self.nodes:
            node.init_parent(self)

    def load_nodes(self, node_datas, colors):
        for node_data, color in zip(node_datas, colors):
            node = SectionNodeXY()
            node.x, node.y = node_data
            node.Col = QColor(color)
            self.nodes.append(node)
        self.nodes.sort(key=lambda x: x.y)

    def to_dict(self):
        return {
            "z": self.z,
            "nodes": [[node.x, node.y] for node in self.nodes],
            "col": [f"#{node.Col.red():02x}{node.Col.green():02x}{node.Col.blue():02x}" for node in self.nodes],
            "armor": self.armor
        }


class HullSectionGroup(SectionHandler):
    """
    船体截面组
    不进行整体绘制（因为要分截面进行选中操作），绘制交给截面对象
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, name, pos, rot, col, sections):
        self.hullProject = prj
        self.name = name
        self.Pos: QVector3D = pos
        self.Rot: List[float] = rot
        self.Col: QColor = col
        self.topCur = 1.0  # 上层曲率
        self.botCur = 1.0  # 下层曲率
        # 截面组
        self.__sections: List[HullSection] = sections
        self.__sections.sort(key=lambda x: x.z)
        self._frontSection: HullSection = self.__sections[-1]
        self._backSection: HullSection = self.__sections[0]
        for i in range(len(self.__sections) - 1):
            self.__sections[i]._frontSection = self.__sections[i + 1]
            self.__sections[i + 1]._backSection = self.__sections[i]
        # 栏杆
        self.rail: Union[Railing, Handrail, None] = None
        super().__init__()
        paint_item = HullSectionGroupItem(self.hullProject, self.__sections)
        self.setPaintItem(paint_item)
        self.setPos(pos)
        self.setRot(rot)
        for section in self.__sections:
            section.init_parent(self)
            section.init_paintItem_as_child()
            section.setPaintItem(HullSectionItem(section, section.z, section.nodes))

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._hsg_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._hsg_tab.widget)

    def get_sections(self):
        return self.__sections

    def create_frontSection(self):
        new_hs = HullSection(self.hullProject,
                             self._frontSection.z + 2,
                             [[node.x, node.y] for node in self._frontSection.nodes],
                             [node.Col.rgba() for node in self._frontSection.nodes])
        self._frontSection = new_hs

    def _add_section(self, section: HullSection):
        # 根据z值插入
        for i, hs in enumerate(self.__sections):
            if section.z > hs.z:
                self.__sections.insert(i, section)
                return
        raise ValueError(f"Can't insert {section} into {self.__sections}")

    def _del_section(self, section: HullSection):
        if section in self.__sections:
            self.__sections.remove(section)
        else:
            print(f"[WARNING] {section} not in {self.__sections}")

    def to_dict(self):
        if isinstance(self.Rot, QVector3D):
            self.Rot = [self.Rot.x(), self.Rot.y(), self.Rot.z()]
            print(f"[WARNING] {self} Rot is QVector3D, change to list")
        return {
            "name": f"{self.name}",
            "center": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": 0,
            "sections": [section.to_dict() for section in self.__sections],
            "rail": self.rail.to_dict() if self.rail else None
        }

    def delete(self):
        HullSectionGroup.idMap.pop(self.getId())
        SectionHandler._hsg_tab._items.pop(self)  # noqa
