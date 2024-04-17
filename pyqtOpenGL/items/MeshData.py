import math
from ctypes import c_float, c_void_p
from pathlib import Path
from time import time
from typing import List, Union, Tuple, Literal, Optional

import OpenGL.GL as gl
import assimp_py as assimp
import numpy as np
from PyQt5.QtGui import QColor

from .BufferObject import VAO, VBO, EBO
from .shader import Shader
from .texture import Texture2D
from ..functions import dispatchmethod
from ..transform3d import Vector3

__all__ = [
    "Mesh", "Material", "EditItemMaterial", "direction_matrixs", "vertex_normal_smooth",
    "sphere", "cylinder", "cube", "cone", "plane"
]

Vec2 = (2 * c_float)
Vec3 = (3 * c_float)

TextureType = {
    assimp.TextureType_DIFFUSE: "tex_diffuse",  # map_Kd
    assimp.TextureType_SPECULAR: "tex_specular",  # map_Ks
    assimp.TextureType_AMBIENT: "tex_ambient",  # map_Ka
    assimp.TextureType_HEIGHT: "tex_height",  # map_Bump
}


class Material:

    @dispatchmethod
    def __init__(
            self,
            ambient=(0.4, 0.4, 0.4),
            diffuse=(0.8, 0.8, 0.8),
            specular=(0.2, 0.2, 0.2),
            shininess: float = 10.,
            opacity: float = 1.,
            textures: List[Texture2D] = None,
            textures_paths: dict = None,
            directory: Union[str, Path] = Path(),
    ):
        self.ambient = Vector3(ambient)
        self.diffuse = Vector3(diffuse)
        self.specular = Vector3(specular)
        self.shininess = shininess
        self.opacity = opacity
        self.textures = list()
        self.textures.extend(textures) if textures else None
        self.texture_paths = textures_paths if textures_paths else dict()
        self.directory = directory

    @__init__.register(dict)
    def _(self, material_dict: dict, directory=None):
        self.__init__(
            material_dict.get("COLOR_AMBIENT", [0.4, 0.4, 0.4]),  # Ka
            material_dict.get("COLOR_DIFFUSE", [1.0, 1.0, 1.0]),  # Kd
            material_dict.get("COLOR_SPECULAR", [0.2, 0.2, 0.2]),  # Ks
            material_dict.get("SHININESS", 10),
            material_dict.get("OPACITY", 1),
            textures_paths=material_dict.get("TEXTURES", None),
            directory=directory,
        )

    def load_textures(self):
        """在 initializeGL() 中调用 """
        for type_, path in self.texture_paths.items():
            if isinstance(path, list):
                path = path[0]
            if type_ in TextureType.keys():
                type_ = TextureType[type_]
            self.textures.append(
                Texture2D(self.directory / path, tex_type=type_)
            )

    def set_uniform(self, shader: Shader, name: str):
        use_texture = False
        for tex in self.textures:
            if tex.type == "tex_diffuse":
                tex.bind()
                shader.set_uniform(f"{name}.tex_diffuse", tex, "sampler2D")
                use_texture = True
        shader.set_uniform(name + ".ambient", self.ambient, "vec3")
        shader.set_uniform(name + ".diffuse", self.diffuse, "vec3")
        shader.set_uniform(name + ".specular", self.specular, "vec3")
        shader.set_uniform(name + ".shininess", self.shininess, "float")
        shader.set_uniform(name + ".opacity", self.opacity, "float")
        shader.set_uniform(name + ".use_texture", use_texture, "bool")

    def set_data(self, ambient=None, diffuse=None, specular=None, shininess=None, opacity=None):
        if ambient is not None:
            self.ambient = Vector3(ambient)
        if diffuse is not None:
            self.diffuse = Vector3(diffuse)
        if specular is not None:
            self.specular = Vector3(specular)
        if shininess is not None:
            self.shininess = shininess
        if opacity is not None:
            self.opacity = opacity

    def __repr__(self) -> str:
        return f"Material(ambient={self.ambient}, diffuse={self.diffuse}, specular={self.specular}, shininess={self.shininess}, opacity={self.opacity})"


