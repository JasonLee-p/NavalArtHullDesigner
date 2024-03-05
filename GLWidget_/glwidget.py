# -*- coding: utf-8 -*-
"""

"""
import time
from abc import abstractmethod
from typing import Literal

import numpy as np

from PyQt5.QtWidgets import QOpenGLWidget
# noinspection PyUnresolvedReferences
from PyQt5 import _QOpenGLFunctions_2_0  # 这个库必须导入，否则打包后会报错
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import (QVector3D, QMatrix4x4, QImage, QQuaternion, QOpenGLContext, QOffscreenSurface, QMouseEvent,
                         QCursor, QOpenGLVersionProfile, QWheelEvent, QSurfaceFormat, QKeyEvent)
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_PROJECTION, GL_MODELVIEW, GL_LINE_STIPPLE
from PyQt5.QtCore import Qt

from GUI import TextLabel, GLTheme


class Camera:
    """
    摄像机类，用于处理视角变换
    """
    all_cameras = []

    def __init__(self, width, height, sensitivity: dict, init_pos: QVector3D = QVector3D(100, 20, 40)):
        self.width = width
        self.height = height
        self.tar = QVector3D(0, 0, 0)  # 摄像机的目标位置
        self.pos = init_pos  # 摄像机的位置
        self.angle = self.calculate_angle()  # 摄像机的方向
        self.distance = (self.tar - self.pos).length()  # 摄像机到目标的距离
        self.up = QVector3D(0, 1, 0)  # 摄像机的上方向，y轴正方向
        self.fovy = 45
        # 灵敏度
        self.sensitivity: dict = sensitivity
        Camera.all_cameras.append(self)

    @property
    def modelview_matrix(self):
        matrix = QMatrix4x4()
        return matrix.lookAt(self.pos, self.tar, self.up)

    @property
    def model_matrix(self):
        matrix = QMatrix4x4()
        return matrix.lookAt(self.pos, self.tar, self.up)

    @property
    def projection_matrix(self):
        matrix = QMatrix4x4()
        return matrix.perspective(self.fovy, self.width / self.height, 0.1, 100000)

    @property
    def viewport(self):
        return 0, 0, self.width, self.height

    def change_view(self, mode):
        # 切换正交投影和透视投影
        if mode == OpenGLWin.Perspective:
            self.fovy = 45
        elif mode == OpenGLWin.Orthogonal:
            self.fovy = 0

    def change_target(self, tar):
        self.pos = tar + (self.pos - self.tar).normalized() * self.distance
        self.tar = tar
        self.angle = self.calculate_angle()

    def calculate_angle(self):
        return QVector3D(self.tar - self.pos).normalized()

    def translate(self, dx, dy):
        """
        根据鼠标移动，沿视角法相平移摄像头
        :param dx:
        :param dy:
        :return:
        """
        dx = dx * 0.02 * self.sensitivity["平移"]
        dy = dy * 0.02 * self.sensitivity["平移"]
        rate_ = self.distance / 1500
        _left = QVector3D.crossProduct(self.angle, self.up).normalized()
        up = QVector3D.crossProduct(_left, self.angle).normalized()
        self.tar += up * dy * rate_ - _left * dx * rate_
        self.pos += up * dy * rate_ - _left * dx * rate_
        self.distance = (self.tar - self.pos).length()

    def zoom(self, add_rate):
        """
        缩放摄像机
        """
        self.pos = self.tar + (self.pos - self.tar) * (1 + add_rate * 0.01 * self.sensitivity["缩放"])
        self.distance = (self.tar - self.pos).length()

    def rotate(self, dx, dy):
        """
        根据鼠标移动，以视点为锚点，等距，旋转摄像头
        """
        _rate = 0.002
        dx = dx * self.sensitivity["旋转"] * _rate
        dy = dy * self.sensitivity["旋转"] * _rate
        _left = QVector3D.crossProduct(self.angle, self.up).normalized()
        up = QVector3D.crossProduct(_left, self.angle).normalized()
        # 计算旋转矩阵
        rotation = QQuaternion.fromAxisAndAngle(up, -dx) * QQuaternion.fromAxisAndAngle(_left, -dy)
        # 更新摄像机位置
        self.pos -= self.tar  # 将坐标系原点移到焦点
        self.pos = rotation.rotatedVector(self.pos)  # 应用旋转
        self.pos += self.tar  # 将坐标系原点移回来
        # 更新摄像机的方向向量
        self.angle = rotation.rotatedVector(self.angle)
        # 如果到顶或者到底，就不再旋转
        if self.angle.x() > 0.99 and dy > 0:
            return
        if self.angle.x() < -0.99 and dy < 0:
            return

    @property
    def save_data(self):
        # return {"tar": list(self.tar), "pos": list(self.pos), "fovy": int(self.fovy)}
        return {"tar": [self.tar.x(), self.tar.y(), self.tar.z()],
                "pos": [self.pos.x(), self.pos.y(), self.pos.z()],
                "fovy": int(self.fovy)}

    def __str__(self):
        return str(
            f"target:     {self.tar.x()}, {self.tar.y()}, {self.tar.z()}\n"
            f"position:   {self.pos.x()}, {self.pos.y()}, {self.pos.z()}\n"
            f"angle:      {self.angle.x()}, {self.angle.y()}, {self.angle.z()}\n"
            f"distance:   {self.distance}\n"
            f"sensitivity:\n"
            f"    zoom:   {self.sensitivity['缩放']}\n"
            f"    rotate: {self.sensitivity['旋转']}\n"
            f"    move:   {self.sensitivity['平移']}\n"
        )


