import OpenGL.GL as gl
import numpy as np
from main_logger import Log

from .MeshData import Mesh
from .light import LightMixin, light_fragment_shader
from .shader import Shader
from ..GLGraphicsItem import GLGraphicsItem
from ..transform3d import Matrix4x4

__all__ = ['GLMeshItem', 'mesh_vertex_shader']


class GLMeshItem(GLGraphicsItem, LightMixin):
    """
    GLMeshItem 类表示 OpenGL 中的 3D 网格项。
    它支持光照、材质属性和选择高亮显示。

    属性:
        vertexes (np.ndarray): 顶点位置数组。
        indices (np.ndarray): 用于索引绘制的顶点索引数组。
        normals (np.ndarray): 顶点法线数组。
        texcoords (np.ndarray): 纹理坐标数组。
        lights (list): 影响网格的光源列表。
        material (object): 网格的材质属性。
        drawLine (bool): 指示是否以线框模式绘制网格的标志。
        calc_normals (bool): 指示是否计算法线的标志。
        mesh (Mesh): 可选的 Mesh 对象。
        glOptions (str): OpenGL 选项。
        parentItem (GLGraphicsItem): 父图形项。
        selectable (bool): 指示项是否可选择的标志。
        lineColor (tuple): 线框颜色。
        lineWidth (float): 线框宽度。
        selectedColor (tuple): 项被选择时使用的颜色。
    """

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
            glUsage=gl.GL_STATIC_DRAW,
            parentItem=None,
            selectable=False,
            lineColor=(0.0, 0.0, 0.0, 0.2),
            lineWidth=0.6,
            selectedColor=(0.1, 0.9, 1.0, 0.3)
    ):
        """
        初始化 GLMeshItem 实例。

        :param np.ndarray vertexes: 顶点位置数组。
        :param np.ndarray indices: 用于索引绘制的顶点索引数组。
        :param np.ndarray normals: 顶点法线数组。
        :param np.ndarray texcoords: 纹理坐标数组。
        :param list lights: 影响网格的光源列表。
        :param object material: 网格的材质属性。
        :param bool drawLine: 指示是否以线框模式绘制网格的标志。
        :param bool calc_normals: 指示是否计算法线的标志。
        :param Mesh mesh: 可选的 Mesh 对象。
        :param str glOptions: OpenGL 选项。
        :param GLGraphicsItem parentItem: 父图形项。
        :param bool selectable: 指示项是否可选择的标志。
        :param tuple lineColor: 线框颜色。
        :param float lineWidth: 线框宽度。
        :param tuple selectedColor: 项被选择时使用的颜色。
        """
        super().__init__(parentItem=parentItem, selectable=selectable, selectedColor=selectedColor)

        if vertexes is None:
            raise ValueError("vertexes 是必需的")
        if lights is None:
            lights = list()
        self.setGLOptions(glOptions)
        self.glUsage = glUsage
        if mesh is not None:
            self._mesh = mesh
        else:
            self._mesh = Mesh(vertexes, indices, texcoords, normals,
                              material, None, glUsage,
                              calc_normals)
        self.addLight(lights)
        self.__drawLine = drawLine
        self.__lineWidth = lineWidth
        self.__lineColor = lineColor

    def initializeGL(self):
        """
        初始化 OpenGL 环境，加载着色器和网格。
        """
        self.shader = Shader(mesh_vertex_shader, light_fragment_shader)
        self.pick_shader = Shader(mesh_vertex_shader, self.pick_fragment_shader)
        self.selected_shader = Shader(mesh_vertex_shader, self.selected_fragment_shader)
        self._mesh.initializeGL()

    def updateVertexes(self, vertexes: np.ndarray):
        """
        更新网格的顶点数据。

        :param np.ndarray vertexes: 新的顶点数组。
        """
        self._mesh.update_vertexes(vertexes)

    def updateVertex(self, index, vertex):
        """
        更新单个顶点的数据。

        :param int index: 被更新的顶点索引。
        :param np.ndarray vertex: 新的顶点坐标。
        """
        self._mesh.update_vertex(index, vertex)

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
                    self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
                    self._mesh.paint(self.shader)
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
            self._mesh.paint(self.shader)
            self.shader.set_uniform("highlight", False, "bool")
        gl.glLineWidth(0.6)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("paintLine", self.__drawLine, "bool")
            self.shader.set_uniform("lineColor", self._selectedColor, "vec4")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
            self._mesh.paint(self.shader)
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
            self._mesh.paint(self.pick_shader)

    def setMaterial(self, material):
        """
        设置网格的材质属性。

        :param object material: 新的材质属性。
        """
        self._mesh.setMaterial(material)

    def getMaterial(self):
        """
        获取网格的材质属性。

        :return: 当前的材质属性。
        :rtype: object
        """
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
