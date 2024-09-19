# -*- coding: utf-8 -*-
"""
This module provides a widget for displaying 3D data.
"""
import sys
import time
import traceback
import warnings
from math import radians, tan
from typing import List, Set, Literal, Optional

import OpenGL.GL as gl
import numpy as np
import numpy.core._exceptions as np_core_exc  # noqa
from GUI import TextLabel, WIN_WID, WIN_HEI
from OpenGL.GL import *  # noqa
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QPoint, QMutex
from PyQt5.QtGui import QPainter, QColor, QCursor
from PyQt5.QtWidgets import QMessageBox
from main_logger import Log
from pyqtOpenGL.items.GL2DSelectBox import GLSelectBox

from .GLGraphicsItem import GLGraphicsItem, PickColorManager
from .camera import Camera
from .functions import mkColor
from .items.light import PointLight
from .transform3d import Vector3

__TAG = "GLViewWidget"


def _drawItemTree(item):
    try:
        item.drawItemTree()
    except np_core_exc._ArrayMemoryError as _:  # noqa
        QMessageBox().warning(None, "严重错误", "申请内存错误，程序即将退出")
        Log().error(traceback.format_exc(), __TAG, "申请内存错误，程序即将退出")
        sys.exit(1)
    except Exception as e:  # noqa
        printExc()
        Log().error(traceback.format_exc(), __TAG, "Error while drawing item %s." % str(item))


