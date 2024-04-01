"""
模型
"""
from GUI.element_structure_widgets import *
from PyQt5.QtGui import QVector3D
from ShipRead.sectionHandler.baseSH import SectionHandler
from path_vars import CURRENT_PATH
from pyqtOpenGL import GLModelItem


class Model(SectionHandler):
    """
    模型
    """
    idMap = {}
    deleted_s = pyqtSignal()

    def __init__(self, prj, name, pos: QVector3D, rot: List[float], scl: List[float], file_path):
        self.hullProject = prj
        self.name = name
        self.Pos = pos
        self.Rot = rot
        self.Scl = scl
        self.file_path = file_path
        super().__init__('PosShow')
        modelRenderConfig = configHandler.get_config("ModelRenderSetting")
        modelItem = GLModelItem(file_path, lights=[],
                                selectable=True,
                                glOptions="translucent",
                                drawLine=modelRenderConfig["ModelDrawLine"],
                                lineWidth=modelRenderConfig["ModelLineWith"],
                                lineColor=modelRenderConfig["ModelLineColor"])
        self.setPaintItem(modelItem)
        self.setPos(pos)
        self.setRot(rot)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._model_bt_scroll_widget.layout().addWidget(self._showButton)

    def set_showButton_checked(self, selected: bool):
        super().set_showButton_checked(selected)
        # 设置左侧结构树当前的tab
        self._structure_tab.setCurrentTab(self._model_tab.widget)

    def setDrawLine(self, drawLine: bool):
        self.paintItem.setDrawLine(drawLine)

    def delete(self):
        """
        所有的删除操作都应该调用这个方法，即使是在控件中删除
        :return:
        """
        SectionHandler._model_tab._items.pop(self)  # noqa
        Model.idMap.pop(self.getId())
        super().delete()

    def to_dict(self):
        if isinstance(self.Rot, QVector3D):
            self.Rot = [self.Rot.x(), self.Rot.y(), self.Rot.z()]
            print(f"[WARNING] {self} Rot is QVector3D, change to list")
        if isinstance(self.Scl, QVector3D):
            self.Scl = [self.Scl.x(), self.Scl.y(), self.Scl.z()]
            print(f"[WARNING] {self} Scl is QVector3D, change to list")
        return {
            "name": f"{self.name}",
            "pos": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "scl": self.Scl,
            "file_path": str(self.file_path)
        }
