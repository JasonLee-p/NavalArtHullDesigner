"""
缓冲区对象
"""
from ctypes import c_void_p
from typing import List

import OpenGL.GL as gl
import numpy as np

GL_Type = {
    np.dtype("f4"): gl.GL_FLOAT,
    np.dtype("u4"): gl.GL_UNSIGNED_INT,
    np.dtype("f2"): gl.GL_HALF_FLOAT,
}


class MemoryBlock:
    def __init__(
            self,
            blocks: List[np.ndarray],
            dsize,
    ):
        # 初始化内存块
        self.block_lens = [0 if x is None else x.nbytes for x in blocks]
        self.block_used = np.array(self.block_lens, dtype=np.uint32)
        self.block_offsets = [0] + np.cumsum(self.block_lens).tolist()[:-1]
        self.sum_lens = sum(self.block_lens)
        self.dtype = [np.dtype('f4') if x is None else x.dtype for x in blocks]

        # 属性相关设置
        self.attr_size = [[4, 4, 4, 4] if x == 16 else x for x in dsize]
        id_ = 0
        self.attr_idx = []
        for size in self.attr_size:
            if isinstance(size, list):
                self.attr_idx.append(list(range(id_, id_ + len(size))))
                id_ += len(size)
            else:  # isinstance(size, int)
                self.attr_idx.append(id_)
                id_ += 1

    def setBlock(self, ids: List[int], blocks: List[int]):
        """设置内存块大小，返回复制的块和保持的块

        :param ids: 内存块的id
        :param blocks: 内存块的新长度
        :return:
            copy_blocks: 更新数据应该复制到的内存位置，列表形式，每个元素为[写入偏移量, 大小]
            keep_blocks: 未更新数据应该复制到的内存位置，列表形式，每个元素为[读取偏移量, 大小, 写入偏移量]
            extend: 缓冲区是否扩展了
        """
        extend = False
        keep_blocks = []  # 读取偏移量, 大小, 写入偏移量
        copy_blocks = []  # 写入偏移量, 大小
        ptr = 0

        # 更新块大小和块使用情况，并计算保持块
        for _id, _len in zip(ids, blocks):
            t = self.block_offsets[_id] - ptr
            if t > 0:
                keep_blocks.append([ptr, t, _id])  # 读取偏移量, 大小, id(然后转换为写入偏移量)

            ptr = self.block_offsets[_id] + self.block_lens[_id]
            self.block_used[_id] = _len
            if _len > self.block_lens[_id]:
                self.block_lens[_id] = _len
                extend = True
        if ptr < self.sum_lens:
            keep_blocks.append([ptr, self.sum_lens - ptr, -1])

        if extend:
            self.block_offsets = [0] + np.cumsum(self.block_lens).tolist()[:-1]  # 更新块偏移量
            self.sum_lens = sum(self.block_lens)
            for kb in keep_blocks:  # 计算写入偏移量
                _id = kb[2]
                end = self.block_offsets[_id] if _id != -1 else self.sum_lens
                kb[2] = end - kb[1]

        for _id, _len in zip(ids, blocks):
            copy_blocks.append([self.block_offsets[_id], _len])  # 写入偏移量, 大小

        return copy_blocks, keep_blocks, extend

    def locBlock(self, _id):
        return self.block_offsets[_id], self.block_lens[_id]

    @property
    def nblocks(self):
        return len(self.block_lens)

    @property
    def nbytes(self):
        return self.sum_lens

    def __len__(self):
        return self.sum_lens

    def __getitem__(self, _id):
        return {
            "offset": self.block_offsets[_id],
            "length": self.block_lens[_id],
            "used": self.block_used[_id],
            "dtype": self.dtype[_id],
            "attr_size": self.attr_size[_id],
            "attr_idx": self.attr_idx[_id],
        }

    def __repr__(self) -> str:
        _repr = "|"
        for i in range(len(self.block_lens)):
            _repr += f"{self.block_offsets[i]}> {self.block_used[i]}/{self.block_lens[i]}|"
        return _repr


