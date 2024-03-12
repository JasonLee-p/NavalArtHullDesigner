# -*- coding: utf-8 -*-
"""
编辑器运行逻辑
"""
import webbrowser
from typing import Union

from GUI import MainEditorGUI
from ShipRead.na_project import ShipProject
from funcs_utils import not_implemented


class MainEditor(MainEditorGUI):

    @not_implemented
    def new_prj(self):
        # 弹出临时窗口，让用于选择创建新工程的方式
        # 若确定了创建新工程，则询问是否保存当前工程
        pass

    @not_implemented
    def open_prj(self):
        # 打开文件选择窗口，选择工程文件
        # 若用户确认选择了打开文件，则询问是否保存当前工程
        pass

    def save_prj(self):
        self.currentPrj.save() if self.currentPrj else None

    @not_implemented
    def save_as_prj(self):
        # 打开文件夹选择窗口，选择保存位置
        pass

    @not_implemented
    def export_to_na(self):
        # 将当前工程导出为 NavalArt 工程文件
        # 先打开文件夹选择窗口，选择保存位置，默认为NavalArt工程文件的保存位置
        pass

    @not_implemented
    def set_theme(self):
        pass

    @not_implemented
    def set_camera(self):
        pass

    def about(self):
        webbrowser.open("http://naval_plugins.e.cn.vc/")

    @not_implemented
    def tutorial(self):
        pass

    def __init__(self, gl_widget, configHandler, logger):
        super().__init__(gl_widget, configHandler, logger)
        self.currentPrj: Union[None, ShipProject] = None
