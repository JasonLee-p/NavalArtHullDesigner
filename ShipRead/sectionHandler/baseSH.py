"""

"""
from GUI.element_structure_widgets import *
from PyQt5.QtGui import QVector3D
from main_logger import Log

from pyqtOpenGL import GLMeshItem, sphere, cube, EditItemMaterial, GLGraphicsItem


class SectionHandler(QObject):
    SPHERE_VER, SHPERE_IDX, SPHERE_UV, SPHERE_NORM = sphere(2, 16, 16, calc_uv_norm=True)
    CUBE_VER, CUBE_NORM, CUBE_TEX = cube(1, 1, 1)

    _main_handler = None
    _gl_widget = None
    _structure_tab = None
    _hsg_tab = None
    _asg_tab = None
    _bridge_tab = None
    _ladder_tab = None
    _model_tab = None
    _hsg_bt_scroll_widget = None
    _asg_bt_scroll_widget = None
    _bridge_bt_scroll_widget = None
    _ladder_bt_scroll_widget = None
    _model_bt_scroll_widget = None

    @classmethod
    def update_sphere(cls, radius, rows, cols):
        cls.SPHERE_VER, cls.SHPERE_IDX, cls.SPHERE_UV, cls.SPHERE_NORM = sphere(radius, rows, cols, calc_uv_norm=True)

    @classmethod
    def init_widgets(cls, hullPrj):
        cls._main_handler = hullPrj.main_handler
        cls._gl_widget = cls._main_handler.gl_widget
        cls._structure_tab = cls._main_handler.structure_tab
        cls._hsg_tab = cls._structure_tab.hullSectionGroup_tab
        cls._asg_tab = cls._structure_tab.armorSectionGroup_tab
        cls._bridge_tab = cls._structure_tab.bridge_tab
        cls._ladder_tab = cls._structure_tab.ladder_tab
        cls._model_tab = cls._structure_tab.model_tab
        cls._hsg_bt_scroll_widget = cls._hsg_tab.scroll_widget
        cls._asg_bt_scroll_widget = cls._asg_tab.scroll_widget
        cls._bridge_bt_scroll_widget = cls._bridge_tab.scroll_widget
        cls._ladder_bt_scroll_widget = cls._ladder_tab.scroll_widget
        cls._model_bt_scroll_widget = cls._model_tab.scroll_widget

    @classmethod
    def clear_widgets(cls):
        cls._main_handler = None
        cls._gl_widget = None
        cls._structure_tab = None
        cls._hsg_tab = None
        cls._asg_tab = None
        cls._bridge_tab = None
        cls._ladder_tab = None
        cls._model_tab = None
        cls._hsg_bt_scroll_widget = None
        cls._asg_bt_scroll_widget = None
        cls._bridge_bt_scroll_widget = None
        cls._ladder_bt_scroll_widget = None
        cls._model_bt_scroll_widget = None

    def __init__(self, showButton_type: Literal['PosShow', 'PosRotShow'] = 'PosRotShow'):
        """
        初始化绘制对象，连接到主绘制窗口
        """
        self.paintItem = None
        self._showButton = None
        super().__init__(None)
        # 获取主绘制窗口，使其能够连接到主窗口及其下属控件
        if not hasattr(self, "hullProject"):
            if hasattr(self, "_parent"):
                self.hullProject = self._parent.hullProject
            else:
                raise AttributeError("No hullProject attribute or parent attribute")
        # 初始化供子类使用的控件的引用
        SectionHandler.init_widgets(self.hullProject)
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
        if hasattr(self, "hullProject"):
            if self.hullProject is not None:
                return True
        return False

    def hasPaintItem(self):
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
            print(f"[INFO] {self} remove paintItem")
        if paintItem == "default":
            paintItem = GLMeshItem(
                vertexes=SectionHandler.SPHERE_VER, indices=SectionHandler.SHPERE_IDX,
                normals=SectionHandler.SPHERE_NORM,
                lights=[SectionHandler._gl_widget.light],
                # 随机颜色
                material=EditItemMaterial(color=np.random.randint(128, 255, 3).tolist()),
                glOptions='translucent',
                selectable=True
            ).translate(self.Pos.x(), self.Pos.y(), self.Pos.z())
        else:
            paintItem.addLight([SectionHandler._gl_widget.light])
        self.paintItem = paintItem
        # 绑定handler
        self.paintItem.set_selected_s.connect(self.set_showButton_checked)
        self.paintItem.handler = self
        SectionHandler._gl_widget.addItem(self.paintItem)
        self.setSelected(False, set_button=True)

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
        self._showButton.setPos(pos)
        self.paintItem.moveTo(pos.x(), pos.y(), pos.z())

    def setPosX(self, x: float):
        self.Pos.setX(x)
        self._showButton.setPosX(round(x, 4))
        self.paintItem.moveTo(x, self.Pos.y(), self.Pos.z())

    def setPosY(self, y: float):
        self.Pos.setY(y)
        self._showButton.setPosY(round(y, 4))
        self.paintItem.moveTo(self.Pos.x(), y, self.Pos.z())

    def setPosZ(self, z: float):
        self.Pos.setZ(z)
        self._showButton.setPosZ(round(z, 4))
        self.paintItem.moveTo(self.Pos.x(), self.Pos.y(), z)

    def addPos(self, vec: QVector3D):
        self.Pos += vec
        self.paintItem.moveTo(self.Pos.x(), self.Pos.y(), self.Pos.z())

    def setRot(self, rot: List[float]):
        self.Rot = rot
        self.paintItem.setEuler(rot[0], rot[1], rot[2])

    def setRotX(self, x: float):
        self.Rot[0] = x
        self.paintItem.setEuler(x, self.Rot[1], self.Rot[2])

    def setRotY(self, y: float):
        self.Rot[1] = y
        self.paintItem.setEuler(self.Rot[0], y, self.Rot[2])

    def setRotZ(self, z: float):
        self.Rot[2] = z
        self.paintItem.setEuler(self.Rot[0], self.Rot[1], z)

    def setScl(self, scl: QVector3D):
        self.paintItem.scale(scl.x(), scl.y(), scl.z())

    @classmethod
    def get_by_id(cls, id_):
        if isinstance(id_, str):
            # noinspection PyUnresolvedReferences
            return cls.idMap.get(id_)
        else:
            return None

    @abstractmethod
    def delete(self):
        # noinspection PyUnresolvedReferences
        self.deleted_s.emit()
        self._showButton.deleteLater()
        self.deleteLater()
        self._gl_widget.removeItem(self.paintItem)

    @abstractmethod
    def to_dict(self):
        ...


