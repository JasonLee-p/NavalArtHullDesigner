import os
from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QSizePolicy, QMessageBox, QApplication, QWidget

from .basic_data import *
from .basic_widgets import BasicDialog, ButtonGroup, ImageTextButton, ScrollArea, TextButton, NumberEdit
from na_design_tools import get_avg_position, offset_position
from path_lib import NA_SHIP_PATH
from string_src import *


class NaDesignSelectDialog(BasicDialog):
    Instance: Optional['NaDesignSelectDialog'] = None
    select_design_s = pyqtSignal(str)  # noqa

    def __init__(self, parent=None):
        self.selected_design = None
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
        self.scroll_area.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.scroll_area.setFixedHeight(self.height() - 95)
        self._center_layout.addWidget(self.scroll_area, stretch=1)

    @classmethod
    def select_design(cls, func: Optional[Callable[[str], None]] = None):
        """
        选择图纸
        :param func: 回调函数，当选择图纸后调用，参数为图纸名称。
        """
        # 选择图纸
        if NaDesignSelectDialog.Instance is None:
            NaDesignSelectDialog(None)
        else:
            NaDesignSelectDialog.Instance.update_design_map()
        NaDesignSelectDialog.Instance.show()
        # 绑定回调函数
        if func is not None:
            NaDesignSelectDialog.Instance.select_design_s.connect(func)

    def ensure(self):
        selected_design_bt = self.button_group.current
        if selected_design_bt is None:
            QMessageBox.warning(self, "警告", "您尚未选择图纸！", QMessageBox.Ok)
            return
        self.selected_design = selected_design_bt.get_text()
        self.select_design_s.emit(self.selected_design)
        self.close()


