"""
左侧结构树中的元素结构窗口
"""
from .element_structure_single_item import *
from .basic_widgets import *


class ESW(QObject):
    def __init__(self, main_editor, tab_widget):
        super().__init__()
        self._items = {
            # item: item_widget
        }
        self.title = ""
        self.main_editor = main_editor
        self.widget = tab_widget
        self.scroll_widget = QWidget()
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
        self.scroll_area.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

    def _bind_signal(self):
        self.add_button.clicked.connect(self.create_item)

    def create_item(self):
        """
        新建一个元素
        :return: 是否可以添加
        """
        if self.main_editor.getCurrentPrj() is None:
            QMessageBox.warning(self.main_editor, "警告", "请先打开或新建项目")
            return False
        return True

    def add_item(self, item):
        """
        在加入元素后更新界面
        :param item: 元素
        :return: 是否添加成功
        """
        ...

    def del_item(self, item):
        """
        删除元素后更新界面
        :param item: 元素
        :return: 是否删除成功
        """
        pass


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


class RailingESW(ESW):
    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget)
        self.title = "栏杆："
        self._setup_ui()
        self._bind_signal()


class HandrailESW(ESW):
    def __init__(self, main_editor, tab_widget):
        super().__init__(main_editor, tab_widget)
        self.title = "栏板："
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
        self.title = "外部模型："
        self._setup_ui()
        self._bind_signal()

    def _setup_ui(self):
        super()._setup_ui()

    def _bind_signal(self):
        super()._bind_signal()

    def create_item(self):
        if not super().create_item():
            return False
        self.main_editor.getCurrentPrj().new_model()

    def add_item(self, item):
        show_widget = OnlyPosShow(self.scroll_widget, item)
        self.scroll_widget.layout().addWidget(show_widget)

    def add_model_item(self, path):
        self.main_editor.getCurrentPrj().add_model_byPath(path)
