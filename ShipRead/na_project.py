# -*- coding: utf-8 -*-
"""
读取NavalArt设计文件

文件格式：
<root>
  <ship author="XXXXXXXXX" description="description" hornType="1" hornPitch="0.9475011" tracerCol="E53D4FFF">
    <newPart id="0">
      <data length="4.5" height="1" frontWidth="0.2" backWidth="0.5" frontSpread="0.05" backSpread="0.2" upCurve="0" downCurve="1" heightScale="1" heightOffset="0" />
      <position x="0" y="0" z="114.75" />
      <rotation x="0" y="0" z="0" />
      <scale x="1" y="1" z="1" />
      <color hex="975740" />
      <armor value="5" />
    </newPart>
    <newPart id="190">
      <position x="0" y="-8.526513E-14" z="117.0312" />
      <rotation x="90" y="0" z="0" />
      <scale x="0.03333336" y="0.03333367" z="0.1666679" />
      <color hex="975740" />
      <armor value="5" />
    </newPart>
  </root>
"""
import xml.etree.ElementTree as ET
from typing import List, Dict

import numpy as np
from PyQt5.QtCore import pyqtSignal

import const
from main_logger import Log


class NaPart:
    """
    零件类
    """
    def __init__(self, ship, Id: str, pos: np.ndarray, rot: np.ndarray, scale: np.ndarray, color: str, armor: int):
        """

        :param ship:
        :param Id:
        :param pos:
        :param rot:
        :param scale:
        :param color: 包含#的十六进制颜色
        :param armor:
        """
        if color[0] != '#':
            raise ValueError("颜色必须为十六进制颜色，包含“#”")
        self.Ship = ship
        self.Id: str = Id
        self.Pos: np.ndarray = pos
        self.Rot: np.ndarray = rot
        self.Scl: np.ndarray = scale
        self.Col: str = color
        self.Amr: int = armor

    def __deepcopy__(self, memo):
        return self

    def __str__(self):
        part_type = "NaPart"
        return str(
            f"\n\nTyp:  {part_type}\n"
            f"Id:   {self.Id}\n"
            f"Pos:  {self.Pos}\n"
            f"Rot:  {self.Rot}\n"
            f"Scl:  {self.Scl}\n"
            f"Col:  #{self.Col}\n"
            f"Amr:  {self.Amr} mm\n"
        )

    def __repr__(self):  # 用于print
        return self.__str__()


class AdjustableHull(NaPart):
    """
    可调节船体
    """
    def __init__(
            self, ship, Id, pos, rot, scale, color, armor,
            length, height, frontWidth, backWidth, frontSpread, backSpread, upCurve, downCurve,
            heightScale, heightOffset,
    ):
        """
        :param ship: 船体设计读取器 NaDesignReader
        :param Id: 字符串，零件ID
        :param pos: 元组，三个值分别为x,y,z轴的位置
        :param rot: 元组，三个值分别为x,y,z轴的旋转角度
        :param scale: 元组，三个值分别为x,y,z轴的缩放比例
        :param color: 字符串，颜色的十六进制表示
        :param armor: 整型，装甲厚度
        :param length: 浮点型，长度
        :param height: 浮点型，高度
        :param frontWidth: 浮点型，前宽
        :param backWidth: 浮点型，后宽
        :param frontSpread: 浮点型，前扩散
        :param backSpread: 浮点型，后扩散
        :param upCurve: 浮点型，上曲率
        :param downCurve: 浮点型，下曲率
        :param heightScale: 浮点型，前端高度缩放
        :param heightOffset: 浮点型，前端高度偏移
        """
        NaPart.__init__(self, ship, Id, pos, rot, scale, color, armor)
        self.Len = length
        self.Hei = height
        self.FWid = frontWidth
        self.BWid = backWidth
        self.FSpr = frontSpread
        self.BSpr = backSpread
        self.UCur = upCurve
        self.DCur = downCurve
        self.HScl = heightScale  # 高度缩放
        self.HOff = heightOffset  # 高度偏移


