import pygame
from settings import *

class Renderer:
    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else pygame.font.Font(None, 22)

    def render(self, screen, player, level):
        screen.fill(WATER_COLOR)

        # 绘制障碍物
        for plat in level.platforms:
            pygame.draw.rect(screen, (70, 82, 94), plat, border_radius=4)
            pygame.draw.rect(screen, (120, 140, 150), plat, 1, border_radius=4)

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
            hazard_surf = pygame.Surface((haz[2], haz[3]), pygame.SRCALPHA)
            hazard_surf.fill((130, 0, 135, 120))
            screen.blit(hazard_surf, (haz[0], haz[1]))
            pygame.draw.rect(screen, (220, 60, 220), haz, 2)

        # 绘制终点
        ex, ey = level.end_pos
        pygame.draw.rect(screen, (245, 230, 80), (ex-28, ey-12, 56, 24), border_radius=6)
        pygame.draw.rect(screen, (255, 255, 210), (ex-28, ey-12, 56, 24), 2, border_radius=6)

        # 绘制玩家
        player.draw(screen)

        self._render_hud(screen, player, level)

    def _render_hud(self, screen, player, level):
        title = self.font.render(level.title, True, TEXT_COLOR)
        screen.blit(title, (12, 10))

        self._draw_bar(screen, 12, 45, 170, 10, player.energy / MAX_ENERGY,
                       (255, 225, 90), "生命能量")
        self._draw_bar(screen, 12, 75, 170, 10, player.contamination / POLLUTION_LIMIT,
                       (185, 65, 210), "污染")

        density_text = self.small_font.render(
            f"密度 {player.get_density():.2f}  能量种子 {level.collected_energy}/{level.total_energy}",
            True,
            (220, 235, 245),
        )
        screen.blit(density_text, (12, 100))

    def _draw_bar(self, screen, x, y, w, h, ratio, color, label):
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(screen, (30, 45, 60), (x, y, w, h), border_radius=4)
        pygame.draw.rect(screen, color, (x, y, int(w * ratio), h), border_radius=4)
        text = self.small_font.render(label, True, (220, 235, 245))
        screen.blit(text, (x + w + 8, y - 7))
