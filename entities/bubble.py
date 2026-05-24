import pygame
from settings import *
from core.physics import compute_vertical_velocity

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 20          # 体积的代表
        self.mass = 10            # 质量
        self.energy = 100         # 生命种子能量
        self.contamination = 0    # 污染值 (0-100)
        
    def get_volume(self):
        # 体积与半径的立方成正比（简化计算用半径直接表示体积感）
        return self.radius
    
    def get_density(self):
        if self.radius <= 0:
            return float('inf')
        return self.mass / self.get_volume()
    
    def absorb(self, amount=VOLUME_STEP):
        self.radius += amount
    
    def release(self, amount=VOLUME_STEP):
        if self.radius > amount + 5:
            self.radius -= amount
    
    def collect_energy(self, amount=MASS_STEP):
        self.mass += amount
    
    def update(self, dt, level):
        keys = pygame.key.get_pressed()
        # 水平移动
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -200
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = 200
        
        # 密度控制：按下 W 或 上箭头 → 释放质量/增大体积 → 密度减小 → 上浮
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.release(0.05)        # 暂时简化：释放小泡泡增大体积
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.absorb(0.05)         # 吸收小泡泡减小体积
        
        # 垂直移动由密度决定
        density = self.get_density()
        self.vy = compute_vertical_velocity(density) * 60  # 放大系数
        
        # 简单边界碰撞
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x - self.radius < 0:
            self.x = self.radius
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
        if self.y - self.radius < 0:
            self.y = self.radius
        if self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
        
        # 能量自然消耗（稍后添加）
        self.energy -= 1 * dt
    
    def handle_event(self, event):
        # 可扩展吸收/释放的按键（如空格、shift）
        pass
    
    def draw(self, screen):
        # 根据污染和能量改变颜色与透明度
        color = BUBBLE_COLOR
        if self.contamination > 50:
            color = (150, 0, 150)  # 紫色污染
        alpha = min(255, int(self.energy / 100 * 255))
        # Pygame 不支持直接 alpha，用表面绘制
        bubble_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, (*color, alpha), (self.radius, self.radius), self.radius)
        screen.blit(bubble_surf, (self.x - self.radius, self.y - self.radius))