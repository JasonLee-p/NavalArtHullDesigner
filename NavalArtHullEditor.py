# -*- coding: utf-8 -*-
"""
NavalArt Hull Editor
NavalArt 船体编辑器
Author: @JasonLee
Date: 2024-2-26
"""

# 系统库
import sys
import traceback
import webbrowser

from config_read import ConfigHandler
from main_editor import MainEditor
from startWindow import StartWindow

# 第三方库和自定义库
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    from GUI import *
except Exception as e:
    traceback.print_exc()
    print(f"[ERROR] {e}")
    input(f"[INFO] Press any key to exit...")
    sys.exit(1)

VERSION = "1.0.0.0"
TESTING = False


class MainEditorHandler(list):
    def __init__(self, gl_widget_, configHandler_):
        super().__init__()
        self.gl_widget = gl_widget_
        self.configHandler = configHandler_

    def new(self):
        global startWindow
        if len(self) < 5:
            # 新建主编辑窗口
            self.append(MainEditor(self.gl_widget, self.configHandler))
            # 绑定mainWindow的close信号到该类的close函数
            self[-1].closed.connect(lambda: self.close(self[-1]))
            # 删除开始界面
            startWindow.close()
            return self[-1]
        else:
            QMessageBox.warning(None, "警告", "编辑窗口数量已达上限（5）", QMessageBox.Ok)
            return None

    def close(self, mainEditor: MainEditor):
        global startWindow
        # 将窗口从数组删除
        self.remove(mainEditor)
        # 保存配置
        self.configHandler.save_config()
        # # 如果没有窗口了，关闭程序
        # 没有窗口了，打开开始界面
        if len(self) == 0:
            # sys.exit(QApp.exec_())
            startWindow = StartWindow(None)
            linkSignal(startWindow)
            startWindow.show()


def lastEdit():
    color_print("[INFO] 最近编辑", "green")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def newPrj():
    color_print("[INFO] 新建项目", "green")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def openPrj():
    color_print("[INFO] 打开项目", "green")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def setting():
    color_print("[INFO] 设置", "green")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def _help():
    color_print("[INFO] 帮助", "green")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def about():
    webbrowser.open("http://naval_plugins.e.cn.vc/")


def linkSignal(startwindow: StartWindow):
    # 链接开始界面信号
    startwindow.lastEdit_signal.connect(lastEdit)
    startwindow.newPrj_signal.connect(newPrj)
    startwindow.openPrj_signal.connect(openPrj)
    startwindow.setting_signal.connect(setting)
    startwindow.help_signal.connect(_help)
    startwindow.about_signal.connect(about)


if __name__ == '__main__':
    # 设置 OpenGL 版本
    # fmt = QSurfaceFormat()
    # fmt.setVersion(2, 0)
    # fmt.setProfile(QSurfaceFormat.CoreProfile)
    # QSurfaceFormat.setDefaultFormat(fmt)
    # 设置QApp
    QApp = QApplication(sys.argv)
    QApp.setWindowIcon(QIcon(QPixmap(ICO_IMAGE)))
    QApp.setApplicationName("NavalArt HullEditor")
    QApp.setApplicationVersion(VERSION)
    QApp.setOrganizationName("JasonLee")
    # 打开欢迎界面
    startWindow = StartWindow()
    startWindow.show()
    # 初始化编辑界面集合
    gl_widget = GLWidgetGUI(configHandler)  # configHandler已经在GUI中初始化
    mainEditors: MainEditorHandler = MainEditorHandler(gl_widget, configHandler)
    # 链接信号
    linkSignal(startWindow)
    # 结束程序
    sys.exit(QApp.exec_())
