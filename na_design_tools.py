import os
import xml.etree.ElementTree as ET

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")


def offset_position(xml_str, offset_x, offset_y, offset_z):
    """
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

    file_name = "KMS Hindenburg.na"
    path = os.path.join(DESKTOP, file_name)
    offset_design_position(path, 0.0, -6.0, 0.0)
