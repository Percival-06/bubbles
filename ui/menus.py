import pygame
from settings import *
from ui.background import RisingBubbleField, draw_ocean_background
from world.level_parser import Level


class ButtonMenu:
    def __init__(self, title, options, start_y=None):
        self.font = pygame.font.Font(MENU_TITLE_FONT_PATH, 48) if MENU_TITLE_FONT_PATH else pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(MENU_TEXT_FONT_PATH, 30) if MENU_TEXT_FONT_PATH else pygame.font.Font(None, 30)
        self.hint_font = pygame.font.Font(MENU_TEXT_FONT_PATH, 22) if MENU_TEXT_FONT_PATH else pygame.font.Font(None, 22)
        self.title = title
        self.options = options
        self.hover_index = 0
        self.buttons = []
        self.start_y = start_y if start_y is not None else SCREEN_HEIGHT // 2 - 120
        self._layout_buttons()

    def _layout_buttons(self):
        btn_width = 310
        btn_height = 48
        gap = 58
        start_x = (SCREEN_WIDTH - btn_width) // 2
        self.buttons = []
        for i, option in enumerate(self.options):
            rect = pygame.Rect(start_x, self.start_y + i * gap, btn_width, btn_height)
            self.buttons.append(rect)

    def set_options(self, options):
        self.options = options
        self.hover_index = min(self.hover_index, max(0, len(options) - 1))
        self._layout_buttons()

    def _get_hover(self, pos):
        for i, rect in enumerate(self.buttons):
            if rect.collidepoint(pos):
                return i
        return None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            hovered = self._get_hover(event.pos)
            if hovered is not None:
                self.hover_index = hovered
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            index = self._get_hover(event.pos)
            if index is not None and not self.options[index].get("disabled", False):
                return self.options[index]["action"]
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_hover(1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._move_hover(-1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                option = self.options[self.hover_index]
                if not option.get("disabled", False):
                    return option["action"]
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def _move_hover(self, direction):
        if not self.options:
            return
        for _ in self.options:
            self.hover_index = (self.hover_index + direction) % len(self.options)
            if not self.options[self.hover_index].get("disabled", False):
                break

    def _draw_glass_button(self, screen, rect, hovered=False, disabled=False):
        radius = 14
        glow_pad = 12
        layer = pygame.Surface((rect.width + glow_pad * 2, rect.height + glow_pad * 2), pygame.SRCALPHA)
        local = pygame.Rect(glow_pad, glow_pad, rect.width, rect.height)

        if disabled:
            base_top = (115, 135, 154, 62)
            base_bottom = (35, 52, 68, 108)
            border = (185, 205, 222, 78)
            highlight = (245, 252, 255, 55)
        elif hovered:
            pygame.draw.rect(layer, (110, 205, 255, 46), local.inflate(16, 16), border_radius=radius + 8)
            base_top = (180, 232, 255, 104)
            base_bottom = (28, 124, 188, 150)
            border = (238, 252, 255, 226)
            highlight = (255, 255, 255, 150)
        else:
            base_top = (142, 218, 250, 74)
            base_bottom = (22, 92, 160, 126)
            border = (218, 244, 255, 152)
            highlight = (255, 255, 255, 100)

        for y in range(rect.height):
            t = y / max(1, rect.height - 1)
            color = tuple(int(base_top[i] + (base_bottom[i] - base_top[i]) * t) for i in range(4))
            line = pygame.Rect(local.left, local.top + y, local.width, 1)
            pygame.draw.rect(layer, color, line)

        mask = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), local, border_radius=radius)
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        shine = pygame.Rect(local.left + 10, local.top + 6, local.width - 20, max(8, local.height // 3))
        pygame.draw.rect(layer, highlight, shine, border_radius=radius)
        pygame.draw.line(layer, (255, 255, 255, 86), (local.left + 18, local.top + 7), (local.right - 18, local.top + 7), 1)
        pygame.draw.rect(layer, border, local, 2, border_radius=radius)
        pygame.draw.rect(layer, (255, 255, 255, 52), local.inflate(-7, -7), 1, border_radius=radius - 4)

        screen.blit(layer, (rect.x - glow_pad, rect.y - glow_pad))

    def render(self, screen, subtitle=None, fill_background=True):
        if fill_background:
            draw_ocean_background(screen)
        title_shadow = self.font.render(self.title, True, (4, 22, 42))
        screen.blit(title_shadow, title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 107)))
        title_text = self.font.render(self.title, True, (246, 254, 232))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 105)))

        if subtitle:
            subtitle_surf = self.hint_font.render(subtitle, True, (200, 225, 245))
            screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 145)))

        for i, option in enumerate(self.options):
            rect = self.buttons[i]
            disabled = option.get("disabled", False)
            if disabled:
                text_color = (145, 150, 160)
            elif i == self.hover_index:
                text_color = (255, 255, 255)
            else:
                text_color = (238, 250, 255)
            self._draw_glass_button(screen, rect, hovered=i == self.hover_index, disabled=disabled)
            label = option["label"]
            text_shadow = self.small_font.render(label, True, (8, 32, 54))
            screen.blit(text_shadow, text_shadow.get_rect(center=(rect.centerx + 1, rect.centery + 2)))
            text_surf = self.small_font.render(label, True, text_color)
            screen.blit(text_surf, text_surf.get_rect(center=rect.center))


