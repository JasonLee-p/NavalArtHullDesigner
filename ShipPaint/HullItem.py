"""
定义了船体的绘制类
"""
import ctypes
from typing import Union, Literal

import numpy as np
# from main_logger import Log
from pyqtOpenGL import Matrix4x4, GLGraphicsItem, GLMeshItem, Mesh, Quaternion, vertex_normal_smooth
from pyqtOpenGL.items.MeshData import face_normal, vertex_normal_faceNormal

# 从正下方开始，逆时针排列（向z-方向看）
SQUARE_POINTS = np.array([
    [0, -1],  # 正下
    [np.tan(np.deg2rad(15)), -1],
    [np.tan(np.deg2rad(30)), -1],
    [1, -1],  # 左下
    [1, -np.tan(np.deg2rad(30))],
    [1, -np.tan(np.deg2rad(15))],
    [1, 0],  # 正左
    [1, np.tan(np.deg2rad(15))],
    [1, np.tan(np.deg2rad(30))],
    [1, 1],  # 左上
    [np.tan(np.deg2rad(30)), 1],
    [np.tan(np.deg2rad(15)), 1],
    [0, 1],  # 正上
    [-np.tan(np.deg2rad(15)), 1],
    [-np.tan(np.deg2rad(30)), 1],
    [-1, 1],  # 右上
    [-1, np.tan(np.deg2rad(30))],
    [-1, np.tan(np.deg2rad(15))],
    [-1, 0],  # 正右
    [-1, -np.tan(np.deg2rad(15))],
    [-1, -np.tan(np.deg2rad(30))],
    [-1, -1],  # 右下
    [-np.tan(np.deg2rad(30)), -1],
    [-np.tan(np.deg2rad(15)), -1],
], dtype=np.float32)

CIRCLE_POINTS = np.array([
    [np.cos(np.deg2rad(degree)), np.sin(np.deg2rad(degree))] for degree in range(-90, 270, 15)
], dtype=np.float32)

# 正方形和圆形的差，用于计算弧面的点坐标
# 算法：CIRCLE_POINTS + CUR_ADD_POINTS * (1 - cur)
CUR_ADD_POINTS = SQUARE_POINTS - CIRCLE_POINTS


def get_curve_points(direction: Literal['up', 'bot'], cur, bottom_width, top_width, height):
    """
    获取弧面的局部点坐标（仍需要加上y的偏移量）
    :param direction: 方向，'up'为上，'bot'为下
    :param cur: 曲率
    :param bottom_width: 底部宽度
    :param top_width: 顶部宽度
    :param height: 高度
    :return: 左侧点坐标，右侧点坐标，包括中点，所以两侧各有6个点
    """
    result_left = None
    result_right = None
    if direction == 'bot':
        result_left = CIRCLE_POINTS[1:7] + CUR_ADD_POINTS[1:7] * (1 - cur)
        result_right = CIRCLE_POINTS[18:] + CUR_ADD_POINTS[18:] * (1 - cur)
    elif direction == 'up':
        result_left = CIRCLE_POINTS[6:12] + CUR_ADD_POINTS[6:12] * (1 - cur)
        result_right = CIRCLE_POINTS[13:19] + CUR_ADD_POINTS[13:19] * (1 - cur)
    # 对点的x坐标按y在0到1之间的比例，以bottom_width和top_width为基准进行缩放
    result_left[:, 0] = result_left[:, 0] * (bottom_width + (top_width - bottom_width) * (result_left[:, 1] + 1) / 2)
    result_right[:, 0] = result_right[:, 0] * (bottom_width + (top_width - bottom_width) * (result_left[:, 1] + 1) / 2)
    # 对点的y坐标按y在0到1之间的比例，以height为基准进行缩放
    result_left[:, 1] = result_left[:, 1] * height
    result_right[:, 1] = result_right[:, 1] * height
    # print(result_left, result_right)
    return result_left, result_right


