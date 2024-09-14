# -*- coding: utf-8 -*-
"""
main_editor的功能性子控件，例如专门显示船体截面组的控件
"""
import traceback

import const
from main_logger import Log

from .basic_widgets import *
from operation import *


class EditTabWidget(QWidget):
    pos_changed_s = pyqtSignal(list)  # noqa
    rot_changed_s = pyqtSignal(list)  # noqa

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
        self.posX_edit = NumberEdit(None, self, (68, 24), float, rounding=const.DECIMAL_PRECISION, step=0.1, font=_font)
        self.posY_edit = NumberEdit(None, self, (68, 24), float, rounding=const.DECIMAL_PRECISION, step=0.1, font=_font)
        self.posZ_edit = NumberEdit(None, self, (68, 24), float, rounding=const.DECIMAL_PRECISION, step=0.1, font=_font)
        self.rotX_edit = NumberEdit(None, self, (68, 24), float, (-180, 180), 2, step=0.5, font=_font)
        self.rotY_edit = NumberEdit(None, self, (68, 24), float, (-180, 180), 2, step=0.5, font=_font)
        self.rotZ_edit = NumberEdit(None, self, (68, 24), float, (-180, 180), 2, step=0.5, font=_font)
        self.sclX_edit = NumberEdit(None, self, (68, 24), float, (0.0001, 100000), const.DECIMAL_PRECISION, 1, 0.1, YAHEI[9])
        self.sclY_edit = NumberEdit(None, self, (68, 24), float, (0.0001, 100000), const.DECIMAL_PRECISION, 1, 0.1, YAHEI[9])
        self.sclZ_edit = NumberEdit(None, self, (68, 24), float, (0.0001, 100000), const.DECIMAL_PRECISION, 1, 0.1, YAHEI[9])

    def _getMainEditor(self):
        """
        利用递归获取最顶层的MainEditor对象
        :return:
        """
        widget = self.parent()
        while widget.parent():
            widget = widget.parent()
        return widget

    def currentItem(self):
        return self._current_item

    def _init_ui(self):
        """
        仅初始化基础界面，具体界面请重载_init_sub_elements_ui
        :return:
        """
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
        self.basic_info_layout.addWidget(ColoredTextLabel(
            None, "中心位置", _font, bg='transparent'), 0, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.posX_edit, 0, 1)
        self.basic_info_layout.addWidget(self.posY_edit, 0, 2)
        self.basic_info_layout.addWidget(self.posZ_edit, 0, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(
            None, "旋转角度", _font, bg='transparent'), 1, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
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
        self.sclX_edit.value_changed.connect(
            lambda x: self.setSclX(x, [self.sclX_edit, self.sclY_edit, self.sclZ_edit]))
        self.sclY_edit.value_changed.connect(
            lambda y: self.setSclY(y, [self.sclX_edit, self.sclY_edit, self.sclZ_edit]))
        self.sclZ_edit.value_changed.connect(
            lambda z: self.setSclZ(z, [self.sclX_edit, self.sclY_edit, self.sclZ_edit]))

    @abstractmethod
    def updateSectionHandler(self, item):
        self._current_item = item
        self.posX_edit.setValue(item.Pos.x())
        self.posY_edit.setValue(item.Pos.y())
        self.posZ_edit.setValue(item.Pos.z())

    def setPosX(self, x, edits):
        op = MoveToOperation(self._current_item, QVector3D(x, self._current_item.Pos.y(), self._current_item.Pos.z()),
                             edits)
        self.operationStack.execute(op)

    def setPosY(self, y, edits):
        op = MoveToOperation(self._current_item, QVector3D(self._current_item.Pos.x(), y, self._current_item.Pos.z()),
                             edits)
        self.operationStack.execute(op)

    def setPosZ(self, z, edits):
        op = MoveToOperation(self._current_item, QVector3D(self._current_item.Pos.x(), self._current_item.Pos.y(), z),
                             edits)
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

    def setSclX(self, x, edits):
        op = ScaleOperation(self._current_item, [x, self._current_item.Scl[1], self._current_item.Scl[2]], edits)
        self.operationStack.execute(op)

    def setSclY(self, y, edits):
        op = ScaleOperation(self._current_item, [self._current_item.Scl[0], y, self._current_item.Scl[2]], edits)
        self.operationStack.execute(op)

    def setSclZ(self, z, edits):
        op = ScaleOperation(self._current_item, [self._current_item.Scl[0], self._current_item.Scl[1], z], edits)
        self.operationStack.execute(op)


class EditHullSectionGroupWidget(EditTabWidget):
    Instance: Optional['EditHullSectionGroupWidget'] = None

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
        self.front_addSection_bt = Button(None, "向前添加截面", bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3),
                                          bd_radius=(12, 12, 0, 0), align=Qt.AlignLeft | Qt.AlignTop, size=None)
        self.back_addSection_bt = Button(None, "向后添加截面", bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3),
                                         bd_radius=(0, 0, 12, 12), align=Qt.AlignLeft | Qt.AlignTop, size=None)
        self.hullSections_widget = QWidget()  # 截面的ShowButton将会被添加到这个widget中
        self.hullSections_layout = QVBoxLayout(self.hullSections_widget)
        self.hullSections_scroll = ScrollArea(
            None, self.hullSections_widget, Qt.Vertical, bd_radius=0, bg=BG_COLOR0, bar_bg=BG_COLOR1)
        self._init_ui()
        self._bind_signals()
        EditHullSectionGroupWidget.Instance = self

    def _init_ui(self):
        super()._init_ui()
        self.hullSections_layout.setAlignment(Qt.AlignTop)
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
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "船体大小", _font, bg='transparent'), 2, 0,
                                         alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.sizeX_show, 2, 1)
        self.basic_info_layout.addWidget(self.sizeY_show, 2, 2)
        self.basic_info_layout.addWidget(self.sizeZ_show, 2, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(None, "截面数量", _font, bg='transparent'), 3, 0,
                                         alignment=Qt.AlignLeft | Qt.AlignVCenter)
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
        """
        检测当前被选择的section，在该section的前面添加一个section
        :return:
        """
        ...

    def add_back_section(self):
        """
        检测当前被选择的section，在该section的后面添加一个section
        :return:
        """
        ...

    def add_section_showButton(self, section):
        """
        添加一个section的showButton到界面中
        在sectironGroup初始化中被调用
        最终所有sectionGroup的所有section的showButton都会被添加到控件中，
        但是只有当前被选择的sectionGroup的showButton是可见的。
        :param section:
        :return:
        """
        self.hullSections_layout.addWidget(section.showButton())

    def updateSectionHandler(self, item):
        """
        当item被选择时，更新界面
        函数内将会链接item的值修改信号到界面的槽函数
        :param item: HullSectionGroup
        :return:
        """
        if self._current_item:
            for section in self._current_item.get_sections():
                section.showButton().hide()
                section.showButton().setChecked(False)
        # # 解绑原信号  # TODO
        # if self._current_item:
        #     self._current_item.update_front_z_s.disconnect(self.updateFrontZ)
        #     self._current_item.update_back_z_s.disconnect(self.updateBackZ)
        # 链接信号：
        if hasattr(item, 'update_front_z_s'):
            # 前后截面z值修改信号
            item.update_front_z_s.connect(self.updateFrontZ)
            item.update_back_z_s.connect(self.updateBackZ)
        super().updateSectionHandler(item)
        for section in item.get_sections():
            section.showButton().show()
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])
        self.updateSize()
        self.updateNum()
        self.updateSections()

    def updateSize(self):
        _frontSection = self._current_item._frontSection
        _backSection = self._current_item._backSection
        self.sizeX_show.setText(str(round(2 * self._current_item.getMaxX(), const.DECIMAL_PRECISION)))
        self.sizeY_show.setText(str(round(_frontSection.nodes[-1].y - _frontSection.nodes[0].y, const.DECIMAL_PRECISION)))
        self.sizeZ_show.setText(str(round(_frontSection.z - _backSection.z, const.DECIMAL_PRECISION)))

    def updateFrontZ(self):
        self.sizeZ_show.setText(str(round(self._current_item._frontSection.z - self._current_item._backSection.z, const.DECIMAL_PRECISION)))

    def updateBackZ(self):
        self.sizeZ_show.setText(str(round(self._current_item._frontSection.z - self._current_item._backSection.z, const.DECIMAL_PRECISION)))

    def updateNum(self):
        self.section_num_show.setText(str(len(self._current_item.get_sections())))

    def updateSections(self):
        ...