class Mesh:
    def __init__(
            self,
            vertexes,
            indices=None,
            texcoords=None,
            normals=None,
            material=None,
            directory=None,
            usage=gl.GL_STATIC_DRAW,
            calc_normals=False,
    ):
        self._vertexes = np.array(vertexes, dtype=np.float32)

        if indices is not None:
            try:
                self._indices = np.array(indices, dtype=np.uint32)
            except ValueError:
                # assimp 的 indices 有时出错, 例如 [(0, 1), (2, 3), (4, 5, 6), (7, 8, 9) ...]
                indices = [item for item in indices if len(item) == 3]
                self._indices = np.array(indices, dtype=np.uint32)
        else:
            self._indices = None

        if self._indices is not None:
            if calc_normals and normals is None:
                self._normals = vertex_normal_smooth(self._vertexes, self._indices)
            else:
                self._normals = np.array(normals, dtype=np.float32)
        else:
            self._normals = None

        if texcoords is None:
            self._texcoords = None
        else:
            self._texcoords = np.array(texcoords, dtype=np.float32)[..., :2]

        if isinstance(material, dict):
            self._material = Material(material, directory)
        elif isinstance(material, Material):
            self._material = material
        elif material is None:
            self._material = Material()
        self._usage = usage

    def initializeGL(self):
        self.vao = VAO()
        self.vbo = VBO(
            [self._vertexes, self._normals, self._texcoords],
            [3, 3, 2],
            usage=self._usage
        )
        self.vbo.setAttrPointer([0, 1, 2], attr_id=[0, 1, 2])
        self.ebo = EBO(self._indices)
        self._vertexes_size = int(self._vertexes.size / 3)
        self._material.load_textures()

    def paint(self, shader):
        self._material.set_uniform(shader, "material")

        if self._indices is None:
            shader.set_uniform("material.use_texture", False, 'bool')

        self.vao.bind()
        if self._indices is not None:
            gl.glDrawElements(gl.GL_TRIANGLES, self._indices.size, gl.GL_UNSIGNED_INT, c_void_p(0))
        else:
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self._vertexes_size)

    def setMaterial(self, material=None):
        if isinstance(material, dict):
            self._material = Material(material)
        elif isinstance(material, Material):
            self._material = material

    def setMaterial_data(self, ambient, diffuse, specular, shininess, opacity=1.0):
        self._material.set_data(ambient, diffuse, specular, shininess, opacity)

    def getMaterial(self):
        return self._material

    @classmethod
    def load_model(cls, path: Union[str, Path], material=None) -> List["Mesh"]:
        meshes = list()
        directory = Path(path).parent
        face_num = 0

        start_time = time()
        post_process = (assimp.Process_Triangulate |
                        assimp.Process_FlipUVs |
                        assimp.Process_GenNormals |
                        assimp.Process_PreTransformVertices
                        )
        # assimp.Process_CalcTangentSpace 计算法线空间
        scene = assimp.ImportFile(str(path), post_process)
        # scene = _assimp.load(str(path))
        if not scene:
            raise ValueError("ERROR:: Assimp model failed to load, {}".format(path))

        is_dae = Path(path).suffix == ".dae"
        for m in scene.meshes:

            # 若模型是 dae 文件, 且其中 <up_axis>Z_UP</up_axis>, 则需要将原始坐标绕 x 轴旋转 90 度
            verts = np.array(m.vertices, dtype=np.float32).reshape(-1, 3)
            norms = np.array(m.normals, dtype=np.float32).reshape(-1, 3)
            if is_dae:  # x, y, z -> x, -z, y
                verts[:, 2] = -verts[:, 2]
                verts[:, [1, 2]] = verts[:, [2, 1]]
                norms[:, 2] = -norms[:, 2]
                norms[:, [1, 2]] = norms[:, [2, 1]]

            meshes.append(
                cls(
                    verts,
                    m.indices,
                    m.texcoords[0] if len(m.texcoords) > 0 else None,
                    norms,
                    scene.materials[m.material_index] if not material else material,
                    directory=directory,
                )
            )
            face_num += len(m.indices)

        print(f"Took {round(time() - start_time, 3)}s to load {path} (faces: {face_num})")
        del scene
        return meshes

    def update_vertex(self, vertex_index, vertex: np.ndarray):
        """

        :param vertex_index: 顶点索引
        :param vertex: 顶点坐标
        :return:
        """
        if isinstance(vertex_index, np.ndarray):  # 批量更新
            if len(vertex_index) != len(vertex):
                raise ValueError("vertex_index and vertex must have the same length")
            for i, v in zip(vertex_index, vertex):
                self._vertexes[i] = v
        elif isinstance(vertex_index, int):  # 单个更新
            self._vertexes[vertex_index] = vertex
        # 更新法线
        self._normals = vertex_normal_smooth(self._vertexes, self._indices)
        # 更新缓冲区
        self.vbo.updateData([0], [self._vertexes, self._normals, self._texcoords])

    def update_vertexes(self, vertexes: np.ndarray):
        if vertexes.shape != self._vertexes.shape:
            raise ValueError("vertexes shape must be the same as the original vertexes")
        self._vertexes = np.array(vertexes, dtype=np.float32)
        self._normals = vertex_normal_smooth(self._vertexes, self._indices)  # 更新法线
        self.vbo.updateData([0], [self._vertexes, self._normals, self._texcoords])

    def update_vertex_size(self, vertexes: np.ndarray, indices: np.ndarray):
        """
        更新数组的大小
        :param vertexes:
        :param indices:
        :return:
        """
        self._vertexes = np.array(vertexes, dtype=np.float32)
        self._indices = np.array(indices, dtype=np.uint32)
        self._normals = vertex_normal_smooth(self._vertexes, self._indices)
        self.vbo.updateData([0, 1], [self._vertexes, self._normals, self._texcoords])

    def __del__(self):
        self.vao.delete()
        self.vbo.delete()
        self.ebo.delete()


def cone(radius, height, slices=12):
    slices = max(3, slices)
    vertices = np.zeros((slices + 2, 3), dtype="f4")
    vertices[-2] = [0, 0, height]
    step = 360 / slices  # 圆每一段的角度
    for i in range(0, slices):
        p = step * i * 3.14159 / 180  # 转为弧度
        vertices[i] = [radius * math.cos(p), radius * math.sin(p), 0]
    # 构造圆锥的面索引
    indices = np.zeros((slices * 6,), dtype=np.uint32)
    for i in range(0, slices):
        indices[i * 6 + 0] = i
        indices[i * 6 + 1] = (i + 1) % slices
        indices[i * 6 + 2] = slices
        indices[i * 6 + 3] = i
        indices[i * 6 + 5] = (i + 1) % slices
        indices[i * 6 + 4] = slices + 1
    return vertices, indices.reshape(-1, 3)


