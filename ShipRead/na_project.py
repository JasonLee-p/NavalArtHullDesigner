"""
读取NavalArt工程文件
文件格式名称为.naprj，使用json格式
"""
import os
import time
from typing import Union, List, Literal
from hashlib import sha1

import numpy as np
import ujson
from GUI import configHandler
from GUI.element_structure_widgets import *
from PyQt5.QtGui import QVector3D, QColor
from PyQt5.QtWidgets import QMessageBox
from path_vars import CURRENT_PATH
from pyqtOpenGL import GLModelItem, GLMeshItem, sphere, cube, EditItemMaterial


class SectionHandler(QObject):
    SPHERE_VER, SHPERE_IDX, SPHERE_UV, SPHERE_NORM = sphere(2, 16, 16, calc_uv_norm=True)
    CUBE_VER, CUBE_NORM, CUBE_TEX = cube(1, 1, 1)

    @classmethod
    def update_sphere(cls, radius, rows, cols):
        cls.SPHERE_VER, cls.SHPERE_IDX, cls.SPHERE_UV, cls.SPHERE_NORM = sphere(radius, rows, cols, calc_uv_norm=True)

    def __init__(self, paint_item=None, showButton_type: Literal['PosShow', 'PosRotShow'] = 'PosRotShow'):
        """
        初始化绘制对象，连接到主绘制窗口
        """
        self._showButton = None
        super().__init__(None)
        if not hasattr(self, "Pos"):
            self.Pos = QVector3D(0, 0, 0)
        # 初始化绘制对象
        if paint_item is None:
            random_color = (np.random.randint(100, 255), np.random.randint(0, 255), np.random.randint(0, 255))
            self.paintItem = GLMeshItem(
                vertexes=self.SPHERE_VER, indices=self.SHPERE_IDX, normals=self.SPHERE_NORM,
                lights=[],
                material=EditItemMaterial(color=random_color),
                glOptions='translucent',
                selectable=True
            ).translate(self.Pos.x(), self.Pos.y(), self.Pos.z())
        else:
            self.paintItem = paint_item
        self.paintItem.set_selected_s.connect(self.set_showButton_checked)
        self.paintItem.handler = self
        # 获取主绘制窗口，使其能够连接到主窗口及其下属控件
        if not hasattr(self, "hullProject"):
            if hasattr(self, "_parent"):
                self.hullProject = self._parent.hullProject
            else:
                raise AttributeError("No hullProject attribute or parent attribute")
        self._main_handler = self.hullProject.main_handler
        self._gl_widget = self._main_handler.gl_widget
        self._structure_tab = self._main_handler.structure_tab
        # 初始化左侧结构树窗口
        self._hsg_tab = self._structure_tab.hullSectionGroup_tab
        self._asg_tab = self._structure_tab.armorSectionGroup_tab
        self._bridge_tab = self._structure_tab.bridge_tab
        self._ladder_tab = self._structure_tab.ladder_tab
        self._model_tab = self._structure_tab.model_tab
        self._hsg_bt_scroll_widget = self._hsg_tab.scroll_widget
        self._asg_bt_scroll_widget = self._asg_tab.scroll_widget
        self._bridge_bt_scroll_widget = self._bridge_tab.scroll_widget
        self._ladder_bt_scroll_widget = self._ladder_tab.scroll_widget
        self._model_bt_scroll_widget = self._model_tab.scroll_widget
        # 绘制对象添加到主绘制窗口
        self._gl_widget.addItem(self.paintItem)
        self.paintItem.addLight(self._gl_widget.light)
        # 初始化showButton
        self._init_showButton(showButton_type)
        # 赋值一个唯一的id
        self._custom_id = str(id(self))
        # noinspection PyUnresolvedReferences
        while self._custom_id in self.idMap:
            self._custom_id = str(id(self))
        # noinspection PyUnresolvedReferences
        self.idMap[self._custom_id] = self

    def getId(self):
        return self._custom_id

    @abstractmethod
    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        if type_ == 'PosShow':
            self._showButton = PosShow(self.hullProject.gl_widget, self._model_bt_scroll_widget, self)
        elif type_ == 'PosRotShow':
            self._showButton = PosRotShow(self.hullProject.gl_widget, self._model_bt_scroll_widget, self)
        else:
            raise ValueError(f"Unknown type: {type_}")

    def addLight(self, lights: list):
        self.paintItem.addLight(lights)

    def setVisable(self, visable: bool):
        self.paintItem.setVisible(visable, recursive=True)

    def setSelected(self, selected: bool, set_button=True):
        """
        设置选中状态
        :param selected:
        :param set_button: 是否设置按钮状态
        :return:
        """
        self.paintItem.setSelected(selected)
        self.set_showButton_checked(selected) if set_button else None

    def set_showButton_checked(self, selected: bool):
        self._showButton.setChecked(selected)

    def selected(self):
        return self.paintItem.selected()

    def setPos(self, pos: QVector3D):
        self.Pos = pos
        self.paintItem.moveTo(pos.x(), pos.y(), pos.z())

    def addPos(self, vec: QVector3D):
        self.Pos += vec
        self.paintItem.moveTo(self.Pos.x(), self.Pos.y(), self.Pos.z())

    @classmethod
    def get_by_id(cls, id_):
        if isinstance(id_, str):
            # noinspection PyUnresolvedReferences
            return cls.idMap.get(id_)
        else:
            return None

    def delete(self):
        Model.idMap.pop(self.getId())
        # noinspection PyUnresolvedReferences
        self.deleted_s.emit()
        self._showButton.deleteLater()
        self.deleteLater()
        self._gl_widget.removeItem(self.paintItem)


