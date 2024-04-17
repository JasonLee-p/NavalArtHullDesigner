# -*- coding: utf-8 -*-
"""
主要窗口
"""
import gc
import os

import numpy as np
import PIL.Image as Image
from GUI.element_structure_widgets import *
from ShipRead.na_project import ShipProject
from funcs_utils import not_implemented
from main_logger import StatusBarHandler
from path_vars import CURRENT_PATH
from pyqtOpenGL import *
from pyqtOpenGL.camera import Camera
from pyqtOpenGL.items.MeshData import EditItemMaterial

from .element_edit_widgets import *


class UserInfoTab(MutiDirectionTab):
    def __init__(self, parent):
        super().__init__(parent, CONST.DOWN, "用户", USER_IMAGE)
        self.set_layout(QVBoxLayout())
        self.__init_main_widget()

    def init_top_widget(self):
        ...

    def __init_main_widget(self):
        self.layout().setContentsMargins(5, 5, 5, 0)
        self.layout().setSpacing(5)


class PrjInfoTab(MutiDirectionTab):
    def __init__(self, parent):
        super().__init__(parent, CONST.RIGHT, "船体信息", ELEMENTS_IMAGE)
        self.set_layout(QVBoxLayout())
        # 控件
        self.shipInfo_widget = QWidget()
        self.shipInfo_layout = QGridLayout()
        self.label_designName = ColoredTextLabel(None, "未知", YAHEI[9], FG_COLOR1)
        self.label_designer = ColoredTextLabel(None, "未知", YAHEI[9], FG_COLOR1)
        self.label_length = ColoredTextLabel(None, "0", YAHEI[9])
        self.label_width = ColoredTextLabel(None, "0", YAHEI[9])
        self.label_depth = ColoredTextLabel(None, "0", YAHEI[9])
        # 初始化
        self.__init_main_widget()

    def init_top_widget(self):
        ...

    def __init_main_widget(self):
        self.layout().setContentsMargins(5, 5, 5, 0)
        self.layout().setSpacing(5)
        # 控件
        self.shipInfo_widget.setLayout(self.shipInfo_layout)
        self.shipInfo_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.shipInfo_layout.setContentsMargins(18, 2, 18, 2)
        self.shipInfo_layout.setHorizontalSpacing(8)
        self.shipInfo_layout.setVerticalSpacing(4)
        # 左侧
        self.shipInfo_layout.addWidget(ColoredTextLabel(None, "设计名称:", YAHEI[9]), 0, 0)
        self.shipInfo_layout.addWidget(ColoredTextLabel(None, "设计玩家:", YAHEI[9]), 1, 0)
        self.shipInfo_layout.addWidget(ColoredTextLabel(None, "船体型长:", YAHEI[9]), 2, 0)
        self.shipInfo_layout.addWidget(ColoredTextLabel(None, "船体型宽:", YAHEI[9]), 3, 0)
        self.shipInfo_layout.addWidget(ColoredTextLabel(None, "船体型深:", YAHEI[9]), 4, 0)
        # 右侧
        self.shipInfo_layout.addWidget(self.label_designName, 0, 1)
        self.shipInfo_layout.addWidget(self.label_designer, 1, 1)
        self.shipInfo_layout.addWidget(self.label_length, 2, 1)
        self.shipInfo_layout.addWidget(self.label_width, 3, 1)
        self.shipInfo_layout.addWidget(self.label_depth, 4, 1)
        # 布局
        self.main_layout.addWidget(TextLabel(self, "基础信息", YAHEI[9], FG_COLOR0, Qt.AlignLeft | Qt.AlignTop))
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(HorSpliter(self))
        self.main_layout.addWidget(self.shipInfo_widget)


