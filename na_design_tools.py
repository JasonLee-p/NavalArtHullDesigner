"""
这是一个用于处理NavalArt图纸的工具集合，包括获取平均位置和偏移位置等功能
"""

import os
import xml.etree.ElementTree as ET

import const

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")


def get_avg_position(xml_str):
    """
    :param xml_str: 输入的XML文件字符串
    :return: 平均位置的元组
    """
    # 解析XML字符串
    root = ET.fromstring(xml_str)

    # 初始化位置的累加值和计数
    x_sum = 0
    y_sum = 0
    z_sum = 0
    count = 0

    # 查找所有的<position>标签
    for position in root.findall(".//position"):
        # 获取当前的x, y, z值
        x = float(position.get('x'))
        y = float(position.get('y'))
        z = float(position.get('z'))

        # 累加
        x_sum += x
        y_sum += y
        z_sum += z
        count += 1

    # 计算平均值
    avg_x = round(x_sum / count, const.DECIMAL_PRECISION)
    avg_y = round(y_sum / count, const.DECIMAL_PRECISION)
    avg_z = round(z_sum / count, const.DECIMAL_PRECISION)

    # 返回平均位置元组
    return avg_x, avg_y, avg_z


def get_range_position(xml_str):
    """
    :param xml_str: 输入的XML文件字符串
    :return: 位置的范围元组：min_x, min_y, min_z, max_x, max_y, max_z
    """
    # 解析XML字符串
    root = ET.fromstring(xml_str)

    # 初始化位置的最大最小值
    min_x = const.MAX_VALUE
    min_y = const.MAX_VALUE
    min_z = const.MAX_VALUE
    max_x = const.MIN_VALUE
    max_y = const.MIN_VALUE
    max_z = const.MIN_VALUE

    # 查找所有的<position>标签
    for position in root.findall(".//position"):
        # 获取当前的x, y, z值
        x = float(position.get('x'))
        y = float(position.get('y'))
        z = float(position.get('z'))

        # 更新最大最小值
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        min_z = min(min_z, z)
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        max_z = max(max_z, z)

    # 返回位置范围元组
    return min_x, min_y, min_z, max_x, max_y, max_z


def offset_position(xml_str, offset_x, offset_y, offset_z) -> str:
    """
    将XML文件中的所有position标签进行偏移
    :param xml_str: 输入的XML文件字符串
    :param offset_x: X轴的偏移量
    :param offset_y: Y轴的偏移量
    :param offset_z: Z轴的偏移量
    :return: 偏移后的XML字符串
    """
    # 解析XML字符串
    root = ET.fromstring(xml_str)

    # 查找所有的<position>标签
    for position in root.findall(".//position"):
        # 获取当前的x, y, z值并偏移
        x = round(float(position.get('x')) + offset_x, const.DECIMAL_PRECISION)
        y = round(float(position.get('y')) + offset_y, const.DECIMAL_PRECISION)
        z = round(float(position.get('z')) + offset_z, const.DECIMAL_PRECISION)

        # 更新<position>标签的属性值
        position.set('x', f"{x}")
        position.set('y', f"{y}")
        position.set('z', f"{z}")

    # 返回修改后的XML字符串
    return ET.tostring(root, encoding='unicode')


def offset_design_position(file_path, x, y, z):
    """
    打开XML文件并将其所有position进行偏移
    :param file_path:
    :param x:
    :param y:
    :param z:
    :return:
    """
    # 读取XML文件（utf-8）
    if not file_path.endswith(".na"):
        raise ValueError("文件格式不正确")
    with open(file_path, "r", encoding="utf-8") as f:
        xml_str = f.read()
    new_str = offset_position(xml_str, x, y, z)
    # 写入新的XML文件
    with open(os.path.join(DESKTOP, file_name.replace(".na", "_offset.na")), "w", encoding="utf-8") as inf:
        inf.write(new_str)


def scale_position(xml_str, scale_x, scale_y, scale_z) -> str:
    """
    将XML文件中的所有position标签进行缩放
    :param xml_str: 输入的XML文件字符串
    :param scale_x: X轴的缩放比例
    :param scale_y: Y轴的缩放比例
    :param scale_z: Z轴的缩放比例
    :return: 缩放后的XML字符串
    """
    # 解析XML字符串
    root = ET.fromstring(xml_str)

    # 查找所有带有position子标签的标签
    for tag in root.findall(".//*[@position]"):
        # 获取要修改的属性值
        position = tag.get('position')
        scale = tag.get('scale')

        # 解析属性
        px, py, pz = map(float, position.split())
        sx, sy, sz = map(float, scale.split())

        # 更新属性值
        tag.set('position',
                f"{round(px * scale_x, const.DECIMAL_PRECISION)} "
                f"{round(py * scale_y, const.DECIMAL_PRECISION)} "
                f"{round(pz * scale_z, const.DECIMAL_PRECISION)}")
        tag.set('scale',
                f"{round(sx * scale_x, const.DECIMAL_PRECISION)} "
                f"{round(sy * scale_y, const.DECIMAL_PRECISION)} "
                f"{round(sz * scale_z, const.DECIMAL_PRECISION)}")

    # 返回修改后的XML字符串
    return ET.tostring(root, encoding='unicode')


if __name__ == "__main__":
    # 测试
    file_name = "KMS Hindenburg.na"
    path = os.path.join(DESKTOP, file_name)
    offset_design_position(path, 0.0, -6.0, 0.0)