def _get_index(half_index):
    """
    根据绘制顶点数计算索引数组（和具体顶点无关）
    前面和后面中，各有2*HALF_INDEX - 1个三角形（除去起始点）
    中间面，有2*2*HALF_INDEX个三角形
    因此数组大小为 2*2*HALF_INDEX + 2*2*HALF_INDEX - 2，也就是 8*HALF_INDEX - 2

    顶点索引顺序规则：
    弧面从左下逆时针（向z-方向看）到右下，前面，后面，左面，右面
    :param half_index: 一半的绘制顶点数
    """
    indexes = np.zeros((8 * half_index - 2, 3), dtype=np.uint32)
    """
    设置弧面（包括零件没有弧度的另一半）
    """
    # 后面开始的索引
    BSI = half_index * 2
    # 左上弧开始的索引
    LTCSI = half_index - 6  # 由于索引，-1，又因为前面的点已经添加，所以-6
    # 右下弧开始的索引
    RBCSI = 2 * half_index - 6  # 因为前面的点已经添加，所以-6
    # 设置左下弧
    indexes[:12] = np.array([
        [0, BSI, BSI + 1], [0, BSI + 1, 1], [1, BSI + 1, BSI + 2], [1, BSI + 2, 2],
        [2, BSI + 2, BSI + 3], [2, BSI + 3, 3], [3, BSI + 3, BSI + 4], [3, BSI + 4, 4],
        [4, BSI + 4, BSI + 5], [4, BSI + 5, 5], [5, BSI + 5, BSI + 6], [5, BSI + 6, 6]
    ])
    # 设置左上弧
    indexes[12:24] = indexes[:12] + LTCSI
    # 设置右上弧
    indexes[24:36] = indexes[:12] + half_index
    # 设置右下弧
    indexes[36:48] = indexes[:12] + RBCSI
    # 末尾连接到起始点
    indexes[46] = [BSI - 1, 2 * BSI - 1, BSI]
    indexes[47] = [BSI - 1, BSI, 0]
    """
    设置前面和后面
    """
    for i in range(BSI - 2):
        # 设置前面
        indexes[i + 48] = [0, i + 1, i + 2]
        # 设置后面
        indexes[i + 48 + BSI - 1] = [BSI, BSI + i + 1, BSI + i + 2]
    """
    设置左面和右面
    """
    _CUR_I = 48 + 2 * (BSI - 2)
    # 除去前面和后面的点，弧面的点，剩下的点数
    _REST_P_NUM = half_index - 11
    # for i in range(_REST_P_NUM):
    #     _i0 = 2 * i
    #     _i1 = _i0 + 1
    #     # 左面
    #     indexes[_i0 + _CUR_I] = [_i0 + 7, _i0 + 7 + BSI, _i0 + 8 + BSI]
    #     indexes[_i1 + _CUR_I] = [_i0 + 7, _i0 + 8 + BSI, _i0 + 8]
    #     # 右面
    #     indexes[_i0 + _CUR_I + _REST_P_NUM * 2] = [half_index + _i0 + 7, half_index + _i0 + 8, half_index + _i0 + 8 + BSI]
    #     indexes[_i1 + _CUR_I + _REST_P_NUM * 2] = [half_index + _i0 + 7, half_index + _i0 + 8 + BSI, half_index + _i0 + 7 + BSI]
    return indexes