def reset_matrix(func):
    def _wrapper(*args, **kwargs):
        self = args[0]
        # 保存原来的矩阵
        self.gl2_0.glMatrixMode(GL_PROJECTION)
        self.gl2_0.glPushMatrix()
        self.gl2_0.glLoadIdentity()
        self.gl2_0.glOrtho(0, self.width, self.height, 0, -1, 1)
        self.gl2_0.glMatrixMode(GL_MODELVIEW)
        self.gl2_0.glPushMatrix()
        self.gl2_0.glLoadIdentity()
        func(*args, **kwargs)
        # 恢复原来的矩阵
        self.gl2_0.glMatrixMode(GL_PROJECTION)
        self.gl2_0.glPopMatrix()
        self.gl2_0.glMatrixMode(GL_MODELVIEW)
        self.gl2_0.glPopMatrix()

    return _wrapper


class DrawObjHandler:
    """
    管理所有的绘制物体
    """

    def __init__(self, gl_widget):
        self.gl_widget = gl_widget
        self.gl2_0 = gl_widget.gl2_0
        # 环境物体
        self.background = []
        self.show_background = True
        self.genlist_background = self.gl2_0.glGenLists(1)
        self.useGenlist_background = False
        # 外形船体截块
        self.hullSection = {"created": [], "temp": [], "animation": [], "selected": []}
        self.show_hullSection = {"created": True, "temp": True, "animation": True, "selected": True}
        self.genlist_hullSection = {"created": self.gl2_0.glGenLists(1), "temp": self.gl2_0.glGenLists(1),
                                    "animation": self.gl2_0.glGenLists(1), "selected": self.gl2_0.glGenLists(1)}
        self.useGenlist_hullSection = {"created": False, "temp": False, "animation": False, "selected": False}
        # 装甲船体
        self.armor = {"created": [], "temp": [], "animation": [], "selected": []}
        self.show_armor = {"created": True, "temp": True, "animation": True, "selected": True}
        self.genlist_armor = {"created": self.gl2_0.glGenLists(1), "temp": self.gl2_0.glGenLists(1),
                              "animation": self.gl2_0.glGenLists(1), "selected": self.gl2_0.glGenLists(1)}
        self.useGenlist_armor = {"created": False, "temp": False, "animation": False, "selected": False}
        # 栏杆
        self.railing = {"created": [], "temp": [], "animation": [], "selected": []}
        self.show_railing = {"created": True, "temp": True, "animation": True, "selected": True}
        self.genlist_railing = {"created": self.gl2_0.glGenLists(1), "temp": self.gl2_0.glGenLists(1),
                                "animation": self.gl2_0.glGenLists(1), "selected": self.gl2_0.glGenLists(1)}
        self.useGenlist_railing = {"created": False, "temp": False, "animation": False, "selected": False}
        # 栏板
        self.handrail = {"created": [], "temp": [], "animation": [], "selected": []}
        self.show_handrail = {"created": True, "temp": True, "animation": True, "selected": True}
        self.genlist_handrail = {"created": self.gl2_0.glGenLists(1), "temp": self.gl2_0.glGenLists(1),
                                 "animation": self.gl2_0.glGenLists(1), "selected": self.gl2_0.glGenLists(1)}
        self.useGenlist_handrail = {"created": False, "temp": False, "animation": False, "selected": False}
        # 梯子
        self.ladder = {"created": [], "temp": [], "animation": [], "selected": []}
        self.show_ladder = {"created": True, "temp": True, "animation": True, "selected": True}
        self.genlist_ladder = {"created": self.gl2_0.glGenLists(1), "temp": self.gl2_0.glGenLists(1),
                               "animation": self.gl2_0.glGenLists(1), "selected": self.gl2_0.glGenLists(1)}
        self.useGenlist_ladder = {"created": False, "temp": False, "animation": False, "selected": False}
        # 舰桥船体
        self.bridge = {"created": [], "temp": [], "animation": [], "selected": []}
        self.show_bridge = {"created": True, "temp": True, "animation": True, "selected": True}
        self.genlist_bridge = {"created": self.gl2_0.glGenLists(1), "temp": self.gl2_0.glGenLists(1),
                               "animation": self.gl2_0.glGenLists(1), "selected": self.gl2_0.glGenLists(1)}
        self.useGenlist_bridge = {"created": False, "temp": False, "animation": False, "selected": False}
        # 指示箭头（动态，不使用显示列表）
        self.arrow = []
        self.show_arrow = True

    def add_obj(self, obj, obj_type: Literal["hullSection", "armor", "railing", "deck", "ladder", "bridge"],
                obj_state: Literal["created", "temp", "animation"]):
        if obj_type == "hullSection":
            self.hullSection[obj_state].extend(obj) if isinstance(obj, list) else self.hullSection[obj_state].append(
                obj)
        elif obj_type == "armor":
            self.armor[obj_state].extend(obj) if isinstance(obj, list) else self.armor[obj_state].append(obj)
        elif obj_type == "railing":
            self.railing[obj_state].extend(obj) if isinstance(obj, list) else self.railing[obj_state].append(obj)
        elif obj_type == "deck":
            self.handrail[obj_state].extend(obj) if isinstance(obj, list) else self.handrail[obj_state].append(obj)
        elif obj_type == "ladder":
            self.ladder[obj_state].extend(obj) if isinstance(obj, list) else self.ladder[obj_state].append(obj)
        elif obj_type == "bridge":
            self.bridge[obj_state].extend(obj) if isinstance(obj, list) else self.bridge[obj_state].append(obj)

    def start_all_genlist(self):
        self.useGenlist_background = True
        self.useGenlist_hullSection = {"created": True, "temp": True, "animation": True, "selected": True}
        self.useGenlist_armor = {"created": True, "temp": True, "animation": True, "selected": True}
        self.useGenlist_railing = {"created": True, "temp": True, "animation": True, "selected": True}
        self.useGenlist_handrail = {"created": True, "temp": True, "animation": True, "selected": True}
        self.useGenlist_ladder = {"created": True, "temp": True, "animation": True, "selected": True}
        self.useGenlist_bridge = {"created": True, "temp": True, "animation": True, "selected": True}

    def stop_all_using_genlist(self):
        self.useGenlist_background = False
        self.useGenlist_hullSection = {"created": False, "temp": False, "animation": False, "selected": False}
        self.useGenlist_armor = {"created": False, "temp": False, "animation": False, "selected": False}
        self.useGenlist_railing = {"created": False, "temp": False, "animation": False, "selected": False}
        self.useGenlist_handrail = {"created": False, "temp": False, "animation": False, "selected": False}
        self.useGenlist_ladder = {"created": False, "temp": False, "animation": False, "selected": False}
        self.useGenlist_bridge = {"created": False, "temp": False, "animation": False, "selected": False}


