from PyQt5.QtCore import QPoint

from ..GLGraphicsItem import GLGraphicsItem
from ..transform3d import Matrix4x4
from .shader import Shader
from .BufferObject import VAO, VBO
from .texture import Texture2D
import numpy as np
import OpenGL.GL as gl
from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent

__all__ = ['GL2DSelectBox']


class GL2DSelectBox(GLGraphicsItem):
    """
    2D选择框
    """

    def __init__(self, glOptions='translucent'):
        super().__init__(parentItem=None)
        self.setGLOptions(glOptions)
        self.vertices = np.array([
            # 顶点坐标
            -1, -1, 0,
            1, -1, 0,
            1, 1, 0,
            1, 1, 0,
            -1, 1, 0,
            -1, -1, 0,
        ], dtype=np.float32).reshape(-1, 3)

    def initializeGL(self):
        self.shader = Shader(vertex_shader, fragment_shader)
        self.vao = VAO()
        self.vbo = VBO([self.vertices], [[3]], usage=gl.GL_STATIC_DRAW)
        self.vbo.setAttrPointer([0], attr_id=[[0]])

    def updateGL(self, left_top=QPoint(0, 0), down_right=QPoint(1, 1)):
        self.vertices = np.array([
            # 顶点坐标
            left_top.x(), left_top.y(), 0,
            down_right.x(), left_top.y(), 0,
            down_right.x(), down_right.y(), 0,
            down_right.x(), down_right.y(), 0,
            left_top.x(), down_right.y(), 0,
            left_top.x(), left_top.y(), 0,
        ], dtype=np.float32).reshape(-1, 3)
        self.vbo.updateData([0], [self.vertices])

    def paint(self, view_matrix=Matrix4x4(), left_top=QPoint(0, 0), down_right=QPoint(1, 1)):
        self.updateGL(left_top, down_right)
        self.setupGLState()

        self.shader.set_uniform("proj", Matrix4x4().glData, "mat4")
        self.shader.set_uniform("view", view_matrix.glData, "mat4")
        self.shader.set_uniform("model", Matrix4x4().glData, "mat4")

        with self.shader:
            self.vao.bind()
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)


vertex_shader = """
#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

layout (location = 0) in vec3 iPos;

void main() {
    gl_Position = proj * view * model * vec4(iPos, 1.0);
}
"""

fragment_shader = """
#version 330 core
out vec4 FragColor;

void main() {
    FragColor = vec4(1.0, 1.0, 1.0, 0.3);
}
"""