class EditArmorSectionGroupWidget(EditTabWidget):
    Instance: Optional['EditArmorSectionGroupWidget'] = None

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_signals()
        EditArmorSectionGroupWidget.Instance = self

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])


class EditBridgeWidget(EditTabWidget):
    Instance: Optional['EditBridgeWidget'] = None

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_signals()
        EditBridgeWidget.Instance = self

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)


class EditLadderWidget(EditTabWidget):
    Instance: Optional['EditLadderWidget'] = None

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._bind_signals()
        EditLadderWidget.Instance = self

    def updateSectionHandler(self, item):
        super().updateSectionHandler(item)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])


class EditModelWidget(EditTabWidget):
    TAG = "EditModelWidget"
    Instance: Optional['EditModelWidget'] = None

    def __init__(self):
        super().__init__()
        self.pathButton = Button(None, "单击：重新选择模型路径", bg=('transparent', BG_COLOR3, BG_COLOR2, BG_COLOR3),
                                 bd_radius=5, size=None,
                                 font=YAHEI[9], bd=1, padding=3)
        self._init_ui()
        self._bind_signals()
        EditModelWidget.Instance = self

    def updateSectionHandler(self, item):
        # # 解绑原信号  # TODO
        # if self._current_item:
        #     try:
        #         self._current_item.update_path_s.disconnect(self.updatePath)
        #     except TypeError:
        #         Log().error(traceback.format_exc(), self.TAG, "解绑信号失败")
        #     except Exception as _e:
        #         Log().error(traceback.format_exc(), self.TAG, f"解绑信号失败：{_e}")
        #         raise _e
        # 链接路径修改信号
        if hasattr(item, 'update_path_s'):
            item.update_path_s.connect(self.updatePath)
        super().updateSectionHandler(item)
        self.pathButton.setText(item.file_path)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])

    def updatePath(self, path):
        self.pathButton.setText(path)

    def _init_basic_info_ui(self):
        super()._init_basic_info_ui()
        _font = YAHEI[9]
        self.basic_info_layout.addWidget(ColoredTextLabel(
            None, "模型路径", _font, bg='transparent'), 2, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.pathButton, 2, 1, 1, 3)
        self.pathButton.setFixedHeight(24)
        self.pathButton.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.pathButton.setIcon(QIcon(QPixmap(FOLDER_IMAGE)))
        self.pathButton.clicked.connect(self.selectModelPath)

    def _bind_signals(self):
        super()._bind_signals()

    def selectModelPath(self):
        """
        选择模型路径
        :return:
        """
        # 打开文件选择对话框，路径就是当前button的text
        path = QFileDialog.getOpenFileName(self, "选择模型文件", "", "模型文件 (*.obj *.fbx *.3ds *.stl *.ply *.off)")[0]
        # 过滤掉空路径
        if not path or path == '.':
            return
        op = ChangeModelPathOperation(self._current_item, path, self.pathButton.text())
        self.operationStack.execute(op)


