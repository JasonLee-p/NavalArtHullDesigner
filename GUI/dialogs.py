import os

from GUI import ScrollArea, ButtonGroup, ImageTextButton, TextButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QSizePolicy

from .basic_widgets import BasicDialog
from GUI.basic_data import *
from path_lib import NA_SHIP_PATH
from string_src import *


class NaDesignSelectDialog(BasicDialog):
    Instance: Optional['NaDesignSelectDialog'] = None

    def __init__(self, parent=None):
        self.design_map = {
            # "图纸名称（不含后缀）": 图纸的预览图对象（QPixMap）
            # 图纸文件在NA_SHIP_PATH目录下，图片文件在NA_SHIP_PATH/Thumbnails目录下
        }
        self.widget_map = {
            # "图纸名称（不含后缀）": 图纸的预览图控件对象（ImageTextButton）
        }
        # 每行四个
        self.current_row = 0
        self.current_col = 0
        self.COLS = 4
        # 初始化滚动区
        self.scroll_widget = QFrame(None)
        self.scroll_layout = QGridLayout()
        self.scroll_area = ScrollArea(None, self.scroll_widget, Qt.Vertical)
        # 初始化按钮组
        self.button_group = ButtonGroup([], 0)
        # 初始化布局
        super().__init__(parent, title=f"选择{NA_DESIGN_STR}：", size=QSize(1000, 640))
        # 初始化内容
        self.update_design_map()
        NaDesignSelectDialog.Instance = self

    def update_design_map(self):
        """
        更新图纸字典和控件对象
        :return:
        """
        # 先删除原有的数据和控件
        for key in self.design_map.keys():
            self.design_map[key].deleteLater()
            self.widget_map[key].deleteLater()
        self.design_map.clear()
        self.widget_map.clear()
        self.button_group.clear()
        # 归零行列
        self.current_row = 0
        self.current_col = 0
        # 遍历文件夹下所有文件（不包括子文件夹）
        for file in os.listdir(NA_SHIP_PATH):
            # 寻找.na文件
            if file.endswith(".na"):
                # 寻找对应的图片文件
                design_name = file[:-3]
                thumb_file = os.path.join(NA_SHIP_PATH, "Thumbnails", f"{design_name}.png")
                # 默认的pixmap取自byte BYTES_LOST
                image_bytes = BYTES_LOST
                if os.path.exists(thumb_file):
                    image_bytes = open(thumb_file, "rb").read()
                # 添加到字典
                self.design_map[design_name] = QPixmap(QImage.fromData(QByteArray(image_bytes)))
                # 初始化控件，然后添加到控件字典
                img_size = (190, 135)  # 1024:768
                _button = ImageTextButton(None, design_name, design_name, image_bytes,
                                          ImageTextButton.ImgTop, img_size, 10,
                                          bd_radius=15, spacing=5, padding=8,
                                          bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3), fg=FG_COLOR0, font=YAHEI[9],
                                          size=(220, 165))
                self.widget_map[design_name] = _button
                self.scroll_layout.addWidget(_button, self.current_row, self.current_col, alignment=Qt.AlignCenter)
                self.button_group.add(_button, False)
                # 更新行列
                self.current_col += 1
                if self.current_col >= self.COLS:
                    self.current_col = 0
                    self.current_row += 1

    def init_center_layout(self):
        self.scroll_layout.setContentsMargins(20, 4, 15, 4)
        # self.scroll_widget.setContentsMargins(0, 0, 0, 0)
        # self.scroll_widget.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_widget.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum))
        self.scroll_area.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.scroll_area.setFixedSize(self.width() - 40, self.height() - 95)
        self._center_layout.addWidget(self.scroll_area, stretch=1)

    @classmethod
    def select_design(cls):
        design = None
        # 选择图纸
        if NaDesignSelectDialog.Instance is None:
            dialog = NaDesignSelectDialog(None)
        else:
            dialog = NaDesignSelectDialog.Instance
        dialog.show()

    def ensure(self):
        self.close()


class MoveDialog(BasicDialog):
    Instance = None

    def __init__(self, parent=None):
        self.select_design_button = TextButton(None, "选择图纸", "选择要移动的图纸",
                                               bg=(BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3), fg=FG_COLOR0,
                                               font=YAHEI[9])
        super().__init__(parent, title="整体移动na图纸", hide_bottom=True)
        self.bind_signals()
        MoveDialog.Instance = self

    def init_center_layout(self):
        self.add_widget(self.select_design_button)

    def bind_signals(self):
        self.select_design_button.clicked.connect(NaDesignSelectDialog.select_design)

    def ensure(self):
        self.close()


class ScaleDialog(BasicDialog):
    Instance = None

    def __init__(self, parent=None):
        self.select_design_button = TextButton(None, "选择图纸", "选择要缩放的图纸",
                                               bg=(BG_COLOR1, BG_COLOR3, BG_COLOR2, BG_COLOR3), fg=FG_COLOR0,
                                               font=YAHEI[9])
        super().__init__(parent, title="整体缩放na图纸", hide_bottom=True)
        self.bind_signals()
        ScaleDialog.Instance = self

    def init_center_layout(self):
        self.add_widget(self.select_design_button)

    def bind_signals(self):
        self.select_design_button.clicked.connect(NaDesignSelectDialog.select_design)

    def ensure(self):
        self.close()
