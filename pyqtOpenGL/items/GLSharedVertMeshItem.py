from typing import List

import OpenGL.GL as gl
import numpy as np
from main_logger import Log
from pyqtOpenGL.items.GLMeshItem import mesh_vertex_shader

from .MeshData import Mesh
from .light import LightMixin, light_fragment_shader
from .shader import Shader
from ..GLGraphicsItem import GLGraphicsItem
from ..transform3d import Matrix4x4

__all__ = ['GLSharedVertMeshItem']


class GLSharedVertMeshItem(GLGraphicsItem, LightMixin):
    """
    GLSharedVertMeshItem 类表示 OpenGL 中的 3D 网格项，
    该类支持使用共享的顶点数组对象（VAO）。

    属性:
        vao (int): 顶点数组对象的ID。
        vertexCount (int): 顶点数量。
        lights (list): 影响网格的光源列表。
        material (object): 网格的材质属性。
        drawLine (bool): 指示是否以线框模式绘制网格的标志。
        glOptions (str): OpenGL 选项。
        parentItem (GLGraphicsItem): 父图形项。
        selectable (bool): 指示项是否可选择的标志。
        lineColor (tuple): 线框颜色。
        lineWidth (float): 线框宽度。
        selectedColor (tuple): 项被选择时使用的颜色。
    """

    def __init__(
            self,
            vao: int,
            vertexCount: int,
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
        """
        初始化 GLSharedVertMeshItem 实例。

        :param int vao: 顶点数组对象的ID。
        :param int vertexCount: 顶点数量。
        :param list lights: 影响网格的光源列表。
        :param object material: 网格的材质属性。
        :param bool drawLine: 指示是否以线框模式绘制网格的标志。
        :param str glOptions: OpenGL 选项。
        :param GLGraphicsItem parentItem: 父图形项。
        :param bool selectable: 指示项是否可选择的标志。
        :param tuple lineColor: 线框颜色。
        :param float lineWidth: 线框宽度。
        :param tuple selectedColor: 项被选择时使用的颜色。
        """
        super().__init__(parentItem=parentItem, selectable=selectable, selectedColor=selectedColor)

        if vao is None:
            raise ValueError("vao 是必需的")
        if lights is None:
            lights = list()

        self.vao = vao
        self.vertexCount = vertexCount
        self.material = material
        self.drawLine = drawLine
        self.lineWidth = lineWidth
        self.lineColor = lineColor
        self.setGLOptions(glOptions)
        self.addLight(lights)

    def initializeGL(self):
        """
        初始化 OpenGL 环境，加载着色器。
        """
        self.shader = Shader(mesh_vertex_shader, light_fragment_shader)
        self.pick_shader = Shader(mesh_vertex_shader, self.pick_fragment_shader)
        self.selected_shader = Shader(mesh_vertex_shader, self.selected_fragment_shader)

    def paint(self, model_matrix=Matrix4x4()):
        """
        绘制网格。

        :param Matrix4x4 model_matrix: 模型矩阵。
        """
        if not self.selected():
            self.setupGLState()
            self.setupLight(self.shader)
            with self.shader:
                self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
                self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
                self.shader.set_uniform("model", model_matrix.glData, "mat4")
                self.shader.set_uniform("paintLine", False, "bool")
                self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")

                gl.glBindVertexArray(self.vao)
                gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertexCount)
                gl.glBindVertexArray(0)

            if self.drawLine:
                gl.glLineWidth(self.lineWidth)
                gl.glDepthFunc(gl.GL_LEQUAL)
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                with self.shader:
                    self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
                    self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
                    self.shader.set_uniform("model", model_matrix.glData, "mat4")
                    self.shader.set_uniform("paintLine", self.drawLine, "bool")
                    self.shader.set_uniform("lineColor", self.lineColor, "vec4")
                    self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")

                    gl.glBindVertexArray(self.vao)
                    gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertexCount)
                    gl.glBindVertexArray(0)

                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                gl.glDepthFunc(gl.GL_LESS)
        else:
            self.paint_selected(model_matrix)

    def paint_selected(self, model_matrix=Matrix4x4()):
        """
        绘制选中的网格。

        :param Matrix4x4 model_matrix: 模型矩阵。
        """
        self.setupGLState()
        self.setupLight(self.shader)
        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("paintLine", False, "bool")
            self.shader.set_uniform("highlight", True, "bool")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")

            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertexCount)
            gl.glBindVertexArray(0)

            self.shader.set_uniform("highlight", False, "bool")

        gl.glLineWidth(0.6)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("paintLine", self.drawLine, "bool")
            self.shader.set_uniform("lineColor", self._selectedColor, "vec4")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")

            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertexCount)
            gl.glBindVertexArray(0)

        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        """
        在拾取模式下绘制网格。

        :param Matrix4x4 model_matrix: 模型矩阵。
        """
        self.setupGLState()
        with self.pick_shader:
            self.pick_shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.pick_shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.pick_shader.set_uniform("model", model_matrix.glData, "mat4")
            self.pick_shader.set_uniform("pickColor", self.pickColor(), "float")

            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertexCount)
            gl.glBindVertexArray(0)

    def setMaterial(self, material):
        """
        设置网格的材质属性。

        :param object material: 新的材质属性。
        """
        self.material = material

    def getMaterial(self):
        """
        获取网格的材质属性。

        :return: 当前的材质属性。
        :rtype: object
        """
        return self.material
