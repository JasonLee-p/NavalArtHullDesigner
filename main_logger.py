"""
记录程序运行日志
"""
import time

from GUI import GRAY, LIGHTER_RED, FG_COLOR0
from PyQt5.QtCore import QMutex, pyqtSignal, QObject, QMutexLocker
from funcs_utils import singleton


@singleton
class Log:
    write_mutex = QMutex()

    def __init__(self, path="logging.txt"):
        self.wirte_locker = QMutexLocker(self.write_mutex)
        self.path = path
        self.file = open(path, "a", encoding="utf-8")

    def error(self, trace, info):
        err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with self.wirte_locker:
            self.file.write(f"[ERROR] {err_time}\n{trace}\n{info}\n\n")

    def warning(self, info):
        warn_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with self.wirte_locker:
            self.file.write(f"[WARNING] {warn_time}\n{info}\n\n")

    def info(self, info):
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with self.wirte_locker:
            self.file.write(f"[INFO] {log_time}\n{info}\n\n")

    def save(self):
        self.file.close()


@singleton
class StatusBarHandler(QObject):
    message = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

    def info(self, message):
        self.message.emit(message, FG_COLOR0.__str__())

    def warning(self, message):
        self.message.emit(message, LIGHTER_RED.__str__())

    def progress(self, message):
        self.message.emit(message, GRAY.__str__())


