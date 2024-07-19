"""

"""
from typing import Literal

from PyQt5.QtGui import QVector3D as Qvec3
from .transform3d import Matrix4x4, Vector3


class Camera:
    def __init__(self, pos=Vector3(0., 0., 50.), tar=Vector3(0, 0, 0), up=Vector3(0, 1, 0), fov=45, sensitivity=None):
        self.pos = pos
        self.tar = tar
        self.distance = (self.pos - self.tar).length()
        self.up = up
        self.right = (self.tar - self.pos).cross(Vector3(0, 1, 0)).normalized()
        self.fov = fov
        self.lookAt = Matrix4x4()
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(0, 1, 0))
        self.sensitivity = sensitivity if sensitivity is not None else {
            "旋转": 50,
            "平移": 50,
            "缩放": 50
        }
        self._proj_mode: Literal["perspective", "ortho"] = "perspective"
        self.zoom_factor = 0.1

    def set_proj_mode(self, mode: Literal["perspective", "ortho"]):
        self._proj_mode = mode

    def get_view_matrix(self) -> Matrix4x4:
        return self.lookAt.copy()

    def get_view_pos(self):
        return self.pos.copy()

    def get_projection_matrix(self, width, height):
        if self._proj_mode == "perspective":
            return Matrix4x4.create_perspective_proj(self.fov, width / height, max(0.1, self.distance * 0.05), max(self.distance * 2, 1000))
        else:
            ortho_width = width / 2 * self.zoom_factor
            ortho_height = height / 2 * self.zoom_factor
            return Matrix4x4.create_ortho_proj(-ortho_width, ortho_width, -ortho_height, ortho_height, max(0.1, self.distance * 0.05), max(self.distance * 2, 1000))

    def get_proj_view_matrix(self, width, height):
        return self.get_projection_matrix(width, height) * self.lookAt

    def orbit(self, dx, dy):
        self.right = (self.tar - self.pos).cross(Vector3(0, 1, 0)).normalized()

        right_angle = - dx * self.sensitivity["旋转"] * 0.005
        up_angle = - dy * self.sensitivity["旋转"] * 0.005
        # 保持距离不变，dx决定相机绕y轴旋转的角度，dy决定相机在世界坐标中的俯仰角变化
        self.pos -= self.tar
        # 绕y轴旋转
        self.pos.rotateByAxisAndAngle(0, 1, 0, right_angle)
        # 绕right向量旋转
        self.pos.rotateByAxisAndAngle(self.right.x, 0, self.right.z, up_angle)
        # self.pos = Vector3(self.pos)
        self.pos += self.tar
        self.lookAt.setToIdentity()  # 重置lookAt
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(0, 1, 0))

    def pan(self, dx, dy):
        rate = self.sensitivity["平移"] * self.distance * 0.00002
        self.up = (self.tar - self.pos).cross(self.right).normalized()
        _pan = Vector3(self.right * dx * rate + self.up * dy * rate)
        self.pos -= _pan
        self.tar -= _pan
        self.lookAt.setToIdentity()  # 重置lookAt
        self.lookAt.lookAt(self.pos, self.tar, Vector3(0, 1, 0))

    def zoom(self, delta):
        self.pos -= self.tar
        rate = 1 - delta * self.sensitivity["缩放"] * 0.001
        self.pos *= rate
        self.distance *= rate
        self.pos += self.tar

        self.zoom_factor *= rate

        self.lookAt.setToIdentity()  # 重置lookAt
        self.lookAt.lookAt(self.pos, self.tar, Vector3(0, 1, 0))

    @property
    def quat(self):
        return self.lookAt.toQuaternion()

    def set_sensitive(self, k, v):
        self.sensitivity[k] = v

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
        self.pos = self.lookAt.position()
        self.tar = self.lookAt.center()

    def get_lookAt(self):
        return self.lookAt

    # 设置看向X轴负方向：
    def look_at_negative_direction(self, direction: Vector3, right: Vector3, up: Vector3):
        self.pos = self.tar + direction * self.distance
        self.right = right
        self.up = up
        self.lookAt.setToIdentity()
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(0, 1, 0))

    def lookAtXNegative(self):
        self.look_at_negative_direction(Vector3(-1, 0, 0), Vector3(0, 0, -1), Vector3(0, 1, 0))

    def lookAtYNegative(self):
        self.look_at_negative_direction(Vector3(0, -1, 0), Vector3(1, 0, 0), Vector3(0, 0, 1))

    def lookAtZNegative(self):
        self.look_at_negative_direction(Vector3(0, 0, -1), Vector3(1, 0, 0), Vector3(0, 1, 0))