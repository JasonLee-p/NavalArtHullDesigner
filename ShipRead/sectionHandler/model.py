"""
工程文件组件：模型
"""
from pathlib import Path

from GUI.hierarchy_widgets import *
from PyQt5.QtGui import QVector3D
from .baseComponent import PrjComponent
from pyqtOpenGL import GLModelItem


class Model(PrjComponent):
    """
    模型
    """
    TAG = "Model"

    def getCopy(self):
        model = Model(self.hullProject, self.name, self.Pos, self.Rot, self.Scl, self.file_path)
        return model

    idMap = {}
    update_path_s = pyqtSignal(str)  # noqa
    deleted_s = pyqtSignal()  # noqa

    def __init__(self, prj, name, pos: QVector3D, rot: List[float], scl: List[float], file_path):
        """
        初始化Model对象
        :param prj:
        :param name:
        :param pos:
        :param rot:
        :param scl:
        :param file_path: 允许为不存在的路径（用于加载失败的情况）
        """
        self.hullProject = prj
        self.name = name
        self.Pos = pos
        self.Rot = rot
        self.Scl = scl
        self.file_path = str(Path(file_path))
        super().__init__('PosShow')
        modelRenderConfig = configHandler.get_config("ModelRenderSetting")
        with Log().redirectOutput(self.TAG):  # 模型加载时，库内会有输出，这里重定向到日志
            modelItem = GLModelItem(self.file_path, lights=[],
                                    selectable=True,
                                    glOptions="translucent",
                                    drawLine=modelRenderConfig["ModelDrawLine"],
                                    lineWidth=modelRenderConfig["ModelLineWith"],
                                    lineColor=modelRenderConfig["ModelLineColor"])
            # 如果加载失败，不继续
            if hasattr(modelItem, "load_failed") and modelItem.load_failed:
                self.load_failed = True
                self._showButton.setChecked(False)
                # 将modelItem设置为随机颜色小球
                modelItem = 'default'
            self.setPaintItem(modelItem)
            self.setPos(pos)
            self.setRot(rot)

    def _init_showButton(self, type_: Literal['PosShow', 'PosRotShow']):
        super()._init_showButton(type_)
        self._model_bt_scroll_widget.layout().addWidget(self._showButton)

    def changePath(self, path):
        """
        修改模型路径，然后通知gl_widget更新
        :param path: 新路径
        """
        self.file_path = str(Path(path))
        modelRenderConfig = configHandler.get_config("ModelRenderSetting")
        with Log().redirectOutput(self.TAG):
            modelItem = GLModelItem(self.file_path, lights=[],
                                    selectable=True,
                                    glOptions="translucent",
                                    drawLine=modelRenderConfig["ModelDrawLine"],
                                    lineWidth=modelRenderConfig["ModelLineWith"],
                                    lineColor=modelRenderConfig["ModelLineColor"])
            if hasattr(modelItem, "load_failed") and modelItem.load_failed:
                self.load_failed = True
                self._showButton.setChecked(False)
                modelItem = 'default'
            self.setPaintItem(modelItem)
            self.setPos(self.Pos)
            self.setRot(self.Rot)
            self.hullProject.gl_widget.paintGL_outside()
        # 更新右侧属性栏
        self.update_path_s.emit(self.file_path)

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
            Log().warning(self.TAG, f"{self.name} 不在 Model.idMap 中")

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