class SubSectionHandler(QObject):
    def __init__(self, paint_item=None):
        super().__init__(None)
        if paint_item is None:
            self.paintItem = GLMeshItem(
                vertexes=SectionHandler.SPHERE_VER, indices=SectionHandler.SHPERE_IDX,
                normals=SectionHandler.SPHERE_NORM,
                lights=[],
                material=EditItemMaterial(color=(128, 128, 128)),
                glOptions='translucent',
                selectable=True
            )
            if hasattr(self, "Pos"):
                self.paintItem.translate(self.Pos.x(), self.Pos.y(), self.Pos.z())
        else:
            self.paintItem = paint_item
        self.paintItem.handler = self
        # 获取主绘制窗口，使其能够连接到主窗口及其下属控件
        self.hullProject = self._parent.hullProject
        self._main_handler = self.hullProject.main_handler
        self._gl_widget = self._main_handler.gl_widget
        self._parent.paintItem.addChildItem(self.paintItem)
        # 绘制对象添加到主绘制窗口
        self._gl_widget.addItem(self.paintItem)
        self.paintItem.addLight(self._gl_widget.light)
        # 赋值一个唯一的id
        self._custom_id = str(id(self))

    def getId(self):
        return self._custom_id


class SectionNodeXY(SubSectionHandler):
    """
    xy节点，用于记录船体或装甲截面的节点
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, parent):
        self._parent = parent
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.y = None
        paint_item = None
        super().__init__(paint_item)

    @property
    def vector(self):
        return QVector3D(self.x, self.y, self._parent.z)


class SectionNodeXZ(SubSectionHandler):
    """
    xz节点，用于记录舰桥的节点
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, parent):
        self._parent = parent
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.z = None
        paint_item = None
        super().__init__(paint_item)

    @property
    def vector(self):
        return QVector3D(self.x, self._parent.y, self.z)


class Bridge(SectionHandler):
    """
    舰桥
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, name, rail_only):
        self.hullProject = prj
        self.name = name
        self.rail_only = rail_only  # 是否只有栏杆
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Col = QColor(128, 128, 129)  # 颜色
        self.armor = None
        self.nodes: List[SectionNodeXZ] = []
        self.rail: Union[Railing, Handrail, None] = None
        # 绘制对象（不包括栏杆栏板）
        paint_item = None
        super().__init__(paint_item)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._bridge_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._bridge_tab.widget)

    def to_dict(self):
        return {
            "name": f"{self.name}",
            "pos": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": self.armor,
            "nodes": [[node.x, node.z] for node in self.nodes],
            "rail": self.rail.to_dict() if self.rail else None,
            "rail_only": self.rail_only
        }


class HullSection(SubSectionHandler):
    """
    船体截面
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, parent):
        self.hullProject = prj
        self._parent = parent
        self.z = None
        self.nodes: List[SectionNodeXY] = []
        self.armor = None
        self.draw_obj = None
        paint_item = None
        super().__init__(paint_item)

    def to_dict(self):
        return {
            "z": self.z,
            "nodes": [[node.x, node.y] for node in self.nodes],
            "col": [f"#{node.Col.red():02x}{node.Col.green():02x}{node.Col.blue():02x}" for node in self.nodes],
            "armor": self.armor
        }


