"""
定义了单个元素的显示控件
"""
import numpy as np

from .basic_widgets import *


class NoneShow(Button):
    def __init__(self, height):
        super().__init__(None, "当前无内容", bd_radius=8, size=None, font=YAHEI[9],
                         bg=(BG_COLOR1, BG_COLOR1, BG_COLOR2, BG_COLOR2), fg=GRAY)
        self.setText("无对象")
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setFixedHeight(height)


class ShowButton(Button):

    def __init__(self, gl_widget, scroll_widget, item_handler, height=70):
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
        self.layout_.setContentsMargins(10, 8, 10, 6)
        self.layout_.setVerticalSpacing(4)
        self.setLayout(self.layout_)
        self.vis_btn = CircleSelectButton(None, [], tool_tip="设置是否显示",
                                          check_color=FG_COLOR1, hover_color=BG_COLOR3, color=BG_COLOR0, radius=8)
        self._font = YAHEI[9]
        self.name_edit = TextEdit(self.item_handler.name, parent=None, font=YAHEI[10], bg=BG_COLOR1)
        self.name_edit.setFixedHeight(27)
        if hasattr(self.item_handler, "init_visibility"):
            self.vis_btn.setChecked(self.item_handler.init_visibility)
        else:
            self.vis_btn.setChecked(True)

    def _bind_signal(self):
        self.textChanged = self.name_edit.textChanged
        self.name_edit.textChanged.connect(self.nameTextChanged, Qt.DirectConnection)
        self.vis_btn.clicked.connect(self.visableClicked, Qt.DirectConnection)
        self.item_handler.deleted_s.connect(self.deleteLater, Qt.DirectConnection)

    def nameTextChanged(self, text):
        if len(text) > 20:
            text = text[:20]
            self.name_edit.setText(text)
        self.item_handler.name = text

    def visableClicked(self, checked):
        self.item_handler.setVisable(checked)

    def mousePressEvent(self, event):
        self.gl_widget.set_item_selected(self.item_handler.paintItem, not self.isChecked())


