import OpenGL.GL as gl
import numpy as np

from .shader import Shader
from ..GLGraphicsItem import GLGraphicsItem
from ..transform3d import Matrix4x4, Vector3
from .MeshData import vertex_normal, Mesh
from .light import LightMixin, light_fragment_shader

__all__ = ['GLMeshItem']


class GLMeshItem(GLGraphicsItem, LightMixin):

    def __init__(
            self,
            vertexes=None,
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
            selectedColor=(0.1, 0.9, 1.0, 0.3)
    ):
        super().__init__(parentItem=parentItem, selectable=selectable, selectedColor=selectedColor)
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

    def initializeGL(self):
        self.shader = Shader(mesh_vertex_shader, light_fragment_shader)
        self.pick_shader = Shader(mesh_vertex_shader, self.pick_fragment_shader)
        self.selected_shader = Shader(mesh_vertex_shader, self.selected_fragment_shader)
        self._mesh.initializeGL()

    def paint(self, model_matrix=Matrix4x4()):
        if not self.selected():
            self.setupGLState()
            self.setupLight(self.shader)

            if self.__drawLine:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            with self.shader:
                self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
                self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
                self.shader.set_uniform("model", model_matrix.glData, "mat4")
                self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
                self._mesh.paint(self.shader)
            if self.__drawLine:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
            # with self.shader:
            #     self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            #     self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            #     self.shader.set_uniform("model", model_matrix.glData, "mat4")
            #     self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
            #     self._mesh.paint(self.shader)
        else:
            self.paint_selected(model_matrix)

    def paint_selected(self, model_matrix=Matrix4x4()):
        # 设置模板函数
        # glEnable(GL_STENCIL_TEST)
        # glStencilFunc(GL_ALWAYS, 1, 0xFF)
        # glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        # glStencilMask(0xFF)

        self.setupGLState()
        self.setupLight(self.shader)

        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
            self._mesh.paint(self.shader)

        # # 设置模板缓冲区为只读，关闭深度测试
        # glStencilFunc(GL_NOTEQUAL, 1, 0xFF)
        # glStencilMask(0x00)
        # gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_ALWAYS)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)

        # 绘制border
        with self.selected_shader:
            self.selected_shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.selected_shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.selected_shader.set_uniform("model", model_matrix.glData, "mat4")
            self.selected_shader.set_uniform("selectedColor", self._selectedColor, "vec4")
            self._mesh.paint(self.selected_shader)

        # 恢复深度测试和模板缓冲区
        # glStencilMask(0xFF)
        # glDisable(GL_STENCIL_TEST)
        # glEnable(GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

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