class ArmorSection(SubSectionHandler):
    """
    装甲截面
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, parent):
        self.hullProject = prj
        self._parent = parent
        self.z = None
        self.nodes: List[SectionNodeXY] = []
        self.armor = None
        self.draw_obj = None
        paint_item = None
        super().__init__(paint_item)

    def to_dict(self):
        return {
            "z": self.z,
            "nodes": [[node.x, node.y] for node in self.nodes],
            "armor": self.armor
        }


class HullSectionGroup(SectionHandler):
    """
    船体截面组
    不进行整体绘制（因为要分截面进行选中操作），绘制交给截面对象
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, name):
        self.hullProject = prj
        self.name = name
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Rot: List[float] = [0, 0, 0]
        self.Col: QColor = QColor(128, 128, 128)  # 颜色
        self.topCur = 0.0  # 上层曲率
        self.botCur = 1.0  # 下层曲率
        # 截面组
        self.__sections: List[HullSection] = []
        # 栏杆
        self.rail: Union[Railing, Handrail, None] = None
        paint_item = None
        super().__init__(paint_item)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._hsg_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._hsg_tab.widget)

    def get_sections(self):
        return self.__sections

    @property
    def draw_objs(self):
        return [section.draw_obj for section in self.__sections]

    def add_section(self, section: HullSection):
        self.__sections.append(section)

    def del_section(self, section: HullSection):
        if section in self.__sections:
            self.__sections.remove(section)
        else:
            color_print(f"[WARNING] {section} not in {self.__sections}", "red")

    def to_dict(self):
        return {
            "name": f"{self.name}",
            "center": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": 0,
            "sections": [section.to_dict() for section in self.__sections],
            "rail": self.rail.to_dict() if self.rail else None
        }


class ArmorSectionGroup(SectionHandler):
    """
    装甲截面组
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, name):
        self.hullProject = prj
        self.name = name
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Rot: List[float] = [0, 0, 0]
        self.Col: QColor = QColor(128, 128, 128)  # 颜色
        self.topCur = 0.0  # 上层曲率
        self.botCur = 1.0  # 下层曲率
        # 装甲分区
        self.__sections: List[HullSection] = []
        paint_item = None
        super().__init__(paint_item)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._asg_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._asg_tab.widget)

    @property
    def draw_objs(self):
        return [section.draw_obj for section in self.__sections]

    def add_section(self, section: HullSection):
        self.__sections.append(section)

    def del_section(self, section: HullSection):
        if section in self.__sections:
            self.__sections.remove(section)
        else:
            color_print(f"[WARNING] {section} not in {self.__sections}", "red")

    def to_dict(self):
        return {
            "name": f"{self.name}",
            "center": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": 0,
            "sections": [section.to_dict() for section in self.__sections]
        }


class Railing(SubSectionHandler):
    """
    栏杆
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, parent: Union[Bridge, HullSectionGroup]):
        self.hullProject = prj
        self.height = 1.2  # 栏杆高度
        self.interval = 1.0  # 栏杆间隔
        self.thickness = 0.1  # 栏杆厚度
        self._parent = parent
        self.Col: QColor = QColor(128, 128, 128)  # 颜色
        paint_item = None
        super().__init__(paint_item)

    def to_dict(self):
        return {
            "height": self.height,
            "interval": self.interval,
            "thickness": self.thickness,
            "type": "railing",
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}"
        }


