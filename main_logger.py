"""
日志模块
包括：
1. 日志类Log，用于记录日志信息，包括info、warning、error等
2. 状态栏处理类StatusBarHandler，用于处理状态栏信息

"""
import sys
import time
from contextlib import contextmanager

from PyQt5.QtCore import QMutex, pyqtSignal, QObject
from funcs_utils import singleton, mutexLock


def getTagStr(tag):
    return f"[{tag}]".ljust(24, " ")  # width最好是4的倍数


def getLevelStr(level):
    return f"[{level}]".ljust(12, " ")


# 信息前的空格数
EMPTY_STR = ' ' * 55


def getInfoStr(info):
    info = info.split("\n")
    for i in range(1, len(info)):
        info[i] = EMPTY_STR + info[i]
    return "\n".join(info)


@singleton
class Log:
    write_mutex = QMutex()
    FILE_MAX_SIZE = 1024 * 1024  # 1MB
    LINE_LENGTH = 150
    SEPARATOR = "=" * LINE_LENGTH
    INFO = "[INFO]    "
    WARNING = "[WARNING] "
    ERROR = "[ERROR]   "

    def __init__(self, path="logging.txt"):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        self.path = path
        self._init_log_file()
        logging_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.addString = (f"\n{self.SEPARATOR}\n"
                          f"{logging_time}  {self.INFO}{getTagStr('Log')}程序启动，日志启动\n")

    @mutexLock("write_mutex")
    def _init_log_file(self):
        with open(self.path, "a", encoding="utf-8") as f:
            # 检测文件大小
            f.seek(0, 2)
            # 限制文件大小
            if f.tell() > self.FILE_MAX_SIZE:
                f.truncate(0)  # 清空文件
                # TODO: 可以尝试上传
                truncate_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                f.write(f"{truncate_time}  {self.INFO}{getTagStr('Log')}日志文件超过1MB，已清空\n")

    @mutexLock("write_mutex")
    def error(self, trace, tag, info):
        err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        infoString = getInfoStr(trace + '\n' + info)
        string = f"{err_time}  {self.ERROR}{getTagStr(tag)}{infoString}\n"
        self.addString += string
        # 使用sys.stderr输出
        self._stderr.write(string)
        self._stderr.flush()
        self.save()

    @mutexLock("write_mutex")
    def warning(self, tag, info):
        warn_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        string = f"{warn_time}  {self.WARNING}{getTagStr(tag)}{getInfoStr(info)}\n"
        self.addString += string
        self._stdout.write(string)
        self._stdout.flush()

    @mutexLock("write_mutex")
    def info(self, tag, info):
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        string = f"{log_time}  {self.INFO}{getTagStr(tag)}{getInfoStr(info)}\n"
        self.addString += string
        self._stdout.write(string)
        self._stdout.flush()

    @mutexLock("write_mutex")
    def save(self):
        self._stdout.flush()
        self._stderr.flush()
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.addString += (f"{log_time}  {self.INFO}{getTagStr('Log')}保存日志，程序退出\n"
                           f"{self.SEPARATOR}\n")
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(self.addString)
                self.addString = ''
        except Exception as e:
            self._stderr.write(f"{log_time}  {self.ERROR}{getTagStr('Log')}保存日志失败：{e}\n")

    @contextmanager
    def redirectOutput(self, tag):
        class StreamToLogger:
            def __init__(self, log_instance, _tag, level):
                self.log_instance = log_instance
                self.tag = _tag
                self.level = level

            def write(self, message):
                if message.strip():
                    if self.level == 'error':
                        self.log_instance.error('', self.tag, message)
                    elif self.level == 'warning':
                        self.log_instance.warning(self.tag, message)
                    else:
                        self.log_instance.info(self.tag, message)

            def flush(self):
                pass

        stdout_logger = StreamToLogger(self, tag, 'info')
        stderr_logger = StreamToLogger(self, tag, 'error')
        sys.stdout = stdout_logger
        sys.stderr = stderr_logger
        try:
            yield
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__


@singleton
class StatusBarHandler(QObject):
    """
    用于处理状态栏的信息
    其中的信号将会被连接到主窗口的状态栏
    """
    message = pyqtSignal(str, str)

    def __init__(self):
        from GUI import GRAY, LIGHTER_RED, FG_COLOR0
        self.GRAY = GRAY
        self.LIGHTER_RED = LIGHTER_RED
        self.FG_COLOR0 = FG_COLOR0
        super().__init__()

    def info(self, message):
        self.message.emit(message, self.FG_COLOR0.__str__())

    def warning(self, message):
        self.message.emit(message, self.LIGHTER_RED.__str__())

    def progress(self, message):
        self.message.emit(message, self.GRAY.__str__())
