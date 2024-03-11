# -*- coding: utf-8 -*-
"""
编辑器运行逻辑
"""
from GUI import MainEditorGUI
from funcs_utils import not_implemented


class MainEditor(MainEditorGUI):

    @not_implemented
    def new_prj(self):
        pass

    @not_implemented
    def open_prj(self):
        pass

    @not_implemented
    def save_prj(self):
        pass

    @not_implemented
    def save_as_prj(self):
        pass

    @not_implemented
    def export_to_na(self):
        pass

    @not_implemented
    def set_theme(self):
        pass

    @not_implemented
    def set_camera(self):
        pass

    @not_implemented
    def about(self):
        pass

    @not_implemented
    def tutorial(self):
        pass

    def __init__(self, gl_widget, configHandler):
        super().__init__(gl_widget, configHandler)
