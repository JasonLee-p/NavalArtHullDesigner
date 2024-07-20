# tests/test_funcs_utils.py
import unittest
from unittest.mock import patch, MagicMock
from funcs_utils import *
from PyQt5.QtCore import QMutex


class TestFuncsUtils(unittest.TestCase):

    def test_snake_to_camel(self):
        """
        测试snake_to_camel函数
        :return:
        """
        self.assertEqual(snake_to_camel('snake_case'), 'SnakeCase')
        self.assertEqual(snake_to_camel('another_example'), 'AnotherExample')
        self.assertEqual(snake_to_camel('example_test_case'), 'ExampleTestCase')

    def test_merge_dict(self):
        """
        测试merge_dict函数
        merge_dict(d1, d2)将d2的键值对合并到d1中，d2的键值对优先级高
        :return:
        """
        d1 = {'a': 1, 'b': {'x': 10}}
        d2 = {'b': {'y': 20}, 'c': 3}
        expected = {'a': 1, 'b': {'x': 10, 'y': 20}, 'c': 3}
        self.assertTrue(merge_dict(d1, d2))
        self.assertEqual(d1, expected)

    @patch('PyQt5.QtGui.QDesktopServices.openUrl')
    def test_open_url(self, mock_open_url):
        url = 'https://example.com'
        func = open_url(url)
        mock_event = MagicMock()
        func(mock_event)
        mock_open_url.assert_called_once()

    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_not_implemented(self, mock_information):
        @not_implemented
        def sample_func():
            pass

        sample_func()
        mock_information.assert_called_once_with(None, "提示", "该功能暂未实现，敬请期待！", QMessageBox.Ok)

    def test_singleton(self):
        @singleton
        class SampleClass:
            def __init__(self):
                self.value = 42

        instance1 = SampleClass()
        instance2 = SampleClass()
        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, 42)
        self.assertEqual(instance2.value, 42)

    @patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=True)
    def test_is_admin(self, mock_is_admin):
        self.assertTrue(is_admin())
        mock_is_admin.assert_called_once()

    @patch('builtins.print')
    def test_color_print(self, mock_print):
        color_print("Hello, World!", "red")
        mock_print.assert_called_once_with("\033[31mHello, World!\033[0m")

    @patch('time.time', side_effect=[1, 3])
    @patch('builtins.print')
    def test_time_it(self, mock_print, mock_time):
        @time_it
        def sample_func():
            pass

        sample_func()
        mock_print.assert_called_once_with("函数sample_func运行时间：2")

    @patch('PyQt5.QtCore.QMutexLocker.__enter__')
    @patch('PyQt5.QtCore.QMutexLocker.__exit__')
    def test_operationMutexLock(self, mock_enter, mock_exit):
        class SampleClass:
            def __init__(self):
                self.operationMutex = QMutex()

            @operationMutexLock
            def locked_method(self):
                return "locked"

        instance = SampleClass()
        result = instance.locked_method()
        self.assertEqual(result, "locked")
        mock_enter.assert_called_once()
        mock_exit.assert_called_once()

    @patch('PyQt5.QtCore.QMutexLocker.__enter__')
    @patch('PyQt5.QtCore.QMutexLocker.__exit__')
    def test_mutexLock(self, mock_enter, mock_exit):
        class SampleClass:
            def __init__(self):
                self.myMutex = QMutex()

            @mutexLock('myMutex')
            def locked_method(self):
                return "locked"

        instance = SampleClass()
        result = instance.locked_method()
        self.assertEqual(result, "locked")
        mock_enter.assert_called_once()
        mock_exit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
