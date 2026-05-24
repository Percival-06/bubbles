from settings import *

def compute_vertical_velocity(density, water_density=1.0):
    """根据密度差返回垂直速度（正为下，负为上）"""
    delta = density - water_density
    return delta * BUOYANCY_FORCE