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

from GUI import *
from startWindow import StartWindow

# 第三方库和自定义库
try:
    from GUI import *
except Exception as e:
    traceback.print_exc()
    print(f"[ERROR] {e}")
    input(f"[INFO] Press any key to exit...")
    sys.exit(1)

VERSION = "1.0.0.0"
TESTING = False


class MainWindowHandler(list):
    def __init__(self):
        super().__init__()

    def new(self):
        if len(self) < 5:
            # 新建主编辑窗口
            self.append(MainWindow())
            # 绑定mainWindow的close信号到该类的close函数
            self[-1].closed.connect(lambda: self.close(self[-1]))
            # 隐藏开始界面
            startWindow.hide()
            return self[-1]
        else:
            QMessageBox.warning(None, "警告", "编辑窗口数量已达上限（5）", QMessageBox.Ok)
            return None

    def close(self, mainWindow: MainWindow):
        # 将窗口从数组删除
        self.remove(mainWindow)
        # 如果没有窗口了，显示开始界面
        if len(self) == 0:
            startWindow.show()


def lastEdit():
    color_print("[INFO] 上次编辑", "green")
    mainWindow = mainWindows.new()
    if not mainWindow:
        return


def newPrj():
    color_print("[INFO] 新建项目", "green")
    mainWindow = mainWindows.new()
    if not mainWindow:
        return


def openPrj():
    color_print("[INFO] 打开项目", "green")
    mainWindow = mainWindows.new()
    if not mainWindow:
        return


def setting():
    color_print("[INFO] 设置", "green")
    mainWindow = mainWindows.new()
    if not mainWindow:
        return


def _help():
    color_print("[INFO] 帮助", "green")
    mainWindow = mainWindows.new()
    if not mainWindow:
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
    # 设置QApp
    QApp = QApplication(sys.argv)
    QApp.setWindowIcon(QIcon(QPixmap(ICO_IMAGE)))
    QApp.setApplicationName("NavalArt HullEditor")
    QApp.setApplicationVersion(VERSION)
    QApp.setOrganizationName("JasonLee")
    # 打开欢迎界面
    startWindow = StartWindow(None)
    startWindow.show()
    # 初始化编辑界面集合
    mainWindows: MainWindowHandler[MainWindow] = MainWindowHandler()
    # 链接信号
    linkSignal(startWindow)
    # 结束程序
    sys.exit(QApp.exec_())
