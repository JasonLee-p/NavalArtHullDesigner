"""
定义了船体的绘制类
"""
import ctypes

# from main_logger import Log
from pyqtOpenGL import Matrix4x4, GLGraphicsItem, GLMeshItem, Mesh, Quaternion


class HullSectionItem(GLMeshItem):
    def __init__(self, section_data):
        super().__init__()
        self.section_data = section_data


class HullSectionGroupItem(GLGraphicsItem):
    all_section_group = {
        # "project": set(section_group_item, section_group_item, ...)
    }
    edit_manager = {
        # "project": whether there is a section group being edited
    }

    def __init__(self, prj, group_data):
        """
        设置船体截面组整体的变换，并
        :param prj: 工程对象
        :param group_data: 截面组数据
        """
        super().__init__(selectable=True)
        self.prj = prj
        self.group_data = group_data
        self.proj_view_matrix()
        self.__editing = False
        if prj not in HullSectionGroupItem.all_section_group:
            HullSectionGroupItem.all_section_group[prj] = set()
        HullSectionGroupItem.all_section_group[prj].add(self)

    def add_section_item(self, section_item):
        self.addChildItem(section_item)

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

    def setEditing(self, editing: bool):
        if editing == self.__editing:
            return
        if editing:  # 如果开启编辑，则不可被整体选择，这样就可以单独选择每个截面
            if HullSectionGroupItem.edit_manager[self.prj]:
                return
            HullSectionGroupItem.edit_manager[self.prj] = True
            self.setSelectable(True, True)  # 开启单独选择
            for hsg in HullSectionGroupItem.all_section_group[self.prj]:
                hsg.setSelectable(False, False)
        else:
            self.setSelectable(False, True)  # 关闭单独选择
            for hsg in HullSectionGroupItem.all_section_group[self.prj]:
                hsg.setSelectable(True, False)
        self.__editing = editing

    def isEditing(self):
        return self.__editing

