"""
读取NavalArt工程文件
文件格式名称为.naprj，使用json格式
"""
import time
from typing import Union, List, Literal
from hashlib import sha1

import ujson
from PyQt5.QtGui import QVector3D, QColor
from PyQt5.QtWidgets import QMessageBox


class SectionNodeXY:
    """
    xy节点，用于记录船体或装甲截面的节点
    """

    def __init__(self, parent):
        self.parent = parent
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.y = None

    @property
    def vector(self):
        return QVector3D(self.x, self.y, self.parent.z)


class SectionNodeXZ:
    """
    xz节点，用于记录舰桥的节点
    """

    def __init__(self, parent):
        self.parent = parent
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.z = None

    @property
    def vector(self):
        return QVector3D(self.x, self.parent.y, self.z)


class Bridge:
    """
    舰桥
    """

    def __init__(self, rail_only):
        self.rail_only = rail_only  # 是否只有栏杆
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Col = QColor(128, 128, 129)  # 颜色
        self.armor = None
        self.nodes: List[SectionNodeXZ] = []

    def to_dict(self):
        return {
            "pos": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": self.armor,
            "nodes": [[node.x, node.z] for node in self.nodes]
        }


class HullSection:
    """
    船体截面
    """

    def __init__(self, parent):
        self.parent = parent
        self.z = None
        self.nodes: List[SectionNodeXY] = []
        self.armor = None

    def to_dict(self):
        return {
            "z": self.z,
            "nodes": [[node.x, node.y] for node in self.nodes],
            "col": [f"#{node.Col.red():02x}{node.Col.green():02x}{node.Col.blue():02x}" for node in self.nodes],
            "armor": self.armor
        }


class ArmorSection:
    """
    装甲截面
    """

    def __init__(self, parent):
        self.parent = parent
        self.z = None
        self.nodes: List[SectionNodeXY] = []
        self.armor = None

    def to_dict(self):
        return {
            "z": self.z,
            "nodes": [[node.x, node.y] for node in self.nodes],
            "armor": self.armor
        }


class HullSectionGroup:
    """
    船体截面组
    """

    def __init__(self, name):
        self.name = name
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Rot: List[float] = [0, 0, 0]
        self.Col: QColor = QColor(128, 128, 128)   # 颜色
        self.topCur = 0.0  # 上层曲率
        self.botCur = 1.0  # 下层曲率
        # 截面组
        self.sections: List[HullSection] = []

    def to_dict(self):
        return {
            "center": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": 0,
            "sections": [section.to_dict() for section in self.sections]
        }


class ArmorSectionGroup:
    """
    装甲截面组
    """

    def __init__(self, name):
        self.name = name
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Rot: List[float] = [0, 0, 0]
        self.Col: QColor = QColor(128, 128, 128)  # 颜色
        self.topCur = 0.0  # 上层曲率
        self.botCur = 1.0  # 下层曲率
        # 装甲分区
        self.sections: List[HullSection] = []

    def to_dict(self):
        return {
            "center": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}",
            "armor": 0,
            "sections": [section.to_dict() for section in self.sections]
        }


class Railing:
    """
    栏杆
    """
    def __init__(self, parent: Union[Bridge, HullSectionGroup]):
        self.height = 1.2  # 栏杆高度
        self.interval = 1.0  # 栏杆间隔
        self.thickness = 0.1  # 栏杆厚度
        self.parent = parent
        self.Col: QColor = QColor(128, 128, 128)  # 颜色

    def to_dict(self):
        return {
            "height": self.height,
            "interval": self.interval,
            "thickness": self.thickness,
            "type": "railing",
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}"
        }


class Handrail:
    """
    栏板
    """
    def __init__(self, parent: Union[Bridge, HullSectionGroup]):
        self.height = 1.2  # 栏板高度
        self.thickness = 0.1  # 栏板厚度
        self.parent = parent
        self.Col: QColor = QColor(128, 128, 128)

    def to_dict(self):
        return {
            "height": self.height,
            "thickness": self.thickness,
            "type": "handrail",
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}"
        }


class Ladder:
    """
    直梯
    """
    def __init__(self, name, shape: Literal["cylinder", "box"]):
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


