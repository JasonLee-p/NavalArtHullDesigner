"""
程文件组件基类，定义了组件的基本属性和方法，包括渲染，GUI控制，相关操作等。

这个模块包含以下类：
    SectionHandler：管理和渲染船体模型的主要部分。
    SubSectionHandler：主要部分内的子部分的基类，提供常见功能。
    SectionNodeXY：表示XY平面中的节点，用于定义船体或装甲截面。
    SectionNodeXZ：表示XZ平面中的节点，用于定义舰桥截面。
"""
import traceback

from GUI.hierarchy_widgets import *
from GUI.sub_component_edt_widgets import SubElementShow
from PyQt5.QtGui import QVector3D

from pyqtOpenGL import GLMeshItem, sphere, cube, EditItemMaterial, GLGraphicsItem, GLViewWidget


class PrjComponent(QObject):
    """
    项目组件基类，定义了组件的基本属性和方法，包括渲染，GUI控制，相关操作等。
    """
    TAG = "PrjComponent"
    SPHERE_VER, SHPERE_IDX, SPHERE_UV, SPHERE_NORM = sphere(2, 16, 16, calc_uv_norm=True)
    CUBE_VER, CUBE_NORM, CUBE_TEX = cube(1, 1, 1)

    _main_editor = None
    _gl_widget = None
    _structure_tab = None
    _edit_tab = None
    _hsg_tab = None
    _asg_tab = None
    _bridge_tab = None
    _ladder_tab = None
    _model_tab = None
    _image_tab = None

    _hsg_bt_scroll_widget = None
    _asg_bt_scroll_widget = None
    _bridge_bt_scroll_widget = None
    _ladder_bt_scroll_widget = None
    _model_bt_scroll_widget = None
    _image_bt_scroll_widget = None

    @classmethod
    def update_sphere(cls, radius, rows, cols):
        """
        """
        cls.SPHERE_VER, cls.SHPERE_IDX, cls.SPHERE_UV, cls.SPHERE_NORM = sphere(radius, rows, cols, calc_uv_norm=True)

    @classmethod
    def init_ref(cls, main_editor):
        """
        """
        cls._main_editor = main_editor
        cls._gl_widget = cls._main_editor.gl_widget
        cls._structure_tab = cls._main_editor.structure_tab
        cls._edit_tab = cls._main_editor.edit_tab

        cls._hsg_tab = cls._structure_tab.hullSectionGroup_tab
        cls._asg_tab = cls._structure_tab.armorSectionGroup_tab
        cls._bridge_tab = cls._structure_tab.bridge_tab
        cls._ladder_tab = cls._structure_tab.ladder_tab
        cls._model_tab = cls._structure_tab.model_tab
        cls._image_tab = cls._structure_tab.refImage_tab

        cls._hsg_bt_scroll_widget = cls._hsg_tab.scroll_widget
        cls._asg_bt_scroll_widget = cls._asg_tab.scroll_widget
        cls._bridge_bt_scroll_widget = cls._bridge_tab.scroll_widget
        cls._ladder_bt_scroll_widget = cls._ladder_tab.scroll_widget
        cls._model_bt_scroll_widget = cls._model_tab.scroll_widget
        cls._image_bt_scroll_widget = cls._image_tab.scroll_widget

    @classmethod
    def clear_widgets(cls):
        """
        """
        cls._main_editor = None
        cls._gl_widget = None
        cls._structure_tab = None

        cls._hsg_tab = None
        cls._asg_tab = None
        cls._bridge_tab = None
        cls._ladder_tab = None
        cls._model_tab = None
        cls._image_tab = None

        cls._hsg_bt_scroll_widget = None
        cls._asg_bt_scroll_widget = None
        cls._bridge_bt_scroll_widget = None
        cls._ladder_bt_scroll_widget = None
        cls._model_bt_scroll_widget = None
        cls._image_bt_scroll_widget = None

    def __init__(self, showButton_type: Literal['PosShow', 'PosRotShow'] = 'PosRotShow'):
        """
        初始化绘制对象，连接到主绘制窗口
        paintItem被初始化为None，若需要则调用setPaintItem
        :param showButton_type: _showButton被初始化为showButton_typel类型，若需要修改行为则覆写_init_showButton
        """
        self.paintItem: Optional[GLGraphicsItem] = None
        self._showButton: Optional[Union[NoneShow, ShowButton]] = None
        super().__init__(None)
        # 获取主绘制窗口，使其能够连接到主窗口及其下属控件
        if not hasattr(self, "hullProject"):
            if hasattr(self, "_parent"):
                self.hullProject = self._parent.hullProject
            else:
                trace = traceback.extract_stack()[-2]
                Log().error(trace, self.TAG, "No hullProject attribute or parent attribute")
                raise AttributeError("No hullProject attribute or parent attribute")
        # 初始化基础属性
        if not hasattr(self, "Pos"):
            self.Pos = QVector3D(0, 0, 0)
        # 初始化showButton
        self._init_showButton(showButton_type)
        # 赋值一个唯一的id
        self._custom_id = str(id(self))
        while self._custom_id in self.idMap:  # noqa
            self._custom_id = str(id(self))
        self.idMap[self._custom_id] = self  # noqa

    def hasPrj(self):
        """
        """
        if hasattr(self, "hullProject"):
            if self.hullProject is not None:
                return True
        return False

    def hasPaintItem(self):
        """
        """
        return self.paintItem is not None

    def setPaintItem(self, paintItem: Literal["default", GLGraphicsItem]):
        """

        :param paintItem: 无需手动添加lights
        :return:
        """
        if self.hasPaintItem():
            self._gl_widget.removeItem(self.paintItem)
            self.paintItem.set_selected_s.disconnect(self.set_showButton_checked)
            self.paintItem.handler = None
            self.paintItem = None
            Log().info(self.TAG, f"{self} 移除原有paintItem")
        if paintItem == "default":
            Log().warning(self.TAG, f"{self} 将paintItem设置为默认球体")
            paintItem = GLMeshItem(
                vertexes=PrjComponent.SPHERE_VER, indices=PrjComponent.SHPERE_IDX,
                normals=PrjComponent.SPHERE_NORM,
                lights=[PrjComponent._gl_widget.light],
                # 随机颜色
                material=EditItemMaterial(color=np.random.randint(128, 255, 3).tolist()),
                glOptions='translucent',
                selectable=True
            ).translate(self.Pos.x(), self.Pos.y(), self.Pos.z())
        else:
            if hasattr(paintItem, "addLight"):
                paintItem.addLight([PrjComponent._gl_widget.light])
            else:
                Log().warning(self.TAG, f"{self} paintItem没有addLight方法")
        self.paintItem = paintItem
        # 绑定handler
        self.paintItem.set_selected_s.connect(self.set_showButton_checked)
        self.paintItem.handler = self
        PrjComponent._gl_widget.addItem(self.paintItem)
        self.setSelected(False, set_button=True)

    def getId(self):
        """
        """
        return self._custom_id

    @abstractmethod
    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        if type_ == 'PosShow':
            self._showButton = PosShow(self.hullProject.gl_widget, self._model_bt_scroll_widget, self)
        elif type_ == 'PosRotShow':
            self._showButton = PosRotShow(self.hullProject.gl_widget, self._model_bt_scroll_widget, self)
        else:
            trace = traceback.extract_stack()[-2]
            Log().error(trace, self.TAG, f"未知的showButton类型: {type_}")
            raise ValueError(f"未知的showButton类型: {type_}")

    @abstractmethod
    def getCopy(self):
        """
        """
        return PrjComponent()

    def addLight(self, lights: list):
        """
        """
        self.paintItem.addLight(lights)

    def setVisable(self, visable: bool):
        """
        """
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
        """
        """
        self._showButton.setChecked(selected)

    def selected(self):
        """
        """
        return self.paintItem.selected()

    def setPos(self, pos: QVector3D):
        """
        """
        self.Pos = pos
        self._showButton.setPos(pos)
        if self.paintItem:
            self.paintItem.moveTo(pos.x(), pos.y(), pos.z())
        else:
            Log().warning(self.TAG, f"{self} 没有paintItem")

    def setPosX(self, x: float):
        """
        """
        self.Pos.setX(x)
        self._showButton.setPosX(round(x, 4))
        self.paintItem.moveTo(x, self.Pos.y(), self.Pos.z())

    def setPosY(self, y: float):
        """
        """
        self.Pos.setY(y)
        self._showButton.setPosY(round(y, 4))
        self.paintItem.moveTo(self.Pos.x(), y, self.Pos.z())

    def setPosZ(self, z: float):
        """
        """
        self.Pos.setZ(z)
        self._showButton.setPosZ(round(z, 4))
        self.paintItem.moveTo(self.Pos.x(), self.Pos.y(), z)

    def addPos(self, vec: QVector3D):
        """
        """
        self.Pos += vec
        self.paintItem.moveTo(self.Pos.x(), self.Pos.y(), self.Pos.z())

    def setRot(self, rot: List[float]):
        """
        """
        self.Rot = rot
        if self.paintItem:
            self.paintItem.setEuler(rot[0], rot[1], rot[2])

    def setRotX(self, x: float):
        """
        """
        self.Rot[0] = x
        self.paintItem.setEuler(x, self.Rot[1], self.Rot[2])

    def setRotY(self, y: float):
        """
        """
        self.Rot[1] = y
        self.paintItem.setEuler(self.Rot[0], y, self.Rot[2])

    def setRotZ(self, z: float):
        """
        """
        self.Rot[2] = z
        self.paintItem.setEuler(self.Rot[0], self.Rot[1], z)

    def setScl(self, scl: Union[list, np.ndarray]):
        """
        """
        if hasattr(self, "Scl"):
            self.Scl = scl  # noqa
        else:
            Log().warning(self.TAG, f"{self} 没有Scl属性")
        self.paintItem.setScale(scl[0], scl[1], scl[2])



    @classmethod
    def get_by_id(cls, id_):
        """
        """
        if isinstance(id_, str):
            # noinspection PyUnresolvedReferences
            return cls.idMap.get(id_)
        else:
            return None

    def delete_by_user(self):
        """
        用户操作删除组件
        默认为无法撤回的操作；
        若需要用操作栈，则再operation中新建操作类然后调用。
        :return:
        """
        _d = QMessageBox.warning(self._main_editor, "提示", "删除后无法撤回，并清空历史操作记录，是否继续？",
                                 buttons=QMessageBox.Yes | QMessageBox.No)
        if _d == QMessageBox.No:
            return
        self.delete()
        self._main_editor.clearOperationStack()

    @abstractmethod
    def delete(self):
        """
        释放对象
        :return:
        """
        try:
            self._gl_widget.removeItem(self.paintItem)
        except ValueError:
            pass
        try:
            self.hullProject.del_section(self)
        except ValueError:
            pass
        # noinspection PyUnresolvedReferences
        self.deleted_s.emit()
        self._showButton.deleteLater()
        self.deleteLater()

    @abstractmethod
    def to_dict(self):
        """
        """
        ...

    def __str__(self):
        return f"<{self.__class__.__name__}:{self._custom_id} at ({self.Pos.x()}, {self.Pos.y()}, {self.Pos.z()})>"


