# -*- coding: utf-8 -*-
"""
main_editor的功能性子控件，例如专门显示船体截面组的控件
"""
from .basic_widgets import *

from operation import *


class EditTabWidget(QWidget):
    pos_changed_s = pyqtSignal(list)
    rot_changed_s = pyqtSignal(list)

    main_editor = None
    gl_widget = None
    operationStack: OperationStack = None

    def __init__(self):
        super().__init__(None)
        self._current_item = None
        self.basic_info_widget = QWidget()
        self.basic_info_layout = QGridLayout()
        self.sub_elements_widget = QWidget()
        self.sub_elements_layout = QVBoxLayout()
        _font = YAHEI[9]
        self.posX_edit = NumberEdit(None, self, (68, 24), float, rounding=4, step=0.1, font=_font)
        self.posY_edit = NumberEdit(None, self, (68, 24), float, rounding=4, step=0.1, font=_font)
        self.posZ_edit = NumberEdit(None, self, (68, 24), float, rounding=4, step=0.1, font=_font)
        self.rotX_edit = NumberEdit(None, self, (68, 24), float, (-180, 180), 2, step=0.5, font=_font)
        self.rotY_edit = NumberEdit(None, self, (68, 24), float, (-180, 180), 2, step=0.5, font=_font)
        self.rotZ_edit = NumberEdit(None, self, (68, 24), float, (-180, 180), 2, step=0.5, font=_font)

    def _getMainEditor(self):
        """
        利用递归获取最顶层的MainEditor对象
        :return:
        """
        widget = self.parent()
        while widget.parent():
            widget = widget.parent()
        return widget

    def _init_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(10)
        self.setMinimumWidth(300)
        self._init_basic_info_ui()
        self._init_sub_elements_ui()
        self.layout().addWidget(self.basic_info_widget)
        self.layout().addWidget(self.sub_elements_widget)

    def _init_basic_info_ui(self):
        self.basic_info_widget.setLayout(self.basic_info_layout)
        self.basic_info_layout.setAlignment(Qt.AlignTop)
        self.basic_info_layout.setContentsMargins(0, 0, 0, 0)
        self.basic_info_layout.setHorizontalSpacing(6)
        self.basic_info_layout.setVerticalSpacing(1)
        _font = YAHEI[9]
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "中心位置", _font, bg=BG_COLOR1), 0, 0,
                                         alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.posX_edit, 0, 1)
        self.basic_info_layout.addWidget(self.posY_edit, 0, 2)
        self.basic_info_layout.addWidget(self.posZ_edit, 0, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "旋转角度", _font, bg=BG_COLOR1), 1, 0,
                                         alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.rotX_edit, 1, 1)
        self.basic_info_layout.addWidget(self.rotY_edit, 1, 2)
        self.basic_info_layout.addWidget(self.rotZ_edit, 1, 3)

    def _init_sub_elements_ui(self):
        self.sub_elements_widget.setLayout(self.sub_elements_layout)
        self.sub_elements_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_elements_layout.setSpacing(2)

    def _bind_signals(self):
        self.posX_edit.value_changed.connect(
            lambda x: self.setPosX(x, [self.posX_edit, self.posY_edit, self.posZ_edit]))
        self.posY_edit.value_changed.connect(
            lambda y: self.setPosY(y, [self.posX_edit, self.posY_edit, self.posZ_edit]))
        self.posZ_edit.value_changed.connect(
            lambda z: self.setPosZ(z, [self.posX_edit, self.posY_edit, self.posZ_edit]))
        self.rotX_edit.value_changed.connect(
            lambda x: self.setRotX(x, [self.rotX_edit, self.rotY_edit, self.rotZ_edit]))
        self.rotY_edit.value_changed.connect(
            lambda y: self.setRotY(y, [self.rotX_edit, self.rotY_edit, self.rotZ_edit]))
        self.rotZ_edit.value_changed.connect(
            lambda z: self.setRotZ(z, [self.rotX_edit, self.rotY_edit, self.rotZ_edit]))


    @abstractmethod
    def updateSectionHandler(self, item):
        self._current_item = item
        self.posX_edit.setValue(item.Pos.x())
        self.posY_edit.setValue(item.Pos.y())
        self.posZ_edit.setValue(item.Pos.z())

    def setPosX(self, x, edits):
        op = MoveToOperation(self._current_item, QVector3D(x, self._current_item.Pos.y(), self._current_item.Pos.z()), edits)
        self.operationStack.execute(op)

    def setPosY(self, y, edits):
        op = MoveToOperation(self._current_item, QVector3D(self._current_item.Pos.x(), y, self._current_item.Pos.z()), edits)
        self.operationStack.execute(op)

    def setPosZ(self, z, edits):
        op = MoveToOperation(self._current_item, QVector3D(self._current_item.Pos.x(), self._current_item.Pos.y(), z), edits)
        self.operationStack.execute(op)

    def setRotX(self, x, edits):
        op = RotateOperation(self._current_item, [x, self._current_item.Rot[1], self._current_item.Rot[2]], edits)
        self.operationStack.execute(op)

    def setRotY(self, y, edits):
        op = RotateOperation(self._current_item, [self._current_item.Rot[0], y, self._current_item.Rot[2]], edits)
        self.operationStack.execute(op)

    def setRotZ(self, z, edits):
        op = RotateOperation(self._current_item, [self._current_item.Rot[0], self._current_item.Rot[1], z], edits)
        self.operationStack.execute(op)


