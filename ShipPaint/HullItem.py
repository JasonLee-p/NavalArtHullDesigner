"""
定义了船体的绘制类
"""
from typing import Union, Literal
from time import perf_counter

import numpy as np
# from main_logger import Log
import OpenGL.GL as gl
from main_logger import Log
from operation.section_op import SectionNodeXMoveOperation
from pyqtOpenGL import Matrix4x4, GLGraphicsItem, GLMeshItem, Quaternion
from pyqtOpenGL.items.GLScatterPlotItem import GLScatterPlotItem
from pyqtOpenGL.items.GLLinePlotItem import GLLinePlotItem
from pyqtOpenGL.items.MeshData import SymetryCylinderMesh, EditItemMaterial

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


class HullVerSecItem(GLMeshItem):
    NODE_HIT_RADIUS = 18
    NODE_MARKER_SIZE = 17
    NODE_MARKER_COLOR = (1.0, 0.05, 0.85)
    SELECTED_CAP_COLOR = (1.0, 0.45, 0.0, 0.42)

    # noinspection PyProtectedMember
    def __init__(self, handler, z, nodes: Union[list, tuple]):
        """
        """
        self.sectionGroup = None  # 船体截面组，将会在HullSectionGroupItem中设置
        self.handler = handler  # 船体截面的处理器
        self._z = z
        self._nodes = nodes
        self._nodes.sort(key=lambda x: x.y)
        self.mesh_data = SymetryCylinderMesh("z")
        if self._z >= 0 and self.handler._backSection is not None:
            # 从前后两个截面的点集中获取点
            front_nodes_data = np.concatenate((
                self.getCurPoints('bot', self._nodes[0], self._nodes[1]),
                self.handler.nodes_data[1: -1],
                self.getCurPoints('up', self._nodes[-2], self._nodes[-1])
            ))
            back_section = self.handler._backSection
            back_nodes_data = np.concatenate((
                self.getCurPoints('bot', back_section.nodes[0], back_section.nodes[1]),
                self.handler._backSection.nodes_data[1: -1],
                self.getCurPoints('up', back_section.nodes[-2], back_section.nodes[-1])
            ))
            self.mesh_data.initPoints(front_nodes_data, back_nodes_data, self._z, back_section.z)
        elif self._z <= 0 and self.handler._frontSection is not None:
            front_section = self.handler._frontSection
            front_nodes_data = np.concatenate((
                self.getCurPoints('bot', front_section.nodes[0], front_section.nodes[1]),
                self.handler._frontSection.nodes_data[1: -1],
                self.getCurPoints('up', front_section.nodes[-2], front_section.nodes[-1])
            ))
            back_nodes_data = np.concatenate((
                self.getCurPoints('bot', self._nodes[0], self._nodes[1]),
                self.handler.nodes_data[1: -1],
                self.getCurPoints('up', self._nodes[-2], self._nodes[-1])
            ))
            self.mesh_data.initPoints(front_nodes_data, back_nodes_data, front_section.z, self._z)
        else:
            raise ValueError("Hull section needs an adjacent section to build mesh")
        self.mesh_data.initVertexes()
        super().__init__(vertexes=self.mesh_data.vertexes,
                         normals=self.mesh_data.normals,
                         indices=np.array([i for i in range(len(self.mesh_data.vertexes))], dtype=np.uint32),
                         material=EditItemMaterial(),
                         # drawLine=True,
                         glOptions='opaque',
                         glUsage=gl.GL_DYNAMIC_DRAW)
        # 用于判断整个截面组是否被选中
        self.parentSelected = False
        self._dragging_node = None
        self._dragging_node_side = 1.0
        self._drag_start_screen_x = 0.0
        self._drag_origin_x = 0.0
        self._drag_screen_per_x = 1.0
        self._drag_operation_started = False
        self.node_marker_item = GLScatterPlotItem(
            pos=self._node_marker_positions(),
            size=self.NODE_MARKER_SIZE,
            color=self.NODE_MARKER_COLOR,
            glOptions='ontop',
            parentItem=self,
        )
        self.node_marker_item.setVisible(False)
        self.node_marker_item.setSelectable(False)
        self.selected_key_line_item = GLLinePlotItem(
            pos=self._selected_key_line_positions(),
            lineWidth=1.8,
            color=(0.1, 0.9, 1.0),
            opacity=0.95,
            glOptions='ontop',
            mode='lines',
            parentItem=self,
        )
        self.selected_key_line_item.setVisible(False)
        self.selected_key_line_item.setSelectable(False)

    def _node_marker_entries(self):
        entries = []
        for node in self._nodes:
            entries.append((node, 1.0, np.array([node.x, node.y, self._z], dtype=np.float32)))
            if abs(node.x) > 1e-6:
                entries.append((node, -1.0, np.array([-node.x, node.y, self._z], dtype=np.float32)))
        return entries

    def _node_marker_positions(self):
        return np.array([entry[2] for entry in self._node_marker_entries()], dtype=np.float32)

    @staticmethod
    def _section_key_loop(section):
        nodes = sorted(section.nodes, key=lambda item: item.y)
        left_points = [[node.x, node.y, section.z] for node in nodes]
        right_points = [[-node.x, node.y, section.z] for node in reversed(nodes)]
        return np.array(left_points + right_points, dtype=np.float32)

    def _segment_key_loops(self):
        if self._z >= 0 and self.handler._backSection is not None:
            return (
                self._section_key_loop(self.handler),
                self._section_key_loop(self.handler._backSection),
            )
        if self._z <= 0 and self.handler._frontSection is not None:
            return (
                self._section_key_loop(self.handler._frontSection),
                self._section_key_loop(self.handler),
            )
        return None, None

    @staticmethod
    def _append_loop_edges(line_points, loop):
        if loop is None or len(loop) < 2:
            return
        for index in range(len(loop)):
            line_points.extend((loop[index], loop[(index + 1) % len(loop)]))

    def _selected_key_line_positions(self):
        line_points = []
        front_loop, back_loop = self._segment_key_loops()
        self._append_loop_edges(line_points, front_loop)
        self._append_loop_edges(line_points, back_loop)
        if front_loop is not None and back_loop is not None:
            for index in range(min(len(front_loop), len(back_loop))):
                line_points.extend((front_loop[index], back_loop[index]))
        if not line_points:
            return np.empty((0, 3), dtype=np.float32)
        return np.array(line_points, dtype=np.float32)

    def _update_selected_key_lines(self):
        self.selected_key_line_item.setData(
            pos=self._selected_key_line_positions(),
            color=(0.1, 0.9, 1.0),
            opacity=0.95,
        )
        if self.selected_key_line_item.visible():
            self.selected_key_line_item.setVisible(False, recursive=False)

    def _update_node_markers(self, positions=None):
        if positions is None:
            positions = self._node_marker_positions()
        self.node_marker_item.setData(pos=positions, color=self.NODE_MARKER_COLOR, size=self.NODE_MARKER_SIZE)
        if self.node_marker_item.visible():
            self.node_marker_item.setVisible(False, recursive=False)

    def paint_selected(self, model_matrix=Matrix4x4()):
        self._flush_pending_vertex_update()
        self.setupGLState()
        self.setupLight(self.shader)
        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("paintLine", False, "bool")
            self.shader.set_uniform("highlight", False, "bool")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
            self._mesh.paint(self.shader)

    def paint_overlay(self, model_matrix=Matrix4x4()):
        if self.selected():
            self._paint_selected_surface_overlay(model_matrix)
            self._paint_node_marker_overlay(model_matrix)
        if self.selected() or self.parentSelected:
            self._paint_selected_key_line_overlay(model_matrix)

    def _setup_overlay_state(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_ALPHA_TEST)
        gl.glDepthFunc(gl.GL_ALWAYS)
        gl.glDepthMask(gl.GL_FALSE)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def _restore_overlay_state(self):
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glDepthMask(gl.GL_TRUE)

    def _paint_selected_surface_overlay(self, model_matrix):
        self._flush_pending_vertex_update()
        cap_start, cap_count = self._selected_cap_range()
        if cap_count == 0:
            return
        self._setup_overlay_state()
        self.setupLight(self.shader)
        with self.shader:
            self.shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.shader.set_uniform("model", model_matrix.glData, "mat4")
            self.shader.set_uniform("paintLine", True, "bool")
            self.shader.set_uniform("lineColor", self.SELECTED_CAP_COLOR, "vec4")
            self.shader.set_uniform("ViewPos", self.view_pos(), "vec3")
            self._mesh._material.set_uniform(self.shader, "material")
            self._mesh.vao.bind()
            gl.glDrawArrays(gl.GL_TRIANGLES, cap_start, cap_count)
            self.shader.set_uniform("paintLine", False, "bool")
        self._restore_overlay_state()

    def _selected_cap_range(self):
        top_count = 0 if self.mesh_data.top_vert is None else len(self.mesh_data.top_vert)
        bottom_count = 0 if self.mesh_data.bottom_vert is None else len(self.mesh_data.bottom_vert)
        if top_count == 0 and bottom_count == 0:
            return 0, 0
        if abs(self.mesh_data.topPos - self._z) <= abs(self.mesh_data.bottomPos - self._z):
            return 0, top_count
        return top_count, bottom_count

    def _paint_selected_key_line_overlay(self, model_matrix):
        if self.selected_key_line_item._num == 0:
            return
        self.selected_key_line_item.initialize()
        self.selected_key_line_item.paint(model_matrix)

    def _paint_node_marker_overlay(self, model_matrix):
        if self.node_marker_item._npoints == 0:
            return
        self.node_marker_item.initialize()
        self.node_marker_item.paint(model_matrix)

    def setSelected(self, s, children=True):
        result = super().setSelected(s, children)
        self._update_node_markers()
        self._update_selected_key_lines()
        return result

    def setSelectable(self, s, children=True):
        super().setSelectable(s, children)
        if hasattr(self, "node_marker_item"):
            self.node_marker_item.setSelectable(False)
        if hasattr(self, "selected_key_line_item"):
            self.selected_key_line_item.setSelectable(False)

    def _effective_view(self):
        view = self.view()
        if view is None and self.parentItem() is not None:
            view = self.parentItem().view()
        return view

    def _node_screen_positions(self):
        view = self._effective_view()
        if view is None:
            return []
        model = self.viewTransform()
        return [view.project_point(node_pos, model) for node_pos in self._node_marker_positions()]

    def begin_node_drag(self, screen_pos):
        view = self._effective_view()
        if not self.selected() or view is None:
            return False
        screen_xy = np.array([screen_pos.x(), screen_pos.y()], dtype=np.float32)
        best_entry = None
        best_distance = self.NODE_HIT_RADIUS
        entries = self._node_marker_entries()
        for entry, node_screen_pos in zip(entries, self._node_screen_positions()):
            if node_screen_pos is None:
                continue
            distance = np.linalg.norm(node_screen_pos[:2] - screen_xy)
            if distance <= best_distance:
                best_entry = entry
                best_distance = distance
        if best_entry is None:
            return False
        node, side, node_pos = best_entry
        reference_pos = np.array([side * (node.x + 1.0), node.y, self._z], dtype=np.float32)
        model = self.viewTransform()
        start_screen = view.project_point(node_pos, model)
        reference_screen = view.project_point(reference_pos, model)
        if start_screen is None or reference_screen is None:
            return False
        screen_per_x = reference_screen[0] - start_screen[0]
        if abs(screen_per_x) < 1e-5:
            return False
        self._dragging_node = node
        self._dragging_node_side = side
        self._drag_start_screen_x = screen_pos.x()
        self._drag_origin_x = node.x
        self._drag_screen_per_x = screen_per_x
        self._drag_operation_started = True
        return True

    def drag_node_to(self, screen_pos):
        if self._dragging_node is None:
            return
        dx = screen_pos.x() - self._drag_start_screen_x
        x = max(0.0, self._drag_origin_x + dx / self._drag_screen_per_x)
        self.setPoint(self._dragging_node, x, self._dragging_node.y)
        self._update_node_markers()

    def end_node_drag(self):
        if self._dragging_node is not None and self._drag_operation_started:
            target_x = self._dragging_node.x
            if abs(target_x - self._drag_origin_x) > 1e-6:
                operation_stack = self._operation_stack()
                operation = SectionNodeXMoveOperation(
                    self.handler,
                    self._dragging_node,
                    target_x,
                    origin_x=self._drag_origin_x,
                )
                if operation_stack is not None:
                    operation_stack.execute(operation)
                else:
                    Log().warning("HullVerSecItem", "节点横向拖拽未进入操作栈：未找到 operationStack")
        self._dragging_node = None
        self._dragging_node_side = 1.0
        self._drag_operation_started = False

    def _operation_stack(self):
        view = self._effective_view()
        main_editor = getattr(view, "main_editor", None) if view is not None else None
        return getattr(main_editor, "operationStack", None)

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        front_section = self.handler._frontSection
        if self._z < 0 and front_section is not None and front_section.z > 0:
            return
        self._flush_pending_vertex_update()
        self.setupGLState()
        with self.pick_shader:
            self.pick_shader.set_uniform("view", self.view_matrix().glData, "mat4")
            self.pick_shader.set_uniform("proj", self.proj_matrix().glData, "mat4")
            self.pick_shader.set_uniform("model", model_matrix.glData, "mat4")
            self.pick_shader.set_uniform("pickColor", self.pickColor(parent=False), "float")
            self._mesh.paint(self.pick_shader)

    def getCurPoints(self, direction: Literal['up', 'bot'], p0: np.ndarray, p1: np.ndarray):
        """
        获取弧度点集（仅左侧）
        :param direction: 方向，'up'为上，'bot'为下
        :param p0: 第一个点（y小）
        :param p1: 第二个点（y大）
        """
        if not isinstance(p0, np.ndarray):
            p0 = np.array([p0.x, p0.y], dtype=np.float32)
        if not isinstance(p1, np.ndarray):
            p1 = np.array([p1.x, p1.y], dtype=np.float32)
        if p1[1] < p0[1]:
            p0, p1 = p1, p0
        offset = (p0[1] + p1[1]) / 2
        if direction == 'up':
            result = CIRCLE_POINTS[6:13] + CUR_ADD_POINTS[6:13] * (1 - self.getTopCur())
        elif direction == 'bot':
            result = CIRCLE_POINTS[:7] + CUR_ADD_POINTS[:7] * (1 - self.getBotCur())
        else:
            raise ValueError("direction参数错误")
        result[:, 0] = result[:, 0] * (p0[0] + (p1[0] - p0[0]) * (result[:, 1] + 1) / 2)
        result[:, 1] = result[:, 1] * (p1[1] - p0[1]) / 2
        result[:, 1] += offset
        return result

    def setZ(self, _z):
        """
        设置z值
        :return:
        """
        if self._z > 0:
            self.mesh_data.setMeshZ(_z, self.handler._backSection.z)
            front_section = self.handler._frontSection
            back_section = self.handler._backSection
            if front_section:
                front_section.paintItem.mesh_data.setMeshZ(front_section.z, _z)
                front_section.paintItem.updateVertexes(
                    front_section.paintItem.mesh_data.vertexes, front_section.paintItem.mesh_data.normals)
            if back_section and back_section.z < 0:
                back_section.paintItem.mesh_data.setMeshZ(_z, back_section.z)
                back_section.paintItem.updateVertexes(
                    back_section.paintItem.mesh_data.vertexes, back_section.paintItem.mesh_data.normals)
        elif self._z < 0:
            self.mesh_data.setMeshZ(self.handler._frontSection.z, _z)
            front_section = self.handler._frontSection
            back_section = self.handler._backSection
            if front_section and front_section.z > 0:
                front_section.paintItem.mesh_data.setMeshZ(front_section.z, _z)
                front_section.paintItem.updateVertexes(
                    front_section.paintItem.mesh_data.vertexes, front_section.paintItem.mesh_data.normals)
            if back_section:
                back_section.paintItem.mesh_data.setMeshZ(_z, back_section.z)
                back_section.paintItem.updateVertexes(
                    back_section.paintItem.mesh_data.vertexes, back_section.paintItem.mesh_data.normals)
        # 更新
        self._z = _z
        self.updateVertexes(self.mesh_data.vertexes, self.mesh_data.normals)

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

    # def get_mesh_data(self):
    #     """
    #     获取用于绘制的数据
    #     顶点坐标顺序规则：
    #     前：从左下靠中间（x0，y-）开始，逆时针排列（向z-方向看）
    #     后：从左下靠中间（x0，y-）开始，逆时针排列（向z-方向看）
    #     顶点索引顺序规则：
    #     弧面从左下逆时针（向z-方向看）到右下，前面，后面，左面，右面
    #     添加顶点时，需要按点的y值按索引添加，不打乱顺序
    #     :return:
    #     """
    #     if self._z == 0:
    #         raise ValueError("z不能为0")
    #     front_z = self._z
    #     back_z = self._z
    #     front_nodes = self._nodes
    #     back_nodes = self._nodes
    #     if self._z > 0:  # 前
    #         back_z = self.get_backSection().z  # noqa
    #         back_nodes = self.get_backSection().nodes  # noqa
    #     elif self._z < 0:
    #         front_z = self.get_frontSection().z  # noqa
    #         front_nodes = self.get_frontSection().nodes  # noqa
    #     front_top_point0, front_top_point1 = front_nodes[-1], front_nodes[-2]
    #     back_top_point0, back_top_point1 = back_nodes[-1], back_nodes[-2]
    #     front_bot_point0, front_bot_point1 = front_nodes[0], front_nodes[1]
    #     back_bot_point0, back_bot_point1 = back_nodes[0], back_nodes[1]
    #     _HALF_INDEX = 11 + len(self._nodes)  # 顶部和底部中点分别+1，弧面分别+5，两侧顶部底部重合平均-1，得出11
    #     # 将前后两个截面的点分别初始化
    #     front_points = np.array([[0, 0, front_z] for _ in range(2 * _HALF_INDEX)], dtype=np.float32)
    #     back_points = np.array([[0, 0, back_z] for _ in range(2 * _HALF_INDEX)], dtype=np.float32)
    #     """先计算带弧度的点"""
    #     top_cur = self.getTopCur()
    #     bot_cur = self.getBotCur()
    #     # 先初始化最底部和最顶部的点的y坐标（x坐标都为0）
    #     front_points[0][1] = front_bot_point0.y
    #     back_points[0][1] = back_bot_point0.y
    #     front_points[_HALF_INDEX][1] = front_top_point0.y
    #     back_points[_HALF_INDEX][1] = back_top_point0.y
    #     # 计算弧面的点
    #     up_cur_height = (front_top_point0.y - front_top_point1.y) / 2
    #     down_cur_height = (front_bot_point1.y - front_bot_point0.y) / 2
    #     front_down_left, front_down_right = get_curve_points('bot', bot_cur, front_bot_point0.x, front_bot_point1.x,
    #                                                          down_cur_height)
    #     front_up_left, front_up_right = get_curve_points('up', top_cur, front_top_point1.x, front_top_point0.x,
    #                                                      up_cur_height)
    #     back_down_left, back_down_right = get_curve_points('bot', bot_cur, back_bot_point0.x, back_bot_point1.x,
    #                                                        down_cur_height)
    #     back_up_left, back_up_right = get_curve_points('up', top_cur, back_top_point1.x, back_top_point0.x,
    #                                                    up_cur_height)
    #     # 将弧面的y坐标加上顶点的y坐标
    #     down_offset = (front_bot_point1.y + front_bot_point0.y) / 2
    #     up_offset = (front_top_point1.y + front_top_point0.y) / 2
    #     front_down_left[:, 1] += down_offset
    #     front_down_right[:, 1] += down_offset
    #     front_up_left[:, 1] += up_offset
    #     front_up_right[:, 1] += up_offset
    #     back_down_left[:, 1] += down_offset
    #     back_down_right[:, 1] += down_offset
    #     back_up_left[:, 1] += up_offset
    #     back_up_right[:, 1] += up_offset
    #     # 将弧面的点扩展为xyz坐标
    #     front_down_left = np.hstack((front_down_left, np.full((6, 1), front_z)))
    #     front_down_right = np.hstack((front_down_right, np.full((6, 1), front_z)))
    #     front_up_left = np.hstack((front_up_left, np.full((6, 1), front_z)))
    #     front_up_right = np.hstack((front_up_right, np.full((6, 1), front_z)))
    #     back_down_left = np.hstack((back_down_left, np.full((6, 1), back_z)))
    #     back_down_right = np.hstack((back_down_right, np.full((6, 1), back_z)))
    #     back_up_left = np.hstack((back_up_left, np.full((6, 1), back_z)))
    #     back_up_right = np.hstack((back_up_right, np.full((6, 1), back_z)))
    #     # 按顺序添加到点集中
    #     front_points[1:7] = front_down_left
    #     back_points[1:7] = back_down_left
    #     # 添加普通点
    #     for i in range(1, len(self._nodes) - 1):  # 1到-1是为了舍掉顶部底部的已经添加的点
    #         left_point_i = i + 6  # 左侧顺序填充
    #         right_point_i = 2 * _HALF_INDEX - i - 6  # 右侧倒序填充
    #         front_points[left_point_i] = [front_nodes[i].x, front_nodes[i].y, front_z]
    #         front_points[right_point_i] = [- front_nodes[i].x, front_nodes[i].y, front_z]
    #         back_points[left_point_i] = [back_nodes[i].x, back_nodes[i].y, back_z]
    #         back_points[right_point_i] = [- back_nodes[i].x, back_nodes[i].y, back_z]
    #     # 当前已填充到的索引为 5 + len(self._nodes)
    #     front_points[_HALF_INDEX - 6:_HALF_INDEX] = front_up_left
    #     front_points[_HALF_INDEX + 1:_HALF_INDEX + 7] = front_up_right
    #     front_points[_HALF_INDEX * 2 - 6:] = front_down_right
    #     back_points[_HALF_INDEX - 6:_HALF_INDEX] = back_up_left
    #     back_points[_HALF_INDEX + 1:_HALF_INDEX + 7] = back_up_right
    #     back_points[_HALF_INDEX * 2 - 6:] = back_down_right
    #     vertexes = np.vstack([front_points, back_points])
    #     """计算索引"""
    #     indexes = _get_index(_HALF_INDEX)
    #     """计算法向量"""
    #     normals = self._get_vertex_normal(vertexes, indexes, _HALF_INDEX)
    #     return vertexes, indexes, normals
    #
    # def _get_vertex_normal(self, vert, ind, half_index):
    #     """
    #     计算顶点法向量
    #     :param vert: 顶点坐标
    #     :param ind: 顶点索引
    #     :return: 法向量
    #     """
    #     return vertex_normal_faceNormal(vert, ind)

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
        self.handler.update_node_data(index, x, y)
        self._rebuild_mesh()
        for neighbor in (self.handler._frontSection, self.handler._backSection):
            if neighbor is not None and neighbor.paintItem is not None:
                neighbor.paintItem._rebuild_mesh()

    def _rebuild_mesh(self):
        """
        Rebuild this section's mesh from the current handler node data.
        """
        start_time = perf_counter()
        mesh_data = SymetryCylinderMesh("z")
        if self._z >= 0 and self.handler._backSection is not None:
            back_section = self.handler._backSection
            front_nodes_data = np.concatenate((
                self.getCurPoints('bot', self._nodes[0], self._nodes[1]),
                self.handler.nodes_data[1: -1],
                self.getCurPoints('up', self._nodes[-2], self._nodes[-1])
            ))
            back_nodes_data = np.concatenate((
                self.getCurPoints('bot', back_section.nodes[0], back_section.nodes[1]),
                back_section.nodes_data[1: -1],
                self.getCurPoints('up', back_section.nodes[-2], back_section.nodes[-1])
            ))
            mesh_data.initPoints(front_nodes_data, back_nodes_data, self._z, back_section.z)
        elif self._z <= 0 and self.handler._frontSection is not None:
            front_section = self.handler._frontSection
            front_nodes_data = np.concatenate((
                self.getCurPoints('bot', front_section.nodes[0], front_section.nodes[1]),
                front_section.nodes_data[1: -1],
                self.getCurPoints('up', front_section.nodes[-2], front_section.nodes[-1])
            ))
            back_nodes_data = np.concatenate((
                self.getCurPoints('bot', self._nodes[0], self._nodes[1]),
                self.handler.nodes_data[1: -1],
                self.getCurPoints('up', self._nodes[-2], self._nodes[-1])
            ))
            mesh_data.initPoints(front_nodes_data, back_nodes_data, front_section.z, self._z)
        else:
            Log().warning(self.TAG, f"{self.handler} has no adjacent section to rebuild mesh")
            return
        mesh_data.initVertexes()
        self.mesh_data = mesh_data
        if self.isInitialized:
            self.updateVertexes(self.mesh_data.vertexes, self.mesh_data.normals)
        else:
            self._mesh._vertexes = self.mesh_data.vertexes
            self._mesh._normals = self.mesh_data.normals
        self._update_node_markers()
        self._update_selected_key_lines()
        self.update()
        view = self.view()
        if view is not None and hasattr(view, "_record_render_stat"):
            view._record_render_stat("hull_rebuild_mesh_ms", (perf_counter() - start_time) * 1000.0)

    def setParentSelected(self, selected):
        """
        当父项被选中时
        """
        self.parentSelected = selected
        if hasattr(self, "selected_key_line_item"):
            self._update_selected_key_lines()


