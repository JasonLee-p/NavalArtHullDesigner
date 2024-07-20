"""
船体截面组
"""
from typing import List, Union, Literal, Optional

import numpy as np
from GUI.sub_element_edt_widgets import SubSectionShow
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QVector3D
from ShipPaint import HullSectionItem, HullSectionGroupItem
from ShipRead.sectionHandler.baseSH import SectionNodeXY, SectionHandler, SubSectionHandler
from ShipRead.sectionHandler.bridge import Railing, Handrail
from main_logger import Log
from operation.section_op import SectionZMoveOperation


class HullSection(SubSectionHandler):
    """
    船体截面
    __init__后仍需调用：
    init_parent(...)  链接自己的父对象
    init_paintItem_as_child()  链接绘图对象的父对象
    setPaintItem(HullSectionItem(...))  设置绘图对象
    parent._edit_tab.edit_hullSectionGroup_widget.add_section_showButton(section) 往编辑控件添加按钮
    """
    TAG = "HullSection"
    idMap = {}
    deleted_s = pyqtSignal()

    def getCopy(self):
        hullSection = HullSection(self.hullProject, self.z, self.nodes_data, [node.Col for node in self.nodes],
                                  self.armor)
        return hullSection

    def __init__(self, prj, z, node_datas, colors, armor, name=None):
        """
        初始化node，_showButton
        """
        self.hullProject = prj
        if name is None:
            name = "未命名"
        self.name: str = name
        self._parent: Optional[HullSectionGroup] = None
        self._frontSection = None
        self._backSection = None
        self.z = z
        self.nodes: List[SectionNodeXY] = []
        self.nodes_data: Optional[np.ndarray] = None
        self.load_nodes(node_datas, colors)
        self.armor = armor if armor else 5
        super().__init__()
        self.maxX = 0
        for node in self.nodes:
            node.init_parent(self)
            self.maxX = max(self.maxX, node.x)
        self._showButton = SubSectionShow(SectionHandler._gl_widget, SectionHandler._hsg_bt_scroll_widget, self)

    def load_nodes(self, node_datas, colors):
        for node_data, color in zip(node_datas, colors):
            node = SectionNodeXY()
            node.x, node.y = node_data
            node.Col = QColor(color)
            self.nodes.append(node)
        self.nodes.sort(key=lambda x: x.y)

    def update_node_data(self, index, x):
        self.nodes[index].x = x
        self.maxX = max(self.maxX, x)

    def _add_node(self, node):
        """
        用于内部添加节点，由用户直接添加节点属于operation类，不在此类定义。
        :param node:
        :return:
        """
        for i, n in enumerate(self.nodes):
            if node.y < n.y:
                self.nodes.insert(i, node)
                return
        self.maxX = max(self.maxX, node.x)

    def _del_node(self, index):
        """
        用于内部删除节点，由用户直接删除节点属于operation类，不在此类定义。
        :param index:
        :return:
        """
        if len(self.nodes) < 3:
            raise ValueError("Can't delete node, less than 3 nodes")
        self.nodes.pop(index)
        self.maxX = max([node.x for node in self.nodes])

    def init_node_data(self):
        """
        在HullSectionGroup的__init__函数重载前调用
        从self.nodes（Node对象）初始化节点数据self.nodes_data（数组）
        :return:
        """
        self.nodes_data = np.array([[node.x, node.y] for node in self.nodes])

    def setZ(self, z_, undo=False):
        """
        设置z值
        :param z_: z值
        :param undo: 是否被撤回操作调用，如果是则不对z值进行限制
        :return:
        """
        if not undo:
            # 限制z在前后两个截面之间
            if self._frontSection and z_ > self._frontSection.z:
                z_ = self._frontSection.z - 0.01
            elif self._backSection and z_ < self._backSection.z:
                z_ = self._backSection.z + 0.01
            # 让前后截面无法相互转化（z>0的截面不能变成z<0）
            if self.z > 0:
                z_ = max(0.005, z_)
            elif self.z < 0:
                z_ = min(0.005, z_)
        self.z = z_
        self._showButton.setEditTextZ(self.z)
        self.paintItem.setZ(self.z)
        if self._parent._frontSection == self:
            self._parent.update_front_z_s.emit(self.z)
            # EditHullSectionGroupWidget.Instance.updateFrontZ()
        elif self._parent._backSection == self:
            self._parent.update_back_z_s.emit(self.z)
            # EditHullSectionGroupWidget.Instance.updateBackZ()

    def delete_by_user(self):
        pass

    def get_array(self) -> np.ndarray:
        """
        返回二维numpy float32数组：
        [节点数，3]
        :return:
        """
        return np.array([[node.x, node.y, self.z] for node in self.nodes])

    def to_dict(self):
        return {
            "name": self.name,
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
    TAG = "HullSectionGroup"
    idMap = {}
    deleted_s = pyqtSignal()
    update_front_z_s = pyqtSignal(float)
    update_back_z_s = pyqtSignal(float)

    def getCopy(self):
        hullSections = [section.getCopy() for section in self.__sections]
        return HullSectionGroup(self.hullProject, self.name, self.Pos, self.Rot, self.Col, self.topCur, self.botCur,
                                hullSections)

    # noinspection PyProtectedMember
    def __init__(self, prj, name, pos, rot, col, topCur, botCur, sections):
        self.hullProject = prj
        self.name = name
        self.Pos: QVector3D = pos
        self.Rot: List[float] = rot
        self.Col: QColor = col
        self.topCur = topCur
        self.botCur = botCur
        # 截面组
        self.__sections: List[HullSection] = sections
        self.__sections.sort(key=lambda x: x.z)  # 从小到大
        self._frontSection: HullSection = self.__sections[-1]
        self._backSection: HullSection = self.__sections[0]
        for i in range(len(self.__sections) - 1):
            self.__sections[i]._frontSection = self.__sections[i + 1]
            self.__sections[i + 1]._backSection = self.__sections[i]
        # 栏杆
        self.rail: Union[Railing, Handrail, None] = None
        for section in self.__sections:
            section.init_node_data()
        super().__init__()
        # 绘制对象
        paint_item = HullSectionGroupItem(self.hullProject, self.__sections)
        self.setPaintItem(paint_item)
        self.setPos(pos)
        self.setRot(rot)

        # 倒过来，从大到小排列
        for section in self.__sections[::-1]:
            section.init_parent(self)
            section.setPaintItem(HullSectionItem(section, section.z, section.nodes))
            # 将截面展示的button控件加入右侧滚动区域
            self._edit_tab.edit_hullSectionGroup_widget.add_section_showButton(section)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._hsg_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._hsg_tab.widget)

    def get_sections(self):
        return self.__sections

    def get_array(self) -> np.ndarray:
        """
        返回三维numpy float32数组，可以用于mlp预测
        [截面数，节点数，3]
        :return:
        """
        return np.array([section.get_array() for section in self.__sections])

    def getMaxX(self):
        return max([section.maxX for section in self.__sections])

    def create_frontSection(self):
        new_hs = HullSection(self.hullProject,
                             self._frontSection.z + 2,
                             [[node.x, node.y] for node in self._frontSection.nodes],
                             [node.Col.rgba() for node in self._frontSection.nodes],
                             5)
        self._frontSection = new_hs

    def _add_section(self, section: HullSection):
        # 根据z值插入
        for i, hs in enumerate(self.__sections):
            if section.z > hs.z:
                # 初始化前后部分
                if len(self.__sections) > i + 1:
                    section._frontSection = self.__sections[i + 1]
                if i != 0:
                    section._backSection = self.__sections[i - 1]
                # 初始化绘制数组
                section.init_node_data()
                section.init_parent(self)
                if section.paintItem:
                    section.init_paintItems_parent()
                else:
                    # section.setPaintItem(HullSectionItem(section,
                    ...
                self.__sections.insert(i, section)

                return
        raise ValueError(f"Can't insert {section} into {self.__sections}")

    def _del_section(self, section: HullSection):
        if section in self.__sections:
            self.__sections.remove(section)
        else:
            Log().warning(self.TAG, f"{section} not in {self.__sections}")

    def to_dict(self):
        if isinstance(self.Rot, QVector3D):
            self.Rot = [self.Rot.x(), self.Rot.y(), self.Rot.z()]
            Log().warning(self.TAG, f"{self.name} Rot 的类型为 QVector3D，已转换为 List[float]")
        return {
            "name": f"{self.name}",
            "center": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": 0,
            "top_cur": self.topCur,
            "bot_cur": self.botCur,
            "sections": [section.to_dict() for section in self.__sections],
            "rail": self.rail.to_dict() if self.rail else None
        }

    def delete(self):
        super().delete()
        try:
            HullSectionGroup.idMap.pop(self.getId())
        except KeyError:
            Log().warning(self.TAG, f"{self.name} 不在 HullSectionGroup.idMap 中")