class HullSectionItem(GLMeshItem):
    def __init__(self, handler, z, nodes: Union[list, tuple]):
        """
        """
        self.sectionGroup = None  # 船体截面组，将会在HullSectionGroupItem中设置
        self.handler = handler  # 船体截面的处理器
        self._z = z
        self._nodes = nodes
        self._nodes.sort(key=lambda x: x.y)
        _vertexes, _indices, _normals = self.get_mesh_data()
        super().__init__(vertexes=_vertexes,
                         indices=_indices,
                         normals=_normals,
                         glOptions='translucent')

    def getTopCur(self):
        """
        从截面组获取顶部弧度
        """
        return self.handler._parent.topCur  # noqa

    def getBotCur(self):
        """
        从截面组获取底部弧度
        """
        return self.handler._parent.botCur  # noqa

    def get_backSection(self):
        return self.handler._parent._backSection  # noqa

    def get_frontSection(self):
        return self.handler._parent._frontSection  # noqa

    def get_mesh_data(self):
        """
        获取用于绘制的数据
        顶点坐标顺序规则：
        前：从左下靠中间（x0，y-）开始，逆时针排列（向z-方向看）
        后：从左下靠中间（x0，y-）开始，逆时针排列（向z-方向看）
        顶点索引顺序规则：
        弧面从左下逆时针（向z-方向看）到右下，前面，后面，左面，右面
        添加顶点时，需要按点的y值按索引添加，不打乱顺序
        :return:
        """
        if self._z == 0:
            raise ValueError("z不能为0")
        front_z = self._z
        back_z = self._z
        front_nodes = self._nodes
        back_nodes = self._nodes
        if self._z > 0:  # 前
            back_z = self.get_backSection().z  # noqa
            back_nodes = self.get_backSection().nodes  # noqa
        elif self._z < 0:
            front_z = self.get_frontSection().z  # noqa
            front_nodes = self.get_frontSection().nodes  # noqa
        front_top_point0, front_top_point1 = front_nodes[-1], front_nodes[-2]
        back_top_point0, back_top_point1 = back_nodes[-1], back_nodes[-2]
        front_bot_point0, front_bot_point1 = front_nodes[0], front_nodes[1]
        back_bot_point0, back_bot_point1 = back_nodes[0], back_nodes[1]
        _HALF_INDEX = 11 + len(self._nodes)  # 顶部和底部中点分别+1，弧面分别+5，两侧顶部底部重合平均-1，得出11
        # 将前后两个截面的点分别初始化
        front_points = np.array([[0, 0, front_z] for _ in range(2 * _HALF_INDEX)], dtype=np.float32)
        back_points = np.array([[0, 0, back_z] for _ in range(2 * _HALF_INDEX)], dtype=np.float32)
        """先计算带弧度的点"""
        top_cur = self.getTopCur()
        bot_cur = self.getBotCur()
        # 先初始化最底部和最顶部的点的y坐标（x坐标都为0）
        front_points[0][1] = front_bot_point0.y
        back_points[0][1] = back_bot_point0.y
        front_points[_HALF_INDEX][1] = front_top_point0.y
        back_points[_HALF_INDEX][1] = back_top_point0.y
        # 计算弧面的点
        up_cur_height = (front_top_point0.y - front_top_point1.y) / 2
        down_cur_height = (front_bot_point1.y - front_bot_point0.y) / 2
        front_down_left, front_down_right = get_curve_points('bot', bot_cur, front_bot_point0.x, front_bot_point1.x,
                                                             down_cur_height)
        front_up_left, front_up_right = get_curve_points('up', top_cur, front_top_point1.x, front_top_point0.x,
                                                         up_cur_height)
        back_down_left, back_down_right = get_curve_points('bot', bot_cur, back_bot_point0.x, back_bot_point1.x,
                                                           down_cur_height)
        back_up_left, back_up_right = get_curve_points('up', top_cur, back_top_point1.x, back_top_point0.x,
                                                       up_cur_height)
        # 将弧面的y坐标加上顶点的y坐标
        down_offset = (front_bot_point1.y + front_bot_point0.y) / 2
        up_offset = (front_top_point1.y + front_top_point0.y) / 2
        front_down_left[:, 1] += down_offset
        front_down_right[:, 1] += down_offset
        front_up_left[:, 1] += up_offset
        front_up_right[:, 1] += up_offset
        back_down_left[:, 1] += down_offset
        back_down_right[:, 1] += down_offset
        back_up_left[:, 1] += up_offset
        back_up_right[:, 1] += up_offset
        # 将弧面的点扩展为xyz坐标
        front_down_left = np.hstack((front_down_left, np.full((6, 1), front_z)))
        front_down_right = np.hstack((front_down_right, np.full((6, 1), front_z)))
        front_up_left = np.hstack((front_up_left, np.full((6, 1), front_z)))
        front_up_right = np.hstack((front_up_right, np.full((6, 1), front_z)))
        back_down_left = np.hstack((back_down_left, np.full((6, 1), back_z)))
        back_down_right = np.hstack((back_down_right, np.full((6, 1), back_z)))
        back_up_left = np.hstack((back_up_left, np.full((6, 1), back_z)))
        back_up_right = np.hstack((back_up_right, np.full((6, 1), back_z)))
        # 按顺序添加到点集中
        front_points[1:7] = front_down_left
        back_points[1:7] = back_down_left
        # 添加普通点
        for i in range(1, len(self._nodes) - 1):  # 1到-1是为了舍掉顶部底部的已经添加的点
            left_point_i = i + 6  # 左侧顺序填充
            right_point_i = 2 * _HALF_INDEX - i - 6  # 右侧倒序填充
            front_points[left_point_i] = [front_nodes[i].x, front_nodes[i].y, front_z]
            front_points[right_point_i] = [- front_nodes[i].x, front_nodes[i].y, front_z]
            back_points[left_point_i] = [back_nodes[i].x, back_nodes[i].y, back_z]
            back_points[right_point_i] = [- back_nodes[i].x, back_nodes[i].y, back_z]
        # 当前已填充到的索引为 5 + len(self._nodes)
        front_points[_HALF_INDEX - 6:_HALF_INDEX] = front_up_left
        front_points[_HALF_INDEX + 1:_HALF_INDEX + 7] = front_up_right
        front_points[_HALF_INDEX * 2 - 6:] = front_down_right
        back_points[_HALF_INDEX - 6:_HALF_INDEX] = back_up_left
        back_points[_HALF_INDEX + 1:_HALF_INDEX + 7] = back_up_right
        back_points[_HALF_INDEX * 2 - 6:] = back_down_right
        vertexes = np.vstack([front_points, back_points])
        # print(len(front_points), len(back_points), len(vertexes))
        """计算索引"""
        indexes = _get_index(_HALF_INDEX)
        """计算法向量"""
        normals = self._get_vertex_normal(vertexes, indexes, _HALF_INDEX)
        return vertexes, indexes, normals

    def _get_vertex_normal(self, vert, ind, half_index):
        """
        计算顶点法向量
        :param vert: 顶点坐标
        :param ind: 顶点索引
        :return: 法向量
        """
        return vertex_normal_faceNormal(vert, ind)

    def setPoint(self, pointSection, x, y):
        """
        设置船体截面的点
        :param pointSection: 船体截面的点
        :param x: x坐标
        :param y: y坐标
        """
        pointSection.setPoint(x, y)
        self.update_mesh(pointSection.y_index, x, y)

    def update_mesh(self, index, x, y):
        """
        更新网格
        """
        ...  # TODO: Implement this function
        self.update()