class HullHorSecItem(GLMeshItem):
    TAG = "HullHorSecItem"

    def __init__(self):
        super().__init__(selectable=False)
        ...


class HullSecConnection(GLMeshItem):
    TAG = "HullSecConnection"

    def __init__(self):
        super().__init__(selectable=False)
        ...


class HullSectionGroupItem(GLGraphicsItem):
    TAG = "HullSectionGroupItem"

    def __init__(self, prj, hullSections):
        """
        设置船体截面组整体的变换，不负责具体绘制。
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

    def setSelected(self, s, children=False) -> bool:
        """
        默认选中时不修改子项的选中状态
        :param s:
        :param children:
        :return:
        """
        for item in self.childItems():
            if hasattr(item, 'setParentSelected'):
                item.setParentSelected(s)
        return super().setSelected(s, children)

    def addLight(self, light):
        for item in self.childItems():
            item.addLight(light)

    def initializeGL(self):
        for item in self.childItems():
            item.initializeGL()

    def setEulerAngles(self, yaw, pitch, roll, local=True):
        q = Quaternion.fromEulerAngles(yaw, pitch, roll)
        self.__transform.rotate(q, local)

    def addSection(self, section):
        """
        添加截面，在handler中的addSection中调用
        :param section: 截面对象
        """
        # 排序
        for i in range(len(self.hullSections)):
            if self.hullSections[i].z > section.z:
                self.hullSections.insert(i, section)
                break
        else:
            self.hullSections.append(section)
        section.paintItem.setParent(self)
        # 更新前后截面
        self._front_item = self.hullSections[-1]
        self._back_item = self.hullSections[0]

    def delSection(self, section):
        """
        删除截面，在handler中的delSection中调用
        :param section: 截面对象
        """
        self.hullSections.remove(section)
        # 更新前后截面
        self._front_item = self.hullSections[-1]
        self._back_item = self.hullSections[0]


class ArmorSectionItem(HullVerSecItem):
    def __init__(self, handler, z, nodes):
        """
        """
        super().__init__(handler, z, nodes)

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
        super().update_mesh(index, x, y)


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

    def setSelected(self, s, children=False) -> bool:
        for item in self.childItems():
            if hasattr(item, 'setParentSelected'):
                item.setParentSelected(s)
        return super().setSelected(s, children)

    def addLight(self, light):
        for item in self.childItems():
            item.addLight(light)

    def paint(self, model_matrix=Matrix4x4()):
        pass

    def paint_pickMode(self, model_matrix=Matrix4x4()):
        pass

    def paint_selected(self, model_matrix=Matrix4x4()):
        pass

    def initializeGL(self):
        for item in self.childItems():
            item.initializeGL()

    def setEulerAngles(self, yaw, pitch, roll, local=True):
        q = Quaternion.fromEulerAngles(yaw, pitch, roll)
        self.__transform.rotate(q, local)