class ElementStructureTab(MutiDirectionTab):
    def __init__(self, parent, main_editor):
        self.main_editor = main_editor
        super().__init__(parent, CONST.LEFT, "结构层级", STRUCTURE_IMAGE)
        self.set_layout(QVBoxLayout())
        # 控件
        self.tab_widget = TabWidget(None, QTabWidget.West)
        self._hullSectionGroup_tab = QWidget()
        self._armorSectionGroup_tab = QWidget()
        self._bridge_tab = QWidget()
        self._ladder_tab = QWidget()  # 梯子
        self._model_tab = QWidget()  # 外部模型

        self.__init_main_widget()

    def init_top_widget(self):
        ...

    def __init_main_widget(self):
        self.layout().setContentsMargins(5, 5, 5, 0)
        self.layout().setSpacing(5)
        self.tab_widget.addTab(self._hullSectionGroup_tab, "船体截面组")
        self.tab_widget.addTab(self._armorSectionGroup_tab, "装甲截面组")
        self.tab_widget.addTab(self._bridge_tab, "舰桥")
        self.tab_widget.addTab(self._ladder_tab, "梯子")
        self.tab_widget.addTab(self._model_tab, "外部模型")
        self.hullSectionGroup_tab = HullSectionGroupESW(self.main_editor, self._hullSectionGroup_tab)
        self.armorSectionGroup_tab = ArmorSectionGroupESW(self.main_editor, self._armorSectionGroup_tab)
        self.bridge_tab = BridgeESW(self.main_editor, self._bridge_tab)
        self.ladder_tab = LadderESW(self.main_editor, self._ladder_tab)
        self.model_tab = ModelESW(self.main_editor, self._model_tab)
        # 总布局
        self.main_layout.addWidget(self.tab_widget)

    def setCurrentTab(self, tab: QWidget):
        self.tab_widget.setCurrentWidget(tab)

    def add_hullSectionGroup(self, hull_section_group):
        self.hullSectionGroup_tab.add_item(hull_section_group)

    def add_armorSectionGroup(self, armor_section_group):
        self.armorSectionGroup_tab.add_item(armor_section_group)

    def add_bridge(self, bridge):
        self.bridge_tab.add_item(bridge)

    def add_ladder(self, ladder):
        self.ladder_tab.add_item(ladder)

    def add_model(self, model):
        self.model_tab.add_item(model)

    def del_hullSectionGroup(self, hull_section_group):
        self.hullSectionGroup_tab.del_item(hull_section_group)

    def del_armorSectionGroup(self, armor_section_group):
        self.armorSectionGroup_tab.del_item(armor_section_group)

    def del_bridge(self, bridge):
        self.bridge_tab.del_item(bridge)

    def del_ladder(self, ladder):
        self.ladder_tab.del_item(ladder)

    def del_model(self, model):
        self.model_tab.del_item(model)


class ElementEditTab(MutiDirectionTab):
    elementType_updated = pyqtSignal(str)

    def __init__(self, parent):
        """
        元素编辑窗口
        :param parent:
        """
        super().__init__(parent, CONST.RIGHT, "元素编辑", EDIT_IMAGE)
        self.element_mutex = QMutex()  # 互斥锁，用于保证只有一个元素被编辑
        self.element_locker = QMutexLocker(self.element_mutex)
        self.set_layout(QVBoxLayout())
        self.elementType_label = TextLabel(self, "无选中物体", YAHEI[9], FG_COLOR1, Qt.AlignLeft)
        self.elementName_label = TextLabel(self, "", YAHEI[9], FG_COLOR0, Qt.AlignCenter)
        self.edit_hullSectionGroup_widget = EditHullSectionGroupWidget()
        self.edit_armorSectionGroup_widget = EditArmorSectionGroupWidget()
        self.edit_bridge_widget = EditBridgeWidget()
        self.edit_ladder_widget = EditLadderWidget()
        self.edit_model_widget = EditModelWidget()
        self.edit_widgets = {
            self.edit_hullSectionGroup_widget: "船体截面组",
            self.edit_armorSectionGroup_widget: "装甲截面组",
            self.edit_bridge_widget: "舰桥",
            self.edit_ladder_widget: "梯子",
            self.edit_model_widget: "外部模型"
        }
        self.current_edit_widget: Union[None, QWidget] = None

        self.__init_main_widget()

    def init_top_widget(self):
        ...

    def __init_main_widget(self):
        self.layout().setContentsMargins(5, 5, 5, 0)
        self.layout().setSpacing(5)
        # 布局
        top_widget = QWidget()
        top_widget.setLayout(QHBoxLayout())
        top_widget.layout().addWidget(self.elementType_label)
        top_widget.layout().addWidget(self.elementName_label, stretch=1)
        top_widget.layout().setSpacing(0)
        top_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(top_widget)
        self.main_layout.addWidget(HorSpliter(self))
        for ew in self.edit_widgets:
            self.main_layout.addWidget(ew)
            ew.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            ew.hide()
        self.main_layout.setAlignment(Qt.AlignTop)

    def set_editing_item_name(self, _name):
        self.elementName_label.setText(_name)

    def set_editing_widget(
            self,
            element_type: Literal["船体截面组", "装甲截面组", "舰桥", "栏杆", "栏板", "梯子"] = None,
            edit_widget: Union[None, EditTabWidget] = None
    ):
        """
        设置当前编辑的元素，两个参数最好只能填写一个
        :param element_type: "船体截面组", "装甲截面组", "舰桥", "栏杆", "栏板", "梯子"
        :param edit_widget: self.edit_hullSectionGroup_widget, self.edit_armorSectionGroup_widget,
                            self.edit_bridge_widget, self.edit_railing_widget, self.edit_handrail_widget,
                            self.edit_ladder_widget
        :return:
        """
        with self.element_locker:
            if element_type and not edit_widget:  # 使用element_type
                self.elementType_label.setText(element_type)
                for ew, et in self.edit_widgets.items():
                    if et == element_type:
                        ew.show()
                        self.current_edit_widget = ew
                    else:
                        ew.hide()
                self.elementType_updated.emit(element_type)
            elif edit_widget and not element_type:  # 使用edit_widget
                self.elementType_label.setText(self.edit_widgets[edit_widget])
                for ew in self.edit_widgets:
                    if ew == edit_widget:
                        ew.show()
                        self.current_edit_widget = ew
                    else:
                        ew.hide()
                self.elementType_updated.emit(self.edit_widgets[edit_widget])
            elif not element_type and not edit_widget:  # 无选中物体
                self.clear_editing_widget()
            elif element_type and edit_widget:  # 两个参数都有
                if self.edit_widgets[edit_widget] != element_type:
                    raise ValueError("element_type和edit_widget不匹配")
                self.elementType_label.setText(element_type)
                for ew in self.edit_widgets:
                    if ew == edit_widget:
                        ew.show()
                        self.current_edit_widget = ew
                    else:
                        ew.hide()
                self.elementType_updated.emit(element_type)

    def clear_editing_widget(self):
        self.elementType_label.setText("无选中物体")
        self.elementName_label.setText("")
        for ew in self.edit_widgets:
            ew.hide()
        self.current_edit_widget = None
        self.elementType_updated.emit("无选中物体")

    def edit_hullSectionGroup(self, hull_section_group):
        self.edit_hullSectionGroup_widget.updateSectionHandler(hull_section_group)

    def edit_armorSectionGroup(self, armor_section_group):
        self.edit_armorSectionGroup_widget.updateSectionHandler(armor_section_group)

    def edit_ladder(self, ladder):
        self.edit_ladder_widget.updateSectionHandler(ladder)

    def edit_bridge(self, bridge):
        self.edit_bridge_widget.updateSectionHandler(bridge)

    def edit_model(self, model):
        self.edit_model_widget.updateSectionHandler(model)


