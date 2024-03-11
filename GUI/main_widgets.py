# -*- coding: utf-8 -*-
"""
主要窗口
"""
import numpy as np
from GUI.basic_widgets import *
import PIL.Image as Image
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from ShipRead.na_project import ShipProject
from funcs_utils import not_implemented
from pyqtOpenGL import *
from pyqtOpenGL.camera import Camera

from .sub_widgets import *


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
    def __init__(self, parent):
        super().__init__(parent, CONST.LEFT, "结构层级", STRUCTURE_IMAGE)
        self.set_layout(QVBoxLayout())
        # 控件
        self.tab_widget = TabWidget(None, QTabWidget.West)
        self.hullSectionGroup_tab = QWidget()
        self.armorSectionGroup_tab = QWidget()
        self.bridge_tab = QWidget()
        self.railing_tab = QWidget()  # 栏杆
        self.handrail_tab = QWidget()  # 栏板
        self.ladder_tab = QWidget()
        self.hullSectionGroup_layout = QVBoxLayout()
        self.armorSectionGroup_layout = QVBoxLayout()
        self.bridge_layout = QVBoxLayout()
        self.railing_layout = QVBoxLayout()
        self.handrail_layout = QVBoxLayout()
        self.ladder_layout = QVBoxLayout()

        self.__init_main_widget()

    def init_top_widget(self):
        ...

    def __init_main_widget(self):
        self.layout().setContentsMargins(5, 5, 5, 0)
        self.layout().setSpacing(5)
        # self.main_layout.addWidget(TextLabel(self, "船体截面组：", YAHEI[9], FG_COLOR1, Qt.AlignLeft))
        # self.main_layout.addWidget(HorSpliter(self))
        # self.main_layout.addWidget(TextLabel(self, "装甲截面组：", YAHEI[9], FG_COLOR1, Qt.AlignLeft))
        # self.main_layout.addWidget(HorSpliter(self))
        # self.main_layout.addWidget(TextLabel(self, "舰桥：", YAHEI[9], FG_COLOR1, Qt.AlignLeft))
        # self.main_layout.addWidget(HorSpliter(self))
        # self.main_layout.addWidget(TextLabel(self, "栏杆：", YAHEI[9], FG_COLOR1, Qt.AlignLeft))
        # self.main_layout.addWidget(HorSpliter(self))
        # self.main_layout.addWidget(TextLabel(self, "栏板：", YAHEI[9], FG_COLOR1, Qt.AlignLeft))
        # self.main_layout.addWidget(HorSpliter(self))
        # self.main_layout.addWidget(TextLabel(self, "梯子：", YAHEI[9], FG_COLOR1, Qt.AlignLeft))
        # self.main_layout.addWidget(HorSpliter(self))
        self.tab_widget.addTab(self.hullSectionGroup_tab, "船体截面组")
        self.tab_widget.addTab(self.armorSectionGroup_tab, "装甲截面组")
        self.tab_widget.addTab(self.bridge_tab, "舰桥")
        self.tab_widget.addTab(self.railing_tab, "栏杆")
        self.tab_widget.addTab(self.handrail_tab, "栏板")
        self.tab_widget.addTab(self.ladder_tab, "梯子")
        # 布局
        self.hullSectionGroup_tab.setLayout(self.hullSectionGroup_layout)
        self.armorSectionGroup_tab.setLayout(self.armorSectionGroup_layout)
        self.bridge_tab.setLayout(self.bridge_layout)
        self.railing_tab.setLayout(self.railing_layout)
        self.handrail_tab.setLayout(self.handrail_layout)
        self.ladder_tab.setLayout(self.ladder_layout)
        # 总布局
        self.main_layout.addWidget(self.tab_widget)

    def add_hullSectionGroup(self, hull_section_group):
        pass

    def add_armorSectionGroup(self, armor_section_group):
        pass

    def add_bridge(self, bridge):
        pass

    def add_railing(self, railing):
        pass

    def add_handrail(self, handrail):
        pass

    def add_ladder(self, ladder):
        pass

    def del_hullSectionGroup(self, hull_section_group):
        pass

    def del_armorSectionGroup(self, armor_section_group):
        pass

    def del_bridge(self, bridge):
        pass

    def del_railing(self, railing):
        pass

    def del_handrail(self, handrail):
        pass

    def del_ladder(self, ladder):
        pass


