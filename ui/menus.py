import pygame
from settings import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        # 使用中文字体（如果可用）
        self.font = pygame.font.Font(FONT_PATH, 48) if FONT_PATH else pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(FONT_PATH, 36) if FONT_PATH else pygame.font.Font(None, 36)
        self.options = ["开始游戏", "退出"]
        self.buttons = []   # 每个按钮：Rect, text, normal_color, hover_color
        self.hover_index = None

        # 构建按钮位置
        btn_width = 250
        btn_height = 60
        start_x = (SCREEN_WIDTH - btn_width) // 2
        start_y = SCREEN_HEIGHT // 2 - btn_height
        gap = 90

        for i, text in enumerate(self.options):
            rect = pygame.Rect(start_x, start_y + i * gap, btn_width, btn_height)
            self.buttons.append({
                "rect": rect,
                "text": text,
                "color_normal": (50, 120, 200),
                "color_hover": (100, 180, 255),
                "color_text": (255, 255, 255)
            })

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover_index = self._get_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                index = self._get_hover(event.pos)
                if index == 0:
                    return "start"
                elif index == 1:
                    return "quit"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.hover_index is not None:
                    if self.hover_index == 0:
                        return "start"
                    elif self.hover_index == 1:
                        return "quit"
            elif event.key == pygame.K_DOWN:
                self.hover_index = (self.hover_index + 1) % 2 if self.hover_index is not None else 0
            elif event.key == pygame.K_UP:
                self.hover_index = (self.hover_index - 1) % 2 if self.hover_index is not None else 1
        return None

    def _get_hover(self, pos):
        for i, btn in enumerate(self.buttons):
            if btn["rect"].collidepoint(pos):
                return i
        return None

    def render(self, screen):
        screen.fill((20, 40, 70))  # 深海背景，可保留 WATER_COLOR 或其他
        # 标题
        title_text = self.font.render("泡泡上升", True, (255, 255, 200))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        screen.blit(title_text, title_rect)

        # 按钮
        for i, btn in enumerate(self.buttons):
            color = btn["color_hover"] if i == self.hover_index else btn["color_normal"]
            pygame.draw.rect(screen, color, btn["rect"], border_radius=12)
            pygame.draw.rect(screen, (255,255,255), btn["rect"], 3, border_radius=12)  # 边框
            text_surf = self.small_font.render(btn["text"], True, btn["color_text"])
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            screen.blit(text_surf, text_rect)

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(FONT_PATH, 48) if FONT_PATH else pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(FONT_PATH, 36) if FONT_PATH else pygame.font.Font(None, 36)
        self.options = ["继续游戏", "重新开始", "返回主菜单", "退出游戏"]
        self.buttons = []
        self.hover_index = None

        # 构建按钮位置
        btn_width = 250
        btn_height = 60
        start_x = (SCREEN_WIDTH - btn_width) // 2
        start_y = SCREEN_HEIGHT // 2 - btn_height
        gap = 90

        for i, text in enumerate(self.options):
            rect = pygame.Rect(start_x, start_y + i * gap, btn_width, btn_height)
            self.buttons.append({
                "rect": rect,
                "text": text,
                "color_normal": (50, 120, 200),
                "color_hover": (100, 180, 255),
                "color_text": (255, 255, 255)
            })

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover_index = self._get_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                index = self._get_hover(event.pos)
                if index == 0:
                    return "resume"
                elif index == 1:
                    return "restart"
                elif index == 2:
                    return "menu"
                elif index == 3:
                    return "quit"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume"
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.hover_index is not None:
                    if self.hover_index == 0:
                        return "resume"
                    elif self.hover_index == 1:
                        return "restart"
                    elif self.hover_index == 2:
                        return "menu"
                    elif self.hover_index == 3:
                        return "quit"
            elif event.key == pygame.K_DOWN:
                self.hover_index = (self.hover_index + 1) % 4 if self.hover_index is not None else 0
            elif event.key == pygame.K_UP:
                self.hover_index = (self.hover_index - 1) % 4 if self.hover_index is not None else 3
        return None

    def _get_hover(self, pos):
        for i, btn in enumerate(self.buttons):
            if btn["rect"].collidepoint(pos):
                return i
        return None

    def render(self, screen):
        # 半透明遮罩
        mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        mask.set_alpha(128)
        mask.fill((0, 0, 0))
        screen.blit(mask, (0, 0))

        # 暂停标题
        title_text = self.font.render("暂停", True, (255, 255, 200))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 - 30))
        screen.blit(title_text, title_rect)

        # 按钮
        for i, btn in enumerate(self.buttons):
            color = btn["color_hover"] if i == self.hover_index else btn["color_normal"]
            pygame.draw.rect(screen, color, btn["rect"], border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), btn["rect"], 3, border_radius=12)  # 边框
            text_surf = self.small_font.render(btn["text"], True, btn["color_text"])
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            screen.blit(text_surf, text_rect)