class SymetryCylinderMesh:
    def __init__(self, direction: Literal['x', 'y', 'z'] = 'z'):
        """
        左右对称的柱体网格
        :param direction: 延伸方向
        """
        self.topPos = 0.0
        self.bottomPos = 0.0
        self.direction = direction
        self.topPoints: Optional[np.ndarray] = None  # 二维点集，全部为左侧点，右侧点通过变换得到
        self.bottomPoints: Optional[np.ndarray] = None  # 二维点集，全部为左侧点，右侧点通过变换得到

        # 顶面和底面的顶点数组
        self.vertexes: Optional[np.ndarray] = None
        self.normals: Optional[np.ndarray] = None

        # 点集生成过程的中间变量
        self.rightTopPoints: Optional[np.ndarray] = None  # 二维点集，右侧点
        self.rightBottomPoints: Optional[np.ndarray] = None  # 二维点集，右侧点
        self._topPoints: Optional[np.ndarray] = None  # 二维点集，所有的顶面点，从六点钟方向开始逆时针排列
        self._bottomPoints: Optional[np.ndarray] = None  # 二维点集，所有的底面点，从六点钟方向开始逆时针排列
        self.top_vert: Optional[np.ndarray] = None  # 顶面的顶点数组
        self.bottom_vert: Optional[np.ndarray] = None  # 底面的顶点数组
        self.side_vert: Optional[np.ndarray] = None  # 侧面的顶点数组

    def getVertexes(self):
        return self.vertexes

    def initPoints(self, topPoints: np.ndarray, bottomPoints: np.ndarray, topPos, bottomPos):
        """

        :param topPoints: 二维点集，全部为左侧点，从小到大。右侧点通过变换得到
        :param bottomPoints: 二维点集，全部为左侧点，从小到大。右侧点通过变换得到
        :param topPos: 顶面在延伸方向上的局部坐标
        :param bottomPos: 底面在延伸方向上的局部坐标
        :return:
        """
        if not isinstance(topPoints, np.ndarray):
            if topPoints is None:
                raise ValueError("topPoints must be initialized")
            raise ValueError("topPoints must be a numpy array")
        if not isinstance(bottomPoints, np.ndarray):
            if bottomPoints is None:
                raise ValueError("bottomPoints must be initialized")
            raise ValueError("bottomPoints must be a numpy array")
        if topPoints.shape != bottomPoints.shape:
            raise ValueError("topPoints and bottomPoints must have the same shape")
        if topPos < bottomPos:
            topPos, bottomPos = bottomPos, topPos
        elif abs(topPos - bottomPos) < 1e-6:
            raise ValueError("topPos and bottomPos must be different")
        self.topPoints = topPoints
        self.bottomPoints = bottomPoints
        self.topPos = topPos
        self.bottomPos = bottomPos

    def initVertexes(self):
        """
        返回不使用索引数组的顶点数组
        :return:
        """
        if self.topPoints is None or self.bottomPoints is None:
            raise ValueError("topPoints and bottomPoints must be initialized")
        vertexLen = self.topPoints.shape[0] * 2
        FI, LI, UI = self.getDirIndex()
        # 右侧点
        self.updateRightPoints()
        # 拼接左右点，结果为从六点钟方向开始逆时针排列的点
        self._topPoints = np.concatenate((self.topPoints, self.rightTopPoints), axis=0)
        self._bottomPoints = np.concatenate((self.bottomPoints, self.rightBottomPoints), axis=0)
        # 顶面和底面的点
        self.top_vert = np.zeros((vertexLen * 3, 3), dtype=np.float32)
        self.bottom_vert = np.zeros((vertexLen * 3, 3), dtype=np.float32)
        self._updateTopBottom(FI, LI, UI)
        self.side_vert = np.zeros((vertexLen * 6, 3), dtype=np.float32)
        self._updateSide(FI, LI, UI)
        self.vertexes = np.concatenate((self.top_vert, self.bottom_vert, self.side_vert), axis=0)
        self.normals = vertex_normal_faceNormal(self.vertexes)
        # self.normals = vertex_normal_smooth(self.vertexes, np.arange(vertexLen * 3).reshape(-1, 3))

    def updateRightPoints(self):
        self.rightTopPoints = self.topPoints.copy()
        self.rightTopPoints[:, 0] = -self.rightTopPoints[:, 0]
        self.rightBottomPoints = self.bottomPoints.copy()
        self.rightBottomPoints[:, 0] = -self.rightBottomPoints[:, 0]
        # 逆向右侧点
        self.rightTopPoints = self.rightTopPoints[::-1]
        self.rightBottomPoints = self.rightBottomPoints[::-1]

    def getDirIndex(self):
        FI = 0  # 前后方向索引
        LI = 1  # 左右方向索引
        UI = 2  # 上下方向索引
        if self.direction == 'y':
            FI = 1
            LI = 0
            UI = 2
        elif self.direction == 'z':
            FI = 2
            LI = 0
            UI = 1
        return FI, LI, UI

    def _updateTopBottom(self, FI, LI, UI):
        # 顶面和底面
        for i in range(len(self._topPoints) - 1):
            p0 = self._topPoints[i]
            p1 = self._topPoints[i + 1]
            self.top_vert[i * 3][FI] = self.topPos
            self.top_vert[i * 3][LI] = p0[0]
            self.top_vert[i * 3][UI] = p0[1]
            self.top_vert[i * 3 + 1][FI] = self.topPos
            self.top_vert[i * 3 + 1][LI] = p1[0]
            self.top_vert[i * 3 + 1][UI] = p1[1]
            self.top_vert[i * 3 + 2][FI] = self.topPos
            self.top_vert[i * 3 + 2][LI] = self._topPoints[-1][0]
            self.top_vert[i * 3 + 2][UI] = self._topPoints[-1][1]
            p0 = self._bottomPoints[i]
            p1 = self._bottomPoints[i + 1]
            self.bottom_vert[i * 3][FI] = self.bottomPos
            self.bottom_vert[i * 3][LI] = p0[0]
            self.bottom_vert[i * 3][UI] = p0[1]
            self.bottom_vert[i * 3 + 1][FI] = self.bottomPos
            self.bottom_vert[i * 3 + 1][LI] = p1[0]
            self.bottom_vert[i * 3 + 1][UI] = p1[1]
            self.bottom_vert[i * 3 + 2][FI] = self.bottomPos
            self.bottom_vert[i * 3 + 2][LI] = self._bottomPoints[-1][0]
            self.bottom_vert[i * 3 + 2][UI] = self._bottomPoints[-1][1]

    def _updateSide(self, FI, LI, UI):
        # 侧面
        if self.side_vert.shape[0] != len(self._topPoints) * 6:
            self.side_vert = np.zeros((len(self._topPoints) * 6, 3), dtype=np.float32)
        for i in range(len(self._topPoints)):
            tp0 = self._topPoints[i]
            tp1 = self._topPoints[(i + 1) % len(self._topPoints)]
            bp0 = self._bottomPoints[i]
            bp1 = self._bottomPoints[(i + 1) % len(self._bottomPoints)]
            # 第一个三角
            self.side_vert[i * 6][FI] = self.topPos
            self.side_vert[i * 6][LI] = tp0[0]
            self.side_vert[i * 6][UI] = tp0[1]
            self.side_vert[i * 6 + 1][FI] = self.bottomPos
            self.side_vert[i * 6 + 1][LI] = bp0[0]
            self.side_vert[i * 6 + 1][UI] = bp0[1]
            self.side_vert[i * 6 + 2][FI] = self.bottomPos
            self.side_vert[i * 6 + 2][LI] = bp1[0]
            self.side_vert[i * 6 + 2][UI] = bp1[1]
            # 第二个三角
            self.side_vert[i * 6 + 3][FI] = self.topPos
            self.side_vert[i * 6 + 3][LI] = tp0[0]
            self.side_vert[i * 6 + 3][UI] = tp0[1]
            self.side_vert[i * 6 + 4][FI] = self.bottomPos
            self.side_vert[i * 6 + 4][LI] = bp1[0]
            self.side_vert[i * 6 + 4][UI] = bp1[1]
            self.side_vert[i * 6 + 5][FI] = self.topPos
            self.side_vert[i * 6 + 5][LI] = tp1[0]
            self.side_vert[i * 6 + 5][UI] = tp1[1]

    def addPoint(self, point: tuple, side: Literal['top', 'bottom']):
        """
        添加一个点
        :param point: 点坐标
        :param side: 添加到顶面还是底面
        :return:
        """
        if self.topPoints is None or self.bottomPoints is None:
            raise ValueError("topPoints and bottomPoints must be initialized")
        # 将点根据y坐标排序放入点集
        if side == 'top':
            # 在顶面点集中插入点
            self.topPoints = np.append(self.topPoints, np.array(point).reshape(1, 2), axis=0)  # 扩容
            idx = np.searchsorted(self.topPoints[:, 1], point[1])  # 二分查找
            self.topPoints = np.insert(self.topPoints, idx, point, axis=0)
            # 在底面点集中用线性插值插入y相同的点
            self.bottomPoints = np.append(self.bottomPoints, np.array(point).reshape(1, 2), axis=0)
            self.bottomPoints = np.insert(self.bottomPoints, idx, point, axis=0)
            # 拟合底面点集
            self.bottomPoints = self._fitX(self.topPoints, self.bottomPoints, idx)
        elif side == 'bottom':
            # 在底面点集中插入点
            self.bottomPoints = np.append(self.bottomPoints, np.array(point).reshape(1, 2), axis=0)
            idx = np.searchsorted(self.bottomPoints[:, 1], point[1])
            self.bottomPoints = np.insert(self.bottomPoints, idx, point, axis=0)
            # 在顶面点集中用线性插值插入y相同的点
            self.topPoints = np.append(self.topPoints, np.array(point).reshape(1, 2), axis=0)
            self.topPoints = np.insert(self.topPoints, idx, point, axis=0)
            # 拟合顶面点集
            self.topPoints = self._fitX(self.bottomPoints, self.topPoints, idx)
        vertexLen = self.topPoints.shape[0] * 2 - 2
        # 更新点集
        self.updateRightPoints()
        FI, LI, UI = self.getDirIndex()
        # 拼接左右点，结果为从六点钟方向开始逆时针排列的点
        self._topPoints = np.concatenate((self.topPoints, self.rightTopPoints), axis=0)
        self._bottomPoints = np.concatenate((self.bottomPoints, self.rightBottomPoints), axis=0)
        # 顶面和底面的点
        self.top_vert = np.zeros((vertexLen * 3, 3), dtype=np.float32)
        self.bottom_vert = np.zeros((vertexLen * 3, 3), dtype=np.float32)
        self._updateTopBottom(FI, LI, UI)
        # 侧面
        self._updateSide(FI, LI, UI)
        self.vertexes = np.concatenate((self.top_vert, self.bottom_vert, self.side_vert), axis=0)
        # self.normals = vertex_normal_faceNormal(self.vertexes)
        self.normals = vertex_normal_smooth(self.vertexes, None)

    def updateTopPoint(self, idx, point: tuple, updateBottom=True):
        """
        更新顶面点
        :param idx: 索引
        :param point: 新的点坐标
        :param updateBottom: 当新点坐标的y值与底面相应索引的y值相同时，是否更新底面点
        :return:
        """
        if self.topPoints is None or self.bottomPoints is None:
            raise ValueError("topPoints and bottomPoints must be initialized")
        updateBottom = False if abs(self.bottomPoints[idx][1] - point[1]) < 1e-6 else updateBottom
        self.topPoints[idx] = point
        # 更新对称点
        right_idx = idx
        for i in range(idx - 1, idx + 2):
            if abs(self.topPoints[i][1] - point[1]) < 1e-6:
                right_idx = i
                self.rightTopPoints[i][0] = -point[0]
                self.rightTopPoints[i][1] = point[1]
                break
        # 更新顶面点
        self._topPoints[idx] = point  # 左
        self._topPoints[len(self.topPoints) + right_idx] = (-point[0], point[1])  # 右
        # 更新顶点数组
        FI, LI, UI = self.getDirIndex()
        self._updateTopVertex(idx, point, FI, LI, UI)
        if updateBottom:
            self.bottomPoints[idx][1] = point[1]
            self.rightBottomPoints[right_idx][1] = point[1]
            # 更新底面点
            self._bottomPoints[idx][1] = point[1]  # 左
            self._bottomPoints[len(self.bottomPoints) + right_idx][1] = point[1]  # 右
            self._updateBottomVertex(idx, point, FI, LI, UI)
        self._updateNormal(idx, point, FI, LI, UI)

    def updateBottomPoint(self, idx, point: tuple, updateTop=True):
        """
        更新底面点
        :param idx: 索引
        :param point: 新的点坐标
        :param updateTop: 当新点坐标的y值与顶面相应索引的y值相同时，是否更新顶面点
        :return:
        """
        if self.topPoints is None or self.bottomPoints is None:
            raise ValueError("topPoints and bottomPoints must be initialized")
        updateTop = False if abs(self.topPoints[idx][1] - point[1]) < 1e-6 else updateTop
        self.bottomPoints[idx] = point
        # 更新对称点
        right_idx = idx
        for i in range(idx - 1, idx + 2):
            if abs(self.bottomPoints[i][1] - point[1]) < 1e-6:
                right_idx = i
                self.rightBottomPoints[i][0] = -point[0]
                self.rightBottomPoints[i][1] = point[1]
                break
        # 更新底面点
        self._bottomPoints[idx] = point  # 左
        self._bottomPoints[len(self.bottomPoints) + right_idx] = (-point[0], point[1])  # 右
        # 更新底面点数组
        FI, LI, UI = self.getDirIndex()
        self._updateBottomVertex(idx, point, FI, LI, UI)
        if updateTop:
            self.topPoints[idx][1] = point[1]
            self.rightTopPoints[right_idx][1] = point[1]
            # 更新顶面点
            self._topPoints[idx][1] = point[1]
            self._topPoints[len(self.topPoints) + right_idx][1] = point[1]
            self._updateTopVertex(idx, point, FI, LI, UI)
        self._updateNormal(idx, point, FI, LI, UI)

    def _updateTopVertex(self, idx, point, FI, LI, UI):
        ...
        # # 更新顶面
        # if idx == 0:
        #     p0 = self._topPoints[0]
        #     p1 = self._topPoints[1]
        #     self.top_vert[0][FI] = self.topPos
        #     self.top_vert[0][LI] = p0[0]
        #     self.top_vert[0][UI] = p0[1]
        #     self.top_vert[1][FI] = self.topPos
        #     self.top_vert[1][LI] = p1[0]
        #     self.top_vert[1][UI] = p1[1]
        # elif idx == len(self._topPoints) - 1:
        #     p0 = self._topPoints[-2]
        #     p1 = self._topPoints[-1]
        #     self.top_vert[-2][FI] = self.topPos
        #     self.top_vert[-2][LI] = p0[0]
        #     self.top_vert[-2][UI] = p0[1]
        #     self.top_vert[-1][FI] = self.topPos
        #     self.top_vert[-1][LI] = p1[0]
        #     self.top_vert[-1][UI] = p1[1]
        # else:
        #     p0 = self._topPoints[idx - 1]
        #     p1 = self._topPoints[idx]
        #     p2 = self._topPoints[idx + 1]
        #     self.top_vert[idx * 3][FI] = self.topPos
        #     self.top_vert[idx * 3][LI] = p0[0]
        #     self.top_vert[idx * 3][UI] = p0[1]
        #     self.top_vert[idx * 3 + 1][FI] = self.topPos
        #     self.top_vert[idx * 3 + 1][LI] = p1[0]
        #     self.top_vert[idx * 3 + 1][UI] = p1[1]
        #     self.top_vert[idx * 3 + 2][FI] = self.topPos
        #     self.top_vert[idx * 3 + 2][LI] = p2[0]
        #     self.top_vert[idx * 3 + 2][UI] = p2[1]

    def _updateBottomVertex(self, idx, point, FI, LI, UI):
        ...

    def _updateNormal(self, idx, point, FI, LI, UI):
        ...

    def _fitX(self, srcPoints, dstPoints, idx):  # noqa
        """
        拟合点集
        :param srcPoints: 拟合的源点集
        :param dstPoints: 拟合的目标点集
        :param idx: 需要拟合的索引
        :return:
        """
        # TODO:
        return dstPoints


