SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 物理参数
BASE_DENSITY = 1.0          # 水的密度
BUOYANCY_FORCE = 0.5        # 密度差产生的加速度系数
VOLUME_INCREMENT = 8.0      # 每次吸收/释放的体积变化量
MASS_INCREMENT = 2.5        # 收集能量种子的质量增加

# 颜色
WATER_COLOR = (10, 30, 60)
BUBBLE_COLOR = (200, 240, 255)
MENU_BG = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

# 其余参数
WATER_DENSITY = 1.0        # 水的参考密度
BUOYANCY_ACCEL = -1400     # 浮力加速度（屏幕坐标 y 向下为正，负值表示上浮）
DRAG_COEFF = 0.95          # 水阻力系数（每帧）
VOLUME_TO_RADIUS = 0.25    # 体积→半径缩放因子（便于视觉）
BASE_RADIUS = 28
MAX_ENERGY = 100
ENERGY_GAIN = 20.0         # 收集一个能量种子的能量回复
ENERGY_DRAIN = 2.0         # 每秒自然消耗
POLLUTION_LIMIT = 100.0
POLLUTION_RATE = 30.0      # 每秒污染增长
POLLUTION_ENERGY_DRAIN = 6.0
MIN_VOLUME = 14.0

# 关卡参数
COLLECTIBLE_RADIUS = 12
ENERGY_COLOR = (255, 220, 50)       # 能量种子：金色
BUBBLE_SMALL_COLOR = (150, 200, 255) # 小泡泡：浅蓝

# 字体设置
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 优先使用项目内置字体，避免不同操作系统缺少中文字体导致乱码/方块。
_PROJECT_FONT_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", "fonts", "NotoSansCJKsc-Regular.otf"),
    os.path.join(BASE_DIR, "assets", "fonts", "NotoSansSC-Regular.otf"),
    os.path.join(BASE_DIR, "assets", "fonts", "SourceHanSansSC-Regular.otf"),
]

_PROJECT_TITLE_FONT_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", "fonts", "NotoSansCJKsc-Bold.otf"),
    os.path.join(BASE_DIR, "assets", "fonts", "NotoSansSC-Bold.otf"),
    os.path.join(BASE_DIR, "assets", "fonts", "SourceHanSansSC-Bold.otf"),
]

# 系统字体仅作兜底，覆盖 Windows / macOS / 常见 Linux 发行版。
_SYSTEM_TEXT_FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/Deng.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]

_SYSTEM_TITLE_FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]


def _first_existing_font(candidates):
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


FONT_PATH = _first_existing_font(_PROJECT_FONT_CANDIDATES + _SYSTEM_TEXT_FONT_CANDIDATES)
MENU_TITLE_FONT_PATH = _first_existing_font(
    _PROJECT_TITLE_FONT_CANDIDATES + _PROJECT_FONT_CANDIDATES + _SYSTEM_TITLE_FONT_CANDIDATES
) or FONT_PATH
MENU_TEXT_FONT_PATH = FONT_PATH
