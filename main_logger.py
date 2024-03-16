"""
记录程序运行日志
"""
import time

from PyQt5.QtCore import QMutex
from funcs_utils import singleton


@singleton
class Log:
    write_mutex = QMutex()

    def __init__(self, path="logging.txt"):
        self.path = path
        self.file = open(path, "a", encoding="utf-8")

    def error(self, trace, info):
        err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.write_mutex.lock()
        self.file.write(f"[ERROR] {err_time}\n{trace}\n{info}\n\n")
        self.write_mutex.unlock()

    def warning(self, info):
        warn_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.write_mutex.lock()
        self.file.write(f"[WARNING] {warn_time}\n{info}\n\n")
        self.write_mutex.unlock()

    def info(self, info):
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.write_mutex.lock()
        self.file.write(f"[INFO] {log_time}\n{info}\n\n")
        self.write_mutex.unlock()

    def save(self):
        self.file.close()