def direction_matrixs(starts, ends):
    arrows = ends - starts
    arrows = arrows.reshape(-1, 3)
    # 处理零向量，归一化
    arrow_lens = np.linalg.norm(arrows, axis=1)
    zero_idxs = arrow_lens < 1e-3
    arrows[zero_idxs] = [0, 0, 1]
    arrow_lens[zero_idxs] = 1
    arrows = arrows / arrow_lens[:, np.newaxis]
    # 构造标准箭头到目标箭头的旋转矩阵
    T = np.zeros_like(arrows)
    B = np.zeros_like(arrows)
    mask = arrows[:, 2] < -0.99999
    T[mask, 1] = -1
    B[mask, 0] = -1
    mask = np.logical_not(mask)
    a = 1 / (1 + arrows[mask, 2])
    b = -arrows[mask, 0] * arrows[mask, 1] * a
    T[mask] = np.stack((
        1 - arrows[mask, 0] * arrows[mask, 0] * a,
        b,
        -arrows[mask, 0],
    ), axis=1)
    B[mask] = np.stack((
        b,
        1 - arrows[mask, 1] * arrows[mask, 1] * a,
        -arrows[mask, 1],
    ), axis=1)
    # 转化成齐次变换矩阵
    transforms = np.stack((T, B, arrows, ends.reshape(-1, 3)), axis=1)  # (n, 4(new), 3)
    transforms = np.pad(transforms, ((0, 0), (0, 0), (0, 1)), mode="constant", constant_values=0)  # (n, 4, 4)
    transforms[:, 3, 3] = 1
    # 将 arrow_vert(n, 3) 变换至目标位置
    # vertexes = vertexes @ transforms  #  (n, 3)
    return transforms.copy()


