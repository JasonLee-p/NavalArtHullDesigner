from pathlib import Path

import OpenGL.GL as gl
from PyQt5.QtCore import pyqtSignal

# from pyqtOpenGL import PointLight

from ..GLGraphicsItem import GLGraphicsItem, PickColorManager
from ..transform3d import Matrix4x4, Quaternion, Vector3
from .shader import Shader
from .MeshData import Mesh
from .light import LightMixin, light_fragment_shader
from .GLMeshItem import mesh_vertex_shader
from typing import List, Union

__all__ = ['GLModelItem']


class GLModelItem(GLGraphicsItem, LightMixin):

    def __init__(
            self,
            path,
            lights=None,
            material=None,
            drawLine=False,
            glOptions='translucent',
            parentItem=None,
            selectable=False,
            lineColor=(0.0, 0.0, 0.0, 0.2),
            lineWidth=0.6,
            selectedColor=(0.1, 0.9, 1.0, 0.3)
    ):
        super().__init__(parentItem=parentItem, selectable=selectable, selectedColor=selectedColor)
        if lights is None:
            lights = list()
        self._path = path
        self._directory = Path(path).parent
        self.setGLOptions(glOptions)
        # model
        self.meshes: List[Mesh] = Mesh.load_model(path, material=material)
        self._order = list(range(len(self.meshes)))
        self.__drawLine = drawLine
        self.__lineWidth = lineWidth
        self.__lineColor = lineColor
        # light
        self.addLight(lights)

    def addLight(self, light):
        super().addLight(light)

    def setDrawLine(self, drawLine: bool):
        self.__drawLine = drawLine

    def setMaterial_data(self, ambient, diffuse, specular, shininess, opacity=1.0):
        for m in self.meshes:
            m.setMaterial_data(ambient, diffuse, specular, shininess, opacity)

    def initializeGL(self):
        self.shader = Shader(mesh_vertex_shader, light_fragment_shader)
        self.pick_shader = Shader(mesh_vertex_shader, self.pick_fragment_shader)
        self.selected_shader = Shader(mesh_vertex_shader, self.selected_fragment_shader)
        for m in self.meshes:
            m.initializeGL()

    def paint(self, model_matrix=Matrix4x4()):
        if not self.selected():
            self.setupGLState()
            self.setupLight(self.shader)
            with self.shader:
                self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
                self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
                self.shader.set_uniform("model", model_matrix.glData, "mat4")
                self.shader.set_uniform("paintLine", False, "bool")
                self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")  # 计算光线夹角用
                for i in self._order:
                    self.meshes[i].paint(self.shader)
            if self.__drawLine:
                # 设置线宽
                gl.glLineWidth(self.__lineWidth)
                gl.glDepthFunc(gl.GL_LEQUAL)
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            with self.shader:
                self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
                self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
                self.shader.set_uniform("model", model_matrix.glData, "mat4")
                self.shader.set_uniform("paintLine", self.__drawLine, "bool")
                self.shader.set_uniform("lineColor", self.__lineColor, "vec4")
                self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")  # 计算光线夹角用
                for i in self._order:
                    self.meshes[i].paint(self.shader)
            if self.__drawLine:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                gl.glDepthFunc(gl.GL_LESS)
        else:
            self.paint_selected(model_matrix)

    def paint_selected(self, model_matrix=Matrix4x4()):
        self.setupGLState()
        self.setupLight(self.shader)
        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("paintLine", False, "bool")
            # self.shader.set_uniform("lineColor", self._selectedColor, "vec4")
            self.shader.set_uniform("highlight", True, "bool")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")  # 计算光线夹角用
            for i in self._order:
                self.meshes[i].paint(self.shader)
            self.shader.set_uniform("highlight", False, "bool")
        # glDepthFunc(GL_ALWAYS)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        #
        # # 绘制border
        # with self.selected_shader:
        #     self.selected_shader.set_uniform("view", self.view_matrix().glData, "mat4")
        #     self.selected_shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
        #     self.selected_shader.set_uniform("model", model_matrix.glData, "mat4")
        #     self.selected_shader.set_uniform("selectedColor", self._selectedColor, "vec4")
        #     for i in self._order:
        #         self.meshes[i].paint(self.selected_shader)
        # glDepthFunc(GL_LESS)
        # 设置线宽
        gl.glLineWidth(0.6)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("paintLine", self.__drawLine, "bool")
            self.shader.set_uniform("lineColor", self._selectedColor, "vec4")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")  # 计算光线夹角用
            for i in self._order:
                self.meshes[i].paint(self.shader)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    # def paint_selected(self, model_matrix=Matrix4x4()):
    #     # 设置模板函数
    #     # glEnable(GL_STENCIL_TEST)
    #     # glStencilFunc(GL_ALWAYS, 1, 0xFF)
    #     # glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    #     # glStencilMask(0xFF)
    #
    #     self.setupGLState()
    #     # self.setupLight(self.shader)
    #     #
    #     # with self.shader:
    #     #     self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
    #     #     self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
    #     #     self.shader.set_uniform("model", model_matrix.glData, "mat4")
    #     #     self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
    #     #     for i in self._order:
    #     #         self.meshes[i].paint(self.shader)
    #
    #     # # 设置模板缓冲区为只读，关闭深度测试
    #     # glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
    #     # glStencilMask(0x00)
    #     # glDisable(GL_DEPTH_TEST)
    #     glDepthFunc(GL_ALWAYS)
    #     # glBlendEquation(GL_MAX)
    #     glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    #     # 设置混合函数为非透明度叠加
    #     # glDisable(GL_BLEND)
    #
    #     # 绘制border
    #     with self.selected_shader:
    #         self.selected_shader.set_uniform("view", self.view_matrix().glData, "mat4")
    #         self.selected_shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
    #         self.selected_shader.set_uniform("model", model_matrix.glData, "mat4")
    #         self.selected_shader.set_uniform("selectedColor", self._selectedColor, "vec4")
    #         for i in self._order:
    #             self.meshes[i].paint(self.selected_shader)
    #
    #     # 恢复深度测试和模板缓冲区
    #     # glStencilMask(0xFF)
    #     # glDisable(GL_STENCIL_TEST)
    #     # glEnable(GL_DEPTH_TEST)
    #     glDepthFunc(GL_LESS)
    #     # glBlendEquation(GL_FUNC_ADD)
    #     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        gl.glEnable(gl.GL_STENCIL_TEST)
        self.setupGLState()
        with self.pick_shader:
            self.pick_shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.pick_shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.pick_shader.set_uniform("model", model_matrix.glData, "mat4")
            self.pick_shader.set_uniform("pickColor", self._pickColor, "float")
            for i in self._order:
                self.meshes[i].paint(self.pick_shader)

    def setMaterial(self, mesh_id, material):
        self.meshes[mesh_id].setMaterial(material)

    def getMaterial(self, mesh_id):
        return self.meshes[mesh_id]._material

    def setPaintOrder(self, order: list):
        """设置绘制顺序, order为mesh的索引列表"""
        assert max(order) < len(self.meshes) and min(order) >= 0
        self._order = order