class ShipProject:
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
            ]
        }
        """

    def __init__(self, path):
        self.path = path
        self.__check_code = None
        self.project_name = None
        self.author = None
        self.__edit_time = None
        self.__hull_section_group: List[HullSectionGroup] = []
        self.__armor_section_group: List[ArmorSectionGroup] = []
        self.__bridge: List[Bridge] = []
        self.__ladder: List[Ladder] = []

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

    def add_hullSectionGroup(self, prjsection: Union[HullSectionGroup, List[HullSectionGroup]]):
        if isinstance(prjsection, HullSectionGroup):
            self.__hull_section_group.append(prjsection)
        elif isinstance(prjsection, list):
            self.__hull_section_group.extend(prjsection)

    def add_armorSectionGroup(self, prjsection: Union[ArmorSectionGroup, List[ArmorSectionGroup]]):
        if isinstance(prjsection, ArmorSectionGroup):
            self.__armor_section_group.append(prjsection)
        elif isinstance(prjsection, list):
            self.__armor_section_group.extend(prjsection)

    def add_bridge(self, prjsection: Union[Bridge, List[Bridge]]):
        if isinstance(prjsection, Bridge):
            self.__bridge.append(prjsection)
        elif isinstance(prjsection, list):
            self.__bridge.extend(prjsection)

    def add_ladder(self, prjsection: Union[Ladder, List[Ladder]]):
        if isinstance(prjsection, Ladder):
            self.__ladder.append(prjsection)
        elif isinstance(prjsection, list):
            self.__ladder.extend(prjsection)

    def del_section(self, prjsection: Union[HullSectionGroup, ArmorSectionGroup, Bridge, Ladder, Railing, Handrail]):
        if isinstance(prjsection, HullSectionGroup):
            self.__hull_section_group.remove(prjsection)
        elif isinstance(prjsection, ArmorSectionGroup):
            self.__armor_section_group.remove(prjsection)
        elif isinstance(prjsection, Bridge):
            self.__bridge.remove(prjsection)
        elif isinstance(prjsection, Ladder):
            self.__ladder.remove(prjsection)

    def export2NA(self, path):
        """
        导出为NA文件
        :param path: 导出路径，包括文件名
        """

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
            "ladder": [ladder.to_dict() for ladder in self.__ladder]
        }

    def save(self):
        """
        保存工程文件
        """
        dict_data = self.to_dict()
        dict_data_without_check_code = dict_data.copy()
        dict_data_without_check_code.pop("check_code")
        self.__check_code = str(sha1(str(dict(dict_data_without_check_code)).encode("utf-8")).hexdigest())
        dict_data["check_code"] = self.__check_code
        with open(self.path, 'w') as f:
            ujson.dump(dict_data, f)


class NaPrjReader:
    def __init__(self, path, shipProject):
        self.path = path
        self.hullProject = shipProject
        self.load()

    def load(self):
        with open(self.path, 'r') as f:
            data = ujson.load(f)
            self.hullProject.__check_code = data['check_code']
            if not self.check_checkCode(dict(data)):
                QMessageBox.warning(None, "警告", "工程文件已损坏", QMessageBox.Ok)
                return None
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

    def load_rail(self, data, parent):
        if data['type'] == "railing":
            railing = Railing(parent)
            railing.height = data['height']
            railing.interval = data['interval']
            railing.thickness = data['thickness']
            railing.Col = QColor(data['col'])
        elif data['type'] == "handrail":
            handrail = Handrail(parent)
            handrail.height = data['height']
            handrail.thickness = data['thickness']
            handrail.Col = QColor(data['col'])

    def load_hull_section_group(self, data):
        for section_group in data:
            hull_section_group = HullSectionGroup(section_group['name'])
            hull_section_group.Pos = QVector3D(*section_group['center'])
            hull_section_group.Rot = section_group['rot']
            hull_section_group.Col = QColor(section_group['col'])
            hull_section_group.sections = self.load_hull_section(section_group['sections'], hull_section_group)
            self.hullProject.add_hullSectionGroup(hull_section_group)
            if "rail" in section_group:
                self.load_rail(section_group['rail'], hull_section_group)

    def load_hull_section(self, data, parent):
        sections = []
        for section in data:
            hull_section = HullSection(parent)
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
            armor_section_group = ArmorSectionGroup(section_group['name'])
            armor_section_group.Pos = QVector3D(*section_group['center'])
            armor_section_group.Rot = section_group['rot']
            armor_section_group.Col = QColor(section_group['col'])
            armor_section_group.sections = self.load_armor_section(section_group['sections'], armor_section_group)
            self.hullProject.add_armorSectionGroup(armor_section_group)
            if "rail" in section_group:
                self.load_rail(section_group['rail'], armor_section_group)

    def load_armor_section(self, data, parent):
        sections = []
        for section in data:
            armor_section = ArmorSection(parent)
            armor_section.z = section['z']
            armor_section.nodes = self.load_section_node(section['nodes'], armor_section, None)
            sections.append(armor_section)
        return sections

    def load_bridge(self, data):
        for bridge in data:
            bridge_ = Bridge(bridge['rail_only'])
            bridge_.Pos = QVector3D(*bridge['pos'])
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
            ladder_ = Ladder(ladder['name'], ladder['shape'])
            ladder_.Pos = QVector3D(*ladder['pos'])
            ladder_.Rot = ladder['rot']
            ladder_.Col = QColor(ladder['col'])
            ladder_.length = ladder['length']
            ladder_.width = ladder['width']
            ladder_.interval = ladder['interval']
            ladder_.material_width = ladder['material_width']
            self.hullProject.add_ladder(ladder_)

    def check_checkCode(self, data: dict):
        # TODO: 安全码验证
        data.pop("check_code")
        if self.hullProject.__check_code == str(sha1(str(data).encode("utf-8")).hexdigest()):
            return True
        return False
