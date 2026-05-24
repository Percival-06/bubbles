import pygame
from settings import *

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        
        # 核心属性
        self.mass = 10.0          # 质量
        self.volume = 10.0        # 体积（独立属性）
        self.energy = 100.0       # 生命种子能量
        self.contamination = 0.0  # 污染值 0~100
        
        # 视觉半径由体积计算
        self.radius = self._calc_radius()

    def _calc_radius(self):
        """根据体积计算绘制半径，保持视觉与体积关联"""
        return int(VOLUME_TO_RADIUS * (self.volume ** (1/3)))

    def get_density(self):
        if self.volume <= 0:
            return float('inf')
        return self.mass / self.volume

    def absorb(self, amount=2.0):
        """吸收小泡泡：体积增加，质量不变 → 密度减小 → 上浮"""
        self.volume += amount
        self.radius = self._calc_radius()

    def release(self, amount=2.0):
        """分体：体积减少，质量不变 → 密度增大 → 下沉"""
        if self.volume > amount + 2.0:   # 保证最小体积
            self.volume -= amount
            self.radius = self._calc_radius()
            return True
        return False

    def collect_energy(self, amount):
        """收集能量种子：增加质量（也会影响密度），同时恢复能量"""
        self.mass += amount * 0.1
        self.energy = min(MAX_ENERGY, self.energy + amount * 10)

    def update(self, dt, level):
        # 1. 水平移动（帧率无关）
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -200
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = 200

        # 2. 垂直移动：根据密度相对于水的密度决定浮力方向
        density = self.get_density()
        buoyancy = BUOYANCY_ACCEL * (WATER_DENSITY - density)  # 密度>水 → 负 → 下沉
        self.vy += buoyancy * dt

        # 3. 水阻力（模拟缓和运动）
        self.vy *= DRAG_COEFF

        # 4. 更新位置（dt 已乘）
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 5. 简单边界碰撞（保留，后续需要替换为关卡碰撞）
        margin = self.radius
        self.x = max(margin, min(SCREEN_WIDTH - margin, self.x))
        self.y = max(margin, min(SCREEN_HEIGHT - margin, self.y))

        # 6. 能量自然消耗（暂时）
        self.energy -= 2 * dt
        if self.energy < 0:
            self.energy = 0

        # 7. 污染影响能量消耗（后期扩展）

    def handle_event(self, event):
        """处理按键事件：释放小泡泡（按 X）"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:   # 按 X 释放一部分体积
                # 如果释放成功，可以在关卡中生成一个小泡泡（由 level 处理）
                return self.release()
        return False

    def draw(self, screen):
        # 内部光晕（能量强度）
        inner_alpha = int(150 + self.energy / MAX_ENERGY * 105)  # 150~255
        inner_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(inner_surf, (255, 255, 200, inner_alpha),
                           (self.radius, self.radius), int(self.radius*0.7))
        screen.blit(inner_surf, (self.x - self.radius, self.y - self.radius))

        # 泡泡主体（半透明球体）
        outer_alpha = 180
        if self.contamination > 50:
            color = (150, 0, 150)   # 污染严重 → 紫色
        else:
            color = BUBBLE_COLOR
        bubble_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, (*color, outer_alpha),
                           (self.radius, self.radius), self.radius, 0)
        # 边框高光
        pygame.draw.circle(bubble_surf, (255, 255, 255, 100),
                           (self.radius, self.radius), self.radius, 2)
        screen.blit(bubble_surf, (self.x - self.radius, self.y - self.radius))