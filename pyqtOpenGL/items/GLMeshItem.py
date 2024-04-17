import OpenGL.GL as gl
import numpy as np

from .MeshData import Mesh
from .light import LightMixin, light_fragment_shader
from .shader import Shader
from ..GLGraphicsItem import GLGraphicsItem
from ..transform3d import Matrix4x4

__all__ = ['GLMeshItem']


class GLMeshItem(GLGraphicsItem, LightMixin):

    def __init__(
            self,
            vertexes,
            indices=None,
            normals=None,
            texcoords=None,
            lights=None,
            material=None,
            drawLine=False,
            calc_normals=True,
            mesh: Mesh = None,
            glOptions='translucent',
            parentItem=None,
            selectable=False,
            lineColor=(0.0, 0.0, 0.0, 0.2),
            lineWidth=0.6,
            selectedColor=(0.1, 0.9, 1.0, 0.3)
    ):
        super().__init__(parentItem=parentItem, selectable=selectable, selectedColor=selectedColor)
        if vertexes is None:
            raise ValueError("vertexes is required")
        if lights is None:
            lights = list()
        self.setGLOptions(glOptions)
        if mesh is not None:
            self._mesh = mesh
        else:
            self._mesh = Mesh(vertexes, indices, texcoords, normals,
                              material, None, gl.GL_STATIC_DRAW,
                              calc_normals)
        self.addLight(lights)
        self.__drawLine = drawLine
        self.__lineWidth = lineWidth
        self.__lineColor = lineColor

    def initializeGL(self):
        self.shader = Shader(mesh_vertex_shader, light_fragment_shader)
        self.pick_shader = Shader(mesh_vertex_shader, self.pick_fragment_shader)
        self.selected_shader = Shader(mesh_vertex_shader, self.selected_fragment_shader)
        self._mesh.initializeGL()

    def updateVertexes(self, vertexes: np.ndarray):
        self._mesh.update_vertexes(vertexes)

    def updateVertex(self, index, vertex):
        """
        :param index: 被更新的顶点索引
        :param vertex: 新的顶点坐标
        :return:
        """
        self._mesh.update_vertex(index, vertex)

    def paint(self, model_matrix=Matrix4x4()):
        if not self.selected():
            self.setupGLState()
            self.setupLight(self.shader)
            with self.shader:
                self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
                self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
                self.shader.set_uniform("model", model_matrix.glData, "mat4")
                self.shader.set_uniform("paintLine", False, "bool")
                self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
                self._mesh.paint(self.shader)
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
                    self._mesh.paint(self.shader)
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
            self._mesh.paint(self.shader)
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
            self._mesh.paint(self.shader)
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
        self.setupGLState()
        with self.pick_shader:
            self.pick_shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.pick_shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.pick_shader.set_uniform("model", model_matrix.glData, "mat4")
            self.pick_shader.set_uniform("pickColor", self.pickColor(), "float")
            self._mesh.paint(self.pick_shader)

    def setMaterial(self, material):
        self._mesh.setMaterial(material)

    def getMaterial(self):
        return self._mesh.getMaterial()


mesh_vertex_shader = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoords;

out vec2 TexCoords;
out vec3 FragPos;
out vec3 Normal;

uniform mat4 view;
uniform mat4 proj;
uniform mat4 model;

void main() {
    TexCoords = aTexCoords;
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = normalize(mat3(transpose(inverse(model))) * aNormal);
    gl_Position = proj * view * vec4(FragPos, 1.0);
}
"""
