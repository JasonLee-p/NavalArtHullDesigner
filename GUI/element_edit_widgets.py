# -*- coding: utf-8 -*-
"""
main_editor的功能性子控件，例如专门显示船体截面组的控件
"""
from .basic_widgets import *


class StructureHullSectionGroupWidget(Button):
    all_widgets = []
    current_widget = None

    def __init__(self, edit_widget):
        """
        显示船体截面组的控件，包括中心位置，旋转角度（欧拉），截面数量，局部坐标长度，局部坐标宽度，局部坐标高度等信息
        """
        super().__init__(None, "船体截面组", bd_radius=5, align=Qt.AlignLeft | Qt.AlignTop)
        self.widget_change_mutex = QMutex()
        self.widget_change_locker = QMutexLocker(self.widget_change_mutex)
        self.edit_widget = edit_widget
        self.setLayout(QVBoxLayout())
        self.info_widget = QWidget()
        self.info_widget_layout = QGridLayout()
        self.show_name_label = ColoredTextLabel(self.info_widget, "未命名", YAHEI[9], bg=BG_COLOR1)
        self.show_pos_label = ColoredTextLabel(self.info_widget, "0,0,0", YAHEI[9], bg=BG_COLOR1)
        self.show_rot_label = ColoredTextLabel(self.info_widget, "0,0,0", YAHEI[9], bg=BG_COLOR1)
        self.show_size_label = ColoredTextLabel(self.info_widget, "0,0,0", YAHEI[9], bg=BG_COLOR1)
        self.show_section_num_label = ColoredTextLabel(self.info_widget, "0", YAHEI[9], bg=BG_COLOR1)

        self.__init_ui()
        self.__bind_signals()
        self.all_widgets.append(self)

    def __init_ui(self):
        self.setCheckable(True)
        self.setChecked(False)
        self.info_widget_layout.addWidget(ColoredTextLabel(None, "面组名称", YAHEI[9], bg=BG_COLOR1), 0, 0)
        self.info_widget_layout.addWidget(self.show_name_label, 0, 1)
        self.info_widget_layout.addWidget(ColoredTextLabel(None, "中心位置", YAHEI[9], bg=BG_COLOR1), 1, 0)
        self.info_widget_layout.addWidget(self.show_pos_label, 1, 1)
        self.info_widget_layout.addWidget(ColoredTextLabel(None, "旋转角度", YAHEI[9], bg=BG_COLOR1), 2, 0)
        self.info_widget_layout.addWidget(self.show_rot_label, 2, 1)
        self.info_widget_layout.addWidget(ColoredTextLabel(None, "船体大小", YAHEI[9], bg=BG_COLOR1), 3, 0)
        self.info_widget_layout.addWidget(self.show_size_label, 3, 1)
        self.info_widget_layout.addWidget(ColoredTextLabel(None, "截面数量", YAHEI[9], bg=BG_COLOR1), 4, 0)
        self.info_widget_layout.addWidget(self.show_section_num_label, 4, 1)
        self.info_widget.setLayout(self.info_widget_layout)
        self.layout().addWidget(self.info_widget)
        self.update_name("未命名截面组")
        self.update_pos([0, 0, 0])
        self.update_rot([0, 0, 0])
        self.update_size([0, 0, 0])
        self.update_section_num(0)

    def __bind_signals(self):
        ...

    def click(self):
        with self.widget_change_locker:
            super().click()
            if self.isChecked():
                if StructureHullSectionGroupWidget.current_widget is not None:
                    StructureHullSectionGroupWidget.current_widget.setChecked(False)
                StructureHullSectionGroupWidget.current_widget = self
            else:
                StructureHullSectionGroupWidget.current_widget = None

    def update_name(self, name: str):
        self.show_name_label.setText(name)

    def update_pos(self, pos: Union[str, List[float]]):
        if isinstance(pos, str):
            self.show_pos_label.setText(pos)
        else:
            self.show_pos_label.setText(f"{pos[0]:.4f},{pos[1]:.4f},{pos[2]:.4f}")

    def update_rot(self, rot: Union[str, List[float]]):
        if isinstance(rot, str):
            self.show_rot_label.setText(rot)
        else:
            self.show_rot_label.setText(f"{rot[0]:.4f},{rot[1]:.4f},{rot[2]:.4f}")

    def update_size(self, size: Union[str, List[float]]):
        if isinstance(size, str):
            self.show_size_label.setText(size)
        else:
            self.show_size_label.setText(f"{size[0]:.4f},{size[1]:.4f},{size[2]:.4f}")

    def update_section_num(self, num: int):
        self.show_section_num_label.setText(str(num))


class EditHullSectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...


