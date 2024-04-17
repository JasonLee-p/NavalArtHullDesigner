from pathlib import Path

import OpenGL.GL as gl
import numpy as np

from .BufferObject import VAO, VBO, EBO, c_void_p
from .MeshData import Material, surface
from .light import LightMixin, light_fragment_shader
from .shader import Shader
from .texture import Texture2D
from ..GLGraphicsItem import GLGraphicsItem
from ..transform3d import Matrix4x4

BASE_DIR = Path(__file__).resolve().parent

__all__ = ['GLSurfacePlotItem']


def gaussian_kernel(size: tuple, sigma: float):
    x = np.arange(-size[0] // 2 + 1, size[0] // 2 + 1)
    y = np.arange(-size[1] // 2 + 1, size[1] // 2 + 1)
    x, y = np.meshgrid(x, y)
    kernel = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
    return kernel / kernel.sum()


def convolve2d(image: np.ndarray, kernel: np.ndarray, mode='same'):
    return np.real(np.fft.ifft2(np.fft.fft2(image) * np.fft.fft2(kernel, s=image.shape)))


def gaussian_blur(image: np.ndarray, size: tuple, sigma: float):
    if sigma == 0:
        return image
    kernel = gaussian_kernel(size, sigma)
    return convolve2d(image, kernel, mode='same')


class GLSurfacePlotItem(GLGraphicsItem, LightMixin):

    def __init__(
            self,
            zmap=None,
            x_size=10,  # scale width to this size
            material=None,
            lights=None,
            glOptions='translucent',
            parentItem=None
    ):
        super().__init__(parentItem=parentItem)
        if material is None:
            material = dict()
        if lights is None:
            lights = list()
        self.setGLOptions(glOptions)

        self._zmap = None
        self._shape = (0, 0)
        self._x_size = x_size
        self._vert_update_flag = False
        self._indice_update_flag = False
        self._vertexes = None
        self._normals = None
        self._indices = None
        self.scale_ratio = 1
        self.normal_texture = Texture2D(None, flip_x=False, flip_y=True)

        self.setData(zmap)

        # material
        self.setMaterial(material)

        # light
        self.addLight(lights)

    def setData(self, zmap=None):
        if zmap is not None:
            self.update_vertexs(np.array(zmap, dtype=np.float32))

        self.update()

    def update_vertexs(self, zmap):
        self._vert_update_flag = True
        h, w = zmap.shape
        self.scale_ratio = self._x_size / w

        # calc vertexes
        if self._shape != zmap.shape:

            self._shape = zmap.shape
            self._indice_update_flag = True

            self.xy_size = (self._x_size, self.scale_ratio * h)

            self._vertexes, self._indices = surface(zmap, self.xy_size)

        else:
            self._vertexes[:, 2] = zmap.reshape(-1) * self.scale_ratio

        # calc normals texture
        v = self._vertexes[self._indices]  # Nf x 3 x 3
        v = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])  # face Normal Nf(c*r*2) x 3
        v = v.reshape(h - 1, 2, w - 1, 3).sum(axis=1, keepdims=False)  # r x c x 3
        # v = cv2.GaussianBlur(v, (5, 5), 0)  #
        v = gaussian_blur(v, (5, 5), 0)
        self._normal_texture = v / np.linalg.norm(v, axis=-1, keepdims=True)
        self.normal_texture.updateTexture(self._normal_texture)

    def initializeGL(self):
        self.shader = Shader(vertex_shader, light_fragment_shader)
        self.vao = VAO()
        self.vbo = VBO([None], [3], usage=gl.GL_DYNAMIC_DRAW)
        self.vbo.setAttrPointer([0], attr_id=[0])
        self.ebo = EBO(None)

    def updateGL(self):
        if not self._vert_update_flag:
            return

        self.vao.bind()
        self.vbo.updateData([0], [self._vertexes])

        if self._indice_update_flag:
            self.ebo.updateData(self._indices)

        self._vert_update_flag = False
        self._indice_update_flag = False

    def paint(self, model_matrix=Matrix4x4()):
        if self._shape[0] == 0:
            return
        self.updateGL()
        self.setupGLState()

        self.setupLight(self.shader)

        with self.shader:
            self.vao.bind()
            self.normal_texture.bind()

            self.shader.set_uniform("view", self.proj_view_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")

            self._material.set_uniform(self.shader, "material")
            self.shader.set_uniform("norm_texture", self.normal_texture, "sampler2D")

            self.shader.set_uniform("texScale", self.xy_size, "vec2")
            # print("  ", gl.glGetActiveUniform(self.shader.ID, 1, 256))

            gl.glDrawElements(gl.GL_TRIANGLES, self._indices.size, gl.GL_UNSIGNED_INT, c_void_p(0))

    def setMaterial(self, material):
        if isinstance(material, dict):
            self._material = Material(material)
        elif isinstance(material, Material):
            self._material = material

    def getMaterial(self):
        return self._material


vertex_shader = """
#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoords;

uniform mat4 view;
uniform mat4 model;
uniform vec2 texScale;
uniform sampler2D norm_texture;

void main() {
    TexCoords = (aPos.xy + texScale/2) / texScale;
    vec3 aNormal = texture(norm_texture, TexCoords).rgb;
    Normal = normalize(mat3(transpose(inverse(model))) * aNormal);

    FragPos = vec3(model * vec4(aPos, 1.0));
    gl_Position = view * vec4(FragPos, 1.0);
}
"""
