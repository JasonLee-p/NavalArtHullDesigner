"""
用于管理工程文件对象，包括船体、船舱、甲板、船舷，模型等。
*添加图纸组件*请将相应的py文件在此添加引用。
"""
from .baseComponent import ComponentNodeXY, ComponentNodeXZ, SubPrjComponent, PrjComponent
from .hullSectionGroup import HullSectionGroup, HullSection
from .armorSectionGroup import ArmorSectionGroup, ArmorSection
from .bridge import Bridge, Handrail, Railing
from .ladder import Ladder
from .model import Model
from .refImage import RefImage
