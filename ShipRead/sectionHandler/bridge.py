"""

"""
from PyQt5.QtGui import QVector3D, QColor
from GUI.element_structure_widgets import *
from ShipRead.sectionHandler.baseSH import SectionHandler, SubSectionHandler, SectionNodeXZ


class Railing(SubSectionHandler):
    """
    栏杆
    """

    def delete_by_user(self):
        super().delete_by_user()

    def getCopy(self):
        railing = Railing(self.hullProject, self._parent)
        railing.height = self.height
        railing.interval = self.interval
        railing.thickness = self.thickness
        railing.Col = self.Col
        return railing

    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, prj, parent):
        self.hullProject = prj
        self.height = 1.2  # 栏杆高度
        self.interval = 1.0  # 栏杆间隔
        self.thickness = 0.1  # 栏杆厚度
        self._parent = parent
        self.Col: QColor = QColor(128, 128, 128)  # 颜色
        super().__init__()
        self.setPaintItem("default")

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

    def delete_by_user(self):
        super().delete_by_user()

    def getCopy(self):
        handrail = Handrail(self.hullProject, self._parent)
        handrail.height = self.height
        handrail.thickness = self.thickness
        handrail.Col = self.Col
        return handrail

    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, prj, parent):
        self.hullProject = prj
        self.height = 1.2  # 栏板高度
        self.thickness = 0.1  # 栏板厚度
        self._parent = parent
        self.Col: QColor = QColor(128, 128, 128)
        super().__init__()

    def to_dict(self):
        return {
            "height": self.height,
            "thickness": self.thickness,
            "type": "handrail",
            "col": f"#{self.Col.red():02x}{self.Col.green():02x}{self.Col.blue():02x}"
        }


class Bridge(SectionHandler):
    """
    舰桥
    """

    def getCopy(self):
        bridge = Bridge(self.hullProject, self.name, self.rail_only)
        bridge.Pos = self.Pos
        bridge.Col = self.Col
        bridge.armor = self.armor
        bridge.nodes = [node.getCopy() for node in self.nodes]
        if self.rail:
            bridge.rail = self.rail.getCopy()
        return bridge

    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, prj, name, rail_only):
        self.hullProject = prj
        self.name = name
        self.rail_only = rail_only  # 是否只有栏杆
        self.Pos: QVector3D = QVector3D(0, 0, 0)
        self.Col = QColor(128, 128, 129)  # 颜色
        self.armor = None
        self.nodes: List[SectionNodeXZ] = []
        self.rail: Union[Railing, Handrail, None] = None
        super().__init__('PosShow')
        self.setPaintItem("default")
        self.setPos(self.Pos)

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

    def delete(self):
        Bridge.idMap.pop(self.getId())
        SectionHandler._bridge_tab._items.pop(self)  # noqa
        super().delete()
