from math import radians, tan
from enum import Enum, auto

import numpy as np
from PyQt5.QtGui import QVector3D as Qvec3, QMatrix4x4

from .transform3d import Matrix4x4, Quaternion, Vector3


class Camera2:

    def __init__(
            self,
            position=Vector3(0., 0., 5),
            yaw=0,
            pitch=0,
            roll=0,
            fov=45,
            sensitivity=None
    ):
        """View Corrdinate System
        default front vector: (0, 0, -1)
        default up Vector: (0, 1, 0)
        yaw: rotate around VCS y axis
        pitch: rotate around VCS x axis
        roll: rotate around VCS z axis
        """
        self.pos = Vector3(position)  # 世界坐标系原点指向相机位置的向量, 在相机坐标下的坐标
        self.tar = Vector3(0., 0., 0.)
        self.quat = Quaternion.fromEulerAngles(pitch, yaw, roll)  # 世界坐标系到相机坐标系的旋转矩阵
        self.fov = fov
        self.sensitivity = sensitivity if sensitivity is not None else {
            "旋转": 50,
            "平移": 50,
            "缩放": 50
        }

    def get_view_matrix(self):
        return Matrix4x4.fromTranslation(-self.pos.x, -self.pos.y, -self.pos.z) * self.quat

    def set_view_matrix(self, view_matrix: Matrix4x4):
        self.quat = view_matrix.toQuaternion()
        self.pos = -view_matrix.toTranslation()

    def get_quat_pos(self):
        return self.quat.copy(), self.pos.copy()

    def set_quat_pos(self, quat=None, pos=None):
        if quat is not None:
            self.quat = quat
        if pos is not None:
            self.pos = pos

    def get_projection_matrix(self, width, height, fov=None):
        distance = max(self.pos.z, 1)
        if fov is None:
            fov = self.fov

        return Matrix4x4.create_projection(
            fov,
            width / height,
            0.001 * distance,
            100.0 * distance
        )

    def get_proj_view_matrix(self, width, height, fov=None):
        return self.get_projection_matrix(width, height, fov) * self.get_view_matrix()

    def get_view_pos(self):
        """计算相机在世界坐标系下的坐标"""
        return self.quat.inverse() * self.pos

    def orbit(self, yaw, pitch, roll=0, base=None):
        """Orbits the camera around the center position.
        *yaw* and *pitch* are given in degrees."""
        q = Quaternion.fromEulerAngles(pitch, yaw, roll)

        if base is None:
            base = self.quat

        self.quat = q * base

    def orbit_in_view(self, dx, dy, dz=0.0, base=None):
        """在世界坐标系下绕目标点y轴旋转，dx决定相机绕y轴旋转的角度，dy决定相机在世界坐标中的俯仰角变化"""
        if base is None:
            base = self.quat
        q = Quaternion.fromEulerAngles(dy, dx, 0)
        self.quat = q * base

    def pan(self, dx, dy, dz=0.0, width=1000, base=None):
        """Pans the camera by the given amount of *dx*, *dy* and *dz*."""
        if base is None:
            base = self.pos

        scale = self.pos.z * 2. * tan(0.5 * radians(self.fov)) / width
        offset = Vector3([-dx * scale, -dy * scale, dz * scale])
        self.pos = base + offset
        self.tar = self.tar + offset
        if self.pos.z < 0.1:
            self.pos.z = 0.1

    def set_params(self, position=None, pitch=None, yaw=None, roll=0, fov=None):
        if position is not None:
            self.pos = Vector3(position)
        if yaw is not None or pitch is not None:
            self.quat = Quaternion.fromEulerAngles(pitch, yaw, roll)
        if fov is not None:
            self.fov = fov

    def get_params(self):
        return self.pos, self.quat.toEulerAngles()


class Camera:
    def __init__(self, pos=Vector3(0., 0., 50.), tar=Vector3(0, 0, 0), up=Vector3(0, 1, 0), fov=45, sensitivity=None):
        self.pos = pos
        self.tar = tar
        self.up = up
        self.fov = fov
        self.lookAt = Matrix4x4()
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(0, 1, 0))
        self.sensitivity = sensitivity if sensitivity is not None else {
            "旋转": 50,
            "平移": 50,
            "缩放": 50
        }

    def get_distance(self):
        return (self.pos - self.tar).length()

    def get_view_matrix(self):
        return self.lookAt.copy()
        # self.lookAt = Matrix4x4()
        # self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(*self.up))
        # return Matrix4x4.fromTranslation(-self.pos.x, -self.pos.y, -self.pos.z) * self.lookAt.toQuaternion()

    def get_quat_pos(self):
        return self.lookAt.toQuaternion().copy(), self.pos.copy()

    def get_view_pos(self):
        return self.pos

    def get_projection_matrix(self, width, height):
        return Matrix4x4.create_projection(self.fov, width / height, 0.1, 1000)

    def get_proj_view_matrix(self, width, height):
        return self.get_projection_matrix(width, height) * self.get_view_matrix()

    def orbit(self, dx, dy):
        right = self.lookAt.right()
        # up = self.lookAt.up()
        rate = self.sensitivity["旋转"] * 0.005
        right_angle = - dx * rate
        up_angle = - dy * rate
        # 保持距离不变，dx决定相机绕y轴旋转的角度，dy决定相机在世界坐标中的俯仰角变化
        self.pos -= self.tar
        # 绕y轴旋转
        self.pos = Matrix4x4().fromAxisAndAngle(0, 1, 0, right_angle) * self.pos
        # 绕right向量旋转
        self.pos = Matrix4x4().fromAxisAndAngle(right.x(), 0, right.z(), up_angle) * self.pos
        self.pos = Vector3(self.pos)
        self.pos += self.tar
        self.lookAt = Matrix4x4()
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(0, 1, 0))

    def pan(self, dx, dy):
        rate = self.sensitivity["平移"] * self.get_distance() * 0.00005
        right = (self.tar - self.pos).cross(self.up).normalized()
        right_offset = right * dx * rate
        up_offset = Vector3(0, 1, 0) * dy * rate
        _pan = Vector3(right_offset - up_offset)
        self.pos -= _pan
        self.tar -= _pan
        self.lookAt = Matrix4x4()
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(0, 1, 0))

    def zoom(self, delta):
        self.pos -= self.tar
        rate = - delta * self.sensitivity["缩放"] * 0.00001
        print(self.pos)
        self.pos *= (1 + rate)
        print(self.pos)
        self.pos += self.tar
        self.lookAt = Matrix4x4()
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(0, 1, 0))

    def set_params_by_euler(self, pos, pitch, yaw, roll, fov):
        self.pos = pos
        self.fov = fov
        self.lookAt = Matrix4x4().lookAt(self.pos, self.tar, self.up).rotate(pitch, yaw, roll)

    def set_params(self, pos=None, tar=None, up=None, fov=None):
        if pos is not None:
            self.pos = pos
        if tar is not None:
            self.tar = tar
        if up is not None:
            self.up = up
        if fov is not None:
            self.fov = fov

    def get_params(self):
        return self.pos, self.tar, self.up, self.fov

    def set_lookAt(self, lookAt):
        self.lookAt = lookAt

    def get_lookAt(self):
        return self.lookAt