class MainWeapon(NaPart):
    """
    主武器
    """
    def __init__(self, ship, Id, pos, rot, scale, color, armor, manual_control, elevator):
        """
        :param manual_control: 是否手动控制
        :param elevator: 升降机高度
        """
        super().__init__(ship, Id, pos, rot, scale, color, armor)
        self.ManualControl = manual_control
        self.ElevatorH = elevator


class NaDesignReader:
    """
    NavalArt 设计读取，将图纸信息读取到实例
    """
    TAG = "NaDesignReader"
    progress = pyqtSignal(str, str)

    def __init__(self, filepath):
        """
        NavalArt 设计读取
        :param filepath: .na文件的路径
        """
        self.filename = filepath.split('\\')[-1]
        self.filepath = filepath
        # 初始化零件集
        self.Parts: List[NaPart] = []
        self.Weapons: List[MainWeapon] = []
        self.AdjustableHulls: List[AdjustableHull] = []
        self.ColorPartsMap: Dict[str, List[NaPart]] = {}
        # 读取根节点
        try:
            self.root = ET.parse(filepath).getroot()
        except ET.ParseError:
            Log().warning(self.TAG, f"文件{filepath}读取失败")
        self.ShipName = self.filename[:-3]
        # ship
        self._ship = self.root.find('ship')
        self.Author = self._ship.attrib.get('author', None)
        self.HornType = self._ship.attrib.get('hornType', None)
        self.HornPitch = self._ship.attrib.get('hornPitch', None)
        self.TracerCol = self._ship.attrib.get('tracerCol', None)
        self._xml_all_parts = self.root.findall('ship/part')
        # 遍历所有零件
        part_num = len(self._xml_all_parts)
        for i, part in enumerate(self._xml_all_parts):
            # 输出进度
            if i % 13 == 0:
                process = round(i / part_num * 100, 2)
                # TODO: 发射进度信号
                self.progress.emit(f"正在读取文件：{self.filename} 进度：{process}%", "process")
            _id = str(part.attrib['id'])
            _pos = part.find('position').attrib
            _rot = part.find('rotation').attrib
            _scl = part.find('scale').attrib
            _pos = np.array([float(_pos['x']), float(_pos['y']), float(_pos['z'])])
            _rot = np.array([round(float(_rot['x']), const.DECIMAL_PRECISION), round(float(_rot['y']), const.DECIMAL_PRECISION), round(float(_rot['z']), const.DECIMAL_PRECISION)])
            _scl = np.array([float(_scl['x']), float(_scl['y']), float(_scl['z'])])
            _scl = np.array([abs(i) for i in _scl])
            _col = str(part.find('color').attrib['hex'])
            _amr = int(part.find('armor').attrib['value'])
            if _id == '0':  # 如果ID为0，就添加到可调节船体
                _data = part.find('data').attrib
                obj = AdjustableHull(
                    self, _id, _pos, _rot, _scl, _col, _amr,
                    float(_data['length']), float(_data['height']),
                    float(_data['frontWidth']), float(_data['backWidth']),
                    float(_data['frontSpread']), float(_data['backSpread']),
                    float(_data['upCurve']), float(_data['downCurve']),
                    float(_data['heightScale']), float(_data['heightOffset'])
                )
                self.AdjustableHulls.append(obj)

            elif part.find('turret') is not None:  # 如果有turret，就添加到主武器
                manual_control = part.find('turret').attrib.get('manualControl', None)
                elevatorH = part.find('turret').attrib.get('evevator', None)
                obj = MainWeapon(self, _id, _pos, _rot, _scl, _col, _amr, manual_control, elevatorH)
                self.Weapons.append(obj)

            else:  # 最后添加到普通零件
                obj = NaPart(self, _id, _pos, _rot, _scl, _col, _amr)
            # 添加颜色
            _color = f"#{part.find('color').attrib['hex']}"
            if _color not in self.ColorPartsMap.keys():
                self.ColorPartsMap[_color] = []
            self.ColorPartsMap[_color].append(obj)
            self.Parts.append(obj)