class SettingTab(MutiDirectionTab):
    def __init__(self, parent, configHandler_, camera):
        self.__configHandler = configHandler_
        self.__camera_sensitivity = configHandler_.get_config("Sensitivity")
        self.__camera: Camera = camera
        super().__init__(parent, CONST.RIGHT, "设置", SETTINGS_IMAGE)
        self.set_layout(QVBoxLayout())
        # 初始化标签页，分别为：主题、相机灵敏度 =================================================================
        self.tab_widget = TabWidget(None)
        # 相机灵敏度
        self.camera_tab = QWidget()
        self.camera_layout = QGridLayout()
        self.slider_trans = Slider(self.camera_tab, Qt.Vertical, [0, 100], 1, self.__camera_sensitivity["平移"])
        self.slider_zoom = Slider(self.camera_tab, Qt.Vertical, [0, 100], 1, self.__camera_sensitivity["缩放"])
        self.slider_rot = Slider(self.camera_tab, Qt.Vertical, [0, 100], 1, self.__camera_sensitivity["旋转"])
        # 主题
        self.theme_tab = QWidget()
        self.theme_layout = QVBoxLayout()
        # 样式和布局初始化
        self.__init_tab_widgets()
        # ===================================================================

    def init_top_widget(self):
        ...

    def __init_tab_widgets(self):
        self.layout().setContentsMargins(5, 5, 5, 0)
        self.layout().setSpacing(5)
        self.tab_widget.addTab(self.camera_tab, "相机灵敏度")
        self.tab_widget.addTab(self.theme_tab, "主题")
        # 相机灵敏度
        self.camera_layout.setContentsMargins(38, 38, 38, 38)
        self.camera_layout.setHorizontalSpacing(20)
        self.camera_layout.setVerticalSpacing(12)
        self.camera_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.camera_tab.setLayout(self.camera_layout)
        self.camera_layout.addWidget(self.slider_trans, 0, 0)
        self.camera_layout.addWidget(self.slider_zoom, 0, 1)
        self.camera_layout.addWidget(self.slider_rot, 0, 2)
        self.camera_layout.addWidget(TextLabel(self.camera_tab, "平移", font=YAHEI[9]), 1, 0)
        self.camera_layout.addWidget(TextLabel(self.camera_tab, "缩放", font=YAHEI[9]), 1, 1)
        self.camera_layout.addWidget(TextLabel(self.camera_tab, "旋转", font=YAHEI[9]), 1, 2)
        # 绑定事件
        self.slider_trans.value_changed.connect(self.update_camera_setting)
        self.slider_zoom.value_changed.connect(self.update_camera_setting)
        self.slider_rot.value_changed.connect(self.update_camera_setting)
        # 主题
        self.theme_layout.setContentsMargins(10, 30, 10, 30)
        self.theme_tab.setLayout(self.theme_layout)
        self.theme_layout.setAlignment(Qt.AlignTop)
        self.theme_layout.addWidget(TextLabel(self.theme_tab, "（该功能未完成）", YAHEI[18], GRAY, Qt.AlignCenter))
        self.theme_layout.addWidget(HSLColorPicker())  # 取色器
        # 布局
        self.main_layout.addWidget(self.tab_widget)

    def update_camera_setting(self):
        sensitivity = {
            "平移": self.slider_trans.value(),
            "缩放": self.slider_zoom.value(),
            "旋转": self.slider_rot.value()
        }
        self.__configHandler.set_config("Sensitivity", sensitivity)
        if self.__camera:
            self.__camera.sensitivity = sensitivity


