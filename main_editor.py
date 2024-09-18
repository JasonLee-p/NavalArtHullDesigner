# -*- coding: utf-8 -*-
"""
编辑器运行逻辑
"""
import webbrowser

import psutil


from GUI import MainEditorGUI, EditTabWidget
from GUI.sub_component_edt_widgets import SubElementShow
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QAction

from ShipRead.designer_project import *
from utils.funcs_utils import not_implemented, snake_to_camel
from main_logger import Log, StatusBarHandler
from operation import OperationStack
from operation.basic_op import Operation
from path_lib import DESKTOP_PATH


def update_structure(action):
    """
    装饰器，用于简化结构视图中组件的添加和删除操作。
    :param action: 动作类型（'add' 或 'del'）
    :return: 装饰器函数
    """

    def decorator(func):
        """_"""
        # 蛇形命名
        snake_component_type = func.__name__[4:-2]  # 去除开头add_/del_四个字符以及_s结尾

        def wrapper(self, component_id):
            """
            链接工程文件组件的信号，到ElementStructureTab的对应函数
            """
            # 将蛇形命名改为大驼峰，作为类名
            camel_component_type = snake_to_camel(snake_component_type)
            # 类名转为类对象
            component_class = globals()[camel_component_type]
            # 获取组件对象
            component = component_class.get_by_id(component_id)
            # 调用structure_tab（GUI.main_widgets.ElementStructureTab）对应的函数
            getattr(self.structure_tab, f'{action}_{snake_component_type}')(component)

        if not func.__doc__:
            func.__doc__ = f"""
            通过对象ID，将{snake_component_type} {'添加到' if action == 'add' else '从'} structure_tab（结构视图）中{'添加' if action == 'add' else '删除'}。
            该函数将会链接到ShipProject对象的同名pyqtSignal，
            以在通过ShipProject执行{'添加' if action == 'add' else '删除'}该组件的操作时{'往' if action == 'add' else '从'}structure_tab{'添加' if action == 'add' else '删除'}该组件的显示控件。
            :param component_id: {snake_component_type} ID
            :return: None
            """
        return wrapper

    return decorator


class MemoryThread(QtCore.QThread):
    """
    内存监控线程，随时发出信号，通知主窗口相应的控件更新
    """
    TAG = "MemoryThread"
    memory_updated_s = pyqtSignal(int)  # noqa
    cpu_updated_s = pyqtSignal(float)  # noqa

    def __init__(self):
        super().__init__(None)
        self.process = psutil.Process()

    def run(self):
        while True:
            memory_bytes = self.process.memory_info().rss
            cpu_percent = self.process.cpu_percent()
            memory_mb = memory_bytes // (1024 * 1024)
            self.memory_updated_s.emit(memory_mb)
            self.cpu_updated_s.emit(cpu_percent)
            self.sleep(2)

    def __del__(self):
        Log().info(self.TAG, "MemoryThread已销毁")


