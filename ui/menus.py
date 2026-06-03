import pygame
from settings import *
from world.level_parser import Level


class ButtonMenu:
    def __init__(self, title, options, start_y=None):
        self.font = pygame.font.Font(FONT_PATH, 46) if FONT_PATH else pygame.font.Font(None, 46)
        self.small_font = pygame.font.Font(FONT_PATH, 30) if FONT_PATH else pygame.font.Font(None, 30)
        self.hint_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else pygame.font.Font(None, 22)
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

    def render(self, screen, subtitle=None, fill_background=True):
        if fill_background:
            screen.fill((16, 36, 66))
        title_text = self.font.render(self.title, True, (255, 255, 210))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 105)))

        if subtitle:
            subtitle_surf = self.hint_font.render(subtitle, True, (200, 225, 245))
            screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 145)))

        for i, option in enumerate(self.options):
            rect = self.buttons[i]
            disabled = option.get("disabled", False)
            if disabled:
                color = (48, 58, 74)
                text_color = (145, 150, 160)
            elif i == self.hover_index:
                color = (95, 170, 235)
                text_color = (255, 255, 255)
            else:
                color = (42, 112, 182)
                text_color = (245, 250, 255)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, (225, 240, 255), rect, 2, border_radius=8)
            label = option["label"]
            text_surf = self.small_font.render(label, True, text_color)
            screen.blit(text_surf, text_surf.get_rect(center=rect.center))


class MainMenu(ButtonMenu):
    def __init__(self):
        super().__init__("泡泡上升", [
            {"label": "开始游戏", "action": "start"},
            {"label": "继续游戏", "action": "continue"},
            {"label": "关卡目录", "action": "levels"},
            {"label": "设置", "action": "settings"},
            {"label": "退出", "action": "quit"},
        ], start_y=200)


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

    def refresh(self):
        settings = self.save_manager.data["settings"]
        self.set_options([
            {"label": f"背景音乐：{'开' if settings['music'] else '关'}", "action": ("toggle", "music")},
            {"label": f"音效：{'开' if settings['sfx'] else '关'}", "action": ("toggle", "sfx")},
            {"label": "返回主菜单", "action": "back"},
        ])


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
