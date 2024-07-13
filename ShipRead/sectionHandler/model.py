"""
模型
"""
from GUI.element_structure_widgets import *
from PyQt5.QtGui import QVector3D
from ShipRead.sectionHandler.baseSH import SectionHandler
from pyqtOpenGL import GLModelItem


class Model(SectionHandler):
    """
    模型
    """
    TAG = "Model"

    def getCopy(self):
        model = Model(self.hullProject, self.name, self.Pos, self.Rot, self.Scl, self.file_path)
        return model

    idMap = {}
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, prj, name, pos: QVector3D, rot: List[float], scl: List[float], file_path):
        self.hullProject = prj
        self.name = name
        self.Pos = pos
        self.Rot = rot
        self.Scl = scl
        self.file_path = file_path
        super().__init__('PosShow')
        modelRenderConfig = configHandler.get_config("ModelRenderSetting")
        with Log().redirectOutput(self.TAG):  # 模型加载时，库内会有输出，这里重定向到日志
            modelItem = GLModelItem(file_path, lights=[],
                                    selectable=True,
                                    glOptions="translucent",
                                    drawLine=modelRenderConfig["ModelDrawLine"],
                                    lineWidth=modelRenderConfig["ModelLineWith"],
                                    lineColor=modelRenderConfig["ModelLineColor"])
            # 如果加载失败，不继续
            if hasattr(modelItem, "load_failed") and modelItem.load_failed:
                self.load_failed = True
                self.delete()
                return
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
        super().delete()
        try:
            Model.idMap.pop(self.getId())
        except KeyError:
            pass

    def to_dict(self):
        if isinstance(self.Rot, QVector3D):
            self.Rot = [self.Rot.x(), self.Rot.y(), self.Rot.z()]
            Log().warning(self.TAG, f"{self.name} 函数to_dict：Rot 的类型为 QVector3D，已转换为 List[float]")
        if isinstance(self.Scl, QVector3D):
            self.Scl = [self.Scl.x(), self.Scl.y(), self.Scl.z()]
            Log().warning(self.TAG, f"{self.name} 函数to_dict：Scl 的类型为 QVector3D，已转换为 List[float]")
        return {
            "name": f"{self.name}",
            "pos": [self.Pos.x(), self.Pos.y(), self.Pos.z()],
            "rot": self.Rot,
            "scl": self.Scl,
            "file_path": str(self.file_path)
        }
