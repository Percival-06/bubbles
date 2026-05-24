SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 物理参数
BASE_DENSITY = 1.0          # 水的密度
BUOYANCY_FORCE = 0.5        # 密度差产生的加速度系数
VOLUME_INCREMENT = 2.0      # 每次吸收/释放的体积变化量
MASS_INCREMENT = 0.5        # 收集能量种子的质量增加

# 颜色
WATER_COLOR = (10, 30, 60)
BUBBLE_COLOR = (200, 240, 255)
MENU_BG = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

# 其余参数
WATER_DENSITY = 1.0        # 水的参考密度
BUOYANCY_ACCEL = 300       # 浮力加速度（像素/秒²）
DRAG_COEFF = 0.95          # 水阻力系数（每帧）
VOLUME_TO_RADIUS = 0.5     # 体积→半径缩放因子（便于视觉）
BASE_RADIUS = 30
MAX_ENERGY = 100
ENERGY_GAIN = 20.0         # 收集一个能量种子的能量回复

# 关卡参数
COLLECTIBLE_RADIUS = 12
ENERGY_COLOR = (255, 220, 50)       # 能量种子：金色
BUBBLE_SMALL_COLOR = (150, 200, 255) # 小泡泡：浅蓝

# 字体设置
import os
# 尝试加载系统自带的中文字体（按优先级排列）
_FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",    # 黑体
    "C:/Windows/Fonts/simsun.ttc",    # 宋体
    "C:/Windows/Fonts/Deng.ttf",      # 等线
    "C:/Windows/Fonts/msyhbd.ttc",    # 微软雅黑加粗
]
FONT_PATH = None
for _f in _FONT_CANDIDATES:
    if os.path.exists(_f):
        FONT_PATH = _f
        break
