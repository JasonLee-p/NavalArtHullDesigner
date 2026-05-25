"""

"""
from .basic_op import Operation


def _request_section_update(section_handler):
    paint_item = getattr(section_handler, "paintItem", None)
    view = paint_item.view() if paint_item is not None else None
    if view is not None:
        view.update()


class SectionDeleteOperation(Operation):
    def __init__(self, sectionHandler, parent=None):
        """
        删除截面操作
        :param sectionHandler: 被删除的截面
        :param parent: 父对象
        """
        super().__init__()
        self.name = f"删除 {sectionHandler.name}"
        self.sectionHandler = sectionHandler
        self.parent = parent  # sectionGroupItem

    def execute(self):
        self.parent._del_section(self.sectionHandler)

    def undo(self):
        self.parent._add_section(self.sectionHandler)

    def redo(self):
        self.execute()


class SectionZMoveOperation(Operation):
    def __init__(self, sectionHandler, target_posZ, edits=None):
        """
        截面的Z坐标移动操作
        :param sectionHandler: 被移动的元素
        :param target_posZ: 目标位置
        :param edits: 相关的显示控件
        """
        super().__init__()
        self.name = f"移动 {sectionHandler.name} 到 {round(target_posZ, 4)}"
        self.sectionHandler = sectionHandler
        self.target_posZ = target_posZ if target_posZ else sectionHandler.z
        self.origin_pos = sectionHandler.z
        self.edits = edits

    def execute(self):
        self.sectionHandler.setZ(self.target_posZ)
        # 通知gl_widget更新
        _request_section_update(self.sectionHandler)

    def undo(self):
        self.sectionHandler.setZ(self.origin_pos, undo=True)
        for edit in self.edits:
            edit.setValue(self.origin_pos)
        # 通知gl_widget更新
        _request_section_update(self.sectionHandler)

    def redo(self):
        for edit in self.edits:
            edit.setValue(self.target_posZ)
        self.execute()


class SectionNodeXMoveOperation(Operation):
    def __init__(self, sectionHandler, node, target_x, origin_x=None):
        """
        船体截面节点横向移动操作。
        :param sectionHandler: 节点所属截面
        :param node: 被移动的节点对象
        :param target_x: 目标横向坐标
        :param origin_x: 起始横向坐标；拖拽时节点已实时移动，因此需要显式传入
        """
        super().__init__()
        self.sectionHandler = sectionHandler
        self.node = node
        self.node_index = node.y_index
        self.origin_x = node.x if origin_x is None else origin_x
        self.target_x = target_x
        self.name = f"移动 {sectionHandler.name} 节点横向位置到 {round(target_x, 4)}"

    def _node(self):
        if self.node in self.sectionHandler.nodes:
            return self.node
        return self.sectionHandler.nodes[self.node_index]

    def _set_node_x(self, x):
        node = self._node()
        self.sectionHandler.paintItem.setPoint(node, x, node.y)
        _request_section_update(self.sectionHandler)

    def execute(self):
        self._set_node_x(self.target_x)

    def undo(self):
        self._set_node_x(self.origin_x)

    def redo(self):
        self.execute()