class MoveDialog(BasicDialog):
    Instance = None
    # _update_selected_design_label_s = pyqtSignal(str)  # noqa
    # _update_avg_x_label_s = pyqtSignal(str)  # noqa
    # _update_avg_y_label_s = pyqtSignal(str)  # noqa
    # _update_avg_z_label_s = pyqtSignal(str)  # noqa
    # _update_x_label_s = pyqtSignal(str)  # noqa
    # _update_y_label_s = pyqtSignal(str)  # noqa
    # _update_z_label_s = pyqtSignal(str)  # noqa

    def __init__(self, parent=None):
        self.design_xml_str: Optional[str] = None
        self.selected_design_label = TextButton(None, "尚未选择", "点击下面的按钮，选择要移动的图纸",
                                                bg=BG_COLOR0, fg=FG_COLOR0,
                                                font=YAHEI[10], size=(320, 28), bd_radius=8)
        self.select_design_button = TextButton(None, "点击选择图纸", "选择要移动的图纸",
                                               bg=(BG_COLOR0, BG_COLOR3, BG_COLOR2, BG_COLOR3), fg=FG_COLOR1,
                                               font=YAHEI[10], size=(320, 28), bd_radius=8)
        self.input_widget = QFrame(None)
        self.x_input = NumberEdit(None, None, (68, 28), float,
                                  rounding=4, default_value=0.0, step=0.1)
        self.y_input = NumberEdit(None, None, (68, 28), float,
                                  rounding=4, default_value=0.0, step=0.1)
        self.z_input = NumberEdit(None, None, (68, 28), float,
                                  rounding=4, default_value=0.0, step=0.1)
        self.avg_x = TextButton(None, "0.0", "图纸的平均位置X坐标",
                                bg=BG_COLOR0, fg=FG_COLOR0,
                                font=YAHEI[10], size=(68, 28), bd_radius=8)
        self.avg_y = TextButton(None, "0.0", "图纸的平均位置Y坐标",
                                bg=BG_COLOR0, fg=FG_COLOR0,
                                font=YAHEI[10], size=(68, 28), bd_radius=8)
        self.avg_z = TextButton(None, "0.0", "图纸的平均位置Z坐标",
                                bg=BG_COLOR0, fg=FG_COLOR0,
                                font=YAHEI[10], size=(68, 28), bd_radius=8)
        super().__init__(parent, title="整体移动na图纸", ensure_bt_fill=True, size=QSize(400, 300))
        self.bind_signals()
        MoveDialog.Instance = self

    def init_center_layout(self):
        self._center_layout.setContentsMargins(10, 25, 10, 20)
        self._center_layout.setSpacing(5)
        self.add_widget(self.selected_design_label)
        self.add_widget(self.select_design_button)
        self.add_widget(self.input_widget)
        _layout = QGridLayout()
        _layout.addWidget(TextButton(None, "平均位置", "图纸当前的所有零件平均位置",
                                     bg=BG_COLOR0, fg=FG_COLOR0,
                                     font=YAHEI[10], size=(95, 28), bd_radius=8), 0, 0)
        _layout.addWidget(self.avg_x, 0, 1)
        _layout.addWidget(self.avg_y, 0, 2)
        _layout.addWidget(self.avg_z, 0, 3)
        _layout.addWidget(TextButton(None, "偏移量", "在此输入图纸移动量",
                                     bg=BG_COLOR0, fg=FG_COLOR0,
                                     font=YAHEI[10], size=(95, 28), bd_radius=8), 1, 0)
        _layout.addWidget(self.x_input, 1, 1)
        _layout.addWidget(self.y_input, 1, 2)
        _layout.addWidget(self.z_input, 1, 3)

        self.input_widget.setLayout(_layout)

    def bind_signals(self):
        # self._update_selected_design_label_s.connect(self.selected_design_label.setText)
        # self._update_avg_x_label_s.connect(self.avg_x.setText)
        # self._update_avg_y_label_s.connect(self.avg_y.setText)
        # self._update_avg_z_label_s.connect(self.avg_z.setText)
        # self._update_x_label_s.connect(self.x_input.setText)
        # self._update_y_label_s.connect(self.y_input.setText)
        # self._update_z_label_s.connect(self.z_input.setText)
        self.select_design_button.clicked.connect(lambda: NaDesignSelectDialog.select_design(self.design_selected))

    def design_selected(self, design_name: str):
        """
        选择图纸后的回调函数
        """
        # 获得路径
        design_path = os.path.join(NA_SHIP_PATH, f"{design_name}.na")
        # 读取XML文件（utf-8）
        try:
            with open(design_path, "r", encoding="utf-8") as f:
                self.design_xml_str = f.read()
        except Exception as _e:
            QMessageBox.warning(self, "警告", f"读取文件时出错：{_e}", QMessageBox.Ok)
            return
        # 计算平均位置
        avg_x, avg_y, avg_z = get_avg_position(self.design_xml_str)
        self.avg_x.setText(str(avg_x))
        self.avg_y.setText(str(avg_y))
        self.avg_z.setText(str(avg_z))
        # self._update_avg_x_label_s.emit(str(avg_x))
        # self._update_avg_y_label_s.emit(str(avg_y))
        # self._update_avg_z_label_s.emit(str(avg_z))
        # 更新选择的图纸名称
        self.selected_design_label.setText(str(design_name))
        self._center_layout.update()
        # 通知所有的子控件刷新
        QMetaObject.invokeMethod(self, "repaint", Qt.QueuedConnection)
        for widget in self.input_widget.findChildren(QWidget):
            QMetaObject.invokeMethod(widget, "repaint", Qt.QueuedConnection)
            # if isinstance(widget, QWidget):
            #     widget.enterEvent(QEvent(QEvent.Enter))
        QApplication.processEvents()

    def ensure(self):
        # 检查是否选择了图纸
        if self.design_xml_str is None:
            QMessageBox.warning(self, "警告", "您尚未选择图纸！", QMessageBox.Ok)
            return
        # 获取偏移后的XML字符串
        offset_design = offset_position(self.design_xml_str, self.x_input.current_value,
                                        self.y_input.current_value, self.z_input.current_value)
        # 写入新的XML文件
        design_name = self.selected_design_label.text
        if design_name == "尚未选择":
            QMessageBox.warning(self, "警告", "您尚未选择图纸！", QMessageBox.Ok)
            return
        try:
            with open(os.path.join(NA_SHIP_PATH, f"{design_name}.na"), "w", encoding="utf-8") as inf:
                inf.write(offset_design)
        except Exception as _e:
            QMessageBox.warning(self, "警告", f"写入文件时出错：{_e}", QMessageBox.Ok)
            return
        # 更新平均位置
        self.avg_x.setText(str(round(float(self.avg_x.text) + self.x_input.current_value, 4)))
        self.avg_y.setText(str(round(float(self.avg_y.text) + self.y_input.current_value, 4)))
        self.avg_z.setText(str(round(float(self.avg_z.text) + self.z_input.current_value, 4)))
        # self._update_avg_x_label_s.emit(str(round(float(self.avg_x.text) + self.x_input.current_value, 4)))
        # self._update_avg_y_label_s.emit(str(round(float(self.avg_y.text) + self.y_input.current_value, 4)))
        # self._update_avg_z_label_s.emit(str(round(float(self.avg_z.text) + self.z_input.current_value, 4)))
        # 通知主线程刷新控件
        # 通知所有的子控件刷新
        QMetaObject.invokeMethod(self, "repaint", Qt.QueuedConnection)
        for widget in self.input_widget.findChildren(QWidget):
            QMetaObject.invokeMethod(widget, "repaint", Qt.QueuedConnection)
        QApplication.processEvents()
        QMessageBox.information(self, "提示", "图纸移动成功！", QMessageBox.Ok)

    @classmethod
    def open_dialog(cls):
        if cls.Instance is None:
            cls(None)
        cls.Instance.show()

    def closeEvent(self, event):
        self.design_xml_str = None
        self.selected_design_label.setText("尚未选择")
        self.avg_x.setText("0.0")
        self.avg_y.setText("0.0")
        self.avg_z.setText("0.0")
        self.x_input.clear()
        self.y_input.clear()
        self.z_input.clear()
        # self._update_selected_design_label_s.emit("尚未选择")
        # self._update_avg_x_label_s.emit("0.0")
        # self._update_avg_y_label_s.emit("0.0")
        # self._update_avg_z_label_s.emit("0.0")
        # self._update_x_label_s.emit("0.0")
        # self._update_y_label_s.emit("0.0")
        # self._update_z_label_s.emit("0.0")
        super().closeEvent(event)


class ScaleDialog(BasicDialog):
    """
    缩放图纸对话框
    """
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
        self.select_design_button.clicked.connect(lambda: NaDesignSelectDialog.select_design(self.design_selected))

    def design_selected(self, design_name: str):
        print(f"Selected Design: {design_name}")

    def ensure(self):
        self.close()

    @classmethod
    def open_dialog(cls):
        if cls.Instance is None:
            cls(None)
        cls.Instance.show()
