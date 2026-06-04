import pygame
from settings import *
from ui.background import draw_ocean_background
from ui.bubble_sprite import draw_photo_bubble
from ui.energy_sprite import draw_energy_seed
from ui.stars import draw_star_row

class Renderer:
    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else pygame.font.Font(None, 22)
        self.settings_button_rect = pygame.Rect(SCREEN_WIDTH - 58, 14, 42, 42)
        self._animated_level = None
        self._animated_energy = 0
        self._star_animations = {}
        self._pollution_flash_until = 0

    def reset_level_stars(self, level):
        self._animated_level = getattr(level, "name", None)
        self._animated_energy = getattr(level, "collected_energy", 0)
        self._star_animations = {}

    def trigger_energy_collection(self, level, count=1):
        if self._animated_level != getattr(level, "name", None):
            self.reset_level_stars(level)
        now = pygame.time.get_ticks()
        previous = max(0, level.collected_energy - count)
        for index in range(previous, level.collected_energy):
            self._star_animations[index] = now + (index - previous) * 100
        self._animated_energy = level.collected_energy

    def trigger_pollution_warning(self):
        self._pollution_flash_until = pygame.time.get_ticks() + 450

    def render(self, screen, player, level):
        if self._animated_level != getattr(level, "name", None):
            self.reset_level_stars(level)

        draw_ocean_background(screen)

        # 绘制障碍物
        for plat in level.platforms:
            pygame.draw.rect(screen, (70, 82, 94), plat, border_radius=4)
            pygame.draw.rect(screen, (120, 140, 150), plat, 1, border_radius=4)

        # 绘制收集物（能量种子 和 小泡泡）
        for col in level.collectibles:
            x, y, typ = col
            if typ == "energy":
                draw_energy_seed(screen, (x, y), COLLECTIBLE_RADIUS)
            elif typ == "bubble":
                draw_photo_bubble(screen, (x, y), COLLECTIBLE_RADIUS, alpha=225)

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
        self._draw_settings_button(screen)

    def is_settings_button_hit(self, pos):
        rect = getattr(self, "settings_button_rect", pygame.Rect(SCREEN_WIDTH - 58, 14, 42, 42))
        return rect.collidepoint(pos)

    def _render_hud(self, screen, player, level):
        title = self.font.render(level.title, True, TEXT_COLOR)
        screen.blit(title, (12, 10))

        self._draw_bar(screen, 12, 45, 170, 10, player.energy / MAX_ENERGY,
                       (255, 225, 90), "Energy")
        self._draw_bar(screen, 12, 75, 170, 10, player.contamination / POLLUTION_LIMIT,
                       (185, 65, 210), "Pollution")

        density_text = self.small_font.render(
            f"Density {player.get_density():.2f}  Seeds {level.collected_energy}/{level.total_energy}",
            True,
            (220, 235, 245),
        )
        screen.blit(density_text, (12, 100))
        if pygame.time.get_ticks() < getattr(self, "_pollution_flash_until", 0):
            warning = self.small_font.render("Pollution contact! Energy drains faster", True, (255, 188, 255))
            screen.blit(warning, (12, 128))
        self._draw_level_stars(screen, level)

    def _draw_level_stars(self, screen, level):
        total = max(1, level.total_energy)
        now = pygame.time.get_ticks()
        highlight_index = None
        highlight_progress = 0.0
        expired = []
        for index, start_time in self._star_animations.items():
            elapsed = now - start_time
            if elapsed < 0:
                continue
            progress = elapsed / 650
            if progress >= 1:
                expired.append(index)
            elif highlight_index is None or progress > highlight_progress:
                highlight_index = index
                highlight_progress = progress
        for index in expired:
            self._star_animations.pop(index, None)

        draw_star_row(
            screen,
            (SCREEN_WIDTH // 2, 31),
            total=total,
            filled=level.collected_energy,
            radius=13,
            gap=8,
            highlight_index=highlight_index,
            highlight_progress=highlight_progress,
        )

    def _draw_settings_button(self, screen):
        rect = self.settings_button_rect
        layer = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
        local = pygame.Rect(8, 8, rect.width, rect.height)
        pygame.draw.ellipse(layer, (100, 205, 255, 42), local.inflate(12, 12))
        pygame.draw.ellipse(layer, (70, 168, 225, 118), local)
        pygame.draw.ellipse(layer, (235, 252, 255, 188), local, 2)
        pygame.draw.arc(layer, (255, 255, 255, 126), local.inflate(-7, -7), 3.4, 5.9, 2)

        gear_center = pygame.Vector2(local.centerx, local.centery)
        tooth_color = (246, 254, 255, 232)
        for angle in range(0, 360, 45):
            vector = pygame.Vector2(0, -1).rotate(angle)
            start = tuple(int(value) for value in gear_center + vector * 10)
            end = tuple(int(value) for value in gear_center + vector * 14)
            pygame.draw.line(layer, tooth_color, start, end, 3)
        pygame.draw.circle(layer, tooth_color, tuple(int(value) for value in gear_center), 10, 2)
        pygame.draw.circle(layer, tooth_color, tuple(int(value) for value in gear_center), 3)
        screen.blit(layer, (rect.x - 8, rect.y - 8))

    def _draw_bar(self, screen, x, y, w, h, ratio, color, label):
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(screen, (30, 45, 60), (x, y, w, h), border_radius=4)
        pygame.draw.rect(screen, color, (x, y, int(w * ratio), h), border_radius=4)
        text = self.small_font.render(label, True, (220, 235, 245))
        screen.blit(text, (x + w + 8, y - 7))