def get_sphere_uv(verts):
    """采样球面贴图 verts: [n, 3]"""
    r = np.sqrt(verts[0, 0] ** 2 + verts[0, 1] ** 2 + verts[0, 2] ** 2)
    v = verts / r
    uv = np.zeros((verts.shape[0], 2), dtype=np.float32)
    uv[:, 0] = np.arctan2(v[:, 0], v[:, 1])
    uv[:, 1] = np.arcsin(v[:, 2])
    uv *= np.array([1 / (2 * np.pi), 1 / np.pi])
    uv += 0.5
    return uv


def sphere(radius=1.0, rows=12, cols=12, calc_uv_norm=False):
    """
        Return a MeshData instance with vertexes and faces computed
        for a spherical surface.
    """
    if rows > 2048:
        raise RuntimeWarning("rows > 2048, may cause memory error")
    if cols > 2048:
        raise RuntimeWarning("cols > 2048, may cause memory error")
    verts = np.empty((rows + 1, cols + 1, 3), dtype=np.float32)

    # compute vertexes
    phi = np.linspace(0, np.pi, rows + 1, dtype=np.float32).reshape(rows + 1, 1)
    s = radius * np.sin(phi)
    verts[..., 2] = radius * np.cos(phi)

    th = np.linspace(0, 2 * np.pi, cols + 1, dtype=np.float32).reshape(1, cols + 1)
    verts[..., 0] = s * np.cos(th)
    verts[..., 1] = s * np.sin(th)
    verts = verts.reshape(-1, 3)

    # compute faces
    faces = np.empty((rows, 2, cols, 3), dtype=np.uint32)
    rowtemplate1 = np.arange(cols).reshape(1, cols, 1) + np.array([[[0, cols + 1, 1]]])  # 1, cols, 3
    rowtemplate2 = np.arange(cols).reshape(1, cols, 1) + np.array([[[cols + 1, cols + 2, 1]]])  # 1, cols, 3
    rowbase = np.arange(rows).reshape(rows, 1, 1) * (cols + 1)  # nrows, 1, 1
    faces[:, 0] = (rowtemplate1 + rowbase)  # nrows, 1, ncols, 3
    faces[:, 1] = (rowtemplate2 + rowbase)

    faces = faces.reshape(-1, 3)
    faces = faces[cols:-cols]  # cut off zero-area triangles at top and bottom

    # compute uv and normals
    if calc_uv_norm:
        uv = np.zeros((rows + 1, cols + 1, 2), dtype=np.float32)
        uv[..., 0] = th / (2 * np.pi)
        uv[..., 1] = phi / np.pi
        uv = uv.reshape(-1, 2)
        norms = verts / radius  # rows, cols, 2
        return verts, faces, uv, norms

    return verts, faces


