# -*- coding: utf-8 -*-
"""
utils.const 单元测试
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConst(unittest.TestCase):
    """测试常量模块"""

    def test_direction_constants(self):
        """测试方向常量"""
        from utils.const import CONST
        
        # 验证基本方向
        self.assertEqual(CONST.FRONT, "front")
        self.assertEqual(CONST.BACK, "back")
        self.assertEqual(CONST.UP, "up")
        self.assertEqual(CONST.DOWN, "down")
        self.assertEqual(CONST.LEFT, "left")
        self.assertEqual(CONST.RIGHT, "right")

    def test_direction_normal_vectors(self):
        """测试方向法向量"""
        from utils.const import CONST
        
        self.assertEqual(CONST.FRONT_NORMAL, (0., 0., 1.))
        self.assertEqual(CONST.BACK_NORMAL, (0., 0., -1.))
        self.assertEqual(CONST.LEFT_NORMAL, (-1., 0., 0.))
        self.assertEqual(CONST.RIGHT_NORMAL, (1., 0., 0.))
        self.assertEqual(CONST.UP_NORMAL, (0., 1., 0.))
        self.assertEqual(CONST.DOWN_NORMAL, (0., -1., 0.))

    def test_opposite_direction_map(self):
        """测试方向映射"""
        from utils.const import CONST
        
        # 验证反向映射
        self.assertEqual(CONST.DIR_OPPOSITE_MAP[CONST.FRONT], CONST.BACK)
        self.assertEqual(CONST.DIR_OPPOSITE_MAP[CONST.BACK], CONST.FRONT)
        self.assertEqual(CONST.DIR_OPPOSITE_MAP[CONST.UP], CONST.DOWN)
        self.assertEqual(CONST.DIR_OPPOSITE_MAP[CONST.DOWN], CONST.UP)
        self.assertEqual(CONST.DIR_OPPOSITE_MAP[CONST.LEFT], CONST.RIGHT)
        self.assertEqual(CONST.DIR_OPPOSITE_MAP[CONST.RIGHT], CONST.LEFT)

    def test_rotate_order_constants(self):
        """测试旋转顺序常量"""
        from utils.const import CONST
        
        # 验证所有旋转顺序
        self.assertIn(CONST.XYZ, CONST._CONST__orders)
        self.assertIn(CONST.XZY, CONST._CONST__orders)
        self.assertIn(CONST.YXZ, CONST._CONST__orders)
        self.assertIn(CONST.YZX, CONST._CONST__orders)
        self.assertIn(CONST.ZXY, CONST._CONST__orders)
        self.assertIn(CONST.ZYX, CONST._CONST__orders)
        
        # 验证当前使用的旋转顺序
        self.assertIn(CONST.ROTATE_ORDER, CONST._CONST__orders)

    def test_vector_relation_map(self):
        """测试向量关系映射"""
        from utils.const import CONST
        
        # 验证向量关系
        self.assertIn(CONST.FRONT_NORMAL, CONST.VECTOR_RELATION_MAP)
        
        relation = CONST.VECTOR_RELATION_MAP[CONST.FRONT_NORMAL]
        self.assertEqual(relation['Larger'], CONST.FRONT)
        self.assertEqual(relation['Smaller'], CONST.BACK)

    def test_dir_index_map(self):
        """测试方向索引映射"""
        from utils.const import CONST
        
        self.assertEqual(CONST.DIR_INDEX_MAP[CONST.FRONT_BACK], 2)
        self.assertEqual(CONST.DIR_INDEX_MAP[CONST.UP_DOWN], 1)
        self.assertEqual(CONST.DIR_INDEX_MAP[CONST.LEFT_RIGHT], 0)

    def test_subdir_map(self):
        """测试子方向映射"""
        from utils.const import CONST
        
        front_back = CONST.SUBDIR_MAP[CONST.FRONT_BACK]
        self.assertIn(CONST.FRONT, front_back)
        self.assertIn(CONST.BACK, front_back)

    def test_decimal_precision_constant(self):
        """测试小数精度常量"""
        from utils.const import DECIMAL_PRECISION
        
        self.assertEqual(DECIMAL_PRECISION, 4)

    def test_value_limits(self):
        """测试数值限制常量"""
        from utils.const import MAX_VALUE, MIN_VALUE
        
        self.assertEqual(MAX_VALUE, 1000000)
        self.assertEqual(MIN_VALUE, -1000000)


if __name__ == '__main__':
    unittest.main()
