"""
左侧结构层级窗口中，各个组件类的控件容器，包含了添加按钮、滚动区域、元素列表等

*添加图纸组件*请在此继承基类并实现create_item方法
"""
from .hierarchy_single_component import *
from .general_widgets import *


class HierarchyContainer(QObject):
    """
    元素结构窗口中元素容器的基类
    """
    main_editor = None  # 对主编辑器的引用

    def __init__(self, main_editor, tab_widget, title=''):
        """
        :param main_editor: 主编辑器
        :param tab_widget: 用于显示的tab_widget
        :param title: 窗口标题
        """
        super().__init__(None)
        self._items = []
        self.title = title
        HierarchyContainer.main_editor = main_editor
        self.widget = tab_widget
        self.scroll_widget = QWidget()
        self.none_show = NoneShow(80)
        self.scroll_area = ScrollArea(None, self.scroll_widget, Qt.Vertical)
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
        self.widget.layout().setAlignment(Qt.AlignTop)
        self.widget.layout().addWidget(TextLabel(None, self.title, align=Qt.AlignLeft | Qt.AlignTop))
        self.widget.layout().addWidget(self.scroll_area)
        self.widget.layout().addWidget(self.add_button)
        self.scroll_widget.setLayout(QVBoxLayout())
        self.scroll_widget.layout().setAlignment(Qt.AlignTop)
        self.scroll_widget.layout().addWidget(self.none_show)
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
        在加入元素后更新界面，并且如果当前没有元素则隐藏none_show
        :param item: 元素（不是控件，而是实际的元素）
        :return: 是否添加成功
        """
        if not self._items:
            self.none_show.hide()
        self._items.append(item)

    def del_item(self, item, temp=True):
        """
        删除元素后更新界面，并且如果当前没有元素则显示none_show
        :param item: 元素（不是控件，而是实际的元素）
        :return: 是否删除成功
        """
        self._items.remove(item)
        if hasattr(item, "_showButton"):
            if temp:
                item._showButton.hide()
            else:
                item._showButton.deleteLater()
        if not self._items:
            self.none_show.show()

    def clear(self):
        """
        清空所有元素
        在更换项目时调用
        :return:
        """
        for item in self._items:
            self.del_item(item)
        self._items.clear()
        # 刷新界面
        self.none_show.show()


class HullSectionGroupHC(HierarchyContainer):
    """
    船体截面组的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget, "船体截面组：")


class ArmorSectionGroupHC(HierarchyContainer):
    """
    装甲截面组的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget, "装甲截面组：")


class BridgeHC(HierarchyContainer):
    """
    舰桥的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget, "舰桥：")


class LadderHC(HierarchyContainer):
    """
    梯子的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget, "梯子：")


class ModelHC(HierarchyContainer):
    """
    外部模型的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget, "外部模型：")
        tab_widget.setMinimumWidth(250)

    def create_item(self):
        if not super().create_item():
            return False
        self.main_editor.getCurrentPrj().new_model()  # 经过一圈信号传递，最终也调用了self.add_item


class RefImageHC(HierarchyContainer):
    """
    参考图片的层次结构视图容器
    """

    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget, "参考图片：")
        tab_widget.setMinimumWidth(250)

    def create_item(self):
        if not super().create_item():
            return False
        self.main_editor.getCurrentPrj().new_refImage()  # 经过一圈信号传递，最终也调用了self.add_item
