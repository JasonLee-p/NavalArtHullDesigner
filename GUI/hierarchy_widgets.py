"""
左侧结构树中的元素结构窗口
"""
from .hierarchy_single_component import *
from .basic_widgets import *


class ESW(QObject):
    def __init__(self, main_editor, tab_widget):
        """
        Element Structure Widget
        :param main_editor:
        :param tab_widget:
        """
        super().__init__(None)
        self._items = []
        self.title = ""
        self.main_editor = main_editor
        self.widget = tab_widget
        self.scroll_widget = QWidget()
        self.none_show = NoneShow(80)
        self.scroll_area = ScrollArea(None, self.scroll_widget, Qt.Vertical)
        self.add_button = Button(None, "添加", bg=(BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3),
                                 bd_radius=(12, 12, 12, 12), align=Qt.AlignLeft | Qt.AlignTop, size=None)

    def _setup_ui(self):
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

    def _bind_signal(self):
        self.add_button.clicked.connect(self.create_item)

    def create_item(self) -> bool:
        """
        新建一个元素，需要在子类中覆写：
        覆写示例：
        if not super().create_item():
            return False
        :return: 是否可以添加
        """
        if self.main_editor.getCurrentPrj() is None:
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


class HullSectionGroupESW(ESW):
    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget)
        self.title = "船体截面组："
        self._setup_ui()
        self._bind_signal()


class ArmorSectionGroupESW(ESW):
    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget)
        self.title = "装甲截面组："
        self._setup_ui()
        self._bind_signal()


class BridgeESW(ESW):
    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget)
        self.title = "舰桥："
        self._setup_ui()
        self._bind_signal()


class LadderESW(ESW):
    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget)
        self.title = "梯子："
        self._setup_ui()
        self._bind_signal()


class ModelESW(ESW):
    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget)
        tab_widget.setMinimumWidth(250)
        self.title = "外部模型："
        self._setup_ui()
        self._bind_signal()

    def create_item(self):
        if not super().create_item():
            return False
        self.main_editor.getCurrentPrj().new_model()  # 经过一圈信号传递，最终也调用了self.add_item