class GLWidgetGUI(GLViewWidget):
    clear_selected_items = pyqtSignal()
    after_selection = pyqtSignal()

    def __init__(self):
        self.main_editor = None
        camera_sensitivity = configHandler.get_config("Sensitivity")
        super().__init__(Vector3(100., 20., 40.), cam_sensitivity=camera_sensitivity)
        self.__init_GUI()

        # 主光照
        self.light = PointLight(
            pos=[400, 500, 400], ambient=(0.6, 0.6, 0.6), diffuse=(0.7, 0.7, 0.7), specular=(0.95, 0.95, 0.95),
            constant=0.001,
            linear=0.001,
            directional=True,
        )
        # self.light1 = PointLight(pos=[0, -50, 10], diffuse=(0, 0.8, 0))
        # self.light2 = PointLight(pos=[-120, 30, 20], diffuse=(0.8, 0, 0))
        # self.light3 = PointLight(pos=[90, 90, 90], diffuse=(0, 0, 0.8))
        # self.all_lights = [self.light, self.light1, self.light2, self.light3]
        # 基础背景物体
        self.__axis = GLAxisItem(fix_to_corner=True)
        self.__grid = GLGridItem(
            size=(500, 500), spacing=(50, 50),
            lineWidth=0.4,
            color=None,
            lineColor=(0.3, 0.8, 1.0, 1.0),
            lights=[self.light],
            glOptions='translucent'
        )
        self.GRAY_material = EditItemMaterial(color=(128, 128, 128))
        self.R_material = EditItemMaterial(color=(255, 0, 0))
        self.G_material = EditItemMaterial(color=(0, 255, 0))
        self.B_material = EditItemMaterial(color=(0, 0, 255))

        # self.text = GLTextItem(text="BB-63 USS Missouri", pos=(0, 50, 0), color=(0.6, 0.6, 0.6), fixed=False)
        # self.model = GLModelItem(
        #     "./pyqtOpenGL/items/resources/models/BB-63.obj",
        #     lights=[self.light],
        #     selectable=True,
        #     drawLine=True,
        #     material=self.GRAY_material
        # ).translate(0, 0, 0)
        #
        sp_ver, sp_idx, _, sp_norm = sphere(20, 128, 128, calc_uv_norm=True)

        self.sphere_r = GLMeshItem(
            vertexes=sp_ver, indices=sp_idx, normals=sp_norm,
            lights=[self.light],
            material=self.R_material,
            glOptions='translucent',
            selectable=True
        ).translate(-60, 0, 0)
        self.sphere_l = GLMeshItem(
            vertexes=sp_ver, indices=sp_idx, normals=sp_norm,
            lights=[self.light],
            material=self.G_material,
            glOptions='translucent',
            selectable=True
        ).translate(60, 0, 0)

        self.addItem(self.__axis)
        self.addItem(self.__grid)
        # self.addItem(self.model)
        # self.addItem(self.text)
        # self.addItem(self.sphere_r)
        # self.addItem(self.sphere_l)

        # 动画
        # self.frame_rate = 30
        # self.animation_timer = QTimer(self)
        # self.animation_timer.timeout.connect(self.animation)
        # self.animation_timer.start(1000 // self.frame_rate)  # 设置定时器，以便每隔一段时间调用onTimeout函数

    def animation(self):
        # self.light.rotate(0, 1, 0.4, 1)
        # self.light1.rotate(1, 1, 0, -2)
        # self.light2.rotate(0.2, 1., 0., 1.5)
        # self.light3.rotate(0, 0.5, 0.5, 0.5)
        # self.paintGL_outside()
        ...

    def __init_GUI(self):
        self.__init_fps_label()

    def __init_fps_label(self):
        self.fps_label.setGeometry(10, 10, 100, 20)
        style = str(  # 透明背景
            f"color: {FG_COLOR0};"
            f"background-color: rgba(0, 0, 0, 0);"
        )
        self.fps_label.setStyleSheet(style)

    # noinspection PyUnresolvedReferences
    # def __init_mode_toolButton(self):
    #     self.mod1_button.setText("全视图1")
    #     self.mod2_button.setText("横剖面2")
    #     self.mod3_button.setText("纵剖面3")
    #     self.mod4_button.setText("左视图4")
    #     self.subMod1_button.setText("部件模式P")
    #     self.subMod2_button.setText("节点模式N")
    #     self.mod1_button.clicked.connect(lambda: self.set_show_3d_obj_mode(OpenGLWin.ShowAll))
    #     self.mod2_button.clicked.connect(lambda: self.set_show_3d_obj_mode(OpenGLWin.ShowXZ))
    #     self.mod3_button.clicked.connect(lambda: self.set_show_3d_obj_mode(OpenGLWin.ShowXY))
    #     self.mod4_button.clicked.connect(lambda: self.set_show_3d_obj_mode(OpenGLWin.ShowLeft))
    #     self.subMod1_button.clicked.connect(lambda: self.set_show_3d_obj_sub_mode(OpenGLWin.ShowObj))
    #     self.subMod2_button.clicked.connect(lambda: self.set_show_3d_obj_sub_mode(OpenGLWin.ShowDotNode))
    #     for button in self.mod_buttons + self.subMod_buttons:
    #         button.setCheckable(True)
    #         button.setFont(FONT_7)
    #         button.setStyleSheet(
    #             f"QToolButton{{"
    #             f"color: {FG_COLOR0};"
    #             f"background-color: {BG_COLOR1};"
    #             f"border: 1px solid {BG_COLOR1};"
    #             f"border-radius: 6px;}}"
    #             # 鼠标悬停时的样式
    #             f"QToolButton:hover{{"
    #             f"color: {FG_COLOR0};"
    #             f"background-color: {BG_COLOR2};"
    #             f"border: 1px solid {BG_COLOR2};"
    #             f"border-radius: 6px;}}"
    #             # 按下时的样式
    #             f"QToolButton:checked{{"
    #             f"color: {FG_COLOR0};"
    #             f"background-color: {BG_COLOR3};"
    #             f"border: 1px solid {BG_COLOR3};"
    #             f"border-radius: 6px;}}"
    #         )
    #     self.mod1_button.setChecked(True)
    #     self.subMod1_button.setChecked(True)

    def update_GUI_after_resize(self):
        # # 更新按钮位置
        # right = QOpenGLWidget.width(self) - 10 - 4 * (self.ModBtWid + 10)
        # sub_right = QOpenGLWidget.width(self) - 10 - 2 * (self.ModBtWid + 35)
        # for button in self.mod_buttons:
        #     index = self.mod_buttons.index(button)
        #     button.setGeometry(right + 10 + index * (self.ModBtWid + 10), 10, self.ModBtWid, 28)
        # for button in self.subMod_buttons:
        #     index = self.subMod_buttons.index(button)
        #     button.setGeometry(sub_right + 10 + index * (self.ModBtWid + 35), 50, self.ModBtWid + 25, 23)
        ...

    # def add_selected_item(self, item):
    #     """
    #     添加被选中的绘制物体，刷新右侧编辑窗口
    #     """
    #     self.after_selection.emit()
    #     if item in self.selected_items:
    #         return
    #     self._clear_selected_items()
    #     self.selected_items.append(item)
    #     if hasattr(item, "handler"):
    #         item.handler.setSelected(True, set_button=False)
    #     else:
    #         item.setSelected(True)
    #
    # def del_selected_item(self, item):
    #     """
    #     删除被选中的绘制物体，刷新右侧编辑窗口
    #     """
    #     self.after_selection.emit()
    #     if item not in self.selected_items:
    #         return
    #     self.selected_items.remove(item)
    #     if hasattr(item, "handler"):
    #         item.handler.setSelected(False, set_button=False)
    #     else:
    #         item.setSelected(False)

    def set_item_selected(self, item, selected):
        if selected and item not in self.selected_items:
            self.selected_items.append(item)
            if hasattr(item, "handler"):
                item.handler.setSelected(True)
            else:
                item.setSelected(True)
        elif not selected and item in self.selected_items:
            self.selected_items.remove(item)
            if hasattr(item, "handler"):
                item.handler.setSelected(False)
            else:
                item.setSelected(False)
        self._after_selection()

    def _clear_selected_items(self):
        self.clear_selected_items.emit()
        super()._clear_selected_items()

    def _after_selection(self):
        self.after_selection.emit()
        super()._after_selection()

    def clearResources(self):
        # self.animation_timer.stop()
        # self.animation_timer.deleteLater()
        for it in self.items:
            del it
        self.items = []
        for light_ in self.lights:
            del light_
        print(f"unref: {gc.collect()}")  # 手动垃圾回收
        self.lights = []

    def __del__(self):
        self.clearResources()
        self.deleteLater()


