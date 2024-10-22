"""

"""
from typing import Union

import numpy as np
from PyQt5.QtGui import QQuaternion, QMatrix4x4, QVector3D, QMatrix3x3, QVector4D

from .functions import _dispatchmethod


class Quaternion(QQuaternion):
    """
    Extension of QQuaternion with some helpful methods added.
    """

    # constructors
    @_dispatchmethod
    def __init__(self):
        super().__init__()

    @__init__.register(np.ndarray)
    def _(self, array: np.ndarray):
        quat_values = array.astype('f4').flatten().tolist()
        super().__init__(*quat_values)

    @__init__.register(list)
    def _(self, array):
        super().__init__(np.array(array))

    @__init__.register(QQuaternion)
    def _(self, quat):
        super().__init__(quat.scalar(), quat.x(), quat.y(), quat.z())

    def __repr__(self) -> str:
        np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
        return f"Quaternion(w: {self.scalar()}, x: {self.x()}, y: {self.y()}, z: {self.z()})"

    def copy(self):
        return Quaternion(self)

    def conjugate(self):
        """conjugate of quaternion"""
        return Quaternion(super().conjugated())

    def inverse(self):
        """conjugate of quaternion"""
        return Quaternion(super().inverted())

    def normalize(self):
        return Quaternion(super().normalized())

    def toEulerAngles(self):
        angles = super().toEulerAngles()
        return np.array([angles.x(), angles.y(), angles.z()])

    def toMatrix4x4(self):
        matrix3x3 = super().toRotationMatrix()
        matrix = np.identity(4)
        matrix[:3, :3] = np.array(matrix3x3.copyDataTo()).reshape(3, 3)
        return Matrix4x4(matrix)

    @classmethod
    def fromEulerAngles(cls, pitch, yaw, roll):
        """rotates around x, then y, then z"""
        return cls(QQuaternion.fromEulerAngles(pitch, yaw, roll))

    @classmethod
    def fromAxisAndAngle(cls, x=0., y=0., z=0., angle=0.):
        return cls(QQuaternion.fromAxisAndAngle(x, y, z, angle))

    @classmethod
    def fromMatrix4x4(cls, matrix: 'Matrix4x4'):
        matrix3x3 = matrix.matrix33.flatten().tolist()
        matrix3x3 = QMatrix3x3(matrix3x3)
        return cls(QQuaternion.fromRotationMatrix(matrix3x3))

    # operators
    def __mul__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(super().__mul__(other))
        # elif isinstance(other, Matrix4x4):
        #     mat = self.toMatrix4x4()
        #     return mat * other
        elif isinstance(other, QVector3D):
            return super().__mul__(other)

        # apply rotation to vectors np.array([[x1,y1,z1], [x2,y2,z2], ...])
        mat = self.toMatrix4x4()
        return mat * other