class ElementEditTab(MutiDirectionTab):
    element_mutex = QMutex()  # 互斥锁，用于保证只有一个元素被编辑
    elementType_updated = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent, CONST.RIGHT, "元素编辑", EDIT_IMAGE)
        self.set_layout(QVBoxLayout())
        self.elementType_label = TextLabel(self, "无选中物体", YAHEI[9], FG_COLOR1, Qt.AlignLeft)
        self.edit_hullSectionGroup_widget = EditHullSectionGroupWidget()
        self.edit_armorSectionGroup_widget = EditArmorSectionGroupWidget()
        self.edit_bridge_widget = EditBridgeWidget()
        self.edit_railing_widget = EditRailingWidget()
        self.edit_handrail_widget = EditHandrailWidget()
        self.edit_ladder_widget = EditLadderWidget()
        self.edit_widgets = {
            self.edit_hullSectionGroup_widget: "船体截面组",
            self.edit_armorSectionGroup_widget: "装甲截面组",
            self.edit_bridge_widget: "舰桥",
            self.edit_railing_widget: "栏杆",
            self.edit_handrail_widget: "栏板",
            self.edit_ladder_widget: "梯子"
        }
        self.current_edit_widget: Union[None, QWidget] = None

        self.__init_main_widget()

    def init_top_widget(self):
        ...

    def __init_main_widget(self):
        self.layout().setContentsMargins(5, 5, 5, 0)
        self.layout().setSpacing(5)
        # 布局
        self.main_layout.addWidget(self.elementType_label)
        self.main_layout.addWidget(HorSpliter(self))
        for ew in self.edit_widgets:
            ew.hide()
            ew.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            self.main_layout.addWidget(ew)
        self.main_layout.setAlignment(Qt.AlignTop)
        # TODO:
        self.set_edit_widget("船体截面组")

    def set_edit_widget(self,
                        element_type: Literal["船体截面组", "装甲截面组", "舰桥", "栏杆", "栏板", "梯子"] = None,
                        edit_widget: Union[
                            None, EditHullSectionGroupWidget, EditArmorSectionGroupWidget,
                            EditBridgeWidget, EditRailingWidget, EditHandrailWidget, EditLadderWidget] = None):
        """
        设置当前编辑的元素，两个参数最好只能填写一个
        :param element_type: "船体截面组", "装甲截面组", "舰桥", "栏杆", "栏板", "梯子"
        :param edit_widget: self.edit_hullSectionGroup_widget, self.edit_armorSectionGroup_widget,
                            self.edit_bridge_widget, self.edit_railing_widget, self.edit_handrail_widget,
                            self.edit_ladder_widget
        :return:
        """
        self.element_mutex.lock()
        if element_type and not edit_widget:
            self.elementType_label.setText(element_type)
            for ew, et in self.edit_widgets.items():
                if et == element_type:
                    ew.show()
                    self.current_edit_widget = ew
                else:
                    ew.hide()
            self.elementType_updated.emit(element_type)
        elif edit_widget and not element_type:
            self.elementType_label.setText(self.edit_widgets[edit_widget])
            for ew in self.edit_widgets:
                if ew == edit_widget:
                    ew.show()
                    self.current_edit_widget = ew
                else:
                    ew.hide()
            self.elementType_updated.emit(self.edit_widgets[edit_widget])
        elif not element_type and not edit_widget:
            self.elementType_label.setText("无选中物体")
            for ew in self.edit_widgets:
                ew.hide()
            self.current_edit_widget = None
            self.elementType_updated.emit("无选中物体")
        elif element_type and edit_widget:
            if self.edit_widgets[edit_widget] != element_type:
                self.element_mutex.unlock()
                raise ValueError("element_type和edit_widget不匹配")
            self.elementType_label.setText(element_type)
            for ew in self.edit_widgets:
                if ew == edit_widget:
                    ew.show()
                    self.current_edit_widget = ew
                else:
                    ew.hide()
            self.elementType_updated.emit(element_type)
        self.element_mutex.unlock()


