# -*- coding: utf-8 -*-
"""
多种数学运算，该文件暂时没有被使用
"""

from PyQt5.QtGui import QVector3D
from numpy import linalg, cos, sin, radians, array, conj, linspace
from quaternion import quaternion  # noqa  # 这是numpy-quaternion库的quaternion类
from utils.funcs_utils import CONST


def rotate_quaternion(vec, rot: list):
    """
    对np.array类型的向量进行四元数旋转
    :param vec:
    :param rot: list
    :return:
    """
    if rot == [0, 0, 0]:
        # 标准化为单位向量
        return vec / linalg.norm(vec)
    # 转换为弧度
    rot = radians(rot)
    # 计算旋转的四元数
    q_x = array([cos(rot[0] / 2), sin(rot[0] / 2), 0, 0])
    q_y = array([cos(rot[1] / 2), 0, sin(rot[1] / 2), 0])
    q_z = array([cos(rot[2] / 2), 0, 0, sin(rot[2] / 2)])

    # 合并三个旋转四元数
    q = quaternion(1, 0, 0, 0)
    if CONST.ROTATE_ORDER == CONST.XYZ:
        q = q * quaternion(*q_x) * quaternion(*q_y) * quaternion(*q_z)
    elif CONST.ROTATE_ORDER == CONST.XZY:
        q = q * quaternion(*q_x) * quaternion(*q_z) * quaternion(*q_y)
    elif CONST.ROTATE_ORDER == CONST.YXZ:
        q = q * quaternion(*q_y) * quaternion(*q_x) * quaternion(*q_z)
    elif CONST.ROTATE_ORDER == CONST.YZX:
        q = q * quaternion(*q_y) * quaternion(*q_z) * quaternion(*q_x)
    elif CONST.ROTATE_ORDER == CONST.ZXY:
        q = q * quaternion(*q_z) * quaternion(*q_x) * quaternion(*q_y)
    elif CONST.ROTATE_ORDER == CONST.ZYX:
        q = q * quaternion(*q_z) * quaternion(*q_y) * quaternion(*q_x)
    else:
        raise ValueError("Invalid RotateOrder!")

    # 进行四元数旋转
    rotated_point_quat = q * quaternion(0, *vec) * conj(q)
    # 提取旋转后的点坐标
    rotated_point = array([rotated_point_quat.x, rotated_point_quat.x, rotated_point_quat.y])
    # 标准化为单位向量
    rotated_point = rotated_point / linalg.norm(rotated_point)
    return rotated_point


def get_normal(dot1, dot2, dot3, center=None):
    """
    计算三角形的法向量，输入为元组
    :param dot1: 元组，三角形的第一个点
    :param dot2: 元组，三角形的第二个点
    :param dot3: 元组，三角形的第三个点
    :param center: QVector3D，三角形的中心点
    :return: QVector3D
    """
    if isinstance(center, tuple):
        center = QVector3D(*center)
    v1 = QVector3D(*dot2) - QVector3D(*dot1)
    v2 = QVector3D(*dot3) - QVector3D(*dot1)
    if center is None:
        return QVector3D.crossProduct(v1, v2).normalized()
    triangle_center = QVector3D(*dot1) + QVector3D(*dot2) + QVector3D(*dot3)
    # 如果法向量与视线夹角大于90度，翻转法向量
    if QVector3D.dotProduct(QVector3D.crossProduct(v1, v2), triangle_center - center) > 0:
        return QVector3D.crossProduct(v1, v2).normalized()
    else:
        return QVector3D.crossProduct(v1, v2).normalized()


def get_bezier(start, s_control, back, b_control, x):
    """
    计算贝塞尔曲线上的点的坐标，用np.array类型表示
    :param start: 起点
    :param s_control: 起点控制点
    :param back: 终点
    :param b_control: 终点控制点
    :param x: 点的x坐标，x在start[0]和back[0]之间
    :return: 返回贝塞尔曲线上的点坐标
    """
    # 计算 t 值
    t = (x - start[0]) / (back[0] - start[0])
    # 贝塞尔曲线公式
    result = (1 - t) ** 3 * start + 3 * (1 - t) ** 2 * t * s_control + 3 * (1 - t) * t ** 2 * b_control + t ** 3 * back
    return array(result)


def fit_bezier(front_k, back_k, x_scl, y_scl, n, draw=False):
    """
    计算贝塞尔曲线上的区间的斜率
    :param front_k:
    :param back_k:
    :param x_scl:
    :param y_scl:
    :param n:
    :param draw:
    :return:
    """
    # 过滤n值>=2
    if n < 2:
        raise ValueError("n must be greater than or equal to 2")

    # 计算控制点位置
    distance = x_scl / 4
    start = array([0, 0])
    end = array([x_scl, y_scl])
    dir_s = array([1, front_k])
    dir_b = array([1, back_k])
    # 标准化后乘以距离
    dir_s = dir_s * distance / linalg.norm(dir_s)
    dir_b = dir_b * distance / linalg.norm(dir_b)
    start_control = start + dir_s
    end_control = end - dir_b
    if draw:
        # 在matplotlib绘制贝塞尔曲线：
        import matplotlib.pyplot as plt
        # 从0到length之间生成100个点
        t_values = linspace(0, x_scl, 100)
        # 初始化存储曲线上点的空数组
        curve_points = []
        # 计算贝塞尔曲线上的点
        for t in t_values:
            point = get_bezier(start, start_control, end, end_control, t / x_scl)
            curve_points.append(point)
        # 转换为NumPy数组以便于绘图
        curve_points = array(curve_points)
        # 绘制贝塞尔曲线
        plt.figure(figsize=(8, 6))
        plt.plot(curve_points[:, 0], curve_points[:, 1], label='Bezier Curve', color='blue')
        plt.scatter([start[0], start_control[0], end[0], end_control[0]],
                    [start[1], start_control[1], end[1], end_control[1]],
                    color='red', marker='o', label='Control Points')
        plt.title('Bezier Curve')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.grid(True)
        plt.show()
    # 存储斜率的列表
    slopes = []
    # 计算每段的长度
    last_point = None
    step = x_scl / n
    # 计算每段的斜率
    for i in range(n):
        # 计算当前参数值
        x = (i + 1) * step
        # 计算贝塞尔曲线上的点坐标
        point = get_bezier(start, start_control, end, end_control, x)
        # 计算与前一个点的斜率，如果为第一个点则计算与起点的斜率
        if i == 0:
            slope = (point[1] - start[1]) / step
        else:
            slope = (point[1] - last_point[1]) / step
        # 将斜率添加到列表中
        slopes.append(slope)
        # 保存上一个点的坐标
        last_point = point

    return slopes
