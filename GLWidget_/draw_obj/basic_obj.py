# -*- coding: utf-8 -*-
"""
基础绘制物体
"""
from abc import abstractmethod
from typing import List, Union

from ..glwidget import OpenGLWin


class BasicDrawObj:
    def __init__(self, gl_widget: OpenGLWin,
                 pos: Union[List[float], None] = None,
                 rot: Union[List[float], None] = None,
                 scl: Union[List[float], None] = None
                 ):
        if pos is None:
            pos = [0., 0., 0.]
        if rot is None:
            rot = [0., 0., 0.]
        if scl is None:
            scl = [1., 1., 1.]
        self.GLWidget = gl_widget
        self.Pos = pos
        self.Rot = rot
        self.Scl = scl

    @abstractmethod
    def draw(self, *args, **kwargs):
        pass


class LineGroupObject(BasicDrawObj):
    id_map = {}

    def __init__(self, gl_widget: OpenGLWin,
                 pos: Union[List[float], None] = None,
                 rot: Union[List[float], None] = None,
                 scl: Union[List[float], None] = None
                 ):
        self.lines = {
            # 序号: [颜色List(rgba), 线宽float, 点集List[List[float]]]
        }
        super().__init__(gl_widget, pos, rot, scl)
        LineGroupObject.id_map[id(self) % 4294967296] = self

    def add_line(self, line_num: int, color: List[float], line_width: float,
                 dots: List[List[float]]):
        self.lines[line_num] = [color, line_width, dots]

    # noinspection PyUnusedLocal
    def draw(self):
        gl = self.GLWidget.gl2_0
        gl.glLoadName(id(self) % 4294967296)
        for num, line in self.lines.items():
            gl.glLineWidth(line[1])
            gl.glColor4f(*line[0])
            gl.glBegin(gl.GL_LINE_STRIP)
            for dot in line[2]:
                gl.glNormal3f(0, 1, 0)
                gl.glVertex3f(*dot)
            gl.glEnd()


class GridLine(LineGroupObject):
    def __init__(self, gl_widget: OpenGLWin, num=50, scale=10, normal=(0, 1, 0), central=(0.0, 0.0, 0.0),
                 color=(0.4, 0.6, 0.7, 1)):
        self.num = num
        self.normal = normal
        self.central = central
        self.color = color
        self.line_width0 = 0.05
        self.line_width1 = 0.6
        super().__init__(gl_widget)
        for i in range(-num, num + 1):
            if i % 5 == 0 or i == num + 1 or i == -num:
                self.lines[f"{i}"] = [
                    self.color, self.line_width1,
                    [(i * scale + central[0], central[1], -num * scale + central[2]),
                     (i * scale + central[0], central[1], num * scale + central[2])]
                ]
                self.lines[f"{i + num * 2 + 1}"] = [
                    self.color, self.line_width1,
                    [(-num * scale + central[0], central[1], i * scale + central[2]),
                     (num * scale + central[0], central[1], i * scale + central[2])]
                ]
            else:
                ...
                # self.lines[f"{i}"] = [
                #     self.color, self.line_width0,
                #     [(i * scale + central[0], central[1], -num * scale + central[2]),
                #      (i * scale + central[0], central[1], num * scale + central[2])]
                # ]
                # self.lines[f"{i + num * 2 + 1}"] = [
                #     self.color, self.line_width0,
                #     [(-num * scale + central[0], central[1], i * scale + central[2]),
                #      (num * scale + central[0], central[1], i * scale + central[2])]
                # ]
