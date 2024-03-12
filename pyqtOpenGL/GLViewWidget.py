# -*- coding: utf-8 -*-
"""
This module provides a widget for displaying 3D data.
"""
import warnings
import traceback
import sys

import time
from ctypes import c_float, c_void_p

import numpy as np
from GUI import TextLabel
from OpenGL.GL import *  # noqa
import OpenGL.GL as gl
from math import radians, tan
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QPoint
from pyqtOpenGL.items.GL2DSelectBox import GL2DSelectBox

from .camera import Camera
from .functions import mkColor
from .transform3d import Vector3, Matrix4x4
from typing import List, Set, Union
from .GLGraphicsItem import GLGraphicsItem
from .items.light import PointLight
from .items.shader import Shader
from .items.BufferObject import VAO, VBO, EBO


class GLViewWidget(QtWidgets.QOpenGLWidget):
    gl_initialized = pyqtSignal()

    def __init__(
            self,
            cam_position=Vector3(10., 10., 10.),
            cam_tar=Vector3(0., 0., 0.),
            cam_sensitivity=None,
            fov=45.,
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
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        # self.camera = Camera2(cam_position, 0., 0., 0., fov, cam_sensitivity)  # TODO:
        self.camera = Camera(cam_position, cam_tar, fov=fov, sensitivity=cam_sensitivity)
        self.mouse_last_pos = None  # used for mouse move event
        self.pan_btn = pan_btn
        self.orbit_btn = orbit_btn

        # select box
        self.select_btn = select_btn
        self.select_start: Union[QPoint, None] = None
        self.select_end: Union[QPoint, None] = None
        self.select_box = GL2DSelectBox()

        # 被绘制的物体
        self.bg_color = bg_color
        self.items: List[GLGraphicsItem] = []
        self.lights: Set[PointLight] = set()

        # 显示帧率
        self.fps_label = TextLabel(self, "")
        self.__last_time = time.time()

        # 设置多重采样抗锯齿
        _format = QtGui.QSurfaceFormat()
        _format.setSamples(4)
        self.setFormat(_format)

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

    def addItem(self, item: GLGraphicsItem):
        self.items.append(item)
        item.setView(self)
        if hasattr(item, 'lights'):
            self.lights |= set(item.lights)
        self.items.sort(key=lambda a: a.depthValue())
        self.update()

    def addItems(self, items: List[GLGraphicsItem]):
        for item in items:
            self.addItem(item)

    def removeItem(self, item):
        """
        Remove the item from the scene.
        """
        self.items.remove(item)
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
        return (0, 0, self.deviceWidth(), self.deviceHeight())

    def initializeGL(self):
        """initialize OpenGL state after creating the GL context."""
        PointLight.initializeGL()
        self.select_box.initializeGL()

    def paintGL(self):
        """
        viewport specifies the arguments to glViewport. If None, then we use self.opts['viewport']
        region specifies the sub-region of self.opts['viewport'] that should be rendered.
        Note that we may use viewport != self.opts['viewport'] when exporting.
        """

        glClearColor(*self.bg_color)
        glDepthMask(GL_TRUE)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        self.drawItems()
        # 选择框
        if self.select_start and self.select_end:
            self.select_box.paint(self.camera.get_view_matrix(), self.select_start, self.select_end)
        self.__update_FPS()

    def __update_FPS(self):
        if time.time() - self.__last_time != 0:
            self.fps_label.setText(f"FPS: {round(1 / (time.time() - self.__last_time), 1)}")
        self.__last_time = time.time()

    def drawItems(self):
        for it in self.items:
            try:
                it.drawItemTree()
            except Exception as e:  # noqa
                printExc()
                print("Error while drawing item %s." % str(it))

        # draw lights
        for light in self.lights:
            light.paint(self.get_proj_view_matrix())

    def pixelSize(self, pos=Vector3(0, 0, 0)):
        """
        depth: z-value in global coordinate system
        Return the approximate (y) size of a screen pixel at the location pos
        Pos may be a Vector or an (N,3) array of locations
        """
        pos = self.get_view_matrix() * pos  # convert to view coordinates
        fov = self.camera.fov
        return max(-pos[2], 0) * 2. * tan(0.5 * radians(fov)) / self.deviceHeight()

    def mousePressEvent(self, ev):
        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        self.mouse_last_pos = lpos
        if ev.buttons() == self.select_btn:
            self.select_start = QPoint(int(ev.localPos().x()), int(ev.localPos().y()))

    def mouseMoveEvent(self, ev):
        ctrl_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
        shift_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier)
        alt_down = (ev.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier)

        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        diff = lpos - self.mouse_last_pos
        self.mouse_last_pos = lpos

        if alt_down:
            # 不进行视角变换
            return

        if ctrl_down:
            # 视角微调
            diff *= 0.1

        if shift_down:
            # 限制移动方向
            if abs(diff.x()) > abs(diff.y()):
                diff.setY(0)
            else:
                diff.setX(0)

        if ev.buttons() == self.pan_btn:
            self.camera.pan(diff.x(), diff.y())
        elif ev.buttons() == self.orbit_btn:
            if alt_down:
                self.camera.orbit(diff.x(), diff.y())
            elif not alt_down:
                self.camera.orbit(diff.x(), diff.y())
        elif ev.buttons() == self.select_btn:
            self.select_end = QPoint(int(ev.localPos().x()), int(ev.localPos().y()))
        self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == self.select_btn:
            self.select_start = None
            self.select_end = None
            self.update()

    def wheelEvent(self, ev):
        delta = ev.angleDelta().x()
        if delta == 0:
            delta = ev.angleDelta().y()
        if ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:  # 按下ctrl键
            self.camera.zoom(delta * 0.1)
        else:
            self.camera.zoom(delta)
        self.update()

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

    def keyPressEvent(self, a0) -> None:
        """按键处理"""
        if a0.text() == '1':
            pos, euler = self.camera.get_params()
            print(f"pos: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})  "
                  f"euler: ({euler[0]:.2f}, {euler[1]:.2f}, {euler[2]:.2f})")


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


def getExc(indent=4, prefix='|  ', skip=1):
    lines = formatException(*sys.exc_info(), skip=skip)
    lines2 = []
    for line in lines:
        lines2.extend(line.strip('\n').split('\n'))
    lines3 = [" " * indent + prefix + line for line in lines2]
    return '\n'.join(lines3)


def printExc(msg='', indent=4, prefix='|'):
    """Print an error message followed by an indented exception backtrace
    (This function is intended to be called within except: blocks)"""
    exc = getExc(indent=0, prefix="", skip=2)
    # print(" "*indent + prefix + '='*30 + '>>')
    warnings.warn("\n".join([msg, exc]), RuntimeWarning, stacklevel=2)
    # print(" "*indent + prefix + '='*30 + '<<')
