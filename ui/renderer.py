import pygame
from settings import *

class Renderer:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
    
    def render(self, screen, player, level):
        screen.fill(WATER_COLOR)
        
        # 绘制障碍物
        for plat in level.platforms:
            pygame.draw.rect(screen, (100, 100, 100), plat)
        
        # 绘制收集物
        for col in level.collectibles:
            x, y, typ = col
            if typ == "energy":
                pygame.draw.circle(screen, (0, 255, 0), (x, y), 8)
        
        # 绘制危险区
        for haz in level.hazards:
            pygame.draw.rect(screen, (80, 0, 80), haz)
        
        # 绘制终点
        ex, ey = level.end_pos
        pygame.draw.rect(screen, (255, 255, 0), (ex-20, ey-10, 40, 20))
        
        # 绘制玩家
        player.draw(screen)
        
        # 极简 HUD：直接显示泡泡的能量文字（后续可改为视觉特效）
        energy_text = self.font.render(f"Energy: {int(player.energy)}", True, TEXT_COLOR)
        screen.blit(energy_text, (10, 10))