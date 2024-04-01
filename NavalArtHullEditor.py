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

# 第三方库和本地库
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    # 本地库
    from GUI import *
    from main_logger import Log
    from funcs_utils import singleton
    from main_editor import MainEditor
    from startWindow import StartWindow
except Exception as e:
    traceback.print_exc()
    print(f"[ERROR] {e}")
    input(f"[INFO] Press any key to exit...")
    sys.exit(1)

VERSION = "1.0.0.0"
TESTING = False


@singleton
class MainEditorHandler(list):
    def __init__(self, logger_):
        super().__init__()
        self.configHandler = configHandler
        self.logger = logger_
        self.statusBarHandler = StatusBarHandler()

    def new(self, mode: Literal["lastEdit", "newPrj", "openPrj", "setting", "help"] = "lastEdit"):
        global startWindow
        if len(self) < 5:
            # 新建主编辑窗口
            self.append(MainEditor(GLWidgetGUI(), self.logger))
            # 绑定mainWindow的close信号到该类的close函数
            self[-1].closed.connect(lambda: self.close(self[-1]))
            if mode == "lastEdit":
                self[-1].load_last_project()
            elif mode == "newPrj":
                self[-1].new_prj()
            elif mode == "openPrj":
                self[-1].select_prj_toOpen()
            elif mode == "setting":
                self[-1].setting()
            elif mode == "help":
                self[-1].help()
            # 删除开始界面
            startWindow.close()
            self.statusBarHandler.message.connect(lambda message, color: self[-1].show_status(message, color))
            return self[-1]
        else:
            QMessageBox().warning(None, "警告", "编辑窗口数量已达上限（5）", QMessageBox.Ok)
            return None

    def open(self, path: str):
        global startWindow
        if len(self) < 5:
            # 新建主编辑窗口
            self.append(MainEditor(GLWidgetGUI(), self.logger))
            # 绑定mainWindow的close信号到该类的close函数
            self[-1].closed.connect(lambda: self.close(self[-1]))
            self[-1].open_prj(path)
            # 删除开始界面
            startWindow.close()
            self.statusBarHandler.message.connect(lambda message, color: self[-1].show_status(message, color))
            return self[-1]
        else:
            QMessageBox().warning(None, "警告", "编辑窗口数量已达上限（5）", QMessageBox.Ok)
            return None

    def close(self, mainEditor: MainEditor):
        global startWindow
        # 将窗口从数组删除
        self.remove(mainEditor)
        del mainEditor
        print(f"unref: {gc.collect()}")  # 手动垃圾回收
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
    print("[INFO] 最近编辑")
    mainEditor = mainEditors.new("lastEdit")
    if not mainEditor:
        return


def newPrj():
    print("[INFO] 新建项目")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def openPrj():
    print("[INFO] 打开项目")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def setting():
    print("[INFO] 设置")
    mainEditor = mainEditors.new()
    if not mainEditor:
        return


def _help():
    print("[INFO] 帮助")
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
    Log()  # 初始化日志
    try:
        # 读取命令行参数
        opened_file_path = sys.argv[1] if len(sys.argv) > 1 else None
        # 设置QApp
        QApp = QApplication(sys.argv)
        QApp.setWindowIcon(QIcon(QPixmap(ICO_IMAGE)))
        QApp.setApplicationName("NavalArt HullEditor")
        QApp.setApplicationVersion(VERSION)
        QApp.setOrganizationName("JasonLee")
        QApp.setAttribute(Qt.AA_DisableHighDpiScaling)
        # 打开欢迎界面
        startWindow = StartWindow()
        mainEditors: MainEditorHandler = MainEditorHandler(Log())
        linkSignal(startWindow)
        if opened_file_path:
            startWindow.hide()
            mainEditors: MainEditorHandler = MainEditorHandler(Log())
            # 打开文件
            mainEditor = mainEditors.new("openPrjByPath", opened_file_path)
        else:
            startWindow.show()

        # 结束程序
        sys.exit(QApp.exec_())
    except Exception as e:
        QMessageBox().critical(None, "错误", f"发生未知错误：{e}", QMessageBox.Ok)
        Log().error(traceback.format_exc(), f"发生错误：{e}")
    Log().save()