class PosShow(ShowButton):
    def __init__(self, gl_widget, scroll_widget, item_handler, height=70):
        """
        只需要预览位置，并且有名字的元素
        :param gl_widget:
        :param scroll_widget:
        :param item_handler:
        """
        super().__init__(gl_widget, scroll_widget, item_handler, height=height)
        self.pos_text = ColoredTextLabel(None, "位置：", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.posX_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.posY_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.posZ_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self._setup_ui()
        self._bind_signal()

    def _setup_ui(self):
        # 设置自控件样式
        _h = 24
        self.pos_text.setFixedHeight(_h)
        self.posX_show.setFixedHeight(_h)
        self.posY_show.setFixedHeight(_h)
        self.posZ_show.setFixedHeight(_h)
        self.posX_show.setMinimumWidth(40)
        self.posY_show.setMinimumWidth(40)
        self.posZ_show.setMinimumWidth(40)
        # 布局
        self.layout_.addWidget(self.vis_btn, 0, 0)
        self.layout_.addWidget(self.name_edit, 0, 1, 1, 3)
        self.layout_.addWidget(self.pos_text, 1, 0)
        self.layout_.addWidget(self.posX_show, 1, 1)
        self.layout_.addWidget(self.posY_show, 1, 2)
        self.layout_.addWidget(self.posZ_show, 1, 3)

    # noinspection PyTypeChecker
    def setPos(self, pos):
        if isinstance(pos, np.ndarray):
            self.posX_show.setText(str(round(pos[0], 4)))
            self.posY_show.setText(str(round(pos[1], 4)))
            self.posZ_show.setText(str(round(pos[2], 4)))
        elif isinstance(pos, QVector3D):
            self.posX_show.setText(str(round(pos.x(), 4)))
            self.posY_show.setText(str(round(pos.y(), 4)))
            self.posZ_show.setText(str(round(pos.z(), 4)))

    def setPosX(self, x):
        self.posX_show.setText(str(x))

    def setPosY(self, y):
        self.posY_show.setText(str(y))

    def setPosZ(self, z):
        self.posZ_show.setText(str(z))


class PosRotShow(ShowButton):
    def __init__(self, gl_widget, scroll_widget, item_handler, height=96):
        """
        预览位置和旋转角度的元素
        :param gl_widget:
        :param scroll_widget:
        :param item_handler:
        """
        super().__init__(gl_widget, scroll_widget, item_handler, height=height)
        self.pos_text = ColoredTextLabel(None, "位置：", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.rot_text = ColoredTextLabel(None, "旋转：", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.posX_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.posY_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.posZ_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.rotX_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.rotY_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self.rotZ_show = ColoredTextLabel(None, "0", self._font, bg=BG_COLOR0, bd=0, padding=3)
        self._setup_ui()
        self._bind_signal()

    def _setup_ui(self):
        # 设置自控件样式
        _h = 24
        self.pos_text.setFixedHeight(_h)
        self.rot_text.setFixedHeight(_h)
        self.posX_show.setFixedHeight(_h)
        self.posY_show.setFixedHeight(_h)
        self.posZ_show.setFixedHeight(_h)
        self.posX_show.setMinimumWidth(40)
        self.posY_show.setMinimumWidth(40)
        self.posZ_show.setMinimumWidth(40)
        self.rotX_show.setFixedHeight(_h)
        self.rotY_show.setFixedHeight(_h)
        self.rotZ_show.setFixedHeight(_h)
        self.rotX_show.setMinimumWidth(40)
        self.rotY_show.setMinimumWidth(40)
        self.rotZ_show.setMinimumWidth(40)
        # 布局
        self.layout_.addWidget(self.vis_btn, 0, 0)
        self.layout_.addWidget(self.name_edit, 0, 1, 1, 3)
        self.layout_.addWidget(self.pos_text, 1, 0)
        self.layout_.addWidget(self.posX_show, 1, 1)
        self.layout_.addWidget(self.posY_show, 1, 2)
        self.layout_.addWidget(self.posZ_show, 1, 3)
        self.layout_.addWidget(self.rot_text, 2, 0)
        self.layout_.addWidget(self.rotX_show, 2, 1)
        self.layout_.addWidget(self.rotY_show, 2, 2)
        self.layout_.addWidget(self.rotZ_show, 2, 3)

    def setPos(self, pos):
        if isinstance(pos, np.ndarray):
            self.posX_show.setText(str(round(pos[0], 4)))
            self.posY_show.setText(str(round(pos[1], 4)))
            self.posZ_show.setText(str(round(pos[2], 4)))
        elif isinstance(pos, QVector3D):
            self.posX_show.setText(str(round(pos.x(), 4)))
            self.posY_show.setText(str(round(pos.y(), 4)))
            self.posZ_show.setText(str(round(pos.z(), 4)))

    def setPosX(self, x):
        self.posX_show.setText(str(x))

    def setPosY(self, y):
        self.posY_show.setText(str(y))

    def setPosZ(self, z):
        self.posZ_show.setText(str(z))

    # noinspection PyTypeChecker
    def setRot(self, rot):
        if isinstance(rot, np.ndarray):
            self.rotX_show.setText(str(round(rot[0], 2)))
            self.rotY_show.setText(str(round(rot[1], 2)))
            self.rotZ_show.setText(str(round(rot[2], 2)))
        elif isinstance(rot, QVector3D):
            self.rotX_show.setText(str(round(rot.x(), 2)))
            self.rotY_show.setText(str(round(rot.y(), 2)))
            self.rotZ_show.setText(str(round(rot.z(), 2)))

    def setRotX(self, x):
        self.rotX_show.setText(str(x))

    def setRotY(self, y):
        self.rotY_show.setText(str(y))

    def setRotZ(self, z):
        self.rotZ_show.setText(str(z))