class OpenGLWin(QOpenGLWidget):
    # 视图模式
    Perspective = "perspective"
    Orthogonal = "orthogonal"
    # 信号
    gl_initialized = pyqtSignal()

    def __init__(self, parent, camera_sensitivity: dict, init_camera_pos: QVector3D = QVector3D(100, 20, 40),
                 init_prj_mode=Perspective):
        """
        基础的OpenGL窗口，仅附带选择框、绘图和事件接口，不初始化任何物体，作为基类使用
        :param parent: 父控件
        :param camera_sensitivity: 摄像机灵敏度，包括缩放、旋转、平移（0-1）
        :param init_prj_mode: 初始化视图模式，默认为透视投影
        """
        self.prj_mode = init_prj_mode  # 视图模式

        super().__init__(parent)
        # ===================================================================================设置基本参数
        self.setMouseTracking(True)
        self.setStyleSheet("""
            QOpenGLWidget{
            background-color: #000000;
        }
        """)
        # 设置鼠标样式
        self.cs = Qt.ArrowCursor
        self.setCursor(self.cs)
        self.setFocusPolicy(Qt.StrongFocus)  # 设置焦点策略
        self.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置右键菜单策略
        self.width = QOpenGLWidget.width(self)
        self.height = QOpenGLWidget.height(self)
        self.theme_color = GLTheme
        self.light_pos = QVector3D(1000, 700, 1000)
        self.fovy = 45
        # ==================================================================================OpenGL初始化
        self.gl2_0 = None
        # ========================================================================================3D物体
        # =========================================================================================事件
        self.camera = Camera(self.width, self.height, camera_sensitivity, init_camera_pos)
        self.GLinitialized = False
        self.camera_movable = True  # 摄像机是否可移动
        self.lastPos = QPoint()  # 上一次鼠标位置
        self.select_start = None  # 选择框起点
        self.select_end = None  # 选择框终点
        self.rotate_start = None  # 旋转起点
        self.last_frame_time = time.time()  # 帧渲染事件戳
        # ========================================================================================子控件
        self.fps_label = TextLabel(self, "")
        # 绘制物体集合
        self.drawObjHandler: DrawObjHandler = None

    def initializeGL(self) -> None:
        super().initializeGL()
        self.__init_gl()  # 初始化OpenGL相关参数
        self.drawObjHandler = DrawObjHandler(self)
        # ===============================================================================绘制
        # 设置背景颜色
        glClearColor(*self.theme_color["背景"])
        # ===============================================================================绘制
        self.GLinitialized = True
        self.gl_initialized.emit()

    def paintGL(self) -> None:
        """
        绘制
        所有的对象在绘制的时候都会绑定self.glWin = self
        :return:
        """
        super().paintGL()
        self.__before_draw()
        # ============================================================================= 绘制物体
        # 绘制物体
        self.gl2_0.glLoadName(0)
        self.__draw_main_objs()
        self.gl2_0.glLoadName(0)
        # 开启辅助光
        self.gl2_0.glEnable(GL_LIGHT1)
        self.__draw_2D_objs()
        # 关闭辅助光
        self.gl2_0.glDisable(GL_LIGHT1)
        if time.time() - self.last_frame_time != 0:
            self.fps_label.setText(f"FPS: {round(1 / (time.time() - self.last_frame_time), 1)}")
        self.last_frame_time = time.time()

    def __before_draw(self):
        # 获取窗口大小，如果窗口大小改变，就重新初始化
        width = QOpenGLWidget.width(self)
        height = QOpenGLWidget.height(self)
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            try:
                # 更新视口
                self.__init_view()
            except GLError:
                pass
            self.update_GUI_after_resize()
        # 清除颜色缓冲区和深度缓冲区
        self.gl2_0.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # 设置相机
        self.gl2_0.glLoadIdentity()  # 重置矩阵
        self.gl2_0.glDisable(GL_LINE_STIPPLE)  # 禁用虚线模式
        self.__set_camera() if self.camera_movable else None

    def __draw_main_objs(self):
        # 绘制所有self.drawObjHandler中的物体
        # 背景：
        if self.drawObjHandler.show_background:
            if self.drawObjHandler.useGenlist_background:
                self.gl2_0.glCallList(self.drawObjHandler.genlist_background)
            else:
                self.drawObjHandler.useGenlist_background = True
                self.gl2_0.glNewList(self.drawObjHandler.genlist_background, GL_COMPILE)
                for bg in self.drawObjHandler.background:
                    bg.draw()
                self.gl2_0.glEndList()
        # 实体：
        for obj_state in ["created", "temp", "animation", "selected"]:
            # 船体
            if self.drawObjHandler.show_hullSection[obj_state]:
                if self.drawObjHandler.useGenlist_hullSection[obj_state]:
                    self.gl2_0.glCallList(self.drawObjHandler.genlist_hullSection[obj_state])
                else:
                    self.drawObjHandler.genlist_hullSection[obj_state] = self.gl2_0.glGenLists(1)
                    self.gl2_0.glNewList(self.drawObjHandler.genlist_hullSection[obj_state], GL_COMPILE)
                    for obj in self.drawObjHandler.hullSection[obj_state]:
                        obj.draw()
                    self.gl2_0.glEndList()
            # 装甲
            if self.drawObjHandler.show_armor[obj_state]:
                if self.drawObjHandler.useGenlist_armor[obj_state]:
                    self.gl2_0.glCallList(self.drawObjHandler.genlist_armor[obj_state])
                else:
                    self.drawObjHandler.genlist_armor[obj_state] = self.gl2_0.glGenLists(1)
                    self.gl2_0.glNewList(self.drawObjHandler.genlist_armor[obj_state], GL_COMPILE)
                    for obj in self.drawObjHandler.armor[obj_state]:
                        obj.draw()
                    self.gl2_0.glEndList()
            # 栏杆
            if self.drawObjHandler.show_railing[obj_state]:
                if self.drawObjHandler.useGenlist_railing[obj_state]:
                    self.gl2_0.glCallList(self.drawObjHandler.genlist_railing[obj_state])
                else:
                    self.drawObjHandler.genlist_railing[obj_state] = self.gl2_0.glGenLists(1)
                    self.gl2_0.glNewList(self.drawObjHandler.genlist_railing[obj_state], GL_COMPILE)
                    for obj in self.drawObjHandler.railing[obj_state]:
                        obj.draw()
                    self.gl2_0.glEndList()
            # 栏板
            if self.drawObjHandler.show_handrail[obj_state]:
                if self.drawObjHandler.useGenlist_handrail[obj_state]:
                    self.gl2_0.glCallList(self.drawObjHandler.genlist_handrail[obj_state])
                else:
                    self.drawObjHandler.genlist_handrail[obj_state] = self.gl2_0.glGenLists(1)
                    self.gl2_0.glNewList(self.drawObjHandler.genlist_handrail[obj_state], GL_COMPILE)
                    for obj in self.drawObjHandler.handrail[obj_state]:
                        obj.draw()
                    self.gl2_0.glEndList()
            # 梯子
            if self.drawObjHandler.show_ladder[obj_state]:
                if self.drawObjHandler.useGenlist_ladder[obj_state]:
                    self.gl2_0.glCallList(self.drawObjHandler.genlist_ladder[obj_state])
                else:
                    self.drawObjHandler.genlist_ladder[obj_state] = self.gl2_0.glGenLists(1)
                    self.gl2_0.glNewList(self.drawObjHandler.genlist_ladder[obj_state], GL_COMPILE)
                    for obj in self.drawObjHandler.ladder[obj_state]:
                        obj.draw()
                    self.gl2_0.glEndList()
            # 舰桥
            if self.drawObjHandler.show_bridge[obj_state]:
                if self.drawObjHandler.useGenlist_bridge[obj_state]:
                    self.gl2_0.glCallList(self.drawObjHandler.genlist_bridge[obj_state])
                else:
                    self.drawObjHandler.genlist_bridge[obj_state] = self.gl2_0.glGenLists(1)
                    self.gl2_0.glNewList(self.drawObjHandler.genlist_bridge[obj_state], GL_COMPILE)
                    for obj in self.drawObjHandler.bridge[obj_state]:
                        obj.draw()
                    self.gl2_0.glEndList()
        # 指示箭头：
        if self.drawObjHandler.show_arrow:
            for arrow in self.drawObjHandler.arrow:
                arrow.draw()

    def __draw_select_box(self):
        """
        转变为二维视角，画出选择框
        """
        # 画虚线框
        self.gl2_0.glColor4f(*self.theme_color["选择框"][0])
        self.gl2_0.glEnable(GL_LINE_STIPPLE)  # 启用虚线模式
        self.gl2_0.glLineStipple(0, 0x00FF)  # 设置虚线的样式
        self.gl2_0.glBegin(self.gl2_0.GL_LINE_LOOP)
        self.gl2_0.glVertex2f(self.select_start.x(), self.select_start.x())
        self.gl2_0.glVertex2f(self.select_start.x(), self.select_end.x())
        self.gl2_0.glVertex2f(self.select_end.x(), self.select_end.x())
        self.gl2_0.glVertex2f(self.select_end.x(), self.select_start.x())
        self.gl2_0.glEnd()

    @reset_matrix
    def __draw_2D_objs(self):
        self.draw_2D_objs()
        if self.select_start and self.select_end:
            self.__draw_select_box()

    def save_current_image(self, save_dir, prj_name):
        """
        获取当前画面中物体图像，背景为透明，格式为png
        :param save_dir: 保存路径
        :param prj_name: 项目名称
        :return:
        """
        # 在线程A中创建一个QOpenGLContext
        offScreen_surface = QOffscreenSurface()
        offScreen_surface.create()
        offScreen_context = QOpenGLContext()
        offScreen_context.create()
        offScreen_context.makeCurrent(offScreen_surface)
        # TODO: 删除所有环境物体
        self.paintGL()
        self.update()
        # 获取当前画面中物体图像，裁剪边缘，背景为透明，格式为png
        cut = 0
        image = self.grabFramebuffer()
        image = image.copy(cut, cut, image.width() - 2 * cut, image.height() - 2 * cut)
        image = image.convertToFormat(QImage.Format_ARGB32)
        # 检查路径
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # 保存图片
        image.save(os.path.join(save_dir, f"{prj_name}.png"))
        # TODO: 恢复环境物体
        self.paintGL()
        self.update()

    @abstractmethod
    def update_GUI_after_resize(self):
        ...

    @abstractmethod
    def draw_2D_objs(self):
        ...

    def change_view_mode(self):
        if self.prj_mode == OpenGLWin.Perspective:
            self.prj_mode = OpenGLWin.Orthogonal
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glLoadIdentity()
            self.gl2_0.glOrtho(-self.width / 2, self.width / 2, -self.height / 2, self.height / 2, -1000, 1000)
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            self.gl2_0.glLoadIdentity()
            self.camera.change_view(OpenGLWin.Orthogonal)
            self.paintGL()
            self.update()
        elif self.prj_mode == OpenGLWin.Orthogonal:
            self.prj_mode = OpenGLWin.Perspective
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glLoadIdentity()
            self.gl2_0.glFrustum(-self.width / 2, self.width / 2, -self.height / 2, self.height / 2, 500, 100000)
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            self.gl2_0.glLoadIdentity()
            self.camera.change_view(OpenGLWin.Perspective)
            self.paintGL()
            self.update()

    def __add_selected_objects_when_click(self):
        pos = self.select_end
        not_selecting_dots = True
        if not_selecting_dots:
            # 将屏幕坐标点转换为OpenGL坐标系中的坐标点
            _x, _y = pos.x(), self.height - pos.x() - 1
            # 使用拾取技术来确定被点击的三角形
            if self.prj_mode == OpenGLWin.Perspective:  # 如果是透视投影模式：
                glSelectBuffer(2 ** 20)
                glRenderMode(GL_SELECT)
                glInitNames()
                glPushName(0)
                self.gl2_0.glViewport(0, 0, self.width, self.height)
                self.gl2_0.glMatrixMode(GL_PROJECTION)
                self.gl2_0.glPushMatrix()
                self.gl2_0.glLoadIdentity()  # 重置矩阵
                gluPickMatrix(_x, _y, 1, 1, [0, 0, self.width, self.height])
                # 设置透视投影
                aspect_ratio = self.width / self.height
                gluPerspective(self.fovy, aspect_ratio, 0.1, 2000.0)  # 设置透视投影
                self.gl2_0.glMatrixMode(GL_MODELVIEW)
                self.paintGL()  # 重新渲染场景
                self.gl2_0.glMatrixMode(GL_PROJECTION)
                self.gl2_0.glPopMatrix()
                self.gl2_0.glMatrixMode(GL_MODELVIEW)
                hits = glRenderMode(GL_RENDER)
            else:  # 如果是正交投影模式：
                glSelectBuffer(2 ** 20)
                glRenderMode(GL_SELECT)
                glInitNames()
                glPushName(0)
                self.gl2_0.glViewport(0, 0, self.width, self.height)
                self.gl2_0.glMatrixMode(GL_PROJECTION)
                self.gl2_0.glPushMatrix()
                self.gl2_0.glLoadIdentity()
                gluPickMatrix(_x, _y, 1, 1, [0, 0, self.width, self.height])
                self.gl2_0.glOrtho(-self.width / 2, self.width / 2, -self.height / 2, self.height / 2, -1000, 1000)
                self.gl2_0.glMatrixMode(GL_MODELVIEW)
                self.paintGL()
                self.gl2_0.glMatrixMode(GL_PROJECTION)
                self.gl2_0.glPopMatrix()
                self.gl2_0.glMatrixMode(GL_MODELVIEW)
                hits = glRenderMode(GL_RENDER)
            # self.show_statu_func(f"{len(hits)}个零件被选中", "success")
            # 在hits中找到深度最小的零件
            # TODO: 给id_map赋值
            id_map = {}
            min_depth = 100000
            min_depth_part = None
            for hit in hits:
                _name = hit.names[0]
                if _name in id_map:
                    part = id_map[_name]
                    if hit.near < min_depth:
                        min_depth = hit.near
                        min_depth_part = part
            if min_depth_part:
                return min_depth_part
        else:  # 如果是节点模式，扩大选择范围
            min_x, max_x = pos.x() - 5, pos.x() + 5
            # 对y翻转
            min_y, max_y = self.height - pos.x() - 1 - 5, self.height - pos.x() - 1 + 5
            # 使用拾取技术来确定被点击的三角形
            glSelectBuffer(2 ** 20)
            glRenderMode(GL_SELECT)
            glInitNames()
            glPushName(0)
            self.gl2_0.glViewport(0, 0, self.width, self.height)
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glPushMatrix()
            self.gl2_0.glLoadIdentity()
            aspect_ratio = self.width / self.height
            # 设置选择框
            gluPickMatrix(
                (max_x + min_x) / 2, (max_y + min_y) / 2, max_x - min_x, max_y - min_y, [0, 0, self.width, self.height]
            )
            # 设置透视投影
            gluPerspective(self.fovy, aspect_ratio, 0.1, 2000.0)
            # 转换回模型视图矩阵
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            self.paintGL()
            # 恢复原来的矩阵
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glPopMatrix()
            # 转换回模型视图矩阵
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            # 获取选择框内的物体
            hits = glRenderMode(GL_RENDER)
            # id_map = self.selectObjOrigin_map[self.show_3d_obj_mode].id_map
            id_map = {}
            # TODO: 给id_map赋值
            for hit in hits:
                _name = hit.names[0]
                if _name in id_map:
                    part = id_map[_name]
                    return part

    def __add_selected_objects_of_selectBox(self):
        result = []
        if not (self.select_start and self.select_end):
            return result
        # 转化为OpenGL坐标系
        min_x = min(self.select_start.x(), self.select_end.x())
        max_x = max(self.select_start.x(), self.select_end.x())
        # 对y翻转
        min_y = min(self.height - self.select_start.x() - 1, self.height - self.select_end.x() - 1)
        max_y = max(self.height - self.select_start.x() - 1, self.height - self.select_end.x() - 1)
        if max_x - min_x < 3 or max_y - min_y < 3:  # 排除过小的选择框
            return result
        # 使用拾取技术来确定被点击的三角形
        if self.prj_mode == OpenGLWin.Perspective:  # 如果是透视投影模式：
            glSelectBuffer(2 ** 20)
            glRenderMode(GL_SELECT)
            glInitNames()
            glPushName(0)
            self.gl2_0.glViewport(0, 0, self.width, self.height)
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glPushMatrix()
            self.gl2_0.glLoadIdentity()  # 重置矩阵
            # 设置选择框
            gluPickMatrix(
                (max_x + min_x) / 2, (max_y + min_y) / 2, max_x - min_x, max_y - min_y, [0, 0, self.width, self.height]
            )
            # 设置透视投影
            aspect_ratio = self.width / self.height
            gluPerspective(self.fovy, aspect_ratio, 0.1, 2000.0)  # 设置透视投影
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            self.paintGL()  # 重新渲染场景
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glPopMatrix()
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            hits = glRenderMode(GL_RENDER)
        else:  # 如果是正交投影模式：
            glSelectBuffer(2 ** 20)
            glRenderMode(GL_SELECT)
            glInitNames()
            glPushName(1)
            self.gl2_0.glViewport(0, 0, self.width, self.height)
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glPushMatrix()
            self.gl2_0.glLoadIdentity()
            gluPickMatrix(
                (max_x + min_x) / 2, (max_y + min_y) / 2, max_x - min_x, max_y - min_y, [0, 0, self.width, self.height]
            )
            self.gl2_0.glOrtho(-self.width / 2, self.width / 2, -self.height / 2, self.height / 2, -1000, 1000)
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            self.paintGL()
            self.gl2_0.glMatrixMode(GL_PROJECTION)
            self.gl2_0.glPopMatrix()
            self.gl2_0.glMatrixMode(GL_MODELVIEW)
            hits = glRenderMode(GL_RENDER)
        id_map = {}
        # TODO: 给id_map赋值
        for hit in hits:
            _name = hit.names[0]
            if _name in id_map:
                part = id_map[_name]
                if part not in result:
                    result.append(part)
        return result

    @staticmethod
    def get_matrix():
        """
        获取当前的坐标变换矩阵
        :return:
        """
        matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        matrix = np.array(matrix).reshape(4, 4)
        return matrix

    # ----------------------------------------------------------------------------------------------事件

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # a键摄像机目标回（0, 0, 0）
        if event.key() == Qt.Key_A:
            self.camera.change_target(QVector3D(0, 0, 0))
            self.update()
        # ====================================================================================Alt键
        if QApplication.keyboardModifiers() == Qt.AltModifier:
            if event.key() not in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
                return
            # 获取当前被选中的物体
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.AltModifier:  # Alt按下的时候，不移动视角
            return
        elif event.angleDelta().y() > 0:
            self.camera.zoom(-0.11)
        else:
            self.camera.zoom(0.11)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.AltModifier:  # Alt按下的时候，不移动视角
            return
        elif event.button() == Qt.LeftButton:  # 左键按下
            self.select_start = event.pos()
            self.lastPos = event.pos()
            self.drawObjHandler.start_all_genlist()
            # 判断是否按下shift，如果没有按下，就清空选中列表
            if QApplication.keyboardModifiers() != Qt.ShiftModifier:
                ...
            else:
                self.lastPos = event.pos()
        elif event.button() == Qt.RightButton:  # 右键按下
            self.rotate_start = event.pos()
            self.lastPos = event.pos()
        elif event.button() == Qt.MidButton:  # 中键按下
            self.lastPos = event.pos()
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.AltModifier:  # Alt按下的时候，不移动视角
            return
        if event.buttons() == Qt.LeftButton:  # 左键绘制选择框
            self.select_end = event.pos()
            self.lastPos = event.pos()
            self.paintGL()
        elif event.buttons() == Qt.RightButton or event.buttons() == Qt.MidButton:  # 右键或中键旋转
            # 如果鼠标到达屏幕边缘，光标位置就移动到另一侧
            if event.x() < 0:
                QCursor.setPos(self.mapToGlobal(QPoint(self.width - 1, event.y())))
                self.lastPos = QPoint(self.width - event.x(), event.y())
            elif event.x() > self.width - 1:
                QCursor.setPos(self.mapToGlobal(QPoint(0, event.y())))
                self.lastPos = QPoint(self.width - event.x(), event.y())
            elif event.y() < 0:
                QCursor.setPos(self.mapToGlobal(QPoint(event.x(), self.height - 1)))
                self.lastPos = QPoint(event.x(), self.height - event.y())
            elif event.y() > self.height - 1:
                QCursor.setPos(self.mapToGlobal(QPoint(event.x(), 0)))
                self.lastPos = QPoint(event.x(), self.height - event.y())
            elif event.buttons() == Qt.MidButton:  # 中键平移
                dx = event.x() - self.lastPos.x()
                dy = event.y() - self.lastPos.y()
                self.camera.translate(dx, dy)
                self.lastPos = event.pos()
            elif event.buttons() == Qt.RightButton:  # 右键旋转
                dx = event.x() - self.lastPos.x()
                dy = event.y() - self.lastPos.y()
                self.camera.rotate(dx, dy)
                self.lastPos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if QApplication.keyboardModifiers() == Qt.AltModifier:  # Alt按下的时候，不移动视角
            return
        elif event.button() == Qt.LeftButton:  # 左键释放
            self.drawObjHandler.stop_all_using_genlist()
            self.select_end = event.pos()
            # if self.select_start and self.select_end:
            if abs(event.x() - self.select_start.x()) < 3 and abs(event.y() - self.select_start.x()) < 3:
                # 作为单击事件处理，调用click拾取函数
                _p = self.__add_selected_objects_when_click()
                add_list = [_p] if _p is not None else []
            else:
                # 往选中列表中添加选中的物体
                add_list = self.__add_selected_objects_of_selectBox()
            for add_obj in add_list:
                ...
            self.select_start = None
            self.select_end = None
            self.update()

    def __set_camera(self):
        gluLookAt(self.camera.pos.x(), self.camera.pos.y(), self.camera.pos.z(),
                  self.camera.tar.x(), self.camera.tar.y(), self.camera.tar.z(),
                  self.camera.up.x(), self.camera.up.y(), self.camera.up.z())

    def __init_gl(self) -> None:
        version_profile2_0 = QOpenGLVersionProfile()
        version_profile2_0.setVersion(2, 0)
        self.gl2_0 = self.context().versionFunctions(version_profile2_0)
        self.__init_view()  # 初始化视角
        self.__init_light()  # 初始化光源
        self.__init_render()  # 初始化渲染模式

    def __init_light(self):
        # 添加光源
        self.gl2_0.glEnable(self.gl2_0.GL_LIGHTING)
        self.gl2_0.glEnable(self.gl2_0.GL_LIGHT0)
        # 主光源
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_POSITION, (
            self.light_pos.x(), self.light_pos.y(), self.light_pos.z(),  # 光源位置
            100.0))
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_AMBIENT, self.theme_color["主光源"][0])  # 设置环境光
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_DIFFUSE, self.theme_color["主光源"][1])  # 设置漫反射光
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_SPECULAR, self.theme_color["主光源"][2])  # 设置镜面光
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_SPOT_DIRECTION, (0.0, 0.0, 0.0))  # 设置聚光方向
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_SPOT_EXPONENT, (0.0,))  # 设置聚光指数
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_SPOT_CUTOFF, (180.0,))  # 设置聚光角度
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT0, self.gl2_0.GL_QUADRATIC_ATTENUATION, (0.0,))  # 设置二次衰减
        # 辅助光源
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_POSITION, (
            self.light_pos.x(), self.light_pos.y(), self.light_pos.z(),  # 光源位置
            100.0))
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_AMBIENT, self.theme_color["辅助光"][0])  # 设置环境光
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_DIFFUSE, self.theme_color["辅助光"][1])  # 设置漫反射光
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_SPECULAR, self.theme_color["辅助光"][1])  # 设置镜面光
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_SPOT_DIRECTION, (0.0, 0.0, 0.0))  # 设置聚光方向
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_SPOT_EXPONENT, (0.0,))  # 设置聚光指数
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_SPOT_CUTOFF, (180.0,))  # 设置聚光角度
        self.gl2_0.glLightfv(self.gl2_0.GL_LIGHT1, self.gl2_0.GL_QUADRATIC_ATTENUATION, (0.0,))  # 设置二次衰减

    def __init_view(self):
        # 适应窗口大小
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = self.width / self.height
        gluPerspective(self.fovy, aspect_ratio, 0.1, 2000.0)  # 设置透视投影
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def __init_render(self):
        glShadeModel(GL_SMOOTH)  # 设置阴影平滑模式
        glClearDepth(1.0)  # 设置深度缓存
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        # 设置深度缓冲为32位
        _f = QSurfaceFormat()
        _f.setDepthBufferSize(32)
        self.setFormat(_f)
        glDepthFunc(GL_LEQUAL)  # 所作深度测试的类型
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  # 告诉系统对透视进行修正
        glEnable(GL_NORMALIZE)  # 启用法向量规范化
        glEnable(GL_AUTO_NORMAL)  # 启用自动法向量
        glEnable(GL_BLEND)  # 启用混合
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # 设置混合因子
        # 平滑
        glEnable(GL_POINT_SMOOTH)  # 启用点平滑
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)  # 设置点平滑提示
        glEnable(GL_LINE_SMOOTH)  # 启用线条平滑
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)  # 设置线条平滑提示
        # glEnable(GL_POLYGON_SMOOTH)  # 启用多边形平滑
        # glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)  # 设置多边形平滑提示
        # 抗锯齿
        glEnable(GL_MULTISAMPLE)  # 启用多重采样
        glEnable(GL_SAMPLE_ALPHA_TO_COVERAGE)  # 启用alpha值对多重采样的影响
        glSampleCoverage(1, GL_TRUE)  # 设置多重采样的抗锯齿比例
        # 线性差值
        glEnable(GL_TEXTURE_2D)  # 启用纹理
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  # 设置纹理映射的透视修正
        glHint(GL_TEXTURE_COMPRESSION_HINT, GL_NICEST)  # 设置纹理压缩提示
        glHint(GL_FRAGMENT_SHADER_DERIVATIVE_HINT, GL_NICEST)  # 设置片段着色器的提示
        #
        glEnable(GL_COLOR_MATERIAL)  # 启用颜色材质
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)  # 设置颜色材质的面和材质
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.5, 0.5, 0.5, 0.5))  # 设置环境光反射光
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.5, 0.5, 0.5, 0.5))  # 设置漫反射光
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 0.5))  # 设置镜面反射光
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, (10.0,))  # 设置镜面反射指数
        #
        # 背面剔除
        glEnable(GL_CULL_FACE)  # 启用背面剔除
        glCullFace(GL_BACK)  # 剔除背面
        glFrontFace(GL_CCW)  # 设置逆时针为正面
        glPolygonOffset(1, 1)  # 设置多边形偏移