class EditRefImageWidget(EditTabWidget):
    TAG = "EditRefImageWidget"
    Instance: Optional['EditRefImageWidget'] = None

    scl_changed_s = pyqtSignal(list)  # noqa

    def __init__(self):
        super().__init__()

        self.pathButton = Button(None, "单击：重新选择图片路径", bg=('transparent', BG_COLOR3, BG_COLOR2, BG_COLOR3),
                                 bd_radius=5, size=None,
                                 font=YAHEI[9], bd=1, padding=3)
        self._init_ui()
        self._bind_signals()
        EditModelWidget.Instance = self

    def updateSectionHandler(self, item):
        # # 解绑原信号  # TODO
        # if self._current_item:
        #     try:
        #         self._current_item.update_path_s.disconnect(self.updatePath)
        #     except TypeError:
        #         Log().error(traceback.format_exc(), self.TAG, "解绑信号失败")
        #     except Exception as _e:
        #         Log().error(traceback.format_exc(), self.TAG, f"解绑信号失败：{_e}")
        #         raise _e
        # 链接路径修改信号
        if hasattr(item, 'update_path_s'):
            item.update_path_s.connect(self.updatePath)
        super().updateSectionHandler(item)
        self.pathButton.setText(item.file_path)
        self.rotX_edit.setValue(item.Rot[0])
        self.rotY_edit.setValue(item.Rot[1])
        self.rotZ_edit.setValue(item.Rot[2])
        self.sclX_edit.setValue(item.Scl[0])
        self.sclY_edit.setValue(item.Scl[1])
        self.sclZ_edit.setValue(item.Scl[2])

    def updatePath(self, path):
        self.pathButton.setText(path)

    def _init_basic_info_ui(self):
        super()._init_basic_info_ui()
        _font = YAHEI[9]
        self.basic_info_layout.addWidget(ColoredTextLabel(
            None, "缩放大小", _font, bg='transparent'), 2, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.sclX_edit, 2, 1)
        self.basic_info_layout.addWidget(self.sclY_edit, 2, 2)
        self.basic_info_layout.addWidget(self.sclZ_edit, 2, 3)
        self.basic_info_layout.addWidget(ColoredTextLabel(
            None, "图片路径", _font, bg='transparent'), 3, 0, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.basic_info_layout.addWidget(self.pathButton, 3, 1, 1, 3)
        self.pathButton.setFixedHeight(24)
        self.pathButton.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.pathButton.setIcon(QIcon(QPixmap(FOLDER_IMAGE)))
        self.pathButton.clicked.connect(self.selectRefImagePath)

    def _bind_signals(self):
        super()._bind_signals()

    def selectRefImagePath(self):
        """
        选择图片路径
        :return:
        """
        # 打开文件选择对话框，路径就是当前button的text
        path = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.jpg *.png *.bmp *.jpeg)")[0]
        # 过滤掉空路径
        if not path or path == '.':
            return
        op = ChangeRefImagePathOperation(self._current_item, path, self.pathButton.text())
        self.operationStack.execute(op)