def cylinder(radius=None, length=1.0, rows=12, cols=12, offset=False):
    """
    Return a MeshData instance with vertexes and faces computed
    for a cylindrical surface.
    The cylinder may be tapered with different radii at each end (truncated cone)
    """
    if radius is None:
        radius = [1.0, 1.0]
    verts = np.empty(((rows + 3) * cols + 2, 3), dtype=np.float32)  # 顶面的点和底面的点重复一次, 保证法线计算正确
    verts1 = verts[:(rows + 1) * cols, :].reshape(rows + 1, cols, 3)
    if isinstance(radius, int):
        radius = [radius, radius]  # convert to list
    ## compute vertexes
    th = np.linspace(2 * np.pi, (2 * np.pi) / cols, cols).reshape(1, cols)
    r = np.linspace(radius[0], radius[1], num=rows + 1, endpoint=True).reshape(rows + 1, 1)  # radius as a function of z
    verts1[..., 2] = np.linspace(0, length, num=rows + 1, endpoint=True).reshape(rows + 1, 1)  # z
    if offset:
        th = th + ((np.pi / cols) * np.arange(rows + 1).reshape(rows + 1, 1))  ## rotate each row by 1/2 column
    verts1[..., 0] = r * np.cos(th)  # x = r cos(th)
    verts1[..., 1] = r * np.sin(th)  # y = r sin(th)
    verts1 = verts1.reshape((rows + 1) * cols, 3)  # just reshape: no redundant vertices...
    # 顶面, 底面
    verts[(rows + 1) * cols:(rows + 2) * cols] = verts1[-cols:]
    verts[(rows + 2) * cols:-2] = verts1[:cols]
    verts[-2] = [0, 0, 0]  # zero at bottom
    verts[-1] = [0, 0, length]  # length at top

    ## compute faces
    num_side_faces = rows * cols * 2
    num_cap_faces = cols
    faces = np.empty((num_side_faces + num_cap_faces * 2, 3), dtype=np.uint32)
    rowtemplate1 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 0, 1]])) % cols) + np.array([[0, cols, 0]])
    rowtemplate2 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 1]])) % cols) + np.array([[cols, cols, 0]])
    for row in range(rows):
        start = row * cols * 2
        faces[start:start + cols] = rowtemplate1 + row * cols
        faces[start + cols:start + (cols * 2)] = rowtemplate2 + row * cols

    # Bottom face
    bottom_start = num_side_faces
    bottom_row = np.arange((rows + 2) * cols, (rows + 3) * cols)
    bottom_face = np.column_stack((bottom_row, np.roll(bottom_row, -1), np.full(cols, (rows + 3) * cols)))
    faces[bottom_start: bottom_start + num_cap_faces] = bottom_face

    # Top face
    top_start = num_side_faces + num_cap_faces
    top_row = np.arange((rows + 1) * cols, (rows + 2) * cols)
    top_face = np.column_stack((np.roll(top_row, -1), top_row, np.full(cols, (rows + 3) * cols + 1)))
    faces[top_start: top_start + num_cap_faces] = top_face

    return verts, faces


