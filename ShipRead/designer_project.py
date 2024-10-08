"""
读取设计器工程文件
文件格式名称为.naprj，使用json格式

当需要添加新的图纸组件时，直接查询 “ *添加图纸组件* ”关键字，并按照注释添加即可
"""
import os
import time
import traceback
from hashlib import sha1

import ujson
from GUI.hierarchy_widgets import *
from PyQt5.QtGui import QVector3D, QColor
from PyQt5.QtWidgets import QMessageBox
from ShipPaint import *
from ShipRead.sectionHandler import *
from path_lib import CURRENT_PATH


class DesignerProject(QObject):
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
            "ref_image": [
                {
                    "name": "userdefined",
                    "pos": [0, 0, 0],
                    "rot": [0, 0, 0],
                    "file_path": "path/to/file/with/name.png"
                }
            ]
        }
        """
    TAG = "ShipProject"
    # 下面这些信号会被连接到main_handler的同名槽函数，用于更新视图
    # *添加图纸组件*请在此添加组件的信号
    add_hull_section_group_s = pyqtSignal(str)  # noqa  # 添加船体截面组的信号，传出截面组id
    add_armor_section_group_s = pyqtSignal(str)  # noqa  # 添加装甲截面组的信号，传出截面组id
    add_bridge_s = pyqtSignal(str)  # noqa  # 添加舰桥的信号，传出舰桥id
    add_ladder_s = pyqtSignal(str)  # noqa  # 添加梯子的信号，传出梯子id
    add_model_s = pyqtSignal(str)  # noqa  # 添加模型的信号，传出模型id
    add_ref_image_s = pyqtSignal(str)  # noqa  # 添加参考图片的信号，传出参考图片id
    # *添加图纸组件*请在此添加组件的信号
    del_hull_section_group_s = pyqtSignal(str)  # noqa  # 删除船体截面组的信号，传出截面组id
    del_armor_section_group_s = pyqtSignal(str)  # noqa  # 删除装甲截面组的信号，传出截面组id
    del_bridge_s = pyqtSignal(str)  # noqa  # 删除舰桥的信号，传出舰桥id
    del_ladder_s = pyqtSignal(str)  # noqa  # 删除梯子的信号，传出梯子id
    del_model_s = pyqtSignal(str)  # noqa  # 删除模型的信号，传出模型id
    del_ref_image_s = pyqtSignal(str)  # noqa  # 删除参考图片的信号，传出参考图片id

    def __init__(self, path: str):  # noqa
        """

        :param path: 含文件名的路径
        """
        super().__init__(None)
        self.main_editor = None
        # 锁
        self.prj_file_mutex = QMutex()
        self.locker = QMutexLocker(self.prj_file_mutex)

        self.path = path
        self.__check_code = None
        self.project_name = None
        self.author = None
        self.__edit_time = None
        # *添加图纸组件*请在此添加组件的列表，使用__snake_case命名
        self.__hull_section_group: List[HullSectionGroup] = []
        self.__armor_section_group: List[ArmorSectionGroup] = []
        self.__bridge: List[Bridge] = []
        self.__ladder: List[Ladder] = []
        self.__model: List[Model] = []
        self.__ref_image: List[RefImage] = []

    def bind_signal_to_editor(self, main_editor):
        """
        将信号绑定到主处理器
        随后当添加或删除元素时，会发出信号，通知mainEditor控件更新
        *添加图纸组件*请在此添加组件的信号绑定
        :return:
        """
        self.add_hull_section_group_s.connect(main_editor.add_hull_section_group_s)
        self.add_armor_section_group_s.connect(main_editor.add_armor_section_group_s)
        self.add_bridge_s.connect(main_editor.add_bridge_s)
        self.add_ladder_s.connect(main_editor.add_ladder_s)
        self.add_model_s.connect(main_editor.add_model_s)
        self.add_ref_image_s.connect(main_editor.add_ref_image_s)

        self.del_hull_section_group_s.connect(main_editor.del_hull_section_group_s)
        self.del_armor_section_group_s.connect(main_editor.del_armor_section_group_s)
        self.del_bridge_s.connect(main_editor.del_bridge_s)
        self.del_ladder_s.connect(main_editor.del_ladder_s)
        self.del_model_s.connect(main_editor.del_model_s)
        self.del_ref_image_s.connect(main_editor.del_ref_image_s)

        self.main_editor = main_editor

    def unbind_signal_to_handler(self, main_editor):
        """
        解绑信号，在切换工程时使用
        *添加图纸组件*请在此添加组件的信号解绑
        :return:
        """
        self.add_hull_section_group_s.disconnect(main_editor.add_hull_section_group_s)
        self.add_armor_section_group_s.disconnect(main_editor.add_armor_section_group_s)
        self.add_bridge_s.disconnect(main_editor.add_bridge_s)
        self.add_ladder_s.disconnect(main_editor.add_ladder_s)
        self.add_model_s.disconnect(main_editor.add_model_s)
        self.add_ref_image_s.disconnect(main_editor.add_ref_image_s)

        self.del_hull_section_group_s.disconnect(main_editor.del_hull_section_group_s)
        self.del_armor_section_group_s.disconnect(main_editor.del_armor_section_group_s)
        self.del_bridge_s.disconnect(main_editor.del_bridge_s)
        self.del_ladder_s.disconnect(main_editor.del_ladder_s)
        self.del_model_s.disconnect(main_editor.del_model_s)
        self.del_ref_image_s.disconnect(main_editor.del_ref_image_s)

        self.main_editor = None

    def init_in_main_editor(self):
        """
        在main_editor的HierarchyContainer中初始化
        遍历组件，触发信号，更新界面
        *添加图纸组件*请在此添加组件的遍历
        :return:
        """
        for hs_group in self.__hull_section_group:
            self.add_hull_section_group_s.emit(hs_group.getId())
        for as_group in self.__armor_section_group:
            self.add_armor_section_group_s.emit(as_group.getId())
        for bridge_ in self.__bridge:
            self.add_bridge_s.emit(bridge_.getId())
        for ladder_ in self.__ladder:
            self.add_ladder_s.emit(ladder_.getId())
        for model_ in self.__model:
            self.add_model_s.emit(model_.getId())
        for ref_image_ in self.__ref_image:
            self.add_ref_image_s.emit(ref_image_.getId())

    """
    以下为添加图纸组件的方法
    *添加图纸组件*请在此添加组件的方法
    """

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
        file_dialog = QFileDialog(None)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("模型文件 (*.obj)")
        file_dialog.setViewMode(QFileDialog.Detail)
        find_path = configHandler.get_config("FindModelFolder")
        file_dialog.setDirectory(find_path)
        file_dialog.fileSelected.connect(lambda p: self.add_model_byPath(p))  # noqa
        file_dialog.exec_()

    def new_refImage(self):
        """
        产生交互界面，根据用户需求产生相应对象
        :return: PrjSection
        """
        file_dialog = QFileDialog(None)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("图片文件 (*.png *.jpg *.bmp *.jpeg)")
        file_dialog.setViewMode(QFileDialog.Detail)
        find_path = configHandler.get_config("FindModelFolder")
        file_dialog.setDirectory(find_path)
        file_dialog.fileSelected.connect(lambda p: self.add_refImage_byPath(p))
        file_dialog.exec_()

    """
    以下为添加图纸组件的方法
    *添加图纸组件*请在此添加组件的方法
    """

    def add_section(self, prjsection: Union[HullSectionGroup, ArmorSectionGroup, Bridge, Ladder, Model]):
        """
        添加截面组到工程中，同时发出信号，通知视图更新
        :param prjsection: 截面组

        """
        if isinstance(prjsection, HullSectionGroup):
            self.add_hullSectionGroup(prjsection)
        elif isinstance(prjsection, ArmorSectionGroup):
            self.add_armorSectionGroup(prjsection)
        elif isinstance(prjsection, Bridge):
            self.add_bridge(prjsection)
        elif isinstance(prjsection, Ladder):
            self.add_ladder(prjsection)
        elif isinstance(prjsection, Model):
            self.add_model(prjsection)
        elif isinstance(prjsection, RefImage):
            self.add_refImage(prjsection)
        else:
            raise TypeError(f"未知的类型{prjsection}")

    def add_sections(self, prjsections: List[Union[HullSectionGroup, ArmorSectionGroup, Bridge, Ladder, Model]]):
        """
        添加多个截面组到工程中，同时发出信号，通知视图更新
        :param prjsections: 截面组列表
        """
        for prjsection in prjsections:
            self.add_section(prjsection)

    def add_hullSectionGroup(self, prjsection: HullSectionGroup, init=False):
        """
        将船体截面组添加到工程中，同时发出信号，通知视图更新
        :param prjsection: 船体截面组
        :param init: 是否是在工程文件初始化时添加
        """
        if prjsection in self.__hull_section_group:
            self.__hull_section_group.append(prjsection.getCopy())
        else:
            self.__hull_section_group.append(prjsection)
        if not init:
            self.add_hull_section_group_s.emit(str(id(prjsection)))

    def add_armorSectionGroup(self, prjsection: ArmorSectionGroup, init=False):
        """
        将装甲截面组添加到工程中，同时发出信号，通知视图更新
        :param prjsection: 装甲截面组
        :param init: 是否是在工程文件初始化时添加
        """
        if prjsection in self.__armor_section_group:
            self.__armor_section_group.append(prjsection.getCopy())
        else:
            self.__armor_section_group.append(prjsection)
        if not init:
            self.add_armor_section_group_s.emit(str(id(prjsection)))

    def add_bridge(self, prjsection: Bridge, init=False):
        """
        将舰桥添加到工程中，同时发出信号，通知视图更新
        :param prjsection: 舰桥
        :param init: 是否是在工程文件初始化时添加
        """
        if prjsection in self.__bridge:
            self.__bridge.append(prjsection.getCopy())
        else:
            self.__bridge.append(prjsection)
        if not init:
            self.add_bridge_s.emit(str(id(prjsection)))

    def add_ladder(self, prjsection: Ladder, init=False):
        """
        将梯子添加到工程中，同时发出信号，通知视图更新
        :param prjsection: 梯子
        :param init: 是否是在工程文件初始化时添加
        """
        if prjsection in self.__ladder:
            self.__ladder.append(prjsection.getCopy())
        else:
            self.__ladder.append(prjsection)
        if not init:
            self.add_ladder_s.emit(str(id(prjsection)))

    def add_model(self, prjsection: Model, init=False):
        """
        将模型添加到工程中，同时发出信号，通知视图更新
        :param prjsection: 模型
        :param init: 是否是在工程文件初始化时添加
        """
        if prjsection in self.__model:
            self.__model.append(prjsection.getCopy())
        else:
            self.__model.append(prjsection)
        if not init:
            self.add_model_s.emit(prjsection.getId())

    def add_refImage(self, prjsection: RefImage, init=False):
        """
        将参考图片添加到工程中，同时发出信号，通知视图更新
        :param prjsection: 参考图片
        :param init: 是否是在工程文件初始化时添加
        """
        if prjsection in self.__ref_image:
            self.__ref_image.append(prjsection.getCopy())
        else:
            self.__ref_image.append(prjsection)
        if not init:
            self.add_ref_image_s.emit(prjsection.getId())

    def add_model_byPath(self, path: str, init=False):  # TODO
        """
        通过路径添加模型到工程中，同时发出信号，通知视图更新
        :param path: 模型路径
        :param init: 是否初始化（未实现）
        """
        name = os.path.basename(path)
        name = name[:name.rfind(".")]
        path = os.path.abspath(path)
        model_ = Model(self, name, QVector3D(0, 0, 0), [0, 0, 0], [1, 1, 1], path)
        self.add_model(model_)

    def add_refImage_byPath(self, path: str, init=False):  # TODO
        """
        通过路径添加参考图片到工程中，同时发出信号，通知视图更新
        """
        name = os.path.basename(path)
        name = name[:name.rfind(".")]
        path = os.path.abspath(path)
        ref_image = RefImage(self, name, QVector3D(0, 0, 0), [0, 0, 0], [1, 1, 1], path)
        self.add_refImage(ref_image)

    def del_section(self, prjsection: Union[HullSectionGroup, ArmorSectionGroup, Bridge, Ladder, Railing, Handrail]):
        """
        删除截面组，同时发出信号，通知视图更新
        *添加图纸组件*请在此添加组件的删除方法
        :param prjsection: 截面组
        """
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
        elif isinstance(prjsection, RefImage):
            self.__ref_image.remove(prjsection)
            self.del_ref_image_s.emit(prjsection.getId())
        else:
            raise TypeError(f"未知的类型{prjsection}")

    def export2NA(self, path):
        """
        导出为NA文件
        :param path: 导出路径，包括文件名
        """
        self.save()
        with self.locker:
            with open(path, 'w', encoding='utf-8') as f:  # noqa
                # TODO:
                ...

    def to_dict(self):
        """
        将工程文件转换为字典，用于存为json
        *添加图纸组件*请在此添加组件的to_dict方法
        """
        year, month, day, hour, minute, second = time.localtime(time.time())[:6]
        return {
            "check_code": self.__check_code,
            "project_name": self.project_name,
            "author": self.author,
            "edit_time": f"{year}-{month}-{day} {hour}:{minute}:{second}",
            "hull_section_group": [hs_group.to_dict() for hs_group in self.__hull_section_group],
            "armor_section_group": [as_group.to_dict() for as_group in self.__armor_section_group],
            "bridge": [bridge_.to_dict() for bridge_ in self.__bridge],
            "ladder": [ladder_.to_dict() for ladder_ in self.__ladder],
            "model": [model_.to_dict() for model_ in self.__model],
            "ref_image": [ref_image_.to_dict() for ref_image_ in self.__ref_image]
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
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                ujson.dump(dict_data, f, indent=2)
            Log().info(self.TAG, f"工程文件 {self.path} 保存成功")
        except TypeError as e_:
            trace = traceback.format_exc()
            Log().error(trace, self.TAG, f"数据转换时出现错误，无法正常保存！请联系作者修复尝试图纸{e_}")
            QMessageBox.warning(None, "严重错误", f"数据转换时出现错误，无法正常保存！请联系作者修复尝试图纸{e_}",
                                QMessageBox.Ok)
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(str(dict_data))


class DesignerPrjReader:
    """
    读取NavalArt工程文件
    """
    TAG = "DesignerPrjReader"

    def __init__(self, main_editor, path, shipProject: DesignerProject):
        """
        :param main_editor: 主编辑器
        :param path: 文件路径
        :param shipProject: 工程对象
        """
        self.main_editor = main_editor
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
            Log().warning(self.TAG, f"工程文件 {self.path} 已损坏")
            QMessageBox.warning(None, "警告", f"工程文件 {self.path} 已损坏", QMessageBox.Ok)
            return False
        self.hullProject.project_name = data['project_name']
        self.hullProject.author = data['author']
        self.hullProject.__edit_time = data['edit_time']
        # 读取各个组件
        # *添加图纸组件*请在此添加组件的读取
        self.load_hull_section_group(data['hull_section_group'])
        self.load_armor_section_group(data['armor_section_group'])
        self.load_bridge(data['bridge'])
        self.load_ladder(data['ladder'])
        self.load_model(data['model'])
        self.load_ref_image(data['ref_image'])
        return True

    """
    以下为读取图纸组件的方法
    *添加图纸组件*请在此添加组件的读取方法
    """

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
            hull_section_group = HullSectionGroup(
                self.hullProject, section_group['name'],
                QVector3D(*section_group['center']), section_group['rot'], QColor(section_group['col']),
                round(float(section_group['top_cur']), 1), round(float(section_group['bot_cur']), 1),
                self.load_hull_section(section_group['sections']))
            self.hullProject.add_hullSectionGroup(hull_section_group, True)
            if "rail" in section_group:
                self.load_rail(section_group['rail'], hull_section_group)

    def load_hull_section(self, data):
        sections = []
        for section in data:
            if "name" in section:
                _name = section['name']
            else:
                _name = None
            hull_section = HullSection(
                self.hullProject, section['z'], section['nodes'], section['col'], section['armor'], _name)
            sections.append(hull_section)
        return sections

    def load_armor_section_group(self, data):
        for section_group in data:
            armor_section_group = ArmorSectionGroup(
                self.hullProject, section_group['name'],
                QVector3D(*section_group['center']), section_group['rot'], QColor(section_group['col']),
                self.load_armor_section(section_group['sections']))
            self.hullProject.add_armorSectionGroup(armor_section_group, True)

    def load_armor_section(self, data):
        sections = []
        for section in data:
            armor_section = ArmorSection(self.hullProject, section['z'], section['nodes'])
            sections.append(armor_section)
        return sections

    def load_bridge(self, data):
        for bridge_ in data:
            bridge_handler = Bridge(self.hullProject, bridge_['name'], bridge_['rail_only'])
            bridge_handler.setPos(QVector3D(*bridge_['pos']))
            bridge_handler.Col = QColor(bridge_['col'])
            bridge_handler.armor = bridge_['armor']
            bridge_handler.nodes = self.load_bridge_node(bridge_['nodes'], bridge_handler)
            self.hullProject.add_bridge(bridge_handler, True)
            if "rail" in bridge_:
                self.load_rail(bridge_['rail'], bridge_handler)

    # noinspection PyMethodMayBeStatic
    def load_bridge_node(self, data, parent):
        nodes = []
        for node in data:
            section_node = ComponentNodeXZ(parent)
            section_node.x, section_node.z = node
            nodes.append(section_node)
        return nodes

    def load_ladder(self, data):
        for ladder_ in data:
            ladder_handler = Ladder(self.hullProject, ladder_['name'], ladder_['shape'])
            ladder_handler.setPos(QVector3D(*ladder_['pos']))
            ladder_handler.setRot(ladder_['rot'])
            ladder_handler.Col = QColor(ladder_['col'])
            ladder_handler.length = ladder_['length']
            ladder_handler.width = ladder_['width']
            ladder_handler.interval = ladder_['interval']
            ladder_handler.material_width = ladder_['material_width']
            self.hullProject.add_ladder(ladder_handler, True)

    def load_model(self, data):
        """
        从工程文件中读取模型
        :param data:
        :return:
        """
        for model_ in data:
            m_p = model_['file_path']
            if m_p.startswith("resources/"):  # 说明是内置模型，需要转换为绝对路径
                m_p = os.path.join(CURRENT_PATH, m_p)
            try:
                model_handler = Model(
                    self.hullProject, model_['name'], QVector3D(*model_['pos']), model_['rot'], model_['scl'], m_p)
                # 加载失败的模型不添加
                if hasattr(model_handler, "load_failed") and model_handler.load_failed:
                    QMessageBox.warning(None, "警告",
                                        f"模型 {model_['name']} 加载失败，文件路径：{m_p}\n"
                                        f"请检查该路径是否正确，或者重新绑定路径！",
                                        QMessageBox.Ok)
            except KeyError:
                raise KeyError(f"模型 {model_['name']} 的数据不完整")
            self.hullProject.add_model(model_handler, True)

    def load_ref_image(self, data):
        """
        从工程文件中读取参考图片（模式和model一样）
        :param data:
        :return:
        """
        for ref_image_ in data:
            img_p = ref_image_['file_path']
            if img_p.startswith("resources/"):  # 说明是内置图片，需要转换为绝对路径
                img_p = os.path.join(CURRENT_PATH, img_p)
            try:
                ref_image_handler = RefImage(
                    self.hullProject, ref_image_['name'], QVector3D(*ref_image_['pos']),
                    ref_image_['rot'], ref_image_['scl'], img_p)
                # 加载失败的图片不添加
                if hasattr(ref_image_handler, "load_failed") and ref_image_handler.load_failed:
                    QMessageBox.warning(None, "警告",
                                        f"图片 {ref_image_['name']} 加载失败，文件路径：{img_p}\n"
                                        f"请检查该路径是否正确，或者重新绑定路径！",
                                        QMessageBox.Ok)
            except KeyError:
                raise KeyError(f"图片 {ref_image_['name']} 的数据不完整")
            self.hullProject.add_refImage(ref_image_handler, True)

    def check_checkCode(self, data: dict):
        """
        检查校验码是否正确
        """
        data.pop("check_code")
        if self.hullProject.__check_code == str(sha1(str(data).encode("utf-8")).hexdigest()):
            return True
        return True
