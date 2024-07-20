"""
定义了子组件在父组件的编辑窗口的显示控件
"""
from main_logger import Log
from operation.section_op import SectionZMoveOperation

from .basic_widgets import *


class SubElementShow(Button):
    TAG = "SubElementShow"
    operationStack = None  # main_editor在初始化的时候会将其赋值为OperationStack对象

    def __init__(self, gl_widget, scroll_widget, item_handler, height=32):
        """
        预览元素的控件
        :param gl_widget:
        :param scroll_widget:
        :param item_handler:
        """
        self.gl_widget = gl_widget
        self.parent_scroll_widget = scroll_widget
        self.item_handler = item_handler
        super().__init__(None, "点击以编辑", bd_radius=8, size=None,
                         bg=(BG_COLOR1, BG_COLOR2, BG_COLOR3, BG_COLOR3))
        self.setCheckable(True)
        self.setChecked(False)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setFixedHeight(height)
        self.layout_ = QGridLayout()
        self.layout_.setContentsMargins(10, 4, 10, 4)
        self.layout_.setVerticalSpacing(4)
        self.setLayout(self.layout_)
        self.vis_btn = CircleSelectButton(None, [], tool_tip="设置是否显示",
                                          check_color=FG_COLOR1, hover_color=BG_COLOR3, color=BG_COLOR0, radius=8)
        self._font = YAHEI[9]
        if hasattr(self.item_handler, "name"):
            self.name_edit = TextEdit(self.item_handler.name, parent=None, font=YAHEI[9], bg=BG_COLOR1)
        else:
            self.name_edit = TextEdit("不可命名", parent=None, font=YAHEI[9], bg=BG_COLOR1)
            self.name_edit.setReadOnly(True)
            self.item_handler.name = "不可命名"
        self.name_edit.setFixedHeight(24)
        # 初始化菜单
        self.menu = Menu(self)
        self.delete_action = self.menu.addAction("删除")
        self.delete_action.triggered.connect(self.item_handler.delete_by_user)
        if hasattr(self.item_handler, "init_visibility"):
            self.vis_btn.setChecked(self.item_handler.init_visibility)
        else:
            self.vis_btn.setChecked(True)

    @abstractmethod
    def _setup_ui(self):
        pass

    def _bind_signal(self):
        self.textChanged = self.name_edit.textChanged
        self.name_edit.textChanged.connect(self.nameTextChanged, Qt.DirectConnection)
        self.vis_btn.clicked.connect(self.visableClicked, Qt.DirectConnection)
        self.item_handler.deleted_s.connect(self.deleteLater, Qt.DirectConnection)

    def _init_values(self):
        self.name_edit.setText(self.item_handler.name)

    def nameTextChanged(self, text):
        if len(text) > 20:
            text = text[:20]
            self.name_edit.setText(text)
        self.item_handler.name = text

    def visableClicked(self, checked):
        self.item_handler.setVisable(checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 设置选中状态
            self.gl_widget.set_item_selected(self.item_handler.paintItem, not self.isChecked())
            # 不需要调用父类的mousePressEvent，因为gl_widget已经处理了
            # super().mousePressEvent(event)
            Log().info(self.TAG, f"点击了{self.item_handler.name}")
        elif event.button() == Qt.RightButton:
            # 显示右键菜单
            self.show_menu(event)

    def show_menu(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))


class SubSectionShow(SubElementShow):

    def __init__(self, gl_widget, scroll_widget, item_handler):
        """
        单个截面对象的展示控件（只展示名字和z坐标）
        :param gl_widget:
        :param scroll_widget:
        :param item_handler:
        """
        super().__init__(gl_widget, scroll_widget, item_handler)
        _font = YAHEI[9]
        self.posZ_edit = NumberEdit(None, self, (68, 24), float, rounding=4, step=0.1, font=_font)
        self.editNodes_btn = Button(None, None, 0, BG_COLOR1, 6,
                                    bg=("transparent", "transparent", "transparent", "transparent"), size=24)
        self.editNodes_btn.setIcon(QIcon(QPixmap(EDIT_IMAGE)))
        self.editNodes_btn.setFocusPolicy(Qt.NoFocus)
        self.editNodes_btn.setFlat(True)
        self._setup_ui()
        self._bind_signal()
        self._init_values()
        self.hide()

    def _setup_ui(self):
        # 设置控件样式
        self.posZ_edit.setMinimumWidth(40)
        # 布局
        self.layout_.addWidget(self.name_edit, 0, 0, 1, 1)
        self.layout_.addWidget(self.posZ_edit, 0, 1, 1, 1)
        self.layout_.addWidget(self.editNodes_btn, 0, 2, 1, 1)
        self.layout_.setColumnStretch(0, 3)
        self.layout_.setColumnStretch(1, 1)

    def _bind_signal(self):
        super()._bind_signal()
        self.posZ_edit.value_changed.connect(self.setPosZOperation)
        self.editNodes_btn.mousePressEvent = self.editNodes_btn_clicked

    def _init_values(self):
        super()._init_values()
        self.posZ_edit.setValue(self.item_handler.z)

    def editNodes_btn_clicked(self, event):
        self.mousePressEvent(event)

    def setEditTextZ(self, z_):
        self.posZ_edit.setValue(z_)

    def setPosZOperation(self, z_):
        op = SectionZMoveOperation(self.item_handler, z_, [self.posZ_edit])
        self.operationStack.execute(op)
