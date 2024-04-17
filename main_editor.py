# -*- coding: utf-8 -*-
"""
编辑器运行逻辑
"""
import webbrowser

import psutil
from GUI import MainEditorGUI, EditTabWidget
from PyQt5.QtWidgets import QFileDialog
from ShipRead.na_project import *
from funcs_utils import not_implemented
from main_logger import Log, StatusBarHandler
from operation import OperationStack
from path_vars import DESKTOP_PATH


class MemoryThread(QThread):
    memory_updated_s = pyqtSignal(int)  # noqa

    def __init__(self):
        super().__init__(None)
        self.process = psutil.Process()

    def run(self):
        while True:
            memory_bytes = self.process.memory_info().rss
            memory_mb = memory_bytes // (1024 * 1024)
            self.memory_updated_s.emit(memory_mb)
            self.sleep(2)


class MainEditor(MainEditorGUI):

    def undo(self):
        self.operationStack.undo()

    def redo(self):
        self.operationStack.redo()

    def open_prj(self, path):
        # 打开path路径的工程文件
        prj = ShipProject(self, self.gl_widget, path)
        loader = NaPrjReader(path, prj)
        if not loader.successed:
            Log().info(f"打开工程失败：{prj.project_name}")
            return False
        self.currentPrj_button.setText(prj.project_name)
        configHandler.add_prj(prj.project_name, path)
        StatusBarHandler().info(f"打开工程：{prj.project_name}")
        self.setCurrentPrj(prj)

    def select_prj_toOpen(self):
        prjs = self.configHandler.get_config("Projects")
        # 从配置文件读取曾经打开过的所有文件
        if prjs != {}:
            # 打开预览窗口，选择一个工程文件
            ...  # TODO
        else:  # 如果没有历史记录，打开文件夹选择窗口
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            file_dialog.setNameFilter("NA Hull Editor工程文件 (*.naprj)")
            file_dialog.setViewMode(QFileDialog.Detail)
            file_dialog.setDirectory(DESKTOP_PATH)

    def load_last_project(self):
        prjs = self.configHandler.get_config("Projects")
        if not prjs:
            return
        lastPrj_path = prjs[list(prjs.keys())[-1]]
        self.open_prj(lastPrj_path)

    @not_implemented
    def new_prj(self):
        # 弹出临时窗口，让用于选择创建新工程的方式
        # 若确定了创建新工程，则询问是否保存当前工程
        pass

    def setting(self):
        # 打开设置窗口
        pass

    @not_implemented
    def help(self):
        pass

    def about(self):
        webbrowser.open("http://naval_plugins.e.cn.vc/")

    def save_prj(self):
        self._current_prj.save() if self._current_prj else None
        self.show_statu_(f"保存工程：{self._current_prj.project_name}", "success")

    @not_implemented
    def save_as_prj(self):
        # 打开文件夹选择窗口，选择保存位置
        pass

    @not_implemented
    def export_to_na(self):
        # 将当前工程导出为 NavalArt 工程文件
        # 先打开文件夹选择窗口，选择保存位置，默认为NavalArt工程文件的保存位置
        pass

    @not_implemented
    def set_theme(self):
        pass

    @not_implemented
    def set_camera(self):
        pass

    @not_implemented
    def tutorial(self):
        pass

    def __init__(self, gl_widget, logger):
        """
        编辑器中所有事件，操作的主控制器
        :param gl_widget:
        :param logger:
        """

        # 管理所有操作
        self.operationStack = OperationStack(self)
        self.operationStack.init_stack()
        super().__init__(gl_widget, logger)
        # 创建内存监控线程
        self.memoryThread = MemoryThread()
        self.memoryThread.start()
        self._bind_signal()
        # 快捷方式绑定
        self._bind_shortcut({
            "Ctrl+S": self.save_prj,
            "Ctrl+Shift+S": self.save_as_prj,
            "Ctrl+Z": self.undo,
            "Ctrl+Shift+Z": self.redo,
        })
        # 子成员对自己的引用
        EditTabWidget.main_editor = self
        EditTabWidget.gl_widget = gl_widget
        EditTabWidget.operationStack = self.operationStack

    def _bind_signal(self):
        # 内存监控线程
        self.memoryThread.memory_updated_s.connect(self.memory_widget.set_values)
        # 选择船体元素后，显示编辑器
        self.gl_widget.clear_selected_items.connect(self.edit_tab.clear_editing_widget)
        self.gl_widget.after_selection.connect(
            lambda: self.show_editor(self.gl_widget.selected_items_handler()))

    def _bind_shortcut(self, shortcuts: dict):
        # 绑定快捷键
        for key, func in shortcuts.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(func)
            self.addAction(action)

    def setCurrentPrj(self, prj):
        self._current_prj = prj

    def getCurrentPrj(self):
        return self._current_prj

    def add_hull_section_group_s(self, group_id):
        hsGroup = HullSectionGroup.get_by_id(group_id)
        self.structure_tab.add_hullSectionGroup(hsGroup)

    def add_armor_section_group_s(self, group_id):
        asGroup = ArmorSectionGroup.get_by_id(group_id)
        self.structure_tab.add_armorSectionGroup(asGroup)

    def add_bridge_s(self, bridge_id):
        _bridge = Bridge.get_by_id(bridge_id)
        self.structure_tab.add_bridge(_bridge)

    def add_ladder_s(self, ladder_id):
        _ladder = Ladder.get_by_id(ladder_id)
        self.structure_tab.add_ladder(_ladder)

    def add_model_s(self, model_id):
        _model = Model.get_by_id(model_id)
        self.structure_tab.add_model(_model)

    def del_hull_section_group_s(self, group_id):
        hsGroup = HullSectionGroup.get_by_id(group_id)
        self.structure_tab.del_hullSectionGroup(hsGroup)

    def del_armor_section_group_s(self, group_id):
        asGroup = ArmorSectionGroup.get_by_id(group_id)
        self.structure_tab.del_armorSectionGroup(asGroup)

    def del_bridge_s(self, bridge_id):
        _bridge = Bridge.get_by_id(bridge_id)
        self.structure_tab.del_bridge(_bridge)

    def del_ladder_s(self, ladder_id):
        _ladder = Ladder.get_by_id(ladder_id)
        self.structure_tab.del_ladder(_ladder)

    def del_model_s(self, model_id):
        _model = Model.get_by_id(model_id)
        self.structure_tab.del_model(_model)

    def show_editor(self, item):
        if isinstance(item, list):
            if len(item) == 0:
                self.edit_tab.clear_editing_widget()
                # self.setRightTabWidth(40)
                return
            if len(item) == 1:
                item = item[0]
            else:
                # TODO: 多选的情况
                return
        # 单选的情况
        self.setRightTabWidth(336)
        self.main_widget.right_tab_frame.change_tab(self.edit_tab)
        self.edit_tab.set_editing_item_name(item.name)
        if isinstance(item, HullSectionGroup):
            self.edit_tab.set_editing_widget("船体截面组")
            self.edit_tab.edit_hullSectionGroup(item)
        elif isinstance(item, ArmorSectionGroup):
            self.edit_tab.set_editing_widget("装甲截面组")
            self.edit_tab.edit_armorSectionGroup(item)
        elif isinstance(item, Bridge):
            self.edit_tab.set_editing_widget("舰桥")
            self.edit_tab.edit_bridge(item)
        elif isinstance(item, Ladder):
            self.edit_tab.set_editing_widget("梯子")
            self.edit_tab.edit_ladder(item)
        elif isinstance(item, Model):
            self.edit_tab.set_editing_widget("外部模型")
            self.edit_tab.edit_model(item)

    def __del__(self):
        print("MainEditor对象已销毁")
        super().__del__()
