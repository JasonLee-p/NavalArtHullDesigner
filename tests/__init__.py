"""
测试
"""
from .test_APIClient import *
from .test_ShipPaint import *
from .test_ShipRead import *
from .test_main_editor import *
from .test_main_logger import *
from .test_cv2replacement import TestCV2Replacements
from .test_funcs_utils import TestFuncsUtils


def run_test() -> bool:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='.', pattern='test_*.py')
    runner = unittest.TextTestRunner()
    runner.run(suite)
    return True


if __name__ == '__main__':
    run_test()
