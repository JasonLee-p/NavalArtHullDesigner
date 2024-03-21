"""
定义了单个元素的显示控件
"""
from .basic_widgets import *


class HullSectionGroupShow(Button):
    def __int__(self, scroll_widget, hsg):
        self.parent_scroll_widget = scroll_widget
        self.hsg = hsg
        super().__init__(None, "点击以编辑", bd_radius=8, size=None)
        self.layout_ = QGridLayout()
        self.__setup_ui()

    def __setup_ui(self):
        self.setLayout(self.layout_)


class ArmorSectionGroupShow(Button):
    def __int__(self, scroll_widget, asg):
        self.parent_scroll_widget = scroll_widget
        self.asg = asg
        super().__init__(None, "点击以编辑", bd_radius=8, size=None)
        self.layout_ = QGridLayout()
        self.__setup_ui()

    def __setup_ui(self):
        self.setLayout(self.layout_)


class BridgeShow(Button):
    def __int__(self, scroll_widget, bridge):
        self.parent_scroll_widget = scroll_widget
        self.bridge = bridge
        super().__init__(None, "点击以编辑", bd_radius=8, size=None)
        self.layout_ = QGridLayout()
        self.__setup_ui()

    def __setup_ui(self):
        self.setLayout(self.layout_)


class LadderShow(Button):
    def __int__(self, scroll_widget, ladder):
        super().__init__(None, "点击以编辑", bd_radius=8, size=None)
        self.parent_scroll_widget = scroll_widget
        self.ladder = ladder
        self.layout_ = QGridLayout()
        self.__setup_ui()

    def __setup_ui(self):
        self.setLayout(self.layout_)


class OnlyPosShow(Button):
    def __init__(self, scroll_widget, item_handler):
        """
        只需要预览位置，并且有名字的元素
        :param scroll_widget:
        :param item_handler:
        """
        self.parent_scroll_widget = scroll_widget
        self.item_handler = item_handler
        super().__init__(None, "点击以编辑", bd_radius=8, size=None,
                         bg=(BG_COLOR1, BG_COLOR2, BG_COLOR3, BG_COLOR2))
        self.layout_ = QGridLayout()
        self.vis_btn = CircleSelectButton(None, [], tool_tip="设置是否显示",
                                          check_color=FG_COLOR1, hover_color=BG_COLOR3, color=BG_COLOR0, radius=8)
        _font = QFont(YAHEI[9])
        self.name_edit = TextEdit(self.item_handler.name, parent=None, font=_font)
        self.pos_text = ColoredTextLabel(None, "位置：", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.posX_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.posY_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.posZ_show = ColoredTextLabel(None, "0", _font, bg=BG_COLOR0, bd=0, padding=3)
        self.__setup_ui()
        self.__bind_signal()

    def __setup_ui(self):
        # 设置本身样式
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setFixedHeight(80)
        # 其他样式
        self.vis_btn.setChecked(True)
        # 设置布局
        self.setLayout(self.layout_)
        self.pos_text.setFixedHeight(28)
        self.posX_show.setFixedHeight(28)
        self.posY_show.setFixedHeight(28)
        self.posZ_show.setFixedHeight(28)
        # 第一行添加显示按钮和名字编辑框，名字编辑框占1-3三列
        self.layout_.addWidget(self.vis_btn, 0, 0)
        self.layout_.addWidget(self.name_edit, 0, 1, 1, 3)
        # 第二行添加位置显示
        self.layout_.addWidget(self.pos_text, 1, 0)
        self.layout_.addWidget(self.posX_show, 1, 1)
        self.layout_.addWidget(self.posY_show, 1, 2)
        self.layout_.addWidget(self.posZ_show, 1, 3)

    def __bind_signal(self):
        self.textChanged = self.name_edit.textChanged
        self.name_edit.textChanged.connect(self.nameTextChanged)
        self.vis_btn.clicked.connect(self.visableClicked)
        self.item_handler.temp_deleted.connect(self.hide)
        self.item_handler.deleted.connect(self.deleteLater)

    def nameTextChanged(self, text):
        if len(text) > 20:
            text = text[:20]
            self.name_edit.setText(text)
        self.item_handler.name = text

    def visableClicked(self, checked):
        self.item_handler.setVisable(checked)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.item_handler.setSelected(True)