class Handrail(SubSectionHandler):
    """
    栏板
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, parent: Union[Bridge, HullSectionGroup]):
        self.hullProject = prj
        self.height = 1.2  # 栏板高度
        self.thickness = 0.1  # 栏板厚度
        self._parent = parent
        self.Col: QColor = QColor(128, 128, 128)
        paint_item = None
        super().__init__(paint_item)

    def to_dict(self):
        return {
            "height": self.height,
            "thickness": self.thickness,
            "type": "handrail",
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}"
        }


class Ladder(SectionHandler):
    """
    直梯
    """
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
        paint_item = None
        super().__init__(paint_item)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._ladder_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._ladder_tab.widget)

    def to_dict(self):
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


class Model(SectionHandler):
    """
    模型
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, name, pos: QVector3D, rot: List[float], file_path):
        self.hullProject = prj
        self.name = name
        self.Pos = pos
        self.Rot = rot
        self.file_path = file_path
        modelRenderConfig = configHandler.get_config("ModelRenderSetting")
        modelItem = GLModelItem(file_path, lights=[],
                                selectable=True,
                                glOptions="translucent",
                                drawLine=modelRenderConfig["ModelDrawLine"],
                                lineWidth=modelRenderConfig["ModelLineWith"],
                                lineColor=modelRenderConfig["ModelLineColor"])
        super().__init__(modelItem, showButton_type='PosShow')

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._model_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._model_tab.widget)

    def setDrawLine(self, drawLine: bool):
        self.paintItem.setDrawLine(drawLine)

    def moveTo(self, pos: QVector3D):
        self.Pos = pos
        self.paintItem.moveTo(pos.x(), pos.y(), pos.z())

    def delete(self):
        """
        所有的删除操作都应该调用这个方法，即使是在控件中删除
        :return:
        """
        # noinspection PyProtectedMember
        self._model_tab._items.pop(self)
        super().delete()

    def to_dict(self):
        return {
            "name": f"{self.name}",
            "pos": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "file_path": self.file_path
        }


