"""
读取NavalArt工程文件
文件格式名称为.naprj，使用json格式
"""
from typing import Union

import ujson
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QMessageBox


class PrjNode:
    """
    节点
    """

    def __init__(self, parent):
        self.parent = parent
        self.y = None
        self.z = None

    @property
    def vector(self):
        return QVector3D(self.parent.x, self.y, self.z)


class PrjSection:
    """
    截面
    """
    def __init__(self, parent):
        self.parent = parent
        self.z = None
        self.nodes: list[PrjNode] = []
        self.color = None
        self.armor = None


class PrjSectionGroup:
    """
    截面组
    """

    def __init__(self):
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Rot: list[float] = [0, 0, 0]
        # 截面组
        self.sections: list[PrjSection] = []


class HullProject:
    """
        工程文件组织逻辑：
        一级：基础信息。信息：安全码，工程名称，作者，编辑时间，同方向截面组
            二级：同方向截面组。信息：名称，中心点位，欧拉方向角，纵向总颜色 & 装甲厚度分区
                三级：截面。信息：z向位置，节点集合（记录x+，从下到上）， 特殊颜色 & 装甲厚度
        组织格式（json）：
        {
            "check_code": "xxxx",
            "project_name": "xxxx",
            "author": "xxxx",
            "edit_time": "xxxx",
            "section_group": [
                {
                    "name": "xxxx",
                    "center": [x, y, z],
                    "euler": [x, y, z],
                    "color": "#xxxxxx",
                    "armor": x,
                    "section": [
                        {
                            "z": x,
                            "node": [[y, z], ... ],
                            "color": "#xxxxxx",
                            "armor": x
                        }
                    ]
                }
                ...
            ]
        }
        """

    def __init__(self, path):
        self.path = path
        self.__check_code = None
        self.project_name = None
        self.author = None
        self.__edit_time = None
        self.__section_group: list[PrjSectionGroup] = []

    def new_section(self):
        """
        产生交互界面，根据用户需求产生相应对象
        :return: PrjSection
        """

    def add_section(self, prjsection: Union[PrjSectionGroup, list[PrjSectionGroup]]):
        if isinstance(prjsection, PrjSectionGroup):
            self.__section_group.append(prjsection)
        elif isinstance(prjsection, list):
            self.__section_group.extend(prjsection)

    def del_section(self, prjsection: PrjSectionGroup):
        self.__section_group.remove(prjsection)

    def export2NA(self, path):
        """
        导出为NA文件
        :param path: 导出路径，包括文件名
        """

    def save(self):
        """
        保存工程文件
        """
        # TODO: 生成安全码


class NaPrjReader:
    def __init__(self, path, hullProject):
        self.path = path
        self.hullProject = hullProject
        self.load()

    def load(self):
        with open(self.path, 'r') as f:
            data = ujson.load(f)
            self.hullProject.__check_code = data['check_code']
            if not self.check_checkCode():
                QMessageBox.warning(None, "警告", "工程文件已损坏", QMessageBox.Ok)
                return None
            self.hullProject.project_name = data['project_name']
            self.hullProject.author = data['author']
            self.hullProject.__edit_time = data['edit_time']
            for section in data['section_group']:
                prjsection = PrjSectionGroup()
                prjsection.z = section['section']['z']
                for node in section['section']['node']:
                    prjnode = PrjNode(prjsection)
                    prjnode.y = node[0]
                    prjnode.z = node[1]
                    prjsection.nodes.append(prjnode)
                prjsection.color = section['section']['color']
                prjsection.armor = section['section']['armor']
                self.hullProject.add_section(prjsection)

    def check_checkCode(self):
        # TODO: 安全码验证
        if self.hullProject.__check_code == "xxxx":
            return True
        return False
