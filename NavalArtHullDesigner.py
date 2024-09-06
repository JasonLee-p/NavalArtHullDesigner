# -*- coding: utf-8 -*-
"""
NavalArt船体编辑器 主程序
作者: JasonLee-p
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
    from main_logger import Log, StatusBarHandler
    from utils.funcs_utils import singleton
    from path_lib import *
    from main_editor import MainEditor
    from startWindow import StartWindow
    from ShipRead import *
except Exception as e:
    traceback.print_exc()
    print(f"[ERROR] {e}")
    input(f"[INFO] Press any key to exit...")
    sys.exit(1)

VERSION = "1.0.0.0"


@singleton
class MainEditorHandler(list):
    """
    主编辑窗口管理器，用于管理所有的主编辑窗口，提供打开、关闭、新建等功能
    主窗口数量上限为3
    """
    TAG = "MainEditorHandler"

    def __init__(self, logger_):
        super().__init__()
        self.configHandler = configHandler
        self.logger = logger_
        self.statusBarHandler = StatusBarHandler()

    def new(self, mode: Literal["lastEdit", "newPrj", "openPrj", "setting", "help"] = "lastEdit"):
        """
        新建主编辑窗口
        """
        global startWindow
        if len(self) < 3:
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
            QMessageBox().warning(None, "警告", "编辑窗口数量已达上限（3）", QMessageBox.Ok)
            return None

    def open(self, path: str):
        """
        打开项目
        """
        global startWindow
        if len(self) < 3:
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
            QMessageBox().warning(None, "警告", "编辑窗口数量已达上限（3）", QMessageBox.Ok)
            return None

    def close(self, main_editor: MainEditor):
        """
        关闭主编辑窗口
        """
        global startWindow
        # 将窗口从数组删除
        self.remove(main_editor)
        # Log().info(self.TAG, f"unref: {gc.collect()}")  # 手动垃圾回收
        Log().info(self.TAG, f"MainEditor引用计数：{sys.getrefcount(main_editor)}")
        del main_editor
        # 保存配置
        self.configHandler.save_config()
        # 如果没有窗口了，关闭程序
        Log().save()


def lastEdit():
    """
    打开最近编辑的项目，由开始界面调用
    """
    Log().info(Log().GLOBAL_TAG, "最近编辑")
    _mainEditor = mainEditors.new("lastEdit")
    if not _mainEditor:
        return


def newPrj():
    """
    新建项目，由开始界面调用（未完成）
    """
    Log().info(Log().GLOBAL_TAG, "单击：新建项目")
    _mainEditor = mainEditors.new()
    if not _mainEditor:
        return


def openPrj():
    """
    打开选择对话框，选择要打开的项目，由开始界面调用（未完成）
    """
    Log().info(Log().GLOBAL_TAG, "单击：打开项目")
    _mainEditor = mainEditors.new()
    if not _mainEditor:
        return


def setting():
    """
    打开设置页面，由开始界面调用（未完成）
    """
    Log().info(Log().GLOBAL_TAG, "单击：设置")
    _mainEditor = mainEditors.new()
    if not _mainEditor:
        return


def _help():
    """
    打开帮助页面，由开始界面调用（未完成）
    """
    Log().info(Log().GLOBAL_TAG, "单击：帮助")
    _mainEditor = mainEditors.new()
    if not _mainEditor:
        return


def about():
    """
    打开关于页面，由开始界面调用
    """
    Log().info(Log().GLOBAL_TAG, "单击：关于")
    webbrowser.open("http://naval_plugins.e.cn.vc/")


def linkSignal(startwindow: StartWindow):
    """
    将开始界面的信号连接到对应的槽函数
    """
    startwindow.lastEdit_signal.connect(lastEdit)
    startwindow.newPrj_signal.connect(newPrj)
    startwindow.openPrj_signal.connect(openPrj)
    startwindow.setting_signal.connect(setting)
    startwindow.help_signal.connect(_help)
    startwindow.about_signal.connect(about)


if __name__ == '__main__':
    Log()  # 初始化日志
    Log().info(Log().GLOBAL_TAG, f"启动NavalArt船体编辑器 V{VERSION}")
    Log().info(Log().GLOBAL_TAG, f"命令行参数：{sys.argv}")
    # 路径前一共15个字符
    Log().info(Log().GLOBAL_TAG, f"""初始化路径常量：
DeskTop:      {DESKTOP_PATH}
PTB:          {PTB_PATH}
NA design:    {NA_SHIP_PATH}
NA root:      {NA_ROOT_PATH}
Config file:  {CONFIG_PATH}
Current env:  {CURRENT_PATH}""")
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
        Log().info(Log().GLOBAL_TAG, f"QApp初始化完成")
        # 设置全局的提示框字体
        QToolTip.setFont(YAHEI[9])
        # 打开欢迎界面
        startWindow = StartWindow()
        mainEditors: MainEditorHandler = MainEditorHandler(Log())
        linkSignal(startWindow)
        if opened_file_path:
            startWindow.hide()
            mainEditors: MainEditorHandler = MainEditorHandler(Log())
            # 打开文件
            mainEditor = mainEditors.open(opened_file_path)
        else:
            startWindow.show()

        # 结束程序
        sys.exit(QApp.exec_())
    except Exception as e:
        QMessageBox().critical(None, "错误", f"发生未知错误：{e}", QMessageBox.Ok)
        Log().error(traceback.format_exc(), Log().GLOBAL_TAG, f"发生错误：{e}")
