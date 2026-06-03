import pygame
from settings import *

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        
        # 核心属性
        self.mass = 36.0          # 质量
        self.volume = 42.0        # 体积（独立属性）
        self.energy = 100.0       # 生命种子能量
        self.contamination = 0.0  # 污染值 0~100
        
        # 视觉半径由体积计算
        self.radius = self._calc_radius()

    def _calc_radius(self):
        """根据体积计算绘制半径，保持视觉与体积关联"""
        return int(BASE_RADIUS + self.volume * VOLUME_TO_RADIUS)

    def get_density(self):
        if self.volume <= 0:
            return float('inf')
        return self.mass / self.volume

    def absorb(self, amount=VOLUME_INCREMENT):
        """吸收小泡泡：体积增加，质量不变 → 密度减小 → 上浮"""
        self.volume += amount
        self.radius = self._calc_radius()

    def release(self, amount=VOLUME_INCREMENT):
        """分体：体积减少，质量不变 → 密度增大 → 下沉"""
        if self.volume - amount >= MIN_VOLUME:
            self.volume -= amount
            self.radius = self._calc_radius()
            return True
        return False

    def collect_energy(self, amount):
        """收集能量种子：增加质量（也会影响密度），同时恢复能量"""
        self.mass += MASS_INCREMENT
        self.energy = min(MAX_ENERGY, self.energy + amount)

    def apply_pollution(self, dt):
        """污染区域会逐渐污染生命种子，并额外消耗能量。"""
        self.contamination = min(POLLUTION_LIMIT, self.contamination + POLLUTION_RATE * dt)
        self.energy = max(0, self.energy - POLLUTION_ENERGY_DRAIN * dt)

    def has_failed(self):
        return self.energy <= 0 or self.contamination >= POLLUTION_LIMIT

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
        buoyancy = BUOYANCY_ACCEL * (WATER_DENSITY - density)  # 密度<水 → 负 vy → 上浮
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
        self.energy -= ENERGY_DRAIN * dt
        if self.energy < 0:
            self.energy = 0

        # 7. 污染影响能量消耗（后期扩展）

    def handle_event(self, event):
        """预留玩家实体事件入口；释放小泡泡由场景统一处理，避免重复触发。"""
        return False

    def draw(self, screen):
        # 内部光晕（能量强度）
        inner_alpha = int(80 + self.energy / MAX_ENERGY * 175)  # 80~255
        inner_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(inner_surf, (255, 255, 200, inner_alpha),
                           (self.radius, self.radius), int(self.radius*0.7))
        screen.blit(inner_surf, (self.x - self.radius, self.y - self.radius))

        # 泡泡主体（半透明球体）
        outer_alpha = 180
        pollution_ratio = min(1.0, self.contamination / POLLUTION_LIMIT)
        color = (
            int(BUBBLE_COLOR[0] * (1 - pollution_ratio) + 150 * pollution_ratio),
            int(BUBBLE_COLOR[1] * (1 - pollution_ratio) + 20 * pollution_ratio),
            int(BUBBLE_COLOR[2] * (1 - pollution_ratio) + 170 * pollution_ratio),
        )
        bubble_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, (*color, outer_alpha),
                           (self.radius, self.radius), self.radius, 0)
        # 边框高光
        pygame.draw.circle(bubble_surf, (255, 255, 255, 100),
                           (self.radius, self.radius), self.radius, 2)
        screen.blit(bubble_surf, (self.x - self.radius, self.y - self.radius))
