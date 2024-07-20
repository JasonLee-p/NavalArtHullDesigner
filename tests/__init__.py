"""
测试
"""
import unittest


def run_test():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='.', pattern='test_*.py')
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    run_test()