class SubPrjComponent(QObject):
    """
    子项目组件基类，定义了组件的基本属性和方法，包括渲染，GUI控制，相关操作等。
    """
    TAG = "SubPrjComponent"
    _main_editor = None
    _gl_widget: Optional[GLViewWidget] = None

    @classmethod
    def init_ref(cls, main_editor):
        """
        初始化供子类使用的控件的引用
        :return:
        """
        cls._main_editor = main_editor
        cls._gl_widget = cls._main_editor.gl_widget

    def __init__(self):
        """
        初始化id，尝试初始化_parent
        """
        if not hasattr(self, "_parent"):
            self._parent: Union[PrjComponent, SubPrjComponent, None] = None
        elif self._parent is not None:
            self.init_parent(self._parent)
        self.paintItem: Optional[GLGraphicsItem] = None
        self._showButton: Optional[SubElementShow] = None
        super().__init__(None)
        # 赋值一个唯一的id
        self._custom_id = str(id(self))
        while self._custom_id in self.idMap:  # noqa
            self._custom_id = str(id(self))
        self.idMap[self._custom_id] = self  # noqa

    def getId(self):
        """
        """
        return self._custom_id

    def hasParent(self):
        """
        """
        return self._parent is not None

    def showButton(self):
        """
        获取showButton，若没有则创建
        :return:
        """
        if self._showButton is None:
            self._showButton = SubElementShow(self._parent._gl_widget, self._parent._model_bt_scroll_widget, self)
        return self._showButton

    def init_parent(self, parent):
        """
        在父类的__init__函数中调用，初始化子类的self._parent引用
        :param parent:
        :return:
        """
        self._parent = parent

    def init_paintItems_parent(self):
        """
        将paintItem添加到父类的paintItem的子项中，一般在init_parent后调用
        若已经调用了setPaintItem()，则不用再调用该函数
        :return:
        """
        if hasattr(self._parent, "paintItem"):
            self._parent.paintItem.addChildItem(self.paintItem)
        else:
            Log().warning(f"{self} has no parent paintItem")

    def setPaintItem(self, paintItem: Literal["default", GLGraphicsItem]):
        """
        设置paintItem，并尝试将其添加到父对象paintItem的子对象中
        :param paintItem:
        :return:
        """
        if self.paintItem is not None:
            self._parent.paintItem.removeChildItem(self.paintItem)
            self.paintItem.handler = None
            self.paintItem = None
            # print(f"[INFO] {self} remove paintItem")
            Log().info(self.TAG, f"{self} remove paintItem")
        if paintItem == "default":
            paintItem = GLMeshItem(
                vertexes=PrjComponent.CUBE_VER, indices=PrjComponent.CUBE_NORM,
                normals=PrjComponent.CUBE_NORM,
                lights=[SubPrjComponent._gl_widget.light],
                material=EditItemMaterial(color=(128, 128, 128)),
                glOptions='translucent',
                selectable=True
            )
        else:
            paintItem.addLight([SubPrjComponent._gl_widget.light])
        self.paintItem = paintItem
        # 绑定handler
        self.paintItem.handler = self
        self.init_paintItems_parent()
        self.setSelected(False)

    def addLight(self, lights: list):
        """
        """
        if hasattr(self.paintItem, "addLight"):
            self.paintItem.addLight(lights)
        else:
            raise AttributeError(f"{self.paintItem} has no addLight method")

    def setSelected(self, selected: bool):
        """
        设置选中状态
        :param selected:
        :return:
        """
        self.set_showButton_checked(selected)
        self.paintItem.setSelected(selected)

    def set_showButton_checked(self, selected: bool):
        """
        """
        self.showButton().setChecked(selected)

    def selected(self):
        """
        """
        return self.paintItem.selected()

    @abstractmethod
    def getCopy(self):
        """
        """
        return SubPrjComponent()

    @abstractmethod
    def delete_by_user(self):
        """
        由showButton调用，删除控件
        :return:
        """
        pass