class GLViewWidget(QtWidgets.QOpenGLWidget):
    TAG = "GLViewWidget"
    gl_initialized = pyqtSignal()

    # 剪贴板
    clipboard = []

    def selectAll(self):
        self.selected_items.clear()
        for item in self.items:
            if item.setSelected(True):
                self.selected_items.append(item)
        self._after_selection()

    def copy(self):
        GLViewWidget.clipboard = self.selected_items.copy()

    def cut(self):
        self.copy()
        self.delete_selected()

    def delete_selected(self):
        prj = self.selected_items[0].handler.prj
        for item in self.selected_items:
            self.removeItem(item)
            prj.del_section(item.handler)
        self.selected_items.clear()
        self.paintGL_outside()

    def __init__(
            self,
            cam_position=Vector3(-10., 10., 10.),
            cam_tar=Vector3(0., 0., 0.),
            cam_sensitivity=None,
            fov=45.,
            left_hand=True,
            bg_color=(0.1, 0.1, 0.1, 1.),  # 背景颜色
            parent=None,
            select_btn=QtCore.Qt.MouseButton.LeftButton,
            pan_btn=QtCore.Qt.MouseButton.MiddleButton,
            orbit_btn=QtCore.Qt.MouseButton.RightButton,
    ):
        """
        Basic widget for displaying 3D data
          - Rotation/scale controls
        """
        QtWidgets.QOpenGLWidget.__init__(self, parent)
        self.event_mutex = QMutex()
        self._paint_enabled = True  # 作为刷新的开关
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.setStatusTip("3D View")
        self.camera = Camera(cam_position, cam_tar, fov=fov, left_hand=left_hand, sensitivity=cam_sensitivity)
        self.mouse_last_pos = None  # used for mouse move event
        self.shift_movePos = 0  # 限制移动方向，0为无，1为x轴，2为y轴
        self.pan_btn = pan_btn
        self.orbit_btn = orbit_btn

        # 选择框
        self.select_btn = select_btn
        self.select_start = QPoint()
        self.select_end = QPoint()
        self.select_flag = False
        self.select_box = GLSelectBox()
        self.select_box.setView(self)
        self.selected_items = []  # 用于管理物体的选中状态

        # 被绘制的物体
        self.bg_color = bg_color
        self.items: List[GLGraphicsItem] = []
        self.lights: Set[PointLight] = set()

        # 显示帧率
        self.fps_label = TextLabel(self, "")
        self.__last_time = time.time()

        # 设置多重采样抗锯齿
        _format = QtGui.QSurfaceFormat()
        _format.setSamples(9)
        self.setFormat(_format)
        # 加速渲染
        self.setAutoFillBackground(True)
        # self.setUpdateBehavior(QOpenGLWidget.DoubleBuffer)
        self.frameSwapped.connect(self.parent().update) if self.parent() else None  # noqa

        # 绑定信号
        self._bind_signals()

    def _bind_signals(self):
        self.camera.update_gl_widget_s.connect(self.update)
        self.camera.end_animation_s.connect(self.update)

    def set_proj_mode(self, proj_mode: Literal['ortho', 'perspective']):
        self.camera.set_proj_mode(proj_mode)

    def get_proj_view_matrix(self):
        return self.camera.get_proj_view_matrix(
            self.deviceWidth(),
            self.deviceHeight()
        )

    def get_proj_matrix(self):
        return self.camera.get_projection_matrix(
            self.deviceWidth(),
            self.deviceHeight()
        )

    def get_view_matrix(self):
        return self.camera.get_view_matrix()

    def deviceWidth(self):
        dpr = self.devicePixelRatioF()
        return int(self.width() * dpr)

    def deviceHeight(self):
        dpr = self.devicePixelRatioF()
        return int(self.height() * dpr)

    def deviceRatio(self):
        return self.height() / self.width()

    def reset(self):
        self.camera.set_params(Vector3(0., 0., 10.), Vector3(0., 0., 0.), fov=45.)

    def addItem(self, item: GLGraphicsItem, add_light=False):
        self.items.append(item)
        item.setView(self)
        if hasattr(item, 'lights'):
            if not item.lights:
                if hasattr(item, 'addLight') and add_light:
                    item.addLight(self.lights)
        self.items.sort(key=lambda a: a.depthValue())
        self.update()

    def addItems(self, items: List[GLGraphicsItem]):
        for item in items:
            self.addItem(item)

    def removeItem(self, item: GLGraphicsItem, del_light=True):
        """
        Remove the item from the scene.
        Please make sure the item is in the scene before calling this function.
        """
        self.items.remove(item)
        if item.selected():
            item.setSelected(False)
            self.selected_items.remove(item)
        if hasattr(item, 'lights') and del_light:
            for l_ in self.lights:
                if l_ in item.lights:
                    item.lights.remove(l_)
        item.setView(None)
        self.update()

    def clear(self):
        """
        Remove all items from the scene.
        """
        for item in self.items:
            item.setView(None)
        self.items = []
        self.update()

    def setBackgroundColor(self, *args, **kwds):
        """
        Set the background color of the widget. Accepts the same arguments as
        :func:`~pyqtgraph.mkColor`.
        """
        self.bg_color = mkColor(*args, **kwds).getRgbF()
        self.update()

    def getViewport(self):
        return 0, 0, self.deviceWidth(), self.deviceHeight()

    def initializeGL(self):
        """initialize OpenGL state after creating the GL context."""
        PointLight.initializeGL()
        self._createFramebuffer(WIN_WID, WIN_HEI)
        self.select_box.initializeGL()
        gl.glEnable(GL_MULTISAMPLE)
        gl.glEnable(GL_DEPTH_TEST)

    def enablePaint(self, enable: bool):
        self._paint_enabled = enable

    def paintGL(self):
        """
        viewport specifies the arguments to glViewport. If None, then we use self.opts['viewport']
        region specifies the sub-region of self.opts['viewport'] that should be rendered.
        Note that we may use viewport != self.opts['viewport'] when exporting.
        """
        if not self._paint_enabled:
            return
        glClearColor(*self.bg_color)
        glDepthMask(GL_TRUE)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        if self.select_box.visible():
            self.drawItems(pickMode=False, update=False)
            self.select_box.updateGL(self.select_start, self.select_end)
            self.select_box.paint()
            # self.painter.setPen(QColor(255, 255, 255))
            # self.painter.drawRect(self.select_start.x(), self.select_start.y(),
            #                       self.select_end.x() - self.select_start.x(),
            #                       self.select_end.y() - self.select_start.y())
        else:
            self.drawItems(pickMode=False)
        self.__update_FPS()

    def resizeGL(self, w, h):
        """
        Update the viewport and projection matrix.
        """
        glViewport(0, 0, w, h)

    def _createFramebuffer(self, width, height):
        """
        创建帧缓冲区, 用于拾取
        Create a framebuffer for picking
        """
        self.__framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.__framebuffer)
        self.__texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.__texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, width, height, 0, GL_RED, GL_FLOAT, None)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.__texture, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def _resizeFramebuffer(self, width, height):
        glBindFramebuffer(GL_FRAMEBUFFER, self.__framebuffer)
        glBindTexture(GL_TEXTURE_2D, self.__texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, width, height, 0, GL_RED, GL_FLOAT, None)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def pickItems(self, x_, y_, w_, h_):
        ratio = 2  # 为了提高渲染和拾取速度，暂将渲染视口缩小4倍
        x_, y_, w_, h_ = self._normalizeRect(x_, y_, w_, h_, ratio)
        glBindFramebuffer(GL_FRAMEBUFFER, self.__framebuffer)
        glViewport(0, 0, self.deviceWidth() // ratio, self.deviceHeight() // ratio)
        glClearColor(0, 0, 0, 0)
        glDisable(GL_MULTISAMPLE)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        # 设置拾取区域
        glScissor(x_, self.deviceHeight() // ratio - y_ - h_, w_, h_)
        glEnable(GL_SCISSOR_TEST)
        # 在这里设置额外的拾取参数，例如鼠标位置等
        self.drawItems(pickMode=True)
        glDisable(GL_SCISSOR_TEST)
        pixels = glReadPixels(x_, self.deviceHeight() // ratio - y_ - h_, w_, h_, GL_RED, GL_FLOAT)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClearColor(*self.bg_color)
        glEnable(GL_MULTISAMPLE)
        glViewport(0, 0, self.deviceWidth(), self.deviceHeight())
        # 获取拾取到的物体
        pick_data = np.frombuffer(pixels, dtype=np.float32)
        # # 保存为图片
        # img_data = np.frombuffer(pixels, dtype=np.float32).reshape(h_, w_)
        # # 将单通道数据转为三通道灰色图像
        # img_data = np.stack([img_data, img_data, img_data], axis=2)
        # img_data = (img_data * 255).astype(np.uint8)
        # img_data = np.flipud(img_data)
        # import PIL.Image as Image
        # img = Image.fromarray(img_data)
        # img.save('pick.png')
        # 去掉所有为0.0的数据
        pick_data = pick_data[pick_data != 0.0]
        # 获取选中的物体
        selected_items = []
        id_set = list()
        for id_ in pick_data:
            if id_ in id_set:
                continue
            item: GLGraphicsItem = PickColorManager().get(id_)
            if item:
                selected_items.append(item)
            id_set.append(id_)
        return selected_items

    def renderToImage(self, path):
        self.makeCurrent()
        self.grabFramebuffer().save(path)
        self.doneCurrent()

    def _normalizeRect(self, x_, y, w, h, ratio: int = 3):
        """
        防止拾取区域超出窗口范围
        :param x_: 拾取区域左下角的x坐标
        :param y: 拾取区域左下角的y坐标
        :param w: 拾取区域的宽度
        :param h: 拾取区域的高度
        :param ratio: 值越大，拾取区域越小
        :return:
        """
        if ratio > 5:
            ratio = 5
            Log().warning(self.TAG, "ratio should be less than 5")
        # 防止拾取区域超出窗口范围
        if w < 0:
            x_, w = max(0, x_ + w), -w
        if h < 0:
            y, h = max(0, y + h), -h
        if x_ + w > self.deviceWidth():
            w = self.deviceWidth() - x_
        if y + h > self.deviceHeight():
            h = self.deviceHeight() - y
        x_, y, w, h = x_ // ratio, y // ratio, w // ratio, h // ratio

        # 防止拾取区域过小
        if w <= 6 // ratio:
            x_ = max(0, x_ - 1)
            w = 3 // ratio
        if h <= 6 // ratio:
            y = max(0, y - 1)
            h = 3 // ratio

        return x_, y, w, h

    def paintGL_outside(self):
        """
        在外部调用paintGL
        """
        self.makeCurrent()
        self.paintGL()
        self.doneCurrent()
        self.update()

    def __update_FPS(self):
        dt = time.time() - self.__last_time
        if dt != 0:
            self.fps_label.setText(f"FPS: {1 / dt:.1f}")
        self.__last_time = time.time()

    def drawItems(self, pickMode=False, update=True):
        if pickMode:  # 拾取模式
            for it in self.items:
                # try:
                it.drawItemTree_pickMode()
                # except np_core_exc._ArrayMemoryError as _:  # noqa
                #     QMessageBox().warning(None, "严重错误", "申请内存错误，程序即将退出")
                #     Log().error(traceback.format_exc(), self.TAG, "申请内存错误，程序即将退出")
                #     sys.exit(1)
                # except Exception as e:  # noqa
                #     printExc()
                #     Log().error(traceback.format_exc(), self.TAG, "Error while drawing item %s in pick mode." % str(it))
        else:
            for it in self.items:
                # _drawItemTree(it)
                it.drawItemTree()
            # # draw lights
            # for light in self.lights:
            #     light.paint(self.get_proj_view_matrix())

    def get_selected_item(self):
        """
        得到选中的物体，不改变物体的选中状态，不添加到self.selected_items中
        """
        self.makeCurrent()
        size = self.select_end - self.select_start
        selected_items = self.pickItems(self.select_start.x(), self.select_start.y(), size.x(), size.y())
        self.paintGL()
        self.doneCurrent()
        self.update()
        return selected_items

    def pixelSize(self, pos=Vector3(0, 0, 0)):
        """
        depth: z-value in global coordinate system
        Return the approximate (y) size of a screen pixel at the location pos
        Pos may be a Vector or an (N,3) array of locations
        """
        pos = self.get_view_matrix() * pos  # convert to view coordinates
        fov = self.camera.fov
        return max(-pos[2], 0) * 2. * tan(0.5 * radians(fov)) / self.deviceHeight()

    def __mouseMove_otherside(self, lastpos):
        """
        如果鼠标到达屏幕边缘，光标位置就移动到另一侧
        :param lastpos: 鼠标位置
        :return:
        """
        if lastpos.x() < 0:
            QCursor.setPos(self.mapToGlobal(QPoint(self.deviceWidth() - 1, int(lastpos.y()))))
            self.mouse_last_pos = QPoint(self.deviceWidth() - 1, int(lastpos.y()))
        elif lastpos.x() > self.deviceWidth() - 1:
            QCursor.setPos(self.mapToGlobal(QPoint(0, int(lastpos.y()))))
            self.mouse_last_pos = QPoint(0, int(lastpos.y()))
        elif lastpos.y() < 0:
            QCursor.setPos(self.mapToGlobal(QPoint(int(lastpos.x()), self.deviceHeight() - 1)))
            self.mouse_last_pos = QPoint(int(lastpos.x()), self.deviceHeight() - 1)
        elif lastpos.y() > self.deviceHeight() - 1:
            QCursor.setPos(self.mapToGlobal(QPoint(int(lastpos.x()), 0)))
            self.mouse_last_pos = QPoint(int(lastpos.x()), 0)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        elif event.type() == QtCore.QEvent.Type.MouseMove:
            # 鼠标移动事件不传递给父控件，直接处理
            self.mouseMoveEvent(event)
            return True
        elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            self.mouseReleaseEvent(event)
            return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, ev):
        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        self.mouse_last_pos = lpos
        if ev.buttons() == self.select_btn:
            self.select_start.setX(int(ev.localPos().x()))
            self.select_start.setY(int(ev.localPos().y()))
            self.paintGL_outside()

    def mouseMoveEvent(self, ev):
        ctrl_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
        shift_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier)
        alt_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier)

        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        diff = lpos - self.mouse_last_pos
        self.mouse_last_pos = lpos

        if ctrl_down:
            # 视角微调
            diff *= 0.1
        if shift_down:
            if self.shift_movePos == 1:
                diff.setY(0)
            elif self.shift_movePos == 2:
                diff.setX(0)
        else:
            self.shift_movePos = 0

        if ev.buttons() == self.pan_btn:
            self.__mouseMove_otherside(lpos)
            if not alt_down:
                self.camera.pan(diff.x(), diff.y())
            self.paintGL_outside()
        elif ev.buttons() == self.orbit_btn:
            self.__mouseMove_otherside(lpos)
            if not alt_down:
                self.camera.orbit(diff.x(), diff.y())
            self.paintGL_outside()
        elif ev.buttons() == self.select_btn:
            self.select_end.setX(int(ev.localPos().x()))
            self.select_end.setY(int(ev.localPos().y()))
            if not self.select_box.visible():
                self.select_box.setVisible(True)
            self.paintGL_outside()

    def mouseReleaseEvent(self, ev):
        ctl_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
        alt_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier)
        self.select_end.setX(int(ev.localPos().x()))
        self.select_end.setY(int(ev.localPos().y()))
        if ev.button() == self.select_btn:
            self.select_box.setVisible(False)
            new_s_items = self.get_selected_item()  # 此函数仅用于获取选中的物体，不改变物体的选中状态
            # 没有选中的物体，处理后直接返回
            if not new_s_items:
                if ctl_down:  # 如果按下ctrl键，不清空选中的物体
                    self.update()
                # 如果不按下ctrl键，清空选中的物体
                self._clear_selected_items()
            # 有选中的物体：
            # 如果不按下ctrl键，取两集合的交集的补集（即从选中的物体中去掉已经选中的物体）
            if not ctl_down:
                for it in self.selected_items:
                    it.setSelected(False)
                self.selected_items.clear()
                for it in new_s_items:
                    selectable = it.setSelected(True)
                    if selectable:
                        self.selected_items.append(it)
            # 如果按下ctrl键，取两集合相加
            else:
                for it in new_s_items:
                    if it not in self.selected_items:
                        selectable = it.setSelected(True)
                        if selectable:
                            self.selected_items.append(it)
            self._after_selection()
        elif ev.button() == QtCore.Qt.MouseButton.RightButton and alt_down:
            self._rightButtonReleased(ev)
        self.paintGL_outside()

    def _rightButtonReleased(self, ev):
        ...

    def wheelEvent(self, ev):
        self.event_mutex.lock()
        alt_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier)
        delta = ev.angleDelta().y()
        delta = 1 if delta > 0 else -1
        if not alt_down:
            if ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:  # 按下ctrl键
                self.camera.zoom(delta * 0.1)
            else:
                self.camera.zoom(delta)
            self.paintGL_outside()
        self.event_mutex.unlock()

    def _clear_selected_items(self):
        for it in self.selected_items:
            it.setSelected(False)
        self.selected_items.clear()
        self.paintGL_outside()

    def _after_selection(self):
        """
        选中物体后的处理
        :return:
        """
        self.paintGL_outside()

    def readQImage(self):
        """
        Read the current buffer pixels out as a QImage.
        """
        return self.grabFramebuffer()

    def isCurrent(self):
        """
        Return True if this GLWidget's context is current.
        """
        return self.context() == QtGui.QOpenGLContext.currentContext()

    def close(self):
        super().close()


