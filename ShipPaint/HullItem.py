"""
定义了船体的绘制类
"""
import ctypes
from typing import Union

# from main_logger import Log
from pyqtOpenGL import Matrix4x4, GLGraphicsItem, GLMeshItem, Mesh, Quaternion


class HullSectionItem(GLMeshItem):
    def __init__(self, z, nodes):
        """
        """
        super().__init__()
        self.sectionGroup = None  # 船体截面组，将会在HullSectionGroupItem中设置
        self.handler = None  # 船体截面的处理器
        self._z = z
        self._nodes = nodes

    def setPoint(self, pointSection, x, y):
        """
        设置船体截面的点
        :param pointSection: 船体截面的点
        :param x: x坐标
        :param y: y坐标
        """
        pointSection.setPoint(x, y)
        self.update_mesh(pointSection.y_index, x, y)

    def update_mesh(self, index, x, y):
        """
        更新网格
        """
        ...  # TODO: Implement this function
        self.update()


class HullSectionGroupItem(GLGraphicsItem):
    def __init__(self, prj, hullSections):
        """
        设置船体截面组整体的变换，并
        :param prj: 工程对象
        :param hullSections: 截面对象列表
        """
        super().__init__(selectable=True)
        self.prj = prj
        # 对截面进行从小到大排序，z越大，越靠前
        hullSections.sort(key=lambda x: x.z)
        self.hullSections = hullSections
        self._front_item: HullSectionGroupItem = self.hullSections[-1]
        self._back_item: HullSectionGroupItem = self.hullSections[0]

    def addLight(self, light):
        for item in self.childItems():
            item.addLight(light)

    def paint(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint()

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint_pickMode()

    def paint_selected(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint_selected()

    def initializeGL(self):
        for item in self.childItems():
            item.initializeGL()

    def setEulerAngles(self, yaw, pitch, roll, local=True):
        q = Quaternion.fromEulerAngles(yaw, pitch, roll)
        self.__transform.rotate(q, local)


class ArmorSectionItem(GLMeshItem):
    def __init__(self, handler, z, nodes):
        """
        """
        super().__init__()
        self.sectionGroup = None  # 船体截面组，将会在ArmorSectionGroupItem中设置
        self.handler = handler
        self._z = z
        self._nodes = nodes

    def setPoint(self, pointSection, x, y):
        """
        设置船体截面的点
        :param pointSection: 船体截面的点
        :param x: x坐标
        :param y: y坐标
        """
        pointSection.setPoint(x, y)
        self.update_mesh(pointSection.y_index, x, y)

    def update_mesh(self, index, x, y):
        """
        更新网格
        """


class ArmorSectionGroupItem(GLGraphicsItem):
    def __init__(self, prj, armorSections):
        """
        设置船体截面组整体的变换，并
        :param prj: 工程对象
        :param armorSections: 截面对象列表
        """
        super().__init__(selectable=True)
        self.prj = prj
        # 对截面进行从小到大排序，z越大，越靠前
        armorSections.sort(key=lambda x: x.z)
        self.armorSections = armorSections
        self._front_item: ArmorSectionGroupItem = self.armorSections[-1]
        self._back_item: ArmorSectionGroupItem = self.armorSections[0]

    def addLight(self, light):
        for item in self.childItems():
            item.addLight(light)

    def paint(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint()

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint_pickMode()

    def paint_selected(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint_selected()

    def initializeGL(self):
        for item in self.childItems():
            item.initializeGL()

    def setEulerAngles(self, yaw, pitch, roll, local=True):
        q = Quaternion.fromEulerAngles(yaw, pitch, roll)
        self.__transform.rotate(q, local)