class Matrix4x4(QMatrix4x4):
    """
    Extension of QMatrix4x4 with some helpful methods added.
    """

    # constructors
    @_dispatchmethod
    def __init__(self):
        super().__init__()

    @__init__.register(list)
    @__init__.register(tuple)
    @__init__.register(np.ndarray)
    def _(self, array):
        matrix_values = np.array(array).astype('f4').flatten().tolist()
        super().__init__(*matrix_values)

    @__init__.register(QMatrix4x4)
    def _(self, matrix):
        super().__init__(matrix.copyDataTo())

    def copy(self):
        return Matrix4x4(self)

    def right(self):
        return self.column(0).toVector3D()

    def up(self):
        return self.column(1).toVector3D()

    def setByAxisAndAngle(self, x, y, z, angle):
        self.setToIdentity()
        self.rotate(angle, x, y, z)

    def lookAt(self, eye: Union[QVector3D, 'Vector3'], center: Union[QVector3D, 'Vector3'], up: Union[QVector3D, 'Vector3']):
        if isinstance(eye, (list, tuple, np.ndarray, Vector3)):
            super().lookAt(QVector3D(*eye), QVector3D(*center), QVector3D(*up))
        elif isinstance(eye, QVector3D):
            super().lookAt(eye, center, up)

    @classmethod
    def ortho_matrix(cls, left, right, bottom, top, near, far):
        matrix = cls()
        matrix.ortho(left, right, bottom, top, near, far)
        return matrix

    @property
    def matrix33(self):
        m = np.array(self.copyDataTo()).reshape(4, 4)
        return m[:3, :3]

    @property
    def matrix44(self):
        return np.array(self.copyDataTo()).reshape(4, 4)

    @property
    def glData(self):
        """convert to column-major order for use with OpenGL"""
        return self.data()

    def __repr__(self) -> str:
        np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
        return f"Matrix4x4(\n{self.matrix44}\n)"

    @_dispatchmethod
    def rotate(self, q: Quaternion, local=True):
        """rotate by quaternion in local space, it will change the current matrix"""
        if local:
            super().rotate(q)
        else:
            self.setData(q * self)
        return self

    @rotate.register(float)
    @rotate.register(int)
    def _(self, angle, x, y, z, local=True):
        """rotate by angle(degree) around x,y,z in local space, it will change the current matrix"""
        if local:
            super().rotate(angle, x, y, z)
        else:
            self.setData(Matrix4x4.fromAxisAndAngle(x, y, z, angle) * self)
        return self

    def translate(self, x, y, z, local=True):
        """translate by x,y,z in local space, it will change the current matrix"""
        if local:
            super().translate(x, y, z)
        else:
            self.setData(Matrix4x4.fromTranslation(x, y, z) * self)
        return self

    def scale(self, x, y, z, local=True):
        """scale by x,y,z in local space, it will change the current matrix"""
        if local:
            super().scale(x, y, z)
        else:
            self.setData(Matrix4x4.fromScale(x, y, z) * self)
        return self

    def moveto(self, x, y, z):
        """move to x,y,z in world space, it will change the current matrix"""
        self.setColumn(3, QVector4D(x, y, z, 1))
        return self

    def setData(self, matrix: Union[np.ndarray, QMatrix4x4]):
        """set matrix data"""
        if isinstance(matrix, QMatrix4x4):
            for i in range(4):
                self.setRow(i, matrix.row(i))
        elif isinstance(matrix, (list, tuple)):
            matrix = np.array(matrix, dtype='f4')
            assert matrix.shape == (4, 4), f"matrix shape should be (4,4), but got {matrix.shape}"
            for i in range(4):
                self.setRow(i, QVector4D(*matrix[i]))

    def applyTransform(self, matrix, local=False):
        """apply transform to self"""
        if local:
            return self * matrix
        else:
            return matrix * self

    @classmethod
    def fromRotTrans(cls, R: np.ndarray, t=None):
        """rotate by R and translate by t"""
        if t is None:
            t = np.zeros(3, dtype='f4')
        data = np.zeros((4, 4), dtype='f4')
        data[:3, :3] = R
        data[:3, 3] = t
        data[3, 3] = 1
        return cls(data)

    @classmethod
    def fromEulerAngles(cls, pitch, yaw, roll):
        """rotate around x, then y, then z"""
        rot = Quaternion.fromEulerAngles(pitch, yaw, roll)
        return cls.fromQuaternion(rot)

    @classmethod
    def fromTranslation(cls, x=0., y=0., z=0.):
        """translate by x,y,z"""
        trans = QMatrix4x4()
        trans.translate(x, y, z)
        return cls(trans)

    @classmethod
    def fromScale(cls, x=1., y=1., z=1.):
        """scale by x,y,z"""
        scale = QMatrix4x4()
        scale.scale(x, y, z)
        return cls(scale)

    @classmethod
    def fromAxisAndAngle(cls, x=0., y=0., z=0., angle=0.):
        """rotate by angle(degree) around x,y,z"""
        if angle == 0 or x == 0 and y == 0 and z == 0:
            return cls()
        rot = cls()
        rot.rotate(angle, x, y, z)
        return rot

    @classmethod
    def fromQuaternion(cls, q):
        """rotate by quaternion"""
        rot = cls()
        rot.rotate(q)
        return rot

    def inverse(self):
        mat, ret = self.inverted()
        assert ret, "matrix is not invertible"
        return Matrix4x4(mat)

    def toQuaternion(self):
        """convert to quaternion"""
        return Quaternion.fromMatrix4x4(self)

    def toEularAngles(self):
        return self.toQuaternion().toEulerAngles()

    def toTranslation(self):
        trans = self.column(3)
        return Vector3(trans.x(), trans.y(), trans.z())

    def __mul__(self, other):
        if isinstance(other, Matrix4x4):
            return Matrix4x4(super().__mul__(other))
        elif isinstance(other, Quaternion):
            mat = Matrix4x4(self)
            mat.rotate(other)
            return mat

        if isinstance(other, (list, tuple)):
            other = np.array(other, dtype='f4')
        elif isinstance(other, Vector3):
            other = other.xyz
        assert isinstance(other, np.ndarray), f"unsupported type {type(other)}"

        # apply rotation to vectors v = np.array([[x1,y1,z1], [x2,y2,z2], ...]), n,3
        # v * R.T + t
        mat4 = self.matrix44
        rot = mat4[:3, :3]
        trans = mat4[:3, 3]
        if other.ndim == 1:
            if other.shape[0] == 3:
                return np.matmul(rot, other) + trans
            elif other.shape[0] == 4:
                other /= max(other[3], 1e-8)
                other[3] = 1
                return np.matmul(mat4, other)
        elif other.ndim == 2:
            if other.shape[1] == 3:
                return np.matmul(other, rot.T) + trans[None, :]
            elif other.shape[1] == 4:  # homogeneous coordinates
                other[:, :3] /= np.maximum(other[:, 3], 1e-8)[:, None]
                other[:, 3] = 1
                return other @ mat4.T

    @classmethod
    def create_perspective_proj(cls, angle: float, aspect: float, near: float, far: float):
        proj = cls()
        proj.perspective(angle, aspect, near, far)
        return proj

    @classmethod
    def create_ortho_proj(cls, left: float, right: float, bottom: float, top: float, near: float, far: float):
        proj = cls()
        proj.ortho(left, right, bottom, top, near, far)
        return proj