def cube(x, y, z):
    """
    Return a MeshData instance with vertexes and normals computed
    for a rectangular cuboid of the given dimensions.
    """
    vertices = np.array([
        # 顶点坐标             # 法向量       # 纹理坐标
        -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0,
        0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 0.0,
        0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1.0,
        0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1.0,
        -0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0,
        -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0,

        -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,
        0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 1.0,
        -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,

        -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 0.0,
        -0.5, 0.5, -0.5, -1.0, 0.0, 0.0, 1.0, 1.0,
        -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1.0,
        -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1.0,
        -0.5, -0.5, 0.5, -1.0, 0.0, 0.0, 0.0, 0.0,
        -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 0.0,

        0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
        0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 1.0,
        0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 1.0,
        0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 1.0,
        0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 0.0,

        -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 1.0,
        0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 1.0, 1.0,
        0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1.0, 0.0,
        0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1.0, 0.0,
        -0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.0, 0.0,
        -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 1.0,

        -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0,
        0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 1.0,
        0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0,
        -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0,
    ], dtype="f4").reshape(-1, 8)
    verts = vertices[:, :3] * np.array([x, y, z], dtype="f4")
    normals = vertices[:, 3:6]
    texcoords = vertices[:, 6:]
    return verts, normals, texcoords


def plane(x, y):
    """
    返回一个平面的顶点坐标和法向量
    :param x:
    :param y:
    :return:
    """
    vertices = np.array([
        # 顶点坐标             # 法向量       # 纹理坐标
        -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0,
        0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0,
        0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0,
        -0.5, 0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
        -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
    ], dtype=np.float32).reshape(-1, 8)
    verts = vertices[:, :3] * np.array([x, y, 1.0], dtype="f4")
    normals = vertices[:, 3:6]
    texcoords = vertices[:, 6:]
    return verts, normals, texcoords


def face_normal(v1, v2, v3):
    """计算一个三角形的法向量"""
    a = v2 - v1  # 三角形的一条边
    b = v3 - v1  # 三角形的另一条边
    return np.cross(a, b)


def vertex_normal_smooth(vert, ind):
    """计算每个顶点的法向量，显示会平滑一些"""
    if ind is None:
        ind = np.arange(len(vert))
    nv = len(vert)  # 顶点的个数
    nf = len(ind)  # 面的个数
    norm = np.zeros((nv, 3), np.float32)  # 初始化每个顶点的法向量为零向量
    for i in range(nf):  # 遍历每个面
        v1, v2, v3 = vert[ind[i]]  # 获取面的三个顶点
        fn = face_normal(v1, v2, v3)  # 计算面的法向量
        norm[ind[i]] += fn  # 将面的法向量累加到对应的顶点上
    norm_len = np.linalg.norm(norm, axis=1, keepdims=True)  # 计算每个顶点的法向量的长度
    norm_len[norm_len < 1e-5] = 1  # 处理零向量
    norm = norm / norm_len  # 归一化每个顶点的法向量
    return norm


