"""
工程文件组件：装甲截面组
"""
from GUI.element_structure_widgets import *
from PyQt5.QtGui import QColor, QVector3D
from ShipPaint import ArmorSectionGroupItem
from .baseComponent import ComponentNodeXY, PrjComponent, SubPrjComponent


class ArmorSection(SubPrjComponent):
    """
    装甲截面
    """
    TAG = "ArmorSection"

    def getCopy(self):
        armor = ArmorSection(self.hullProject, self.z, [[node.x, node.y] for node in self.nodes])
        armor.armor = self.armor
        return armor

    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, prj, z, node_datas):
        self.hullProject = prj
        self._parent = None
        self.z = z
        self.nodes: List[ComponentNodeXY] = []
        self.load_nodes(node_datas)
        self.armor = None
        super().__init__()
        for node in self.nodes:
            node.init_parent(self)

    def load_nodes(self, node_datas):
        for node_data in node_datas:
            node = ComponentNodeXY()
            node.x, node.y = node_data
            self.nodes.append(node)
        self.nodes.sort(key=lambda x: x.y)

    def set_parentGroup(self, parent):
        self._parent = parent
        self.paintItem.sectionGroup = parent

    def delete_by_user(self):
        pass

    def to_dict(self):
        return {
            "z": self.z,
            "nodes": [[node.x, node.y] for node in self.nodes],
            "armor": self.armor
        }


class ArmorSectionGroup(PrjComponent):
    """
    装甲截面组
    """
    TAG = "ArmorSectionGroup"
    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def getCopy(self):
        armor = ArmorSectionGroup(self.hullProject, self.name, self.Pos, self.Rot, self.Col,
                                    [section.getCopy() for section in self.__sections])
        armor.topCur = self.topCur
        armor.botCur = self.botCur
        return armor

    def __init__(self, prj, name, pos, rot, col, sections):
        self.hullProject = prj
        self.name = name
        self.Pos: QVector3D = pos
        self.Rot: List[float] = rot
        self.Col: QColor = col
        self.topCur = 0.0  # 上层曲率
        self.botCur = 1.0  # 下层曲率
        # 装甲分区
        self.__sections: List[ArmorSection] = sections
        self.__sections.sort(key=lambda x: x.z)
        self._frontSection: ArmorSection = self.__sections[-1]
        self._backSection: ArmorSection = self.__sections[0]

        super().__init__()
        paint_item = ArmorSectionGroupItem(self.hullProject, self.__sections)
        self.setPaintItem(paint_item)
        self.setPos(pos)
        self.setRot(rot)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._asg_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._asg_tab.widget)

    def add_section(self, section: ArmorSection):
        self.__sections.append(section)

    def del_section(self, section: ArmorSection):
        if section in self.__sections:
            self.__sections.remove(section)
        else:
            Log().warning(self.TAG, f"{section} not in {self.__sections}")

    def to_dict(self):
        if isinstance(self.Rot, QVector3D):
            self.Rot = [self.Rot.x(), self.Rot.y(), self.Rot.z()]
            Log().warning(self.TAG, f"{self.name} 函数to_dict：Rot 的类型为 QVector3D，已转换为 List[float]")
        return {
            "name": f"{self.name}",
            "center": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": 0,
            "sections": [section.to_dict() for section in self.__sections]
        }

    def delete(self):
        super().delete()
        try:
            ArmorSectionGroup.idMap.pop(self.getId())
        except KeyError:
            Log().warning(self.TAG, f"{self.name} 不在 ArmorSectionGroup.idMap 中")
