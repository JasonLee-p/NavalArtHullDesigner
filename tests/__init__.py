"""
测试
"""
import subprocess


def run_test():
    subprocess.run(["python", "-m", "unittest", "discover", "tests"])