def vertex_normal_faceNormal(vert):
    """生成面法向量"""
    nv = len(vert)  # 顶点的个数
    norm = np.zeros((nv, 3), np.float32)  # 初始化每个顶点的法向量为零向量
    for i in range(0, nv, 3):  # 遍历每个面
        v1, v2, v3 = vert[i:i + 3]  # 获取面的三个顶点
        fn = face_normal(v1, v2, v3)  # 计算面的法向量
        norm[i:i + 3] = fn  # 将面的法向量赋值给对应的顶点
    # 处理零向量
    norm_len = np.linalg.norm(norm, axis=1, keepdims=True)
    norm_len[norm_len < 1e-5] = 1
    norm = norm / norm_len
    return norm


def vertex_normal_certain_index(org_normals, verts, face_index):
    """
    只更新指定索引的某单个顶点的法向量
    :param org_normals: 原始法向量集
    :param verts: 更新的顶点坐标：([x, y, z], [x, y, z], [x, y, z])
    :param face_index: 新顶点的索引
    :return:
    """
    vert_i = 3 * face_index
    v1, v2, v3 = verts
    fn = face_normal(v1, v2, v3)
    fn /= np.linalg.norm(fn)  # 归一化
    org_normals[vert_i:vert_i + 3] = fn  # 将面的法向量赋值给对应的顶点
    return org_normals


def surface(zmap, xy_size):
    x_size, y_size = xy_size
    h, w = zmap.shape
    scale = x_size / w
    zmap *= scale

    x = np.linspace(-x_size / 2, x_size / 2, w, dtype='f4')
    y = np.linspace(y_size / 2, -y_size / 2, h, dtype='f4')

    xgrid, ygrid = np.meshgrid(x, y, indexing='xy')
    verts = np.stack([xgrid, ygrid, zmap.astype('f4')], axis=-1).reshape(-1, 3)

    # calc indices
    ncol = w - 1
    nrow = h - 1
    if ncol == 0 or nrow == 0:
        raise Exception("cols or rows is zero")

    faces = np.empty((nrow, 2, ncol, 3), dtype=np.uint32)
    rowtemplate1 = np.arange(ncol).reshape(1, ncol, 1) + np.array([[[0, ncol + 1, 1]]])  # 1, ncols, 3
    rowtemplate2 = np.arange(ncol).reshape(1, ncol, 1) + np.array([[[ncol + 1, ncol + 2, 1]]])
    rowbase = np.arange(nrow).reshape(nrow, 1, 1) * (ncol + 1)  # nrows, 1, 1
    faces[:, 0] = (rowtemplate1 + rowbase)  # nrows, 1, ncols, 3
    faces[:, 1] = (rowtemplate2 + rowbase)

    return verts, faces.reshape(-1, 3)


def grid3d(grid):
    # grid: (h, w, 3)
    h, w = grid.shape[:2]
    ncol, nrow = w - 1, h - 1

    rowtemplate = np.arange(ncol, dtype=np.uint32).reshape(1, ncol, 1) + \
                  np.array([[[0, ncol + 1, ncol + 2, 1]]])  # 1, ncols, 4
    rowbase = np.arange(nrow, dtype=np.uint32).reshape(nrow, 1, 1) * (ncol + 1)  # nrows, 1, 1
    faces = (rowtemplate + rowbase).reshape(-1, 4).astype(np.uint32)

    return grid.reshape(-1, 3).astype(np.float32), faces


def mesh_concat(verts: list, faces: list):
    """合并多个网格"""

    vert_nums = [len(v) for v in verts]
    id_bias = np.cumsum(vert_nums)
    for i in range(1, len(faces)):
        faces[i] += id_bias[i - 1]

    verts = np.concatenate(verts, axis=0)
    faces = np.concatenate(faces, axis=0).astype(np.uint32)

    return verts, faces


class EditItemMaterial(Material):
    def __init__(self, color: Union[Tuple[float, float, float], Tuple[int, int, int], QColor] = (128, 128, 128),
                 lightness: float = 0.8):
        if isinstance(color, QColor):
            self._color = color
        elif isinstance(color[0], int):
            self._color = QColor(*color)
        else:
            self._color = QColor(*[int(c * 255) for c in color])
        self.lightness = lightness
        col = self._color.getRgbF()[:3]
        diffuse = (col[0] * 0.2 + 0.1, col[1] * 0.2 + 0.1, col[2] * 0.2 + 0.1)  # 映射到[0.1, 0.3]
        col = (col[0] * self.lightness, col[1] * self.lightness, col[2] * self.lightness)
        super().__init__(
            ambient=col,
            diffuse=diffuse,
            specular=(0.1, 0.1, 0.1),  # 高光颜色
            shininess=16.,
            opacity=1.0
        )

    def setColor(self, r: int = 128, g: int = 128, b: int = 128):
        self._color = QColor(r, g, b)
        col = self._color.getRgbF()[:3]
        diffuse = (col[0] * 0.2 + 0.1, col[1] * 0.2 + 0.1, col[2] * 0.2 + 0.1)  # 映射到[0.1, 0.3]
        col = (col[0] * self.lightness, col[1] * self.lightness, col[2] * self.lightness)
        self.set_data(ambient=col, diffuse=diffuse)

    def setLightness(self, lightness: float):
        self.lightness = lightness
        col = self._color.getRgbF()[:3]
        col = (col[0] * self.lightness, col[1] * self.lightness, col[2] * self.lightness)
        self.set_data(ambient=col)

    def getColor(self) -> tuple[int]:
        return self._color.getRgb()[:3]
