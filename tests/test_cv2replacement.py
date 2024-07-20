"""
测试cv2_replacements.py
"""
import unittest
from PIL import Image
import os

from cv2_replacements import *


class TestCV2Replacements(unittest.TestCase):

    def setUp(self):
        # 创建一个测试用的图像数组
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.test_image[25:75, 25:75] = [255, 0, 0]  # 红色方块

        # 创建一个灰度图像
        self.test_gray_image = np.zeros((100, 100), dtype=np.uint8)
        self.test_gray_image[25:75, 25:75] = 127  # 灰色方块

        # 保存测试图像
        os.makedirs('res', exist_ok=True)
        self.test_image_path = 'res/test_image.png'
        self.test_gray_image_path = 'res/test_gray_image.png'
        imwrite(self.test_image_path, self.test_image)
        imwrite(self.test_gray_image_path, self.test_gray_image)

    def tearDown(self):
        # 删除测试图像
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.test_gray_image_path):
            os.remove(self.test_gray_image_path)

    def test_imread(self):
        img = imread(self.test_image_path)
        self.assertTrue(np.array_equal(img, self.test_image))

    def test_imwrite(self):
        path = 'res/test_save.png'
        imwrite(path, self.test_image)
        saved_img = imread(path)
        self.assertTrue(np.array_equal(saved_img, self.test_image))
        if os.path.exists(path):
            os.remove(path)

    def test_cvtColor_BGR2RGB(self):
        bgr_image = self.test_image[..., ::-1]
        rgb_image = cvtColor(bgr_image, 'COLOR_BGR2RGB')
        self.assertTrue(np.array_equal(rgb_image, self.test_image))

    def test_cvtColor_RGB2BGR(self):
        rgb_image = cvtColor(self.test_image, 'COLOR_RGB2BGR')
        bgr_image = self.test_image[..., ::-1]
        self.assertTrue(np.array_equal(rgb_image, bgr_image))

    def test_cvtColor_BGR2GRAY(self):
        gray_image = cvtColor(self.test_image, 'COLOR_BGR2GRAY')
        expected_gray_image = np.array(Image.fromarray(self.test_image).convert("L"))
        self.assertTrue(np.array_equal(gray_image, expected_gray_image))

    def test_cvtColor_GRAY2BGR(self):
        bgr_image = cvtColor(self.test_gray_image, 'COLOR_GRAY2BGR')
        expected_bgr_image = np.stack([self.test_gray_image] * 3, axis=-1)
        self.assertTrue(np.array_equal(bgr_image, expected_bgr_image))

    def test_resize(self):
        resized_image = resize(self.test_image, (50, 50))
        self.assertEqual(resized_image.shape, (50, 50, 3))

        resized_image_fx_fy = resize(self.test_image, (0, 0), fx=0.5, fy=0.5)
        self.assertEqual(resized_image_fx_fy.shape, (50, 50, 3))

    def test_pyrDown(self):
        downsampled_image = pyrDown(self.test_image)
        self.assertEqual(downsampled_image.shape, (50, 50, 3))


# 只测试当前文件
if __name__ == '__main__':
    unittest.main()