class ComponentNodeXY(SubPrjComponent):
    """
    xy节点，用于记录船体或装甲截面的节点
    """
    TAG = "ComponentNodeXY"

    def delete_by_user(self):
        super().delete_by_user()

    def getCopy(self):
        """
        """
        node = ComponentNodeXY(self._parent)
        node.x = self.x
        node.y = self.y
        node.y_index = self.y_index
        node.Col = self.Col
        return node

    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, parent=None):
        self._parent = parent
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.y = None
        self.y_index = None  # 指示节点在截面上的索引，根据y值从小到大排序
        super().__init__()

    @property
    def vector(self) -> QVector3D:
        """
        返回节点的局部坐标
        """
        return QVector3D(self.x, self.y, self._parent.z)


class ComponentNodeXZ(SubPrjComponent):
    """
    xz节点，用于记录舰桥的节点
    """
    TAG = "ComponentNodeXZ"

    def delete_by_user(self):
        super().delete_by_user()

    def getCopy(self):
        """
        """
        node = ComponentNodeXZ(self._parent)
        node.x = self.x
        node.z = self.z
        node.Col = self.Col
        return node

    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, parent):
        self._parent = parent
        self.has_parent = False if parent is None else True
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.z = None
        super().__init__()

    @property
    def vector(self):
        """
        """
        return QVector3D(self.x, self._parent.y, self.z)