class ShipProject(QObject):
    """
        工程文件组织逻辑：
        一级：基础信息。信息：安全码，工程名称，作者，编辑时间，同方向截面组
            二级：同方向截面组。信息：名称，中心点位，欧拉方向角，纵向总颜色 & 装甲厚度分区
                三级：截面。信息：z向位置，节点集合（记录x+，从下到上）， 特殊颜色 & 装甲厚度
        组织格式（json）：
        {
            "check_code": "xxxx",
            "project_name": "示例工程文件",
            "author": "JasonLee",
            "edit_time": "2024-01-01 00:00:00",
            "hull_section_group": [
                {
                    "name": "船体截面组（1）",
                    "center": [0, 0, 0],
                    "rot": [0, 0, 0],
                    "col": "#888888",
                    "armor": 5,
                    "top_cur": 0.0,
                    "bot_cur": 1.0,
                    "sections": [
                        {
                            "z": 3,
                            "nodes": [[4, -3], [4, 3]],
                            "col": "#888889",
                            "armor": 5
                        }, {
                            "z": -3,
                            "nodes": [[4, -3], [4, 3]],
                            "col": "#888889",
                            "armor": 5
                        }
                    ],
                    "rail": {
                        "type": "railing",
                        "height": 1.2,
                        "interval": 1.0,
                        "thickness": 0.1,
                        "col": "#888889",
                        "armor": 5
                    }
                }
            ],
            "armor_section_group": [
                {
                    "name": "装甲截面组（1）",
                    "center": [0, 0, 0],
                    "rot": [0, 0, 0],
                    "col": "#888889",
                    "armor": 356,
                    "sections": [
                        {
                            "z": 0,
                            "nodes": [[3, 3], [3, 6]],
                            "armor": 5
                        }
                    ]
                }
            ],
            "bridge": [
                {
                    "name": "舰桥（1）",
                    "rail_only": "false",
                    "pos": [0, 0, 0],
                    "col": "#888889",
                    "armor": 5,
                    "nodes": [[3, 3], [3, -3], [-3, -3], [-3, 3]],
                    "rail": {
                        "type": "handrail",
                        "height": 1.2,
                        "thickness": 0.1,
                        "col": "#888889",
                        "armor": 5
                    }
                }
            ],
            "ladder": [
                {
                    "name": "梯子（1）",
                    "pos": [0, 0, 0],
                    "rot": [0, 0, 0],
                    "length": 6,
                    "width": 0.6,
                    "interval": 0.5,
                    "shape": "cylinder",
                    "material_width": 0.05
                }, {
                    "name": "梯子（2）",
                    "pos": [0, 0, 0],
                    "rot": [0, 0, 0],
                    "length": 6,
                    "width": 0.6,
                    "interval": 0.5,
                    "shape": "box",
                    "material_width": 0.05
                }
            ],
            "model": [
                {
                    "name": "userdefined",
                    "pos": [0, 0, 0],
                    "rot": [0, 0, 0],
                    "file_path": "path/to/file/with/name.obj"
                }
            ]
        }
        """
    add_hull_section_group_s = pyqtSignal(str)  # 添加船体截面组的信号，传出截面组id
    add_armor_section_group_s = pyqtSignal(str)  # 添加装甲截面组的信号，传出截面组id
    add_bridge_s = pyqtSignal(str)  # 添加舰桥的信号，传出舰桥id
    add_ladder_s = pyqtSignal(str)  # 添加梯子的信号，传出梯子id
    add_model_s = pyqtSignal(str)  # 添加模型的信号，传出模型id

    del_hull_section_group_s = pyqtSignal(str)  # 删除船体截面组的信号，传出截面组id
    del_armor_section_group_s = pyqtSignal(str)  # 删除装甲截面组的信号，传出截面组id
    del_bridge_s = pyqtSignal(str)  # 删除舰桥的信号，传出舰桥id
    del_ladder_s = pyqtSignal(str)  # 删除梯子的信号，传出梯子id
    del_model_s = pyqtSignal(str)  # 删除模型的信号，传出模型id

    def __init__(self, main_handler, gl_widget: 'GLWidgetGUI', path: str):
        """

        :param main_handler: 主处理器
        :param gl_widget: 用于绘制的GLWidget
        :param path: 含文件名的路径
        """
        super().__init__(None)
        # 锁
        self.prj_file_mutex = QMutex()
        self.locker = QMutexLocker(self.prj_file_mutex)
        # 绑定主处理器
        self.main_handler = main_handler
        self.gl_widget = gl_widget
        self.path = path
        self.__check_code = None
        self.project_name = None
        self.author = None
        self.__edit_time = None
        self.__hull_section_group: List[HullSectionGroup] = []
        self.__armor_section_group: List[ArmorSectionGroup] = []
        self.__bridge: List[Bridge] = []
        self.__ladder: List[Ladder] = []
        self.__model: List[Model] = []
        # 必须提前绑定信号，否则会出现读取阶段信号无法传出的问题
        self.bind_signal_to_handler()

    def bind_signal_to_handler(self):
        self.add_hull_section_group_s.connect(self.main_handler.add_hull_section_group_s)
        self.add_armor_section_group_s.connect(self.main_handler.add_armor_section_group_s)
        self.add_bridge_s.connect(self.main_handler.add_bridge_s)
        self.add_ladder_s.connect(self.main_handler.add_ladder_s)
        self.add_model_s.connect(self.main_handler.add_model_s)
        self.del_hull_section_group_s.connect(self.main_handler.del_hull_section_group_s)
        self.del_armor_section_group_s.connect(self.main_handler.del_armor_section_group_s)
        self.del_bridge_s.connect(self.main_handler.del_bridge_s)
        self.del_ladder_s.connect(self.main_handler.del_ladder_s)
        self.del_model_s.connect(self.main_handler.del_model_s)

    def new_hullSectionGroup(self):
        """
        产生交互界面，根据用户需求产生相应对象
        :return: PrjSection
        """
        ...

    def new_armorSectionGroup(self):
        """
        产生交互界面，根据用户需求产生相应对象
        :return: PrjSection
        """
        ...

    def new_bridge(self):
        """
        产生交互界面，根据用户需求产生相应对象
        :return: PrjSection
        """
        ...

    def new_ladder(self):
        """
        产生交互界面，根据用户需求产生相应对象
        :return: PrjSection
        """
        ...

    def new_model(self):
        """
        产生交互界面，根据用户需求产生相应对象
        :return: PrjSection
        """
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("模型文件 (*.obj)")
        file_dialog.setViewMode(QFileDialog.Detail)
        find_path = configHandler.get_config("FindModelFolder")
        file_dialog.setDirectory(find_path)
        file_dialog.fileSelected.connect(lambda p: self.add_model_byPath(p))
        file_dialog.exec_()

    def add_hullSectionGroup(self, prjsection: HullSectionGroup):
        self.__hull_section_group.append(prjsection)
        self.add_hull_section_group_s.emit(str(id(prjsection)))

    def add_armorSectionGroup(self, prjsection: ArmorSectionGroup):
        self.__armor_section_group.append(prjsection)
        self.add_armor_section_group_s.emit(str(id(prjsection)))

    def add_bridge(self, prjsection: Bridge):
        self.__bridge.append(prjsection)
        self.add_bridge_s.emit(str(id(prjsection)))

    def add_ladder(self, prjsection: Ladder):
        self.__ladder.append(prjsection)
        self.add_ladder_s.emit(str(id(prjsection)))

    def add_model(self, prjsection: Model):
        """
        将模型添加到工程中，同时发出信号，通知视图更新
        """
        self.__model.append(prjsection)
        self.add_model_s.emit(prjsection.getId())

    def add_model_byPath(self, path: str):
        name = os.path.basename(path)
        name = name[:name.rfind(".")]
        model = Model(self, name, QVector3D(0, 0, 0), [0, 0, 0], path)
        self.add_model(model)

    def del_section(self, prjsection: Union[HullSectionGroup, ArmorSectionGroup, Bridge, Ladder, Railing, Handrail]):
        if isinstance(prjsection, HullSectionGroup):
            self.__hull_section_group.remove(prjsection)
            self.del_hull_section_group_s.emit(prjsection.getId())
        elif isinstance(prjsection, ArmorSectionGroup):
            self.__armor_section_group.remove(prjsection)
            self.del_armor_section_group_s.emit(prjsection.getId())
        elif isinstance(prjsection, Bridge):
            self.__bridge.remove(prjsection)
            self.del_bridge_s.emit(prjsection.getId())
        elif isinstance(prjsection, Ladder):
            self.__ladder.remove(prjsection)
            self.del_ladder_s.emit(prjsection.getId())
        elif isinstance(prjsection, Model):
            self.__model.remove(prjsection)
            self.del_model_s.emit(prjsection.getId())

    def export2NA(self, path):
        """
        导出为NA文件
        :param path: 导出路径，包括文件名
        """
        self.save()
        with self.locker:
            ...

    def to_dict(self):
        year, month, day, hour, minute, second = time.localtime(time.time())[:6]
        return {
            "check_code": self.__check_code,
            "project_name": self.project_name,
            "author": self.author,
            "edit_time": f"{year}-{month}-{day} {hour}:{minute}:{second}",
            "hull_section_group": [hs_group.to_dict() for hs_group in self.__hull_section_group],
            "armor_section_group": [as_group.to_dict() for as_group in self.__armor_section_group],
            "bridge": [bridge.to_dict() for bridge in self.__bridge],
            "ladder": [ladder.to_dict() for ladder in self.__ladder],
            "model": [model.to_dict() for model in self.__model]
        }

    def save(self):
        """
        保存工程文件
        """
        with self.locker:
            dict_data = self.to_dict()
            dict_data_without_check_code = dict_data.copy()
            dict_data_without_check_code.pop("check_code")
            self.__check_code = str(sha1(str(dict(dict_data_without_check_code)).encode("utf-8")).hexdigest())
            dict_data["check_code"] = self.__check_code
            with open(self.path, 'w', encoding='utf-8') as f:
                ujson.dump(dict_data, f, indent=2)