def formatException(exctype, value, tb, skip=0):
    """Return a list of formatted exception strings.

    Similar to traceback.format_exception, but displays the entire stack trace
    rather than just the portion downstream of the point where the exception is
    caught. In particular, unhandled exceptions that occur during Qt signal
    handling do not usually show the portion of the stack that emitted the
    signal.
    """
    lines = traceback.format_exception(exctype, value, tb)
    lines = [lines[0]] + traceback.format_stack()[:-(skip + 1)] + ['  --- exception caught here ---\n'] + lines[1:]
    return lines


def getExc(indent=4, prefix='  ', skip=1):
    lines = formatException(*sys.exc_info(), skip=skip)
    lines2 = []
    for line in lines:
        lines2.extend(line.strip('\n').split('\n'))
    lines3 = [" " * indent + prefix + line for line in lines2]
    return '\n'.join(lines3)


def printExc(msg='', indent=0, prefix='|'):
    """Print an error message followed by an indented exception backtrace
    (This function is intended to be called within except: blocks)"""
    exc = getExc(indent=indent, prefix=prefix, skip=2)
    # print(" "*indent + prefix + '='*30 + '>>')
    warnings.warn("\n".join([msg, exc]), RuntimeWarning, stacklevel=2)
    # print(" "*indent + prefix + '='*30 + '<<')