class EditHullSectionGroupWidget(EditTabWidget):
    def __init__(self):
        """
        一次只显示一个船体截面组的编辑控件
        """
        _font = YAHEI[9]
        self.sizeX_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.sizeY_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.sizeZ_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.section_num_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)

        super().__init__()
        # TODO: 需要添加到结构层级控件中，由PrjHullSectionGroup进行管理以及信号传递
        self.front_addSection_bt = Button(None, "向前添加截面", bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3), bd_radius=(12, 12, 0, 0), align=Qt.AlignLeft | Qt.AlignTop, size=None)
        self.back_addSection_bt = Button(None, "向后添加截面", bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3), bd_radius=(0, 0, 12, 12), align=Qt.AlignLeft | Qt.AlignTop, size=None)
        self.hullSections_widget = QWidget()
        self.hullSections_layout = QVBoxLayout()
        self.hullSections_scroll = ScrollArea(
            None, self.hullSections_widget, Qt.Vertical, bd_radius=0, bg=BG_COLOR0, bar_bg=BG_COLOR1)
        self._init_ui()
        self._bind_signals()

    def _init_ui(self):
        super()._init_ui()
        self.sizeX_show.setFixedHeight(24)
        self.sizeY_show.setFixedHeight(24)
        self.sizeZ_show.setFixedHeight(24)
        self.section_num_show.setFixedHeight(24)
        self.front_addSection_bt.setFixedHeight(26)
        self.back_addSection_bt.setFixedHeight(26)
        self.front_addSection_bt.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.back_addSection_bt.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))

    def _init_basic_info_ui(self):
        super()._init_basic_info_ui()
        _font = QFont(YAHEI[9])
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "船体大小", _font, bg=BG_COLOR1), 2, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.sizeX_show, 2, 1)
        self.basic_info_layout.addWidget(self.sizeY_show, 2, 2)
        self.basic_info_layout.addWidget(self.sizeZ_show, 2, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "截面数量", _font, bg=BG_COLOR1), 3, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.section_num_show, 3, 1)

    def _init_sub_elements_ui(self):
        super()._init_sub_elements_ui()
        self.sub_elements_widget.layout().addWidget(self.front_addSection_bt)
        self.sub_elements_widget.layout().addWidget(self.hullSections_scroll)
        self.sub_elements_widget.layout().addWidget(self.back_addSection_bt)
        # 设置图标
        self.front_addSection_bt.setIcon(QIcon(QPixmap(ADD_IMAGE)))
        self.back_addSection_bt.setIcon(QIcon(QPixmap(ADD_IMAGE)))
        # 设置按钮行为
        self.front_addSection_bt.clicked.connect(self.add_front_section)
        self.back_addSection_bt.clicked.connect(self.add_back_section)

    def _bind_signals(self):
        super()._bind_signals()

    def add_front_section(self):
        ...

    def add_back_section(self):
        ...

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])


class EditArmorSectionGroupWidget(EditTabWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_signals()

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])


class EditBridgeWidget(EditTabWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_signals()

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)


class EditLadderWidget(EditTabWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_signals()

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])


class EditModelWidget(EditTabWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_signals()

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])

    def _bind_signals(self):
        super()._bind_signals()
