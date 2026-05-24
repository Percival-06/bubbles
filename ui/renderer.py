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

        # 绘制收集物（能量种子 和 小泡泡）
        for col in level.collectibles:
            x, y, typ = col
            if typ == "energy":
                # 金色能量球，带发光效果
                pygame.draw.circle(screen, ENERGY_COLOR, (int(x), int(y)), COLLECTIBLE_RADIUS)
                pygame.draw.circle(screen, (255, 255, 200), (int(x)-2, int(y)-2), COLLECTIBLE_RADIUS//2, 1)
            elif typ == "bubble":
                # 浅蓝小泡泡
                pygame.draw.circle(screen, BUBBLE_SMALL_COLOR, (int(x), int(y)), COLLECTIBLE_RADIUS)
                pygame.draw.circle(screen, (255, 255, 255), (int(x)-2, int(y)-2), COLLECTIBLE_RADIUS//2, 1)

        # 绘制危险区
        for haz in level.hazards:
            pygame.draw.rect(screen, (80, 0, 80), haz)

        # 绘制终点
        ex, ey = level.end_pos
        pygame.draw.rect(screen, (255, 255, 0), (ex-20, ey-10, 40, 20))

        # 绘制玩家
        player.draw(screen)

        # 极简 HUD：显示泡泡的能量文字
        energy_text = self.font.render(f"Energy: {int(player.energy)}", True, TEXT_COLOR)
        screen.blit(energy_text, (10, 10))