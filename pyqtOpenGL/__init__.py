"""
该库源自Jin Liu写的 pyqtOpenGL 模块，目前由Jason维护。
相比于开源版本，本版本做了一些扩展和修改，主要包括：
1. 修复了一些bug
2. 删除了不必要的资源文件
3. 添加了一些新的功能，例如透视相机和正交相机，以及一些新的图元
4. 添加了一些新的工具函数
5. 移除了opencv的依赖（缩小编译后的体积），转为使用numpy和PIL

✳请不要轻易修改该库的代码，如果有问题或者建议，请联系Jason（Github：JasonLee-p）
"""
from .items import *
from .GLGraphicsItem import GLGraphicsItem
from .GLViewWidget import GLViewWidget
from .transform3d import Matrix4x4, Quaternion, Vector3
import pyqtOpenGL.functions as functions
from .utils import ToolBox as tb
