"""
opencv的部分功能替换
由于cv2打包后体积过大，因此该项目将cv2的部分功能替换为PIL和numpy实现。
"""
from PIL import Image as PILImage
import numpy as np


class ReplaceCV2:
    @classmethod
    def imread(cls, path):
        """读取图片"""
        return np.array(PILImage.open(path))

    @classmethod
    def imwrite(cls, path, img):
        """保存图片"""
        PILImage.fromarray(img).save(path)

    @classmethod
    def cvtColor(cls, img, code):
        """
        将图片颜色通道转换为指定格式
        cv2函数的PIL&np替代方案
        :param img:
        :param code:
        :return:
        """
        if code == 'COLOR_BGR2RGB':
            return img[..., ::-1]
        if code == 'COLOR_RGB2BGR':
            return img[..., ::-1]
        if code == 'COLOR_BGR2GRAY':
            return np.array(PILImage.fromarray(img).convert("L"))
        if code == 'COLOR_GRAY2BGR':
            return np.stack([img] * 3, axis=-1)
        raise ValueError(f"Unsupported code: {code}")

    @classmethod
    def resize(cls, src, dsize, fx=0, fy=0, interpolation='INTER_LINEAR'):
        """
        使用 Pillow 重新调整图像大小并返回 NumPy 数组。

        :param src: 输入的 NumPy 数组表示的图像
        :param dsize: 输出图像的大小 (宽, 高)。如果为 (0, 0)，则使用 fx 和 fy 缩放因子
        :param fx: 水平缩放因子
        :param fy: 垂直缩放因子
        :param interpolation: 插值方法（'INTER_NEAREST', 'INTER_LINEAR', 'INTER_CUBIC', 'INTER_LANCZOS4'）
        :return: 调整大小后的 NumPy 数组表示的图像
        """
        if dsize == (0, 0):
            dsize = (int(src.shape[1] * fx), int(src.shape[0] * fy))

        pil_interpolation = {
            'INTER_NEAREST': PILImage.NEAREST,
            'INTER_LINEAR': PILImage.BILINEAR,
            'INTER_CUBIC': PILImage.BICUBIC,
            'INTER_LANCZOS4': PILImage.LANCZOS
        }.get(interpolation, None)

        if pil_interpolation is None:
            raise ValueError(f"Unsupported interpolation method: {interpolation}")

        pil_image = PILImage.fromarray(src)
        resized_image = pil_image.resize(dsize, pil_interpolation)
        return np.array(resized_image)

    @classmethod
    def pyrDown(cls, img):
        """
        将图片缩小一倍
        cv2函数的PIL&np替代方案
        :param img: 输入图像（NumPy数组）
        :return: 缩小后的图像（NumPy数组）
        """
        h, w = img.shape[:2]
        resized_image = PILImage.fromarray(img).resize((w // 2, h // 2), PILImage.BILINEAR)
        return np.array(resized_image)



# def imread(path):
#     """读取图片"""
#     return np.array(PILImage.open(path))
#
#
# def imwrite(path, img):
#     """保存图片"""
#     PILImage.fromarray(img).save(path)
#
#
# def cvtColor(img, code):
#     """
#     将图片颜色通道转换为指定格式
#     cv2函数的PIL&np替代方案
#     :param img:
#     :param code:
#     :return:
#     """
#     if code == 'COLOR_BGR2RGB':
#         return img[..., ::-1]
#     if code == 'COLOR_RGB2BGR':
#         return img[..., ::-1]
#     if code == 'COLOR_BGR2GRAY':
#         return np.array(PILImage.fromarray(img).convert("L"))
#     if code == 'COLOR_GRAY2BGR':
#         return np.stack([img] * 3, axis=-1)
#     raise ValueError(f"Unsupported code: {code}")
#
#
# def resize(src, dsize, fx=0, fy=0, interpolation='INTER_LINEAR'):
#     """
#     使用 Pillow 重新调整图像大小并返回 NumPy 数组。
#
#     :param src: 输入的 NumPy 数组表示的图像
#     :param dsize: 输出图像的大小 (宽, 高)。如果为 (0, 0)，则使用 fx 和 fy 缩放因子
#     :param fx: 水平缩放因子
#     :param fy: 垂直缩放因子
#     :param interpolation: 插值方法（'INTER_NEAREST', 'INTER_LINEAR', 'INTER_CUBIC', 'INTER_LANCZOS4'）
#     :return: 调整大小后的 NumPy 数组表示的图像
#     """
#     if dsize == (0, 0):
#         dsize = (int(src.shape[1] * fx), int(src.shape[0] * fy))
#
#     pil_interpolation = {
#         'INTER_NEAREST': PILImage.NEAREST,
#         'INTER_LINEAR': PILImage.BILINEAR,
#         'INTER_CUBIC': PILImage.BICUBIC,
#         'INTER_LANCZOS4': PILImage.LANCZOS
#     }.get(interpolation, None)
#
#     if pil_interpolation is None:
#         raise ValueError(f"Unsupported interpolation method: {interpolation}")
#
#     pil_image = PILImage.fromarray(src)
#     resized_image = pil_image.resize(dsize, pil_interpolation)
#     return np.array(resized_image)
#
#
# def pyrDown(img):
#     """
#     将图片缩小一倍
#     cv2函数的PIL&np替代方案
#     :param img: 输入图像（NumPy数组）
#     :return: 缩小后的图像（NumPy数组）
#     """
#     h, w = img.shape[:2]
#     resized_image = PILImage.fromarray(img).resize((w // 2, h // 2), PILImage.BILINEAR)
#     return np.array(resized_image)