class SubSectionHandler(QObject):
    _main_handler = None
    _gl_widget = None

    @classmethod
    def init_widgets(cls, parent):
        cls._main_handler = parent.hullProject.main_handler
        cls._gl_widget = cls._main_handler.gl_widget

    def __init__(self):
        if not hasattr(self, "_parent"):
            self._parent: Union[SectionHandler, SubSectionHandler, None] = None
        elif self._parent is not None:
            self.init_parent(self._parent)
        self.paintItem: Union[GLGraphicsItem, None] = None
        super().__init__(None)
        # 赋值一个唯一的id
        self._custom_id = str(id(self))
        while self._custom_id in self.idMap:  # noqa
            self._custom_id = str(id(self))
        self.idMap[self._custom_id] = self  # noqa

    def getId(self):
        return self._custom_id

    def hasParent(self):
        return self._parent is not None

    def hasPaintItem(self):
        return self.paintItem is not None

    def init_parent(self, parent):
        self._parent = parent
        # 获取主绘制窗口，使其能够连接到主窗口及其下属控件
        SubSectionHandler.init_widgets(self._parent)

    def init_paintItem_as_child(self):
        if hasattr(self._parent, "paintItem"):
            self._parent.paintItem.addChildItem(self.paintItem)
        else:
            raise AttributeError(f"{self} has no parent paintItem")

    def setPaintItem(self, paintItem: Literal["default", GLGraphicsItem]):
        if self.hasPaintItem():
            self._parent.paintItem.removeChildItem(self.paintItem)
            self.paintItem.handler = None
            self.paintItem = None
            print(f"[INFO] {self} remove paintItem")
        if paintItem == "default":
            paintItem = GLMeshItem(
                vertexes=SectionHandler.CUBE_VER, indices=SectionHandler.CUBE_NORM,
                normals=SectionHandler.CUBE_NORM,
                lights=[SubSectionHandler._gl_widget.light],
                material=EditItemMaterial(color=(128, 128, 128)),
                glOptions='translucent',
                selectable=True
            )
        else:
            paintItem.addLight([SubSectionHandler._gl_widget.light])
        self.paintItem = paintItem
        # 绑定handler
        self.paintItem.handler = self
        if hasattr(self._parent, "paintItem"):
            self._parent.paintItem.addChildItem(self.paintItem)
        else:
            print(f"[WARNING] {self} has no parent paintItem")
        self.setSelected(False)

    def addLight(self, lights: list):
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
        self.paintItem.setSelected(selected)

    def selected(self):
        return self.paintItem.selected()


class SectionNodeXY(SubSectionHandler):
    """
    xy节点，用于记录船体或装甲截面的节点
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, parent=None):
        self._parent = parent
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.y = None
        self.y_index = None  # 指示节点在截面上的索引，根据y值从小到大排序
        super().__init__()

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
        self.has_parent = False if parent is None else True
        self.Col = QColor(128, 128, 129)  # 颜色
        self.x = None
        self.z = None
        super().__init__()

    @property
    def vector(self):
        return QVector3D(self.x, self._parent.y, self.z)