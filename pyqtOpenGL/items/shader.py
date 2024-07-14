import OpenGL.GL as gl
from OpenGL.GL import shaders
import numpy as np
import os
from .texture import Texture2D

__all__ = ['Shader']


def _load(shader_source):
    """
    如果shader_source是文件路径，则读取文件内容，否则直接返回shader_source
    """
    if os.path.exists(shader_source):
        with open(shader_source, 'r') as shader_file:
            shader_source = shader_file.readlines()
    return shader_source


class Shader:

    def __init__(self, vertex_str, fragment_str, geometry_str=None, uniform_data=None):
        if geometry_str is not None:
            self.ID = shaders.compileProgram(
                shaders.compileShader(_load(vertex_str), gl.GL_VERTEX_SHADER),
                shaders.compileShader(_load(fragment_str), gl.GL_FRAGMENT_SHADER),
                shaders.compileShader(_load(geometry_str), gl.GL_GEOMETRY_SHADER),
            )
        else:
            self.ID = shaders.compileProgram(
                shaders.compileShader(_load(vertex_str), gl.GL_VERTEX_SHADER),
                shaders.compileShader(_load(fragment_str), gl.GL_FRAGMENT_SHADER),
            )
        if uniform_data is None:
            self.uniform_data: dict = dict()
        else:
            self.uniform_data: dict = uniform_data
        self._in_use = False

    def set_uniform(self, name, data, type_: str):
        if self._in_use:
            self.__set_uniform(name, data, type_)
        else:
            self.uniform_data[name] = (data, type_)

    def use(self):
        # print("use shader", self.ID)
        gl.glUseProgram(self.ID)
        self._in_use = True
        try:  # load uniform values into program
            for key, data in self.uniform_data.items():
                self.__set_uniform(key, *data)
            self.uniform_data.clear()
        except Exception as e:
            gl.glUseProgram(0)
            raise

    def unuse(self):
        self._in_use = False
        gl.glUseProgram(0)
        # clear used texture unit, so that other shader can use it.
        Texture2D.UnitCnt = 0

    def __enter__(self):
        self.use()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"An exception occurred: {exc_type}: {exc_value}")
        self.unuse()

    def __set_uniform(self, name, value, type_: str, cnt=1):
        # print("  set uniform", name, value, type)
        if type_ in ["bool", "int"]:
            gl.glUniform1iv(gl.glGetUniformLocation(self.ID, name), cnt, np.array(value, dtype=np.int32))
        elif type_ == "sampler2D":
            gl.glUniform1i(gl.glGetUniformLocation(self.ID, name), np.array(value.unit, dtype=np.int32))
            # gl.glUniform1iv(gl.glGetUniformLocation(self.ID, name), cnt, np.array(value.unit, dtype=np.int32))
        elif type_ == "float":
            gl.glUniform1fv(gl.glGetUniformLocation(self.ID, name), cnt, np.array(value, dtype=np.float32))
        elif type_ == "vec2":
            gl.glUniform2fv(gl.glGetUniformLocation(self.ID, name), cnt, np.array(value, dtype=np.float32))
        elif type_ == "vec3":
            gl.glUniform3fv(gl.glGetUniformLocation(self.ID, name), cnt, np.array(value, dtype=np.float32))
        elif type_ == "vec4":
            gl.glUniform4fv(gl.glGetUniformLocation(self.ID, name), cnt, np.array(value, dtype=np.float32))
        elif type_ == "mat3":
            gl.glUniformMatrix3fv(gl.glGetUniformLocation(self.ID, name), cnt, gl.GL_FALSE,
                                  np.array(value, dtype=np.float32))
        elif type_ == "mat4":
            gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.ID, name), cnt, gl.GL_FALSE,
                                  np.array(value, dtype=np.float32))

    def delete(self):
        gl.glDeleteProgram(self.ID)
