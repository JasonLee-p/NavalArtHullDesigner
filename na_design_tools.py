"""
这是一个用于处理NavalArt图纸的工具集合，包括获取平均位置和偏移位置等功能
"""

import os
import xml.etree.ElementTree as ET

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
    avg_x = round(x_sum / count, 4)
    avg_y = round(y_sum / count, 4)
    avg_z = round(z_sum / count, 4)

    # 返回平均位置元组
    return avg_x, avg_y, avg_z


def get_range_position(xml_str):
    """
    :param xml_str: 输入的XML文件字符串
    :return: 位置的范围元组
    """
    # 解析XML字符串
    root = ET.fromstring(xml_str)

    # 初始化位置的最大最小值
    min_x = 10000000
    min_y = 10000000
    min_z = 10000000
    max_x = -10000000
    max_y = -10000000
    max_z = -10000000

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
        x = round(float(position.get('x')) + offset_x, 4)
        y = round(float(position.get('y')) + offset_y, 4)
        z = round(float(position.get('z')) + offset_z, 4)

        # 更新<position>标签的属性值
        position.set('x', f"{x:.4f}")
        position.set('y', f"{y:.4f}")
        position.set('z', f"{z:.4f}")

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


if __name__ == "__main__":
    # 测试
    file_name = "KMS Hindenburg.na"
    path = os.path.join(DESKTOP, file_name)
    offset_design_position(path, 0.0, -6.0, 0.0)