class NaPrjReader:
    def __init__(self, path, shipProject):
        self.path = path
        self.hullProject = shipProject
        self.successed = self.load()

    def load(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                data = ujson.load(f)
        except PermissionError:
            QMessageBox.warning(None, "警告", f"文件 {self.path} 打开失败，请检查文件是否被其他程序占用", QMessageBox.Ok)
            return False
        self.hullProject.__check_code = data['check_code']
        if not self.check_checkCode(dict(data)):
            QMessageBox.warning(None, "警告", f"工程文件 {self.path} 已损坏", QMessageBox.Ok)
            return False
        self.hullProject.project_name = data['project_name']
        self.hullProject.author = data['author']
        self.hullProject.__edit_time = data['edit_time']
        # 读取船体截面组
        self.load_hull_section_group(data['hull_section_group'])
        # 读取装甲截面组
        self.load_armor_section_group(data['armor_section_group'])
        # 读取舰桥
        self.load_bridge(data['bridge'])
        # 读取梯子
        self.load_ladder(data['ladder'])
        # 读取模型
        self.load_model(data['model'])
        return True

    def load_rail(self, data, parent):
        if data['type'] == "railing":
            railing = Railing(self.hullProject, parent)
            parent.rail = railing
            railing.height = data['height']
            railing.interval = data['interval']
            railing.thickness = data['thickness']
            railing.Col = QColor(data['col'])
        elif data['type'] == "handrail":
            handrail = Handrail(self.hullProject, parent)
            parent.rail = handrail
            handrail.height = data['height']
            handrail.thickness = data['thickness']
            handrail.Col = QColor(data['col'])

    def load_hull_section_group(self, data):
        for section_group in data:
            hull_section_group = HullSectionGroup(self.hullProject, section_group['name'])
            hull_section_group.setPos(QVector3D(*section_group['center']))
            hull_section_group.Rot = section_group['rot']
            hull_section_group.Col = QColor(section_group['col'])
            hull_section_group.__sections = self.load_hull_section(section_group['sections'], hull_section_group)
            self.hullProject.add_hullSectionGroup(hull_section_group)
            if "rail" in section_group:
                self.load_rail(section_group['rail'], hull_section_group)

    def load_hull_section(self, data, parent):
        sections = []
        for section in data:
            hull_section = HullSection(self.hullProject, parent)
            hull_section.z = section['z']
            hull_section.nodes = self.load_section_node(section['nodes'], hull_section, section['col'])
            sections.append(hull_section)
        return sections

    def load_section_node(self, data, parent, col_list):
        nodes = []
        for node in data:
            section_node = SectionNodeXY(parent)
            section_node.x, section_node.y = node
            if col_list:
                section_node.Col = QColor(col_list[data.index(node)])
            nodes.append(section_node)
        return nodes

    def load_armor_section_group(self, data):
        for section_group in data:
            armor_section_group = ArmorSectionGroup(self.hullProject, section_group['name'])
            armor_section_group.setPos(QVector3D(*section_group['center']))
            armor_section_group.Rot = section_group['rot']
            armor_section_group.Col = QColor(section_group['col'])
            armor_section_group.__sections = self.load_armor_section(section_group['sections'], armor_section_group)
            self.hullProject.add_armorSectionGroup(armor_section_group)

    def load_armor_section(self, data, parent):
        sections = []
        for section in data:
            armor_section = ArmorSection(self.hullProject, parent)
            armor_section.z = section['z']
            armor_section.nodes = self.load_section_node(section['nodes'], armor_section, None)
            sections.append(armor_section)
        return sections

    def load_bridge(self, data):
        for bridge in data:
            bridge_ = Bridge(self.hullProject, bridge['name'], bridge['rail_only'])
            bridge_.setPos(QVector3D(*bridge['pos']))
            bridge_.Col = QColor(bridge['col'])
            bridge_.armor = bridge['armor']
            bridge_.nodes = self.load_bridge_node(bridge['nodes'], bridge_)
            self.hullProject.add_bridge(bridge_)
            if "rail" in bridge:
                self.load_rail(bridge['rail'], bridge_)

    def load_bridge_node(self, data, parent):
        nodes = []
        for node in data:
            section_node = SectionNodeXZ(parent)
            section_node.x, section_node.z = node
            nodes.append(section_node)
        return nodes

    def load_ladder(self, data):
        for ladder in data:
            ladder_ = Ladder(self.hullProject, ladder['name'], ladder['shape'])
            ladder_.setPos(QVector3D(*ladder['pos']))
            ladder_.Rot = ladder['rot']
            ladder_.Col = QColor(ladder['col'])
            ladder_.length = ladder['length']
            ladder_.width = ladder['width']
            ladder_.interval = ladder['interval']
            ladder_.material_width = ladder['material_width']
            self.hullProject.add_ladder(ladder_)

    def load_model(self, data):
        """
        从工程文件中读取模型
        :param data:
        :return:
        """
        for model in data:
            m_p = model['file_path']
            if m_p.startswith("resources/"):  # 说明是内置模型，需要转换为绝对路径
                m_p = os.path.join(CURRENT_PATH, m_p)
            model_ = Model(self.hullProject, model['name'], QVector3D(*model['pos']), model['rot'], m_p)
            self.hullProject.add_model(model_)

    def check_checkCode(self, data: dict):
        data.pop("check_code")
        if self.hullProject.__check_code == str(sha1(str(data).encode("utf-8")).hexdigest()):
            return True
        return True