class SettingTab(MutiDirectionTab):
    def __init__(self, parent, configHandler, camera):
        self.__configHandler = configHandler
        self.__camera_sensitivity = configHandler.get_config("Sensitivity")
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
        self.__camera.sensitivity = sensitivity


class GLWidgetGUI(GLViewWidget):
    def __init__(self, configHandler_):
        camera_sensitivity = configHandler_.get_config("Sensitivity")
        super().__init__(Vector3(100., 20., 40.), cam_sensitivity=camera_sensitivity)
        self.__init_GUI()

        ver1, ind1 = sphere(20, 20, 20)
        normal1 = ver1 / 2
        ver2, ind2 = cylinder(radius=[12, 10], cols=12, rows=8, length=2.4)
        # img = Image.open("./pyqtOpenGL/items/resources/textures/box.png")
        # img = np.array(img, dtype='f4')

        # self.img = GLImageItem(img, width_height=(0.2, 0.2))
        self.ax = GLAxisItem(size=(80, 80, 80))
        self.box = GLBoxTextureItem(size=(20, 20, 20))
        self.box.translate(0, 1.1, 0)
        self.text = GLTextItem(text="Hello World", pos=(2, 6, -1), color=(1, 0.6, 1), fixed=False)
        self.arrow = GLArrowPlotItem(
            start_pos=ver1 + [5, -1, 0],
            end_pos=ver1 + normal1 + [5, -1, 0],
            color=[1, 1, 0]
        )

        # -- scatter and line
        pos = np.random.uniform(-2, 2, size=(15, 3)).astype('f4') * (2, 1, 2) + [0, -3, 0]
        color = np.random.uniform(0, 1, size=(15, 3)).astype('f4')
        self.scatter = GLScatterPlotItem(pos=pos, color=color, size=2)
        self.line = GLLinePlotItem(pos=pos, color=color, lineWidth=2)

        # -- lights
        self.light = PointLight(pos=[0, 50, 40], ambient=(0.8, 0.8, 0.8), diffuse=(0.8, 0.8, 0.8))
        self.light1 = PointLight(pos=[0, -50, 10], diffuse=(0, 0.8, 0))
        self.light2 = PointLight(pos=[-120, 30, 20], diffuse=(0.8, 0, 0))

        # -- grid
        self.grid = GLGridItem(
            size=(70, 70), lineWidth=1,
            lights=[self.light, self.light1, self.light2]
        )

        # -- model
        # self.model = GLModelItem(
        #     "./pyqtOpenGL/items/resources/objects/cyborg/cyborg.obj",
        #     lights=[self.light, self.light1, self.light2]
        # )
        # self.model = GLModelItem(
        #     "./pyqtOpenGL/items/resources/objects/BB-63.obj",
        #     lights=[self.light, self.light1, self.light2]
        # )
        # self.model.translate(0, 2, 0)

        # -- mesh
        self.mesh1 = GLInstancedMeshItem(
            pos=[[50, -10, 0], [-30, 50, -50], [40, 60, -80]],
            lights=[self.light, self.light1, self.light2],
            indices=ind1,
            vertexes=ver1,
            normals=normal1,
            color=(0.7, 0.8, 0.8)
        )

        self.mesh2 = GLMeshItem(
            indices=ind2,
            vertexes=ver2,
            lights=[self.light, self.light1, self.light2],
            material=Material((0.4, 0.1, 0.1), diffuse=(0.6, 0.1, 0.3))
        )
        self.mesh2.rotate(-50, 1, 0.4, 0)
        self.mesh2.translate(-6, 2, -2)

        # -- surface
        self.zmap = np.random.uniform(0, 1.5, (25, 25))
        self.texture = Texture2D(sin_texture(0))
        self.surf = GLSurfacePlotItem(
            zmap=self.zmap, x_size=6, lights=[self.light, self.light1, self.light2],
            material=Material((0.2, 0.2, 0.2), diffuse=(0.5, 0.5, 0.5), textures=[self.texture])
        )
        self.surf.rotate(-90, 1, 0, 0)
        self.surf.translate(-6, -1, 0)

        # -- 3d grid
        z = np.random.uniform(-3, -2, (5, 6))
        y = np.arange(5) + 2
        x = np.arange(6) + 1
        X, Y = np.meshgrid(x, y, indexing='xy')
        grid = np.stack([X, Y, z], axis=2)
        color = np.random.random((5, 6, 3))
        self.grid3d = GL3DGridItem(grid=grid, fill=True, opacity=0.5, color=color)
        self.grid3d.setDepthValue(10)
        self.grid3d1 = GL3DGridItem(grid=grid, fill=False, color=(0, 0, 0))
        self.grid3d1.setDepthValue(-1)

        self.addItem(self.grid3d)
        self.addItem(self.grid3d1)
        self.addItem(self.text)
        # self.addItem(self.img)
        self.addItem(self.ax)
        self.addItem(self.grid)
        self.addItem(self.scatter)
        self.addItem(self.line)
        self.addItem(self.box)
        self.addItem(self.arrow)
        # self.addItem(self.model)
        self.addItem(self.surf)
        self.addItem(self.mesh1)
        self.addItem(self.mesh2)

        # self.drawObjHandler = DrawObjHandler(self)
        # self.gl_initialized.connect(self.__init_drawObjs)  # 链接gl初始化完成和初始化绘制物体

        # 动画
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.onTimeout)
        timer.start(16)  # 设置定时器，以便每隔一段时间调用onTimeout函数

    def onTimeout(self):
        self.light.rotate(0, 1, 0.4, 1)
        self.light1.rotate(1, 1, 0, -2)
        self.light2.rotate(0.2, 1., 0., 1.5)
        self.update()

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

    def draw_2D_objs(self):
        pass

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


