"""
相机类，和相机动画类
"""
from typing import Literal

import numpy as np
from PyQt5.QtCore import QTimer, QMutex, pyqtSignal, QObject
from PyQt5.QtGui import QVector3D as Qvec3
from utils.funcs_utils import mutexLock
from main_logger import Log

from .transform3d import Matrix4x4, Vector3


class CamAnimation(QObject):
    TAG = "CamAnimation"

    def __init__(self, camera):
        super().__init__()
        self.timer = QTimer()
        self.camera: Camera = camera
        # 位姿信息
        self.targetDirection = Vector3(0, 0, -1)
        self.targetDistance = 50
        self.targetRight = Vector3(1, 0, 0)
        self.duration: float = 0.5
        # 四元数
        self.startQuat = self.camera.quat
        self.currentQuat = self.camera.quat
        self.endQuat = self.camera.quat
        # 动画信息
        self.fr = 60
        self.animation_steps = int(self.duration * self.fr)  # 假设60帧每秒
        self.distance_step: float = 0
        # 当前动画步数
        self.animation_current_step: int = 0
        # 绑定定时器
        self.timer.timeout.connect(self._update_animation)
        self.timer.setInterval(1000 // self.fr)
        self.animation_mutex = QMutex()

    def start(self, targetDirection: Vector3, targetDistance: float, targetRight: Vector3, duration: float = 0.5):
        self.targetDirection = targetDirection.normalized()
        self.targetDistance = targetDistance
        self.targetRight = targetRight
        self.duration = duration
        self.animation_steps = int(duration * self.fr)
        # 进行四元数线性插值
        self.startQuat = self.camera.quat
        self.endQuat = Matrix4x4()
        self.endQuat.lookAt(self.camera.pos, self.camera.pos + self.targetDirection * self.targetDistance,
                            Vector3(0, 1, 0))  # 固定up向量为(0, 1, 0)
        self.endQuat = self.endQuat.toQuaternion()

        # 计算距离步长
        self.distance_step = (self.targetDistance - self.camera.distance) / self.animation_steps
        # 开始动画
        self.animation_current_step = 0
        self.currentQuat = self.startQuat  # 初始化当前四元数
        self.camera.update_gl_widget_s.emit()
        self.timer.start()

    # @mutexLock("animation_mutex")
    def _update_animation(self):
        if self.animation_current_step >= self.animation_steps:
            self.stop()
            return
        # 使用插值四元数
        t = (self.animation_current_step + 1) / self.animation_steps
        self.currentQuat = self.startQuat.slerp(self.startQuat, self.endQuat, t)

        self.camera.lookAt.setToIdentity()
        self.camera.lookAt.rotate(self.currentQuat)

        # 更新相机的位置
        self.camera.pos = self.camera.tar - self.targetDirection * (
                    self.camera.distance + self.distance_step * (self.animation_current_step + 1))

        self.camera.update_gl_widget_s.emit()
        self.animation_current_step += 1

    def stop(self):
        # 确保相机设置为最终状态
        self.camera.lookAt.setToIdentity()
        self.camera.lookAt.rotate(self.endQuat)
        self.camera.pos = self.camera.tar - self.targetDirection * self.targetDistance
        self.camera.update_gl_widget_s.emit()

        self.camera._set_lookAt()
        self.camera.end_animation_s.emit()
        self.timer.stop()


class Camera(QObject):
    update_gl_widget_s = pyqtSignal()
    start_animation_s = pyqtSignal()
    end_animation_s = pyqtSignal()

    def __init__(self, pos=Vector3(0., 0., -50.), tar=Vector3(0, 0, 0), up=Vector3(0, 1, 0), fov=45, left_hand=True, sensitivity=None):
        super().__init__()
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
        # 是否为左手坐标系
        self.leftHand = left_hand
        # 锁
        self.transform_mutex = QMutex()
        # 动画器
        self.rotate_animation = CamAnimation(self)

    def set_proj_mode(self, mode: Literal["perspective", "ortho"]):
        self._proj_mode = mode

    def get_view_matrix(self) -> Matrix4x4:
        return self.lookAt.copy()

    def get_view_pos(self):
        return self.pos.copy()

    def get_projection_matrix(self, width, height):
        if self.leftHand:
            width = -width  # 修正坐标系为左手坐标系
        if self._proj_mode == "perspective":
            return Matrix4x4.create_perspective_proj(self.fov, width / height, max(0.1, self.distance * 0.05),
                                                     max(self.distance * 2, 1000))
        else:
            ortho_width = width / 2 * self.zoom_factor
            ortho_height = height / 2 * self.zoom_factor
            return Matrix4x4.create_ortho_proj(-ortho_width, ortho_width, -ortho_height, ortho_height,
                                               max(0.1, self.distance * 0.05), max(self.distance * 2, 1000))

    def get_proj_view_matrix(self, width, height):
        return self.get_projection_matrix(width, height) * self.lookAt

    def _get_right(self):
        """
        由 self.tar，self.pos 和 self.up 向量计算right向量
        :return:
        """
        if self.up[1] == 0:
            self.right = (self.tar - self.pos).cross(self.up).normalized()
        else:
            self.right = (self.tar - self.pos).cross(Vector3(0, 1, 0)).normalized()

    def _set_lookAt(self):
        """
        在更新pos, tar, up等参数后，重新设置lookAt矩阵
        :return:
        """
        self.lookAt.setToIdentity()
        if self.up[1] == 0:
            self.lookAt.lookAt(self.pos, self.tar, self.up)
        else:
            self.lookAt.lookAt(self.pos, self.tar, Vector3(0, 1, 0))

    @mutexLock("transform_mutex")
    def orbit(self, dx, dy):
        self._get_right()
        self.up = self.right.cross(self.tar - self.pos).normalized()

        # 获取旋转的角度（弧度）
        right_angle = dx * self.sensitivity["旋转"] * 0.005
        up_angle = - dy * self.sensitivity["旋转"] * 0.005
        # 保持距离不变，dx决定相机绕y轴旋转的角度，dy决定相机在世界坐标中的俯仰角变化
        self.pos -= self.tar
        # 绕y轴左右旋转
        self.pos.rotateByAxisAndAngle(0, 1, 0, right_angle)
        # 计算当前pos仰角，限制仰角在-90到90度之间
        angle = self.pos.angle(Vector3(0, 1, 0))
        # 转单位为角度
        angle = angle * 180 / np.pi
        # print(angle)
        if 0 < angle + up_angle < 180:
            # 绕right向量旋转
            self.pos.rotateByAxisAndAngle(self.right.x, 0, self.right.z, up_angle)
        # self.pos = Vector3(self.pos)
        self.pos += self.tar
        self._set_lookAt()

    @mutexLock("transform_mutex")
    def pan(self, dx, dy):
        rate = self.sensitivity["平移"] * self.distance * 0.00002
        _pan = Vector3(self.right * dx * rate + self.up * dy * rate)
        self.pos += _pan
        self.tar += _pan
        self._set_lookAt()

    @mutexLock("transform_mutex")
    def zoom(self, delta):
        self.pos -= self.tar
        rate = 1 - delta * self.sensitivity["缩放"] * 0.001
        self.pos *= rate
        self.distance *= rate
        self.pos += self.tar
        self.zoom_factor *= rate

        self._set_lookAt()

    def rotate_animation_start(self, targetDirection, targetDistance, targetRight, targetUp, duration=0.5):
        """
        固定tar坐标点，旋转以及缩放距离动画
        :param targetDirection: pos相对tar的目标方向向量（单位向量）
        :param targetDistance: pos相对tar的目标距离
        :param targetRight: pos相对tar的目标right向量
        :param targetUp: pos相对tar的目标up向量
        :param duration: 动画持续时间，单位秒
        :return:
        """
        self.rotate_animation.start(targetDirection, targetDistance, targetRight, duration)

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

    def get_lookAt(self):
        return self.lookAt

    # 设置看向X轴负方向：
    def look_at_negative_direction(self, direction: Vector3, right: Vector3, up: Vector3):
        self.pos = self.tar + direction * self.distance
        self.right = right
        self.up = up
        self.lookAt.setToIdentity()
        self.lookAt.lookAt(Qvec3(*self.pos), Qvec3(*self.tar), Qvec3(*self.up))
        # self.rotate_animation_start(direction, self.distance, right, up, 5)

    def lookAtXNegative(self):
        self.look_at_negative_direction(Vector3(1, 0, 0), Vector3(0, 0, -1), Vector3(0, 1, 0))

    def lookAtYNegative(self):
        self.look_at_negative_direction(Vector3(0, 1, 0), Vector3(0, 0, -1), Vector3(-1, 0, 0))

    def lookAtZNegative(self):
        self.look_at_negative_direction(Vector3(0, 0, 1), Vector3(1, 0, 0), Vector3(0, 1, 0))