class VBO:
    def __init__(
            self,
            data: List[np.ndarray],
            size: List[int],  # 3为vec3，16为mat4
            usage=gl.GL_STATIC_DRAW,
    ):
        self._usage = usage
        self.blocks = MemoryBlock(data, size)

        # 缓冲区数据
        self._vbo = gl.glGenBuffers(1)
        if self.blocks.nbytes > 0:
            self.bind()
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.blocks.nbytes, None, self._usage)
        self.updateData([i for i in range(len(data))], data)

    def _loadSubDatas(self, block_id: List[int], data: List[np.ndarray]):
        """加载数据到缓冲区"""
        self.bind()

        for _id, da in zip(block_id, data):
            offset = int(self.blocks.block_offsets[_id])
            length = int(self.blocks.block_used[_id])
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, offset, length, da)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def updateData(self, block_id: List[int], data: List[np.ndarray]):
        """更新数据到缓冲区，首先检查是否需要扩展缓冲区"""
        self.bind()
        old_nbytes = self.blocks.nbytes
        copy_blocks, keep_blocks, extend = self.blocks.setBlock(
            block_id,
            [0 if x is None else x.nbytes for x in data]
        )
        if self.blocks.nbytes == 0:
            return

        if extend:
            """扩展子缓冲区到新大小"""
            # 将旧数据复制到具有旧大小的临时缓冲区中
            new_vbo = gl.glGenBuffers(1)
            gl.glBindBuffer(gl.GL_COPY_WRITE_BUFFER, new_vbo)
            gl.glBufferData(gl.GL_COPY_WRITE_BUFFER, old_nbytes, None, self._usage)
            gl.glCopyBufferSubData(gl.GL_ARRAY_BUFFER, gl.GL_COPY_WRITE_BUFFER, 0, 0, old_nbytes)

            # 将数组缓冲区扩展到新大小
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.blocks.nbytes, None, self._usage)

            # 将旧数据复制回数组缓冲区
            for keep in keep_blocks:
                gl.glCopyBufferSubData(
                    gl.GL_COPY_WRITE_BUFFER,
                    gl.GL_ARRAY_BUFFER,
                    keep[0],  # 读取偏移量
                    keep[2],  # 写入偏移量
                    keep[1],  # 大小
                )

            gl.glBindBuffer(gl.GL_COPY_WRITE_BUFFER, 0)
            gl.glDeleteBuffers(1, [new_vbo])

        self._loadSubDatas(block_id, data)

    @property
    def isbind(self):
        return self._vbo == gl.glGetIntegerv(gl.GL_ARRAY_BUFFER_BINDING)

    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo)

    def delete(self):
        gl.glDeleteBuffers(1, [self._vbo])

    def getData(self, _id):
        """从缓冲区获取数据"""
        self.bind()
        offset, nbytes = self.blocks.locBlock(_id)  # 读取数据的偏移量和大小
        dtype = self.blocks.dtype[_id]
        data = np.empty(int(nbytes / dtype.itemsize), dtype=dtype)

        gl.glGetBufferSubData(
            gl.GL_ARRAY_BUFFER,
            offset, nbytes,
            data.ctypes.data_as(c_void_p)
        )
        asize = self.blocks.attr_size[_id]
        return data.reshape(-1, asize if isinstance(asize, int) else sum(asize))

    def setAttrPointer(self, block_id: List[int], attr_id: List[int] = None, divisor=0):
        """
        :param block_id:
        :param attr_id:
        :param divisor: 属性的除数
        """
        self.bind()
        if isinstance(block_id, int):
            block_id = [block_id]

        if attr_id is None:
            attr_id = [self.blocks.attr_idx[b_id] for b_id in block_id]
        elif isinstance(attr_id, int):
            attr_id = [attr_id]

        if isinstance(divisor, int):
            divisor = [divisor] * len(block_id)

        for b_id, a_id, div in zip(block_id, attr_id, divisor):
            a_size = self.blocks.attr_size[b_id]
            dtype = np.dtype(self.blocks.dtype[b_id])

            if isinstance(a_size, list):  # mat4
                stride = sum(a_size) * dtype.itemsize
                a_offsets = [0] + np.cumsum(a_size).tolist()[:-1]
                for i in range(len(a_size)):
                    gl.glVertexAttribPointer(
                        a_id[i],
                        a_size[i],
                        GL_Type[dtype],
                        gl.GL_FALSE,
                        stride,
                        c_void_p(self.blocks.block_offsets[b_id] + a_offsets[i] * dtype.itemsize)
                    )
                    gl.glVertexAttribDivisor(a_id[i], div)
                    gl.glEnableVertexAttribArray(a_id[i])
            else:
                gl.glVertexAttribPointer(
                    a_id,
                    a_size,
                    GL_Type[dtype],
                    gl.GL_FALSE,
                    a_size * dtype.itemsize,
                    c_void_p(self.blocks.block_offsets[b_id])
                )
                gl.glVertexAttribDivisor(a_id, div)
                gl.glEnableVertexAttribArray(a_id)


class VAO:

    def __init__(self):
        self._vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self._vao)

    @property
    def isbind(self):
        return self._vao == gl.glGetIntegerv(gl.GL_VERTEX_ARRAY_BINDING)

    def bind(self):
        # 检查是否有GL错误
        # error = gl.glGetError()
        # if error != gl.GL_NO_ERROR:
        #     raise RuntimeError(f"OpenGL error: {error}")
        gl.glBindVertexArray(self._vao)

    def unbind(self):
        gl.glBindVertexArray(0)

    def delete(self):
        gl.glDeleteVertexArrays(1, [self._vao])


class EBO:

    def __init__(
            self,
            indices: np.ndarray,
            usage=gl.GL_STATIC_DRAW
    ):
        self._ebo = gl.glGenBuffers(1)
        self._usage = usage
        self.updateData(indices)

    @property
    def isbind(self):
        return self._ebo == gl.glGetIntegerv(gl.GL_ELEMENT_ARRAY_BUFFER_BINDING)

    def updateData(self, indices: np.ndarray):
        if indices is None:
            self._size = 0
            return

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            indices.nbytes,
            indices,
            self._usage,
        )
        self._size = indices.size

    @property
    def size(self):
        return self._size

    def bind(self):
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._ebo)

    def delete(self):
        gl.glDeleteBuffers(1, [self._ebo])