class MainMenu(ButtonMenu):
    def __init__(self):
        self.bubble_field = RisingBubbleField()
        super().__init__("泡泡上升", [
            {"label": "开始游戏", "action": "start"},
            {"label": "继续游戏", "action": "continue"},
            {"label": "关卡目录", "action": "levels"},
            {"label": "设置", "action": "settings"},
            {"label": "退出", "action": "quit"},
        ], start_y=200)

    def render(self, screen, subtitle=None, fill_background=True):
        draw_ocean_background(screen)
        self.bubble_field.draw(screen)
        super().render(screen, subtitle, fill_background=False)


class PauseMenu(ButtonMenu):
    def __init__(self):
        super().__init__("暂停", [
            {"label": "继续游戏", "action": "resume"},
            {"label": "重新开始", "action": "restart"},
            {"label": "关卡目录", "action": "levels"},
            {"label": "返回主菜单", "action": "menu"},
            {"label": "退出游戏", "action": "quit"},
        ], start_y=190)

    def handle_event(self, event):
        result = super().handle_event(event)
        if result == "back":
            return "resume"
        return result

    def render(self, screen):
        mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        mask.set_alpha(150)
        mask.fill((0, 0, 0))
        screen.blit(mask, (0, 0))
        super().render(screen, fill_background=False)


class LevelSelectMenu(ButtonMenu):
    def __init__(self, save_manager):
        self.save_manager = save_manager
        super().__init__("关卡目录", [], start_y=190)
        self.refresh()

    def refresh(self):
        options = []
        for info in Level.catalog():
            unlocked = self.save_manager.is_unlocked(info["id"])
            badge = self.save_manager.data["best_badges"].get(info["id"])
            suffix = f"  [{badge}]" if badge else ""
            locked_suffix = "" if unlocked else "  [未解锁]"
            options.append({
                "label": info["title"] + suffix + locked_suffix,
                "action": ("level", info["id"]),
                "disabled": not unlocked,
            })
        options.append({"label": "返回主菜单", "action": "back"})
        self.set_options(options)


class SettingsMenu(ButtonMenu):
    def __init__(self, save_manager):
        self.save_manager = save_manager
        super().__init__("设置", [], start_y=230)
        self.refresh()

    def refresh(self, return_scene="menu"):
        settings = self.save_manager.data["settings"]
        options = [
            {"label": f"背景音乐：{'开' if settings['music'] else '关'}", "action": ("toggle", "music")},
            {"label": f"音效：{'开' if settings['sfx'] else '关'}", "action": ("toggle", "sfx")},
        ]
        if return_scene == "game":
            options.append({"label": "返回游戏", "action": "back"})
            options.append({"label": "返回主菜单", "action": "menu"})
        else:
            options.append({"label": "返回主菜单", "action": "back"})
        self.set_options(options)


class ResultMenu(ButtonMenu):
    def __init__(self):
        self.result = None
        super().__init__("结算", [], start_y=250)

    def set_result(self, result):
        self.result = result
        if result["success"]:
            options = []
            if result.get("next_level"):
                options.append({"label": "下一关", "action": "next"})
            options.extend([
                {"label": "重新挑战", "action": "retry"},
                {"label": "关卡目录", "action": "levels"},
                {"label": "返回主菜单", "action": "menu"},
            ])
            self.title = "运输成功"
        else:
            self.title = "运输失败"
            options = [
                {"label": "重新挑战", "action": "retry"},
                {"label": "关卡目录", "action": "levels"},
                {"label": "返回主菜单", "action": "menu"},
            ]
        self.set_options(options)

    def render(self, screen):
        subtitle = None
        if self.result:
            if self.result["success"]:
                subtitle = (
                    f"徽章：{self.result['badge']}  "
                    f"能量种子：{self.result['energy_collected']}/{self.result['energy_total']}"
                )
            else:
                subtitle = self.result["reason"]
        super().render(screen, subtitle)