def sin_texture(t):
    delta = t % 100
    x = np.linspace(-10, 10, 50, dtype='f4')
    y = x.copy()
    X, Y = np.meshgrid(x, y, indexing='xy')
    Z = (np.sin(np.sqrt(X ** 2 + Y ** 2) * np.pi / 5 - delta * np.pi) + 1) / 5
    return np.stack([Z, Z, Z], axis=2)


class MainEditorGUI(Window):
    active_window = None

    @not_implemented
    @abstractmethod
    def new_prj(self):
        pass

    @not_implemented
    @abstractmethod
    def open_prj(self):
        pass

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

    def __init__(self, gl_widget, config_handler):
        self.gl_widget: GLWidgetGUI = gl_widget
        self.configHandler = config_handler
        self.gl_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # 主窗口
        self.main_widget = MultiDirTabMainFrame(self.gl_widget)
        # 标签页
        self.user_tab = UserInfoTab(self.main_widget)
        self.structure_tab = ElementStructureTab(self.main_widget)
        self.info_tab = PrjInfoTab(self.main_widget)
        self.edit_tab = ElementEditTab(self.main_widget)
        self.setting_tab = SettingTab(self.main_widget, self.configHandler, self.gl_widget.camera)
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
        self.__operating_prj: Union[None, ShipProject] = None

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
        openButton.clicked.connect(self.open_prj)
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
        self.bottom_layout.addWidget(self.status_label, Qt.AlignLeft | Qt.AlignVCenter)

    def resetTheme(self, theme_data):
        ...