class EditHullSectionGroupWidget(QWidget):
    name_changed = pyqtSignal(str)
    pos_changed = pyqtSignal(list)
    rot_changed = pyqtSignal(list)
    size_changed = pyqtSignal(list)
    section_num_changed = pyqtSignal(int)

    def __init__(self):
        """
        一次只显示一个船体截面组的编辑控件
        """
        super().__init__()
        # TODO: 需要添加到结构层级控件中，由PrjHullSectionGroup进行管理以及信号传递
        self.structure_widget = StructureHullSectionGroupWidget(edit_widget=self)

        self.basic_info_widget = QWidget()
        self.basic_info_layout = QGridLayout()
        self.hullSections_outer_widget = QWidget()
        self.front_addSection_bt = Button(None, "向前添加截面", bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3), bd_radius=(12, 12, 0, 0), align=Qt.AlignLeft | Qt.AlignTop, size=None)
        self.back_addSection_bt = Button(None, "向后添加截面", bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3), bd_radius=(0, 0, 12, 12), align=Qt.AlignLeft | Qt.AlignTop, size=None)
        self.hullSections_widget = QWidget()
        self.hullSections_layout = QVBoxLayout()
        self.hullSections_scroll = ScrollArea(
            None, self.hullSections_widget, Qt.Vertical, bd_radius=0, bg=BG_COLOR0, bar_bg=BG_COLOR1)
        _font = QFont(YAHEI[9])
        self.name_edit = TextEdit("未命名船体截面组", parent=None, font=_font)
        self.posX_edit = NumberEdit(None, self, (68, None), float, rounding=4, step=0.1, font=_font)
        self.posY_edit = NumberEdit(None, self, (68, None), float, rounding=4, step=0.1, font=_font)
        self.posZ_edit = NumberEdit(None, self, (68, None), float, rounding=4, step=0.1, font=_font)
        self.rotX_edit = NumberEdit(None, self, (68, None), float, (-180, 180), 2, step=0.5, font=_font)
        self.rotY_edit = NumberEdit(None, self, (68, None), float, (-180, 180), 2, step=0.5, font=_font)
        self.rotZ_edit = NumberEdit(None, self, (68, None), float, (-180, 180), 2, step=0.5, font=_font)
        self.sizeX_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.sizeY_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.sizeZ_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.section_num_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.sizeX_show.setFixedHeight(28)
        self.sizeY_show.setFixedHeight(28)
        self.sizeZ_show.setFixedHeight(28)
        self.section_num_show.setFixedHeight(28)
        self.__init_ui()
        self.__bind_signals()

    def __init_ui(self):
        self.setMinimumWidth(280)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(10)
        self.basic_info_widget.setLayout(self.basic_info_layout)
        self.basic_info_layout.setAlignment(Qt.AlignTop)
        self.basic_info_layout.setContentsMargins(0, 0, 0, 0)
        self.basic_info_layout.setHorizontalSpacing(9)
        self.basic_info_layout.setVerticalSpacing(3)
        self.__init_basic_info_ui()
        self.front_addSection_bt.setFixedHeight(26)
        self.back_addSection_bt.setFixedHeight(26)
        self.front_addSection_bt.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.back_addSection_bt.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.__init_hullSections_ui()
        # 布局
        self.layout().addWidget(self.basic_info_widget)
        self.layout().addWidget(self.hullSections_outer_widget)

    def __init_basic_info_ui(self):
        _font = QFont(YAHEI[9])
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "面组名称", _font, bg=BG_COLOR1), 0, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.name_edit, 0, 1, 1, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "中心位置", _font, bg=BG_COLOR1), 1, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.posX_edit, 1, 1)
        self.basic_info_layout.addWidget(self.posY_edit, 1, 2)
        self.basic_info_layout.addWidget(self.posZ_edit, 1, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "旋转角度", _font, bg=BG_COLOR1), 2, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.rotX_edit, 2, 1)
        self.basic_info_layout.addWidget(self.rotY_edit, 2, 2)
        self.basic_info_layout.addWidget(self.rotZ_edit, 2, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "船体大小", _font, bg=BG_COLOR1), 3, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.sizeX_show, 3, 1)
        self.basic_info_layout.addWidget(self.sizeY_show, 3, 2)
        self.basic_info_layout.addWidget(self.sizeZ_show, 3, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "截面数量", _font, bg=BG_COLOR1), 4, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.section_num_show, 4, 1)

    def __init_hullSections_ui(self):
        self.hullSections_outer_widget.setLayout(QVBoxLayout())
        self.hullSections_outer_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.hullSections_outer_widget.layout().setSpacing(2)
        self.hullSections_outer_widget.layout().addWidget(self.front_addSection_bt)
        self.hullSections_outer_widget.layout().addWidget(self.hullSections_scroll)
        self.hullSections_outer_widget.layout().addWidget(self.back_addSection_bt)
        # 设置图标
        self.front_addSection_bt.setIcon(QIcon(QPixmap(ADD_IMAGE)))
        self.back_addSection_bt.setIcon(QIcon(QPixmap(ADD_IMAGE)))
        # 设置按钮行为
        self.front_addSection_bt.clicked.connect(self.add_front_section)
        self.back_addSection_bt.clicked.connect(self.add_back_section)

    def __bind_signals(self):
        self.name_edit.textChanged.connect(self.name_changed)
        self.posX_edit.value_changed.connect(lambda x: self.pos_changed.emit([x, self.posY_edit.value(), self.posZ_edit.value()]))
        self.posY_edit.value_changed.connect(lambda y: self.pos_changed.emit([self.posX_edit.value(), y, self.posZ_edit.value()]))
        self.posZ_edit.value_changed.connect(lambda z: self.pos_changed.emit([self.posX_edit.value(), self.posY_edit.value(), z]))
        self.rotX_edit.value_changed.connect(lambda x: self.rot_changed.emit([x, self.rotY_edit.value(), self.rotZ_edit.value()]))
        self.rotY_edit.value_changed.connect(lambda y: self.rot_changed.emit([self.rotX_edit.value(), y, self.rotZ_edit.value()]))
        self.rotZ_edit.value_changed.connect(lambda z: self.rot_changed.emit([self.rotX_edit.value(), self.rotY_edit.value(), z]))

    @abstractmethod
    def add_front_section(self):
        ...

    @abstractmethod
    def add_back_section(self):
        ...


class EditArmorSectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...


class EditArmorSectionGroupWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...


class EditBridgeWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...


class EditEngineWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...


class EditRailingWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...


class EditHandrailWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...


class EditLadderWidget(QWidget):
    def __init__(self):
        super().__init__()
        ...