class MainEditor(MainEditorGUI):
    """
    主编辑器，用户交互的主要界面，提供几乎所有的功能，主要为设计器图纸编辑器。
    """
    TAG = "MainEditor"

    def excute(self, operation: Operation):
        """
        向operationStack添加操作并执行
        :param operation: 操作对象
        :return:
        """
        self.operationStack.execute(operation)

    def undo(self):
        """
        使operationStack撤回到上一个操作
        :return:
        """
        self.operationStack.undo()

    def redo(self):
        """
        使operationStack重做到下一个操作
        :return:
        """
        self.operationStack.redo()

    def clearOperationStack(self):
        """
        清空操作栈
        """
        self.operationStack.clear()
        Log().info(self.TAG, "操作栈已清空")

    def open_prj(self, path):
        """
        打开path路径的工程文件
        """
        # 将path进行标准化
        path = os.path.abspath(path)
        prj = DesignerProject(self.gl_widget, path)
        # 加载工程文件
        loader = DesignerPrjReader(self, path, prj)
        if not loader.successed:
            Log().warning(self.TAG, f"打开工程失败：{prj.project_name}")
            return False
        # 只有在成功加载工程文件后才能清空界面
        self.structure_tab.clear()
        self.edit_tab.clear_editing_widget()
        self.repaint()
        # 初始化到主编辑器界面
        prj.bind_signal_to_editor(self)
        prj.init_in_main_editor()
        # 设置顶部按钮文本
        self.currentPrj_button.setText(prj.project_name)
        configHandler.add_prj(prj.project_name, path)
        Log().info(self.TAG, f"打开工程：{prj.project_name}")
        StatusBarHandler().info(f"打开工程：{prj.project_name}")
        self.setCurrentPrj(prj)
        return True

    def select_prj_toOpen(self):
        """
        打开工程文件选择窗口
        """
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
        """
        打开
        """
        prjs = self.configHandler.get_config("Projects")
        if not prjs:
            return
        lastPrj_path = prjs[list(prjs.keys())[-1]]
        self.open_prj(lastPrj_path)

    @not_implemented
    def new_prj(self):
        """
        新建
        """
        # 弹出临时窗口，让用于选择创建新工程的方式
        # 若确定了创建新工程，则询问是否保存当前工程
        pass

    def setting(self):
        """
        设置
        """
        # 打开设置窗口
        pass

    @not_implemented
    def help(self):
        """
        帮助
        """
        pass

    def about(self):
        """
        关于
        """
        Log().info(self.TAG, "打开关于页面")
        webbrowser.open("http://naval_plugins.e.cn.vc/")

    def save_prj(self):
        """
        保存当前工程
        """
        self._current_prj.save() if self._current_prj else None
        self.show_statu_(f"保存工程：{self._current_prj.project_name}", "success")

    @not_implemented
    def save_as_prj(self):
        """
        另存为当前工程
        """
        # 打开文件夹选择窗口，选择保存位置
        pass

    @not_implemented
    def export_to_na(self):
        """
        导出为NavalArt工程文件
        """
        # 将当前工程导出为 NavalArt 工程文件
        # 先打开文件夹选择窗口，选择保存位置，默认为NavalArt工程文件的保存位置
        pass

    @not_implemented
    def set_theme(self):
        """
        设置主题
        """
        pass

    @not_implemented
    def set_camera(self):
        """
        设置相机
        """
        pass

    @not_implemented
    def tutorial(self):
        """
        打开教程
        """
        pass

    def paste(self):
        """
        粘贴剪贴板内容
        """
        sections = set()
        for item in self.gl_widget.clipboard:
            if hasattr(item, "handler"):
                sections.add(item.handler)
        self._current_prj.add_sections(list(sections))

    def __init__(self, gl_widget, logger):
        """
        编辑器中所有事件，操作的主控制器
        :param gl_widget:
        :param logger:
        """

        # 操作管理栈
        self.operationStack = OperationStack(self, max_length=configHandler.get_config("OperationStackMaxLength"))
        self.operationStack.init_stack()
        super().__init__(gl_widget, logger)
        # 创建内存监控线程
        self.memoryThread = MemoryThread()
        self.memoryThread.start()
        # 绑定信号和函数
        self._glWidget_menu_actions = {
            '全选': self.gl_widget.selectAll,
            '复制': self.gl_widget.copy,
            '粘贴': self.paste,
            '删除': self.gl_widget.delete_selected,
        }
        self._bind_glWidget_menu()
        self._bind_signal()
        # 绑定快捷方式
        self._bind_shortcut({
            'Ctrl+S': self.save_prj,
            'Ctrl+Shift+S': self.save_as_prj,
            'Ctrl+Z': self.undo,
            'Ctrl+Shift+Z': self.redo,
            'Ctrl+C': self.gl_widget.copy,
            'Ctrl+X': self.gl_widget.cut,
            'Ctrl+V': self.paste,
            'Ctrl+A': self.gl_widget.selectAll,
        })
        # 子成员对自己的引用
        EditTabWidget.main_editor = self
        EditTabWidget.gl_widget = gl_widget
        EditTabWidget.operationStack = self.operationStack
        SubElementShow.operationStack = self.operationStack
        # 绑定其他类对mainEditor的引用
        PrjComponent.init_ref(self)
        SubPrjComponent.init_ref(self)

    def _bind_glWidget_menu(self):
        """
        绑定gl_widget的右键菜单
        """
        for action_name, func in self._glWidget_menu_actions.items():
            action = QAction(self)
            action.setText(action_name)
            action.triggered.connect(func)
            self.gl_widget.menu.addAction(action)

    def _bind_signal(self):
        """
        绑定信号和函数
        """
        # 内存监控线程
        self.memoryThread.memory_updated_s.connect(self.memory_widget.set_values)
        # self.memoryThread.cpu_updated_s.connect(self.update_cpu)
        # 选择船体元素后，显示编辑器
        self.gl_widget.clear_selected_items.connect(self.edit_tab.clear_editing_widget)
        self.gl_widget.after_selection.connect(
            lambda: self.show_editor(self.gl_widget.selected_items_handler()))

        # 绑定gl_widget的键盘事件
        self.gl_widget.keyPressEvent = self.keyPressEvent
        self.gl_widget.keyReleaseEvent = self.keyReleaseEvent

    def keyPressEvent(self, ev, qKeyEvent=None) -> None:
        """
        键盘事件，显示快捷键指南
        """
        ctrl_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
        shift_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier)
        alt_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier)
        if ctrl_down:
            tip_text = "Ctrl 快捷键指南：微调相机视角\tS 保存工程\tShift+S 另存为工程\tZ 撤销操作\tShift+Z 重做"
            self.show_statu_(tip_text, "highlight")
        elif shift_down:
            tip_text = "Shift 快捷键指南：限制视角移动"
            self.show_statu_(tip_text, "highlight")
        elif alt_down:
            tip_text = "Alt 快捷键指南："
            self.show_statu_(tip_text, "highlight")

    def keyReleaseEvent(self, ev, qKeyEvent=None) -> None:
        if "快捷键指南" in self.status_label.text():
            self.show_statu_("", "success")

    def _bind_shortcut(self, shortcuts: dict):
        """
        绑定快捷键
        :param shortcuts: 例如：{"Ctrl+S": self.save_prj}
        :return:
        """
        for key, func in shortcuts.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(func)  # noqa
            self.addAction(action)

    def setCurrentPrj(self, prj):
        """
        清空元素视图和结构视图的所有内容，然后设置当前工程为prj
        :param prj:
        :return:
        """
        if self._current_prj:
            self._current_prj.unbind_signal_to_handler(self)
            self._current_prj.deleteLater()
        self._current_prj = prj

    def getCurrentPrj(self):
        """
        获取当前正在编辑的工程
        """
        return self._current_prj

    """
    下面是添加或删除组件的函数，这些函数将会被装饰器装饰，以便在添加或删除组件时，自动更新结构视图
    """

    @update_structure('add')
    def add_hull_section_group_s(self, group_id):
        """
        添加船体截面组
        """
        pass

    @update_structure('add')
    def add_armor_section_group_s(self, group_id):
        """
        添加装甲截面组
        """
        pass

    @update_structure('add')
    def add_bridge_s(self, bridge_id):
        """
        添加舰桥
        """
        pass

    @update_structure('add')
    def add_ladder_s(self, ladder_id):
        """
        添加梯子
        """
        pass

    @update_structure('add')
    def add_model_s(self, model_id):
        """
        添加外部模型
        """
        pass

    @update_structure('add')
    def add_ref_image_s(self, ref_image_id):
        """
        添加参考图片
        """
        pass

    @update_structure('del')
    def del_hull_section_group_s(self, group_id):
        """
        删除船体截面组
        """
        pass

    @update_structure('del')
    def del_armor_section_group_s(self, group_id):
        """
        删除装甲截面组
        """
        pass

    @update_structure('del')
    def del_bridge_s(self, bridge_id):
        """
        删除舰桥
        """
        pass

    @update_structure('del')
    def del_ladder_s(self, ladder_id):
        """
        删除梯子
        """
        pass

    @update_structure('del')
    def del_model_s(self, model_id):
        """
        删除外部模型
        """
        pass

    @update_structure('del')
    def del_ref_image_s(self, ref_image_id):
        """
        删除参考图片
        """
        pass

    def show_editor(self, item):
        """
        （选择某item后）显示编辑器，根据item的类型显示不同的编辑器
        """
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
        elif isinstance(item, RefImage):
            self.edit_tab.set_editing_widget("参考图片")
            self.edit_tab.edit_refImage(item)

    def __del__(self):
        Log().info(self.TAG, "MainEditor对象已销毁")
        super().__del__()