class HullSectionGroupItem(GLGraphicsItem):
    def __init__(self, prj, hullSections):
        """
        设置船体截面组整体的变换，并
        :param prj: 工程对象
        :param hullSections: 截面对象列表
        """
        super().__init__(selectable=True)
        self.prj = prj
        # 对截面进行从小到大排序，z越大，越靠前
        hullSections.sort(key=lambda x: x.z)
        self.hullSections = hullSections
        self._front_item: HullSectionGroupItem = self.hullSections[-1]
        self._back_item: HullSectionGroupItem = self.hullSections[0]

    def addLight(self, light):
        for item in self.childItems():
            item.addLight(light)

    def initializeGL(self):
        for item in self.childItems():
            item.initializeGL()

    def setEulerAngles(self, yaw, pitch, roll, local=True):
        q = Quaternion.fromEulerAngles(yaw, pitch, roll)
        self.__transform.rotate(q, local)


class ArmorSectionItem(GLMeshItem):
    def __init__(self, handler, z, nodes):
        """
        """
        super().__init__()
        self.sectionGroup = None  # 船体截面组，将会在ArmorSectionGroupItem中设置
        self.handler = handler
        self._z = z
        self._nodes = nodes

    def setPoint(self, pointSection, x, y):
        """
        设置船体截面的点
        :param pointSection: 船体截面的点
        :param x: x坐标
        :param y: y坐标
        """
        pointSection.setPoint(x, y)
        self.update_mesh(pointSection.y_index, x, y)

    def update_mesh(self, index, x, y):
        """
        更新网格
        """


class ArmorSectionGroupItem(GLGraphicsItem):
    def __init__(self, prj, armorSections):
        """
        设置船体截面组整体的变换，并
        :param prj: 工程对象
        :param armorSections: 截面对象列表
        """
        super().__init__(selectable=True)
        self.prj = prj
        # 对截面进行从小到大排序，z越大，越靠前
        armorSections.sort(key=lambda x: x.z)
        self.armorSections = armorSections
        self._front_item: ArmorSectionGroupItem = self.armorSections[-1]
        self._back_item: ArmorSectionGroupItem = self.armorSections[0]

    def addLight(self, light):
        for item in self.childItems():
            item.addLight(light)

    def paint(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint()

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint_pickMode()

    def paint_selected(self, model_matrix=Matrix4x4()):
        for item in self.childItems():
            item.paint_selected()

    def initializeGL(self):
        for item in self.childItems():
            item.initializeGL()

    def setEulerAngles(self, yaw, pitch, roll, local=True):
        q = Quaternion.fromEulerAngles(yaw, pitch, roll)
        self.__transform.rotate(q, local)