def sin_texture(t):
    delta = t % 100
    x = np.linspace(-10, 10, 50, dtype='f4')
    y = x.copy()
    X, Y = np.meshgrid(x, y, indexing='xy')
    Z = (np.sin(np.sqrt(X ** 2 + Y ** 2) * np.pi / 5 - delta * np.pi) + 1) / 5
    return np.stack([Z, Z, Z], axis=2)


class MainEditorGUI(Window):
    active_window = None
    all = []

    @not_implemented
    @abstractmethod
    def new_prj(self):
        pass

    @not_implemented
    @abstractmethod
    def open_prj(self, path):
        """
        打开工程
        :param path:
        :return:
        """
        pass

    def select_file_to_open(self):
        """
        打开文件选择窗口，然后打开工程
        :return:
        """
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("NA Hull Editor工程文件 (*.naprj)")
        file_dialog.setViewMode(QFileDialog.Detail)
        prjs = self.configHandler.get_config("Projects")
        if prjs:
            last_prj_path = prjs[list(prjs.keys())[-1]]
            last_prj_path = os.path.dirname(last_prj_path)
            if str(last_prj_path) == "sample_projects":
                last_prj_path = os.path.join(CURRENT_PATH, "sample_projects")
        else:
            last_prj_path = DESKTOP_PATH
        file_dialog.setDirectory(last_prj_path)
        file_dialog.fileSelected.connect(lambda path: self.open_prj(path) if path else None)
        file_dialog.exec()

    @not_implemented
    @abstractmethod
    def save_prj(self):
        pass

    @not_implemented
    @abstractmethod
    def save_as_prj(self):
        pass

    @not_implemented
    @abstractmethod
    def export_to_na(self):
        pass

    @not_implemented
    @abstractmethod
    def set_theme(self):
        pass

    @not_implemented
    @abstractmethod
    def set_camera(self):
        pass

    @not_implemented
    @abstractmethod
    def about(self):
        pass

    @not_implemented
    @abstractmethod
    def tutorial(self):
        pass

    def __init__(self, gl_widget, logger):
        """
        编辑器的主要控件及其绑定和布局
        :param gl_widget:
        :param logger:
        """
        self.gl_widget: GLWidgetGUI = gl_widget
        gl_widget.main_editor = self
        self.configHandler = configHandler
        self.gl_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.logger = logger
        # 主窗口
        self.main_widget = MultiDirTabMainFrame(self.gl_widget)
        # 标签页
        self.user_tab = UserInfoTab(self.main_widget)
        self.structure_tab = ElementStructureTab(self.main_widget, self)
        self.info_tab = PrjInfoTab(self.main_widget)
        self.edit_tab = ElementEditTab(self.main_widget)
        if hasattr(self.gl_widget, "camera"):
            self.camera = self.gl_widget.camera
        else:
            self.camera = None
        self.setting_tab = SettingTab(self.main_widget, self.configHandler, self.camera)
        # 初始化标签页
        self.__init_tab_widgets()
        super().__init__(None, title='NavalArt Hull Editor', ico_bites=BYTES_ICO, size=(1000, 618), resizable=True,
                         show_maximize=True, bd_radius=0)
        self.setWindowTitle('NavalArt Hull Editor')
        # 顶部控件
        self.menuButtons = []
        self.menu_map = {
            "文件": {
                "新建工程": self.new_prj,
                "打开工程": self.open_prj,
                "保存工程": self.save_prj,
                "另存工程": self.save_as_prj,
                "导出到NA": self.export_to_na,
            },
            "设置": {
                "主题": self.set_theme,
                "相机灵敏度": self.set_camera,
            },
            "关于": {
                "关于": self.about,
                "教程": self.tutorial,
            }
        }
        self.currentPrj_button = Button(
            self.customized_top_widget, "当前项目", 0, BG_COLOR1, 5, font=YAHEI[9],
            bg=(BG_COLOR1, BG_COLOR3, GRAY, BG_COLOR3), size=None, padding=(5, 5, 5, 15), show_indicator=" ")
        self.prj_menu_maxSize = [400, 700]
        self.prj_menu = self.__init_prjMenu()
        self.__init_cust_top_widget()
        # 状态变量池
        self._current_prj: Union[None, ShipProject] = None
        MainEditorGUI.all.append(self)

    def __init_cust_top_widget(self):
        # 菜单：
        for menu_name, sub_menus in self.menu_map.items():
            menu_bt = Button(self.customized_top_widget, menu_name, 0, BG_COLOR1, 0, font=YAHEI[10],
                             bg=(BG_COLOR1, BG_COLOR3, GRAY, BG_COLOR3), size=None, padding=(8, 11, 8, 11))
            menu_bt.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
            menu_bt.setText(menu_name)
            menu = self.__init_sub_menu(menu_name, self.menu_map)
            menu_bt.setMenu(menu)
            self.menuButtons.append(menu_bt)
        # 按钮：
        self.currentPrj_button.setText("当前无项目")
        self.currentPrj_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.currentPrj_button.setFocusPolicy(Qt.NoFocus)
        self.currentPrj_button.setMenu(self.prj_menu)
        # 布局：
        self.customized_top_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.customized_top_widget.layout().setSpacing(0)
        for menu_bt in self.menuButtons:
            self.customized_top_widget.layout().addWidget(menu_bt, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        # 加一片空区域
        self.customized_top_widget.layout().addWidget(VerSpliter(None, 15), alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.customized_top_widget.layout().addWidget(self.currentPrj_button, alignment=Qt.AlignLeft | Qt.AlignVCenter)

    def __init_sub_menu(self, menu_name, menu_map):
        menu = QMenu()
        menu.setStyleSheet(
            f"QMenu{{background-color:{BG_COLOR1};color:{FG_COLOR0};border:1px solid {GRAY};}}"
            f"QMenu::item{{padding:5px 25px 5px 18px;}}"
            f"QMenu::item:selected{{background-color:{BG_COLOR3};color:{FG_COLOR0};}}"
            f"QMenu::separator{{height:1px;background-color:{GRAY};margin-left:14px;margin-right:7px;}}"
        )
        # 设置当鼠标悬停的时候就显示菜单
        menu.setToolTipsVisible(True)
        # 添加菜单
        for sub_menu_name in menu_map[menu_name]:
            if isinstance(menu_map[menu_name][sub_menu_name], dict):
                # 添加子菜单
                sub_menu = menu.addMenu(sub_menu_name)
                for sub_sub_menu_name in menu_map[menu_name][sub_menu_name]:
                    sub_sub_menu = QAction(sub_sub_menu_name, self)
                    sub_sub_menu.triggered.connect(menu_map[menu_name][sub_menu_name][sub_sub_menu_name])
                    sub_menu.addAction(sub_sub_menu)
            else:
                sub_menu = QAction(sub_menu_name, self)
                sub_menu.triggered.connect(menu_map[menu_name][sub_menu_name])
                menu.addAction(sub_menu)
            # else:
            #     # 添加子菜单
            #     sub_menu = menu.addMenu(sub_menu_name)
            #     for sub_sub_menu_name in menu_map[menu_name][sub_menu_name]:
            #         sub_sub_menu = QAction(sub_sub_menu_name, self)
            #         sub_sub_menu.triggered.connect(menu_map[menu_name][sub_menu_name][sub_sub_menu_name])
            #         sub_menu.addAction(sub_sub_menu)
        return menu

    def __init_prjMenu(self):
        menu = QMenu()
        menu.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        menu.setStyleSheet(f"""
            QMenu{{
                background-color: {BG_COLOR1};
                color: {FG_COLOR0};
                border: 1px solid {GRAY};
                border-radius: 5px;
            }}
            QMenu::item{{
                padding: 5px 25px 5px 18px;
                border-radius: 5px;
            }}
            QMenu::item:selected{{
                background-color: {BG_COLOR3};
                color: {FG_COLOR0};
            }}
            QMenu::separator{{
                height: 1px;
                background-color: {GRAY};
                margin-left: 14px;
                margin-right: 7px;
            }}
        """)
        # 顶部按钮
        openButton = Button(None, None, 0, BG_COLOR1, 5, font=YAHEI[9],
                            bg=("transparent", BG_COLOR3, GRAY, BG_COLOR3), size=None, padding=(8, 11, 8, 11))
        openButton.setFocusPolicy(Qt.NoFocus)
        openButton.setFixedHeight(28)
        openButton.setLayout(QHBoxLayout())
        openButton.layout().setContentsMargins(0, 0, 0, 0)
        openButton.layout().setSpacing(0)
        openButton.layout().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        icon = IconLabel(None, BYTES_FOLDER, None, 16)
        open_text = TextLabel(None, "打开", font=YAHEI[9], color=FG_COLOR0, align=Qt.AlignLeft | Qt.AlignVCenter)
        # open_text.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        openButton.layout().addWidget(icon)
        openButton.layout().addWidget(open_text)
        openButton.clicked.connect(self.select_file_to_open)
        # 菜单
        menu.setFixedWidth(self.prj_menu_maxSize[0])
        menu.setMaximumHeight(self.prj_menu_maxSize[1])
        menu.setLayout(QVBoxLayout())
        menu.layout().setContentsMargins(0, 0, 0, 0)
        menu.layout().addWidget(openButton)
        return menu

    def __init_tab_widgets(self):
        # self.structure_tab.set_layout(QVBoxLayout())
        # self.structure_tab.main_layout.addWidget(HSLColorPicker())
        # 布局
        self.main_widget.add_tab(self.structure_tab)
        self.main_widget.add_tab(self.info_tab)
        self.main_widget.add_tab(self.user_tab)
        self.main_widget.add_tab(self.edit_tab)
        self.main_widget.add_tab(self.setting_tab)

    def init_top_widget(self):
        self.top_widget.setFixedHeight(self.topH)
        self.top_widget.setStyleSheet(f"""
            QFrame{{
                background-color: {self.bg};
                color: {self.fg};
                border-top-left-radius: {self.bd_radius[0]}px;
                border-top-right-radius: {self.bd_radius[1]}px;
            }}
        """)
        self.customized_top_widget.setFixedHeight(self.topH)
        self.customized_top_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.customized_top_widget.setLayout(QHBoxLayout())
        self.customized_top_widget.layout().setContentsMargins(0, 0, 0, 0)
        # 控件
        self.top_layout.addWidget(self.ico_label, Qt.AlignLeft | Qt.AlignVCenter)
        # TODO: 菜单
        # TODO: 显示当前工程名称
        self.top_layout.addWidget(self.customized_top_widget, Qt.AlignLeft | Qt.AlignVCenter)
        self.top_layout.addWidget(self.drag_area, alignment=Qt.AlignLeft | Qt.AlignVCenter, stretch=1)
        self.top_layout.addWidget(self.minimize_button, Qt.AlignRight | Qt.AlignVCenter)
        self.top_layout.addWidget(self.maximize_button, Qt.AlignRight | Qt.AlignVCenter)
        self.top_layout.addWidget(self.close_button, Qt.AlignRight | Qt.AlignVCenter)

    def init_center_widget(self):
        super().init_center_widget()
        self.center_layout.addWidget(self.main_widget)

    def init_bottom_widget(self):
        self.bottom_widget.setFixedHeight(self.bottomH)
        self.bottom_widget.setStyleSheet(f"""
            QFrame{{
                background-color: {self.bg};
                color: {self.fg};
                border-bottom-left-radius: {self.bd_radius[0]}px;
                border-bottom-right-radius: {self.bd_radius[1]}px;
            }}
        """)
        # 控件
        self.bottom_widget.setContentsMargins(15, 0, 15, 0)
        self.bottom_layout.addWidget(
            self.status_label, alignment=Qt.AlignLeft | Qt.AlignVCenter, stretch=1)
        self.bottom_layout.addWidget(self.memory_widget, Qt.AlignRight | Qt.AlignVCenter)
        self.status_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.memory_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.memory_widget.setFixedWidth(150)

    def setLeftTabWidth(self, width):
        sizes = self.main_widget.ver_spliter.sizes()
        sizes[0] = width
        self.main_widget.ver_spliter.setSizes(sizes)

    def setRightTabWidth(self, width):
        sizes = self.main_widget.ver_spliter.sizes()
        sizes[-1] = width
        self.main_widget.ver_spliter.setSizes(sizes)

    def setBottomTabHeight(self, height):
        sizes = self.main_widget.hor_spliter.sizes()
        sizes[-1] = height
        self.main_widget.hor_spliter.setSizes(sizes)

    def show_status(self, message, color):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")

    def close(self):
        closed = super().close()
        if closed is False:
            return closed
        del self.gl_widget
        MainEditorGUI.all.remove(self)
        self.__del__()

    def __del__(self):
        self.deleteLater()
