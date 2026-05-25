"""
左侧结构层级窗口中，各个组件类的控件容器，包含了添加按钮、滚动区域、元素列表等

*添加图纸组件*请在此继承基类并实现create_item方法
"""
from .hierarchy_single_component import *
from .general_widgets import *


class CollapsiblePanel(QWidget):
    """
    Vertical section panel that can be expanded independently.
    """

    def __init__(self, title: str, content_widget: QWidget, expanded: bool = False):
        super().__init__(None)
        self.title = title
        self.content_widget = content_widget
        self.header_button = Button(None, "",
                                    bg=(BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3),
                                    fg=FG_COLOR0, bd_radius=(8, 8, 8, 8),
                                    align=Qt.AlignLeft | Qt.AlignVCenter, size=None,
                                    font=YAHEI[9], padding=(8, 8, 8, 8))

        self.header_button.setCheckable(True)
        self.header_button.setCursor(Qt.PointingHandCursor)
        self.header_button.setFixedHeight(30)
        self.header_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(5)
        self.layout().addWidget(self.header_button)
        self.layout().addWidget(self.content_widget)

        self.header_button.clicked.connect(self.set_expanded)
        self._set_header_text_alignment()
        self.set_expanded(expanded)

    def _set_header_text_alignment(self):
        self.header_button.setStyleSheet(self.header_button.styleSheet() + """
            QPushButton {
                text-align: left;
            }
        """)

    def set_expanded(self, expanded: bool):
        self.header_button.setChecked(expanded)
        self.content_widget.setVisible(expanded)
        self.header_button.setText(f"{'v' if expanded else '>'}  {self.title}")


class HierarchyContainer(QObject):
    """
    元素结构窗口中元素容器的基类
    """
    main_editor = None  # 对主编辑器的引用

    def __init__(self, main_editor, tab_widget, title='', show_title=True):
        """
        :param main_editor: 主编辑器
        :param tab_widget: 用于显示的tab_widget
        :param title: 窗口标题
        """
        super().__init__(None)
        self._items = []
        self.title = title
        self.show_title = show_title
        HierarchyContainer.main_editor = main_editor
        self.widget = tab_widget
        self.scroll_widget = QWidget()
        self.none_show = NoneShow(80)
        if not self.show_title:
            self.none_show.setFixedHeight(32)
        self.scroll_area = ScrollArea(None, self.scroll_widget, Qt.Vertical) if self.show_title else None
        self.add_button = Button(None, "添加", bg=(BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3),
                                 bd_radius=(12, 12, 12, 12), align=Qt.AlignLeft | Qt.AlignTop, size=None)
        self._init_ui()
        self._bind_signals()

    def _init_ui(self):
        self.add_button.setFixedHeight(26)
        self.add_button.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setIcon(QIcon(QPixmap(ADD_IMAGE)))
        self.widget.setLayout(QVBoxLayout())
        self.widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.widget.layout().setAlignment(Qt.AlignTop)
        self.widget.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().setSpacing(5)
        self.widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        if self.show_title:
            self.widget.layout().addWidget(TextLabel(None, self.title, align=Qt.AlignLeft | Qt.AlignTop))
            self.widget.layout().addWidget(self.scroll_area)
        else:
            self.widget.layout().addWidget(self.scroll_widget)
        self.widget.layout().addWidget(self.add_button)
        self.scroll_widget.setLayout(QVBoxLayout())
        self.scroll_widget.layout().setAlignment(Qt.AlignTop)
        self.scroll_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.scroll_widget.layout().setSpacing(5)
        self.scroll_widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.scroll_widget.layout().addWidget(self.none_show)
        self.scroll_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        if self.scroll_area is not None:
            self.scroll_area.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

    def _bind_signals(self):
        self.add_button.clicked.connect(self.create_item)

    def create_item(self) -> bool:
        """
        新建一个元素，需要在子类中覆写：
        覆写示例：
        if not super().create_item():
            return False
        :return: 是否可以添加
        """
        if HierarchyContainer.main_editor.getCurrentPrj() is None:
            QMessageBox.warning(self.main_editor, "警告", "请先打开或新建项目")
            return False
        return True

    def add_item(self, item):
        """
        在加入元素后，将元素的showbutton加入控件，更新界面，并且如果当前没有元素则隐藏none_show
        :param item: 元素（不是控件，而是实际的元素）
        :return: 是否添加成功
        """
        if not self._items:
            self.none_show.hide()
        self._items.append(item)
        self.scroll_widget.layout().addWidget(item._showButton)
        self._refresh_layout_size()

    def del_item(self, item):
        """
        删除元素后更新界面，并且如果当前没有元素则显示none_show
        :param item: 元素（不是控件，而是实际的元素）
        :return: 是否删除成功
        """
        self._items.remove(item)
        self.scroll_widget.layout().removeWidget(item._showButton)
        if not self._items:
            self.none_show.show()
        self._refresh_layout_size()

    def clear(self):
        """
        清空所有元素
        在更换项目时调用
        :return:
        """
        for item in self._items:
            self.scroll_widget.layout().removeWidget(item._showButton)
        self._items.clear()
        # 刷新界面
        self.none_show.show()
        self._refresh_layout_size()

    def _refresh_layout_size(self):
        if self.show_title:
            return
        self.scroll_widget.adjustSize()
        self.scroll_widget.updateGeometry()
        self.widget.adjustSize()
        self.widget.updateGeometry()


class HullSectionGroupHC(HierarchyContainer):
    """
    船体截面组的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget, show_title=True):
        super().__init__(main_editor, tab_widget, "船体截面组：", show_title)


class ArmorSectionGroupHC(HierarchyContainer):
    """
    装甲截面组的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget, show_title=True):
        super().__init__(main_editor, tab_widget, "装甲截面组：", show_title)


class BridgeHC(HierarchyContainer):
    """
    舰桥的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget, show_title=True):
        super().__init__(main_editor, tab_widget, "舰桥：", show_title)


class LadderHC(HierarchyContainer):
    """
    梯子的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget, show_title=True):
        super().__init__(main_editor, tab_widget, "梯子：", show_title)


class ModelHC(HierarchyContainer):
    """
    外部模型的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget, show_title=True):
        super().__init__(main_editor, tab_widget, "外部模型：", show_title)
        tab_widget.setMinimumWidth(250)

    def create_item(self):
        if not super().create_item():
            return False
        self.main_editor.getCurrentPrj().new_model()  # 经过一圈信号传递，最终也调用了self.add_item


class RefImageHC(HierarchyContainer):
    """
    参考图片的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget, show_title=True):
        super().__init__(main_editor, tab_widget, "参考图片：", show_title)
        tab_widget.setMinimumWidth(250)

    def create_item(self):
        if not super().create_item():
            return False
        self.main_editor.getCurrentPrj().new_refImage()  # 经过一圈信号传递，最终也调用了self.add_item
