"""
设计器所需的常量
"""


class CONST:
    """
    通用常量
    """
    # 具体方位
    FRONT = "front"
    BACK = "back"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    SAME = "same"

    FRONT_NORMAL: tuple = (0., 0., 1.)
    BACK_NORMAL: tuple = (0., 0., -1.)
    LEFT_NORMAL: tuple = (-1., 0., 0.)
    RIGHT_NORMAL: tuple = (1., 0., 0.)
    UP_NORMAL: tuple = (0., 1., 0.)
    DOWN_NORMAL: tuple = (0., -1., 0.)

    # 方位组合
    FRONT_BACK = "front_back"
    UP_DOWN = "up_down"
    LEFT_RIGHT = "left_right"

    # 八个卦限
    FRONT_UP_LEFT = "front_up_left"
    FRONT_UP_RIGHT = "front_up_right"
    FRONT_DOWN_LEFT = "front_down_left"
    FRONT_DOWN_RIGHT = "front_down_right"
    BACK_UP_LEFT = "back_up_left"
    BACK_UP_RIGHT = "back_up_right"
    BACK_DOWN_LEFT = "back_down_left"
    BACK_DOWN_RIGHT = "back_down_right"

    DIR_INDEX_MAP = {FRONT_BACK: 2, UP_DOWN: 1, LEFT_RIGHT: 0}
    SUBDIR_MAP = {FRONT_BACK: (FRONT, BACK), UP_DOWN: (UP, DOWN), LEFT_RIGHT: (LEFT, RIGHT)}
    DIR_OPPOSITE_MAP = {FRONT: BACK, BACK: FRONT, UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT, SAME: SAME}
    VERTICAL_DIR_MAP = {
        FRONT: (UP, DOWN, LEFT, RIGHT), BACK: (UP, DOWN, LEFT, RIGHT), FRONT_BACK: (UP, DOWN, LEFT, RIGHT),
        UP: (FRONT, BACK, LEFT, RIGHT), DOWN: (FRONT, BACK, LEFT, RIGHT), UP_DOWN: (FRONT, BACK, LEFT, RIGHT),
        LEFT: (FRONT, BACK, UP, DOWN), RIGHT: (FRONT, BACK, UP, DOWN), LEFT_RIGHT: (FRONT, BACK, UP, DOWN)}
    VERTICAL_RAWDIR_MAP = {
        FRONT: (UP_DOWN, LEFT_RIGHT), BACK: (UP_DOWN, LEFT_RIGHT), FRONT_BACK: (UP_DOWN, LEFT_RIGHT),
        UP: (FRONT_BACK, LEFT_RIGHT), DOWN: (FRONT_BACK, LEFT_RIGHT), UP_DOWN: (FRONT_BACK, LEFT_RIGHT),
        LEFT: (FRONT_BACK, UP_DOWN), RIGHT: (FRONT_BACK, UP_DOWN), LEFT_RIGHT: (FRONT_BACK, UP_DOWN)}
    DIR_TO_RAWDIR_MAP = {
        FRONT: FRONT_BACK, BACK: FRONT_BACK, UP: UP_DOWN, DOWN: UP_DOWN, LEFT: LEFT_RIGHT, RIGHT: LEFT_RIGHT}
    # 旋转顺序
    XYZ = 'XYZ'
    XZY = 'XZY'
    YXZ = 'YXZ'
    YZX = 'YZX'
    ZXY = 'ZXY'
    ZYX = 'ZYX'
    __orders = [XYZ, XZY, YXZ, YZX, ZXY, ZYX]

    ROTATE_ORDER = __orders[2]

    VECTOR_RELATION_MAP = {
        (0., 0., 1.): {"Larger": FRONT, "Smaller": BACK},
        (0., 0., -1.): {"Larger": BACK, "Smaller": FRONT},
        (1., 0., 0.): {"Larger": LEFT, "Smaller": RIGHT},
        (-1., 0., 0.): {"Larger": RIGHT, "Smaller": LEFT},
        (0., 1., 0.): {"Larger": UP, "Smaller": DOWN},
        (0., -1., 0.): {"Larger": DOWN, "Smaller": UP},
    }


"""
设计器配置常量
"""
DECIMAL_PRECISION = 4
MAX_VALUE = 1000000
MIN_VALUE = -1000000