class Vector3:

    @_dispatchmethod
    def __init__(self, x: float = 0., y: float = 0., z: float = 0.):
        self._data = np.array([x, y, z], dtype='f4')

    @__init__.register(np.ndarray)
    @__init__.register(list)
    @__init__.register(tuple)
    def _(self, data):
        self._data = np.array(data, dtype='f4').flatten()[:3]

    @__init__.register(QVector3D)
    def _(self, data):
        self._data = np.array([data.x(), data.y(), data.z()], dtype='f4')

    def copy(self):
        return Vector3(self._data)

    def length(self):
        return np.linalg.norm(self._data)

    def cross(self, other):
        # noinspection PyProtectedMember
        return Vector3(np.cross(self._data, other._data))

    def normalized(self):
        return Vector3(self._data / self.length())

    def rotateByAxisAndAngle(self, x, y, z, angle) -> None:
        """
        rotate by angle(degree) around x,y,z
        :param x: x axis
        :param y: y axis
        :param z: z axis
        :param angle: angle in degree
        """
        self._data = np.dot(Matrix4x4.fromAxisAndAngle(x, y, z, angle).matrix33, self._data)

    def angle(self, other: 'Vector3') -> float:
        """
        calculate the angle in radians between two vectors
        计算两个向量之间的夹角，单位为弧度
        :param other:
        :return:
        """
        return np.arccos(np.dot(self._data, other._data) / (self.length() * other.length()))

    def __len__(self):
        return 3

    def __repr__(self):
        return f"Vec3({self.x:.3g}, {self.y:.3g}, {self.z:.3g})"

    # noinspection PyProtectedMember
    def __sub__(self, other):
        return Vector3(self._data - other._data)

    # noinspection PyProtectedMember
    def __add__(self, other):
        return Vector3(self._data + other._data)

    # noinspection PyProtectedMember
    def __isub__(self, other):
        self._data -= other._data
        return self

    # noinspection PyProtectedMember
    def __iadd__(self, other):
        self._data += other._data
        return self

    def __mul__(self, other):
        if isinstance(other, (int, float, np.float32)):
            return Vector3(self._data * other)
        elif isinstance(other, (Vector3, np.ndarray, list, tuple)):
            return Vector3(self._data[0] * other[0],
                           self._data[1] * other[1],
                           self._data[2] * other[2])
        elif isinstance(other, QVector3D):
            return Vector3(self._data * np.array([other.x(), other.y(), other.z()], dtype='f4'))
        else:
            raise TypeError(f"unsupported type {type(other)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            self._data *= other
        elif isinstance(other, (Vector3, np.ndarray, list, tuple)):
            self._data[0] *= other[0]
            self._data[1] *= other[1]
            self._data[2] *= other[2]
        else:
            raise TypeError(f"unsupported type {type(other)}")
        return self

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Vector3(self._data / other)
        elif isinstance(other, (Vector3, np.ndarray, list, tuple)):
            return Vector3(self._data[0] / other[0],
                           self._data[1] / other[1],
                           self._data[2] / other[2])
        else:
            raise TypeError(f"unsupported type {type(other)}")

    def __itruediv__(self, other):
        if isinstance(other, (int, float)):
            self._data /= other
        elif isinstance(other, (Vector3, np.ndarray, list, tuple)):
            self._data[0] /= other[0]
            self._data[1] /= other[1]
            self._data[2] /= other[2]
        else:
            raise TypeError(f"unsupported type {type(other)}")
        return self

    def __neg__(self):
        return Vector3(-self._data)

    @property
    def xyz(self):
        return self._data

    @property
    def x(self):
        return self._data[0]

    @x.setter
    def x(self, val):
        self._data[0] = val

    @property
    def y(self):
        return self._data[1]

    @y.setter
    def y(self, val):
        self._data[1] = val

    @property
    def z(self):
        return self._data[2]

    @z.setter
    def z(self, val):
        self._data[2] = val

    def __getitem__(self, i):
        if i > 2:
            raise IndexError("Point has no index %s" % str(i))
        return self._data[i]

    def __setitem__(self, i, x):
        self._data[i] = x


@Vector3.__init__.register
def _(self, v: Vector3):
    # noinspection PyProtectedMember
    self._data = np.array(v._data, dtype='f4')


if __name__ == '__main__':
    na = np.array([0, 1, 2, 3,
                   4, 5, 6, 7,
                   8, 9, 10, 11,
                   0, 0, 0, 1], dtype=np.float32).reshape(4, 4)
    a = Matrix4x4(na)
    nt = Matrix4x4([1, 0, 0, 1,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1
                    ])
    # nt = Matrix4x4.fromAxisAndAngle(1, 0, 0, 30)
    q = Quaternion.fromAxisAndAngle(0, 1, 1, 34)
    # q = Quaternion()
