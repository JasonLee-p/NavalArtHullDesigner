import OpenGL.GL as gl
import numpy as np
from PyQt5.QtCore import pyqtSignal

from .BufferObject import VBO, EBO, VAO
from .MeshData import cone, direction_matrixs
from .shader import Shader
from ..GLGraphicsItem import GLGraphicsItem
from ..transform3d import Matrix4x4, Vector3

__all__ = ['GLAxisItem']


class _GLSingleAxisItem(GLGraphicsItem):
    """
    Displays three lines indicating origin and orientation of local coordinate system.
    """
    clicked_s = pyqtSignal()

    stPos = np.array([
        # positions
        0.0, 0.0, 0.0,
    ], dtype="f4")

    endPosX = np.array([1.0, 0.0, 0.0], dtype="f4")
    endPosY = np.array([0.0, 1.0, 0.0], dtype="f4")
    endPosZ = np.array([0.0, 0.0, 1.0], dtype="f4")

    # colorR = np.array([1.0, 0.0, 0.0], dtype="f4")
    # colorG = np.array([0.0, 1.0, 0.0], dtype="f4")
    # colorB = np.array([0.0, 0.0, 1.0], dtype="f4")

    def __init__(
            self,
            size=Vector3(1., 1., 1.),
            width=3,
            tip_size=0.7,
            antialias=True,
            fix_to_corner=False,
            leftHand=True,
            axis=0,
            color: tuple = (1.0, 0.0, 0.0),
            parentItem=None
    ):
        """

        :param size:
        :param width:
        :param tip_size:
        :param antialias:
        :param fix_to_corner:
        :param leftHand: 是否为左手坐标系
        :param axis: 0: x, 1: y, 2: z
        :param parentItem:
        """
        super().__init__(parentItem=parentItem, selectable=True)
        self.__size = Vector3(size)
        self.__width = width
        self.__fix_to_corner = fix_to_corner

        self.axis = axis
        if self.axis == 0:
            self.endPos = _GLSingleAxisItem.endPosX
        elif self.axis == 1:
            self.endPos = _GLSingleAxisItem.endPosY
        else:
            self.endPos = _GLSingleAxisItem.endPosZ
        self.color = np.array(color, dtype="f4")
        # print(self.color)
        self.leftHand: bool = leftHand  # 是否为左手坐标系
        self.antialias = antialias  # 抗锯齿
        self.cone_vertices, self.cone_indices = cone(0.06 * width * tip_size, 0.15 * width * tip_size)

    def setSize(self, x=None, y=None, z=None):
        """
        Set the size of the axes (in its local coordinate system; this does not affect the transform)
        Arguments can be x,y,z.
        """
        x = x if x is not None else self.__size.x
        y = y if y is not None else self.__size.y
        z = z if z is not None else self.__size.z
        self.__size = Vector3(x, y, z)
        self.update()

    def size(self):
        return self.__size.xyz

    def initializeGL(self):
        self.shader = Shader(vertex_shader, fragment_shader, geometry_shader)
        self.shader_cone = Shader(vertex_shader_cone, fragment_shader)
        self.pickShader = Shader(vertex_shader, self.pick_fragment_shader, geometry_shader)
        self.pickShader_cone = Shader(vertex_shader_cone, self.pick_fragment_shader)

        # line
        self.vao_line = VAO()

        self.vbo1 = VBO(
            data=[self.stPos, self.endPos, self.color],
            size=[3, 3, 3],
        )
        self.vbo1.setAttrPointer([0, 1, 2])

        # cone
        self.transforms = direction_matrixs(self.stPos.reshape(-1, 3) * self.__size,
                                            self.endPos.reshape(-1, 3) * self.__size)
        self.vao_cone = VAO()

        self.vbo2 = VBO(
            [self.cone_vertices, self.transforms],
            [3, [4, 4, 4, 4]],
        )
        self.vbo2.setAttrPointer([0, 1], divisor=[0, 1], attr_id=[0, [1, 2, 3, 4]])

        self.vbo1.bind()
        self.vbo1.setAttrPointer(2, divisor=1, attr_id=5)

        self.ebo = EBO(self.cone_indices)

    def setSelected(self, s, children=True) -> bool:
        if s:
            self.clicked_s.emit()
        return super().setSelected(s, children)

    def paint(self, model_matrix=Matrix4x4()):
        self.setupGLState()

        if self.antialias:
            gl.glEnable(gl.GL_LINE_SMOOTH)
            gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glLineWidth(self.__width)

        proj_view = self.proj_view_matrix().glData
        with self.shader:
            self.shader.set_uniform("sizev3", self.size(), "vec3")
            self.shader.set_uniform("view", proj_view, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.vao_line.bind()
            gl.glDrawArrays(gl.GL_POINTS, 0, 3)

        gl.glEnable(gl.GL_CULL_FACE)  # 开启背面剔除
        gl.glCullFace(gl.GL_BACK)
        with self.shader_cone:
            self.shader_cone.set_uniform("view", proj_view, "mat4")
            self.shader_cone.set_uniform("model", model_matrix.glData, "mat4")
            self.vao_cone.bind()
            gl.glDrawElementsInstanced(gl.GL_TRIANGLES, self.cone_indices.size, gl.GL_UNSIGNED_INT, None, 3)
        gl.glDisable(gl.GL_CULL_FACE)

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        self.setupGLState()

        if self.antialias:
            gl.glEnable(gl.GL_LINE_SMOOTH)
            gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glLineWidth(self.__width)

        proj_view = self.proj_view_matrix().glData
        with self.pickShader:
            self.pickShader.set_uniform("sizev3", self.size(), "vec3")
            self.pickShader.set_uniform("view", proj_view, "mat4")
            self.pickShader.set_uniform("model", model_matrix.glData, "mat4")
            self.pickShader.set_uniform("pickColor", self.pickColor(False), "float")
            self.vao_line.bind()
            gl.glDrawArrays(gl.GL_POINTS, 0, 3)

        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        with self.pickShader_cone:
            self.pickShader_cone.set_uniform("view", proj_view, "mat4")
            self.pickShader_cone.set_uniform("model", model_matrix.glData, "mat4")
            self.pickShader_cone.set_uniform("pickColor", self.pickColor(False), "float")
            self.vao_cone.bind()
            gl.glDrawElementsInstanced(gl.GL_TRIANGLES, self.cone_indices.size, gl.GL_UNSIGNED_INT, None, 3)
        gl.glDisable(gl.GL_CULL_FACE)

    def proj_view_matrix(self):
        if self.__fix_to_corner:
            view = self.view()
            aspect = 1 / view.deviceRatio()
            if self.leftHand:
                aspect = -aspect
            proj = Matrix4x4.create_perspective_proj(
                20, aspect, 1, 80.0
            )
            # 计算在这个投影矩阵下, 窗口右上角点在相机坐标系下的坐标
            y_rate = -0.8
            x_rate = 0.2 * view.deviceRatio() - 1
            pos = proj.inverse() * Vector3(x_rate, y_rate, 1)
            return proj * Matrix4x4.fromTranslation(*(pos * 50)) * self.view().camera.quat
        else:
            return super().proj_view_matrix()


class GLAxisItem(GLGraphicsItem):
    """
    Displays three lines indicating origin and orientation of local coordinate system.
    """
    axisX_clicked_s: pyqtSignal
    axisY_clicked_s: pyqtSignal
    axisZ_clicked_s: pyqtSignal

    def __init__(
            self,
            size=Vector3(1., 1., 1.),
            width=4,
            tip_size=0.6,
            antialias=True,
            glOptions='ontop',
            fix_to_corner=False,
            left_hand=True,
            parentItem=None
    ):
        super().__init__(parentItem=parentItem, selectable=True)
        self.setGLOptions(glOptions)
        if fix_to_corner:
            # 保证坐标轴不会被其他物体遮挡
            self.updateGLOptions({"glClear": (gl.GL_DEPTH_BUFFER_BIT,)})
            self.setDepthValue(1000)  # make sure it is drawn last
        self.axisX = _GLSingleAxisItem(size, width, tip_size, antialias, fix_to_corner, left_hand, 0, (1.0, 0.0, 0.0), self)
        self.axisY = _GLSingleAxisItem(size, width, tip_size, antialias, fix_to_corner, left_hand, 1, (0.0, 1.0, 0.0), self)
        self.axisZ = _GLSingleAxisItem(size, width, tip_size, antialias, fix_to_corner, left_hand, 2, (0.0, 0.0, 1.0), self)
        self.axisX_clicked_s = self.axisX.clicked_s
        self.axisY_clicked_s = self.axisY.clicked_s
        self.axisZ_clicked_s = self.axisZ.clicked_s


# class GLAxisItem(GLGraphicsItem):
#     """
#     Displays three lines indicating origin and orientation of local coordinate system.
#     """
#     stPos = np.array([
#         # positions
#         0.0, 0.0, 0.0,
#         0.0, 0.0, 0.0,
#         0.0, 0.0, 0.0,
#     ], dtype="f4")
#
#     endPos = np.array([
#         # positions
#         1.0, 0.0, 0.0,
#         0.0, 1.0, 0.0,
#         0.0, 0.0, 1.0,
#     ], dtype="f4")
#
#     colors = np.array([
#         1.0, 0.0, 0.0,
#         0.0, 1.0, 0.0,
#         0.0, 0.0, 1.0,
#     ], dtype="f4")
#
#     def __init__(
#             self,
#             size=Vector3(1., 1., 1.),
#             width=3,
#             tip_size=0.7,
#             antialias=True,
#             glOptions='opaque',
#             fix_to_corner=False,
#             parentItem=None
#     ):
#         super().__init__(parentItem=parentItem)
#         self.__size = Vector3(size)
#         self.__width = width
#         self.__fix_to_corner = fix_to_corner
#
#         self.setGLOptions(glOptions)
#         if fix_to_corner:
#             # 保证坐标轴不会被其他物体遮挡
#             self.updateGLOptions({"glClear": (gl.GL_DEPTH_BUFFER_BIT,)})
#             self.setDepthValue(1000)  # make sure it is drawn last
#
#         self.antialias = antialias
#         self.cone_vertices, self.cone_indices = cone(0.06 * width * tip_size, 0.15 * width * tip_size)
#
#     def setSize(self, x=None, y=None, z=None):
#         """
#         Set the size of the axes (in its local coordinate system; this does not affect the transform)
#         Arguments can be x,y,z.
#         """
#         x = x if x is not None else self.__size.x
#         y = y if y is not None else self.__size.y
#         z = z if z is not None else self.__size.z
#         self.__size = Vector3(x, y, z)
#         self.update()
#
#     def size(self):
#         return self.__size.xyz
#
#     def initializeGL(self):
#         self.shader = Shader(vertex_shader, fragment_shader, geometry_shader)
#         self.shader_cone = Shader(vertex_shader_cone, fragment_shader)
#
#         # line
#         self.vao_line = VAO()
#
#         self.vbo1 = VBO(
#             data=[self.stPos, self.endPos, self.colors],
#             size=[3, 3, 3],
#         )
#         self.vbo1.setAttrPointer([0, 1, 2])
#
#         # cone
#         self.transforms = direction_matrixs(self.stPos.reshape(-1, 3) * self.__size,
#                                             self.endPos.reshape(-1, 3) * self.__size)
#         self.vao_cone = VAO()
#
#         self.vbo2 = VBO(
#             [self.cone_vertices, self.transforms],
#             [3, [4, 4, 4, 4]],
#         )
#         self.vbo2.setAttrPointer([0, 1], divisor=[0, 1], attr_id=[0, [1, 2, 3, 4]])
#
#         self.vbo1.bind()
#         self.vbo1.setAttrPointer(2, divisor=1, attr_id=5)
#
#         self.ebo = EBO(self.cone_indices)
#
#     def paint(self, model_matrix=Matrix4x4()):
#         self.setupGLState()
#
#         if self.antialias:
#             gl.glEnable(gl.GL_LINE_SMOOTH)
#             gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
#         gl.glLineWidth(self.__width)
#
#         proj_view = self.proj_view_matrix().glData
#         with self.shader:
#             self.shader.set_uniform("sizev3", self.size(), "vec3")
#             self.shader.set_uniform("view", proj_view, "mat4")
#             self.shader.set_uniform("model", model_matrix.glData, "mat4")
#             self.vao_line.bind()
#             gl.glDrawArrays(gl.GL_POINTS, 0, 3)
#
#         gl.glEnable(gl.GL_CULL_FACE)
#         gl.glCullFace(gl.GL_BACK)
#         with self.shader_cone:
#             self.shader_cone.set_uniform("view", proj_view, "mat4")
#             self.shader_cone.set_uniform("model", model_matrix.glData, "mat4")
#             self.vao_cone.bind()
#             gl.glDrawElementsInstanced(gl.GL_TRIANGLES, self.cone_indices.size, gl.GL_UNSIGNED_INT, None, 3)
#         gl.glDisable(gl.GL_CULL_FACE)
#
#     def proj_view_matrix(self):
#         if self.__fix_to_corner:
#             view = self.view()
#             proj = Matrix4x4.create_perspective_proj(
#                 20, 1 / view.deviceRatio(), 1, 80.0
#             )
#             # 计算在这个投影矩阵下, 窗口右上角点在相机坐标系下的坐标
#             y_rate = -0.8
#             x_rate = 0.2 * view.deviceRatio() - 1
#             pos = proj.inverse() * Vector3(x_rate, y_rate, 1)
#             return proj * Matrix4x4.fromTranslation(*(pos * 50)) * self.view().camera.quat
#         else:
#             return super().proj_view_matrix()


vertex_shader = """
#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform vec3 sizev3;

layout (location = 0) in vec3 stPos;
layout (location = 1) in vec3 endPos;
layout (location = 2) in vec3 iColor;

out V_OUT {
    vec4 endPos;
    vec3 color;
} v_out;

void main() {
    mat4 matrix = view * model;
    gl_Position =  matrix * vec4(stPos * sizev3, 1.0);
    v_out.endPos = matrix * vec4(endPos * sizev3, 1.0);
    v_out.color = iColor;
}
"""

vertex_shader_cone = """
#version 330 core

uniform mat4 model;
uniform mat4 view;

layout (location = 0) in vec3 iPos;
layout (location = 1) in vec4 row1;
layout (location = 2) in vec4 row2;
layout (location = 3) in vec4 row3;
layout (location = 4) in vec4 row4;
layout (location = 5) in vec3 iColor;
out vec3 oColor;

void main() {
    mat4 transform = mat4(row1, row2, row3, row4);
    gl_Position =  view * model * transform * vec4(iPos, 1.0);
    oColor = iColor;
}
"""

geometry_shader = """
#version 330 core
layout(points) in;
layout(line_strip, max_vertices = 2) out;

in V_OUT {
    vec4 endPos;
    vec3 color;
} gs_in[];
out vec3 oColor;

void main() {
    oColor = gs_in[0].color;
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    gl_Position = gs_in[0].endPos;
    EmitVertex();
    EndPrimitive();
}
"""

fragment_shader = """
#version 330 core

in vec3 oColor;
out vec4 fragColor;

void main() {
    fragColor = vec4(oColor, 1.0f);
}
"""
