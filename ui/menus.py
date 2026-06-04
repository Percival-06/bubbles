import pygame
from settings import *
from core.save_manager import LEVEL_ORDER
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
        self.font = pygame.font.Font(MENU_TITLE_FONT_PATH, 46) if MENU_TITLE_FONT_PATH else pygame.font.Font(None, 46)
        self.small_font = pygame.font.Font(MENU_TEXT_FONT_PATH, 24) if MENU_TEXT_FONT_PATH else pygame.font.Font(None, 24)
        self.hint_font = pygame.font.Font(MENU_TEXT_FONT_PATH, 20) if MENU_TEXT_FONT_PATH else pygame.font.Font(None, 20)
        self.title = "关卡海图"
        self.hover_index = 0
        self.nodes = []
        self.back_rect = pygame.Rect(SCREEN_WIDTH - 158, SCREEN_HEIGHT - 68, 118, 42)
        self.refresh()

    def refresh(self):
        catalog = Level.catalog()
        route = self._route_points(len(catalog))
        self.nodes = []
        for index, info in enumerate(catalog):
            unlocked = self.save_manager.is_unlocked(info["id"])
            self.nodes.append({
                "info": info,
                "pos": route[index],
                "rect": pygame.Rect(route[index][0] - 24, route[index][1] - 24, 48, 48),
                "unlocked": unlocked,
                "badge": self.save_manager.data["best_badges"].get(info["id"]),
            })

        self.hover_index = self._unlocked_index()

    def _route_points(self, count):
        anchors = [
            (112, 414),
            (282, 326),
            (476, 392),
            (642, 254),
            (706, 146),
        ]
        return anchors[:count]

    def _unlocked_index(self):
        unlocked_level = self.save_manager.data.get("unlocked_level", LEVEL_ORDER[0])
        if unlocked_level not in LEVEL_ORDER:
            return 0
        return min(LEVEL_ORDER.index(unlocked_level), len(self.nodes) - 1)

    def _get_hover_node(self, pos):
        for i, node in enumerate(self.nodes):
            if node["rect"].collidepoint(pos):
                return i
        return None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            hovered = self._get_hover_node(event.pos)
            self.hover_index = hovered
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_rect.collidepoint(event.pos):
                return "back"
            index = self._get_hover_node(event.pos)
            if index is not None and self.nodes[index]["unlocked"]:
                return ("level", self.nodes[index]["info"]["id"])
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d, pygame.K_s):
                self._move_hover(1)
            elif event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a, pygame.K_w):
                self._move_hover(-1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                index = self.hover_index if self.hover_index is not None else self._unlocked_index()
                node = self.nodes[index]
                if node["unlocked"]:
                    return ("level", node["info"]["id"])
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def _move_hover(self, direction):
        if not self.nodes:
            return
        index = self.hover_index if self.hover_index is not None else self._unlocked_index()
        for _ in self.nodes:
            index = (index + direction) % len(self.nodes)
            if self.nodes[index]["unlocked"]:
                self.hover_index = index
                break

    def _draw_map_background(self, screen):
        draw_ocean_background(screen)
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((17, 48, 74, 70))
        screen.blit(veil, (0, 0))

        compass_center = (82, 515)
        pygame.draw.circle(screen, (229, 214, 159), compass_center, 35, 2)
        pygame.draw.line(screen, (229, 214, 159), (compass_center[0], compass_center[1] - 42), (compass_center[0], compass_center[1] + 42), 2)
        pygame.draw.line(screen, (229, 214, 159), (compass_center[0] - 42, compass_center[1]), (compass_center[0] + 42, compass_center[1]), 2)

    def _draw_route_segment(self, screen, start, end, color):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        steps = max(1, int((dx * dx + dy * dy) ** 0.5 // 18))
        for step in range(steps + 1):
            t = step / steps
            x = int(start[0] + dx * t)
            y = int(start[1] + dy * t)
            pygame.draw.circle(screen, color, (x, y), 6)
            pygame.draw.circle(screen, (255, 255, 255), (x - 2, y - 2), 2)

    def _draw_routes(self, screen):
        unlocked_index = self._unlocked_index()
        for i in range(len(self.nodes) - 1):
            color = (224, 67, 55) if i < unlocked_index else (118, 130, 139)
            self._draw_route_segment(screen, self.nodes[i]["pos"], self.nodes[i + 1]["pos"], color)

    def _draw_node(self, screen, node, index):
        x, y = node["pos"]
        unlocked = node["unlocked"]
        hovered = self.hover_index is not None and index == self.hover_index
        newest = index == self._unlocked_index()
        completed = node["info"]["id"] in self.save_manager.data.get("completed_levels", [])

        if not unlocked:
            fill = (119, 126, 132)
            rim = (179, 187, 193)
        elif newest:
            fill = (255, 198, 80)
            rim = (255, 247, 207)
        elif completed:
            fill = (226, 72, 62)
            rim = (255, 220, 204)
        else:
            fill = (96, 201, 246)
            rim = (225, 250, 255)

        if hovered:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 19)
        pygame.draw.circle(screen, fill, (x, y), 16)
        pygame.draw.circle(screen, rim, (x, y), 16, 2)

        if not unlocked:
            lock = self.hint_font.render("锁", True, (60, 68, 72))
            screen.blit(lock, lock.get_rect(center=(x, y + 1)))

        label_y = y + 36 if y < SCREEN_HEIGHT - 105 else y - 42
        title = node["info"]["title"]
        label_color = (247, 253, 237) if unlocked else (178, 188, 194)
        shadow = self.hint_font.render(title, True, (6, 23, 38))
        label = self.hint_font.render(title, True, label_color)
        screen.blit(shadow, shadow.get_rect(center=(x + 1, label_y + 2)))
        screen.blit(label, label.get_rect(center=(x, label_y)))

        if node["badge"]:
            badge = self.hint_font.render(node["badge"], True, (255, 226, 104))
            screen.blit(badge, badge.get_rect(center=(x, label_y + 22)))

    def render(self, screen, subtitle=None, fill_background=True):
        self._draw_map_background(screen)
        title_shadow = self.font.render(self.title, True, (4, 22, 42))
        screen.blit(title_shadow, title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 64)))
        title_text = self.font.render(self.title, True, (246, 254, 232))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 62)))

        if subtitle:
            subtitle_surf = self.hint_font.render(subtitle, True, (213, 236, 242))
            screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 98)))

        self._draw_routes(screen)
        for index, node in enumerate(self.nodes):
            self._draw_node(screen, node, index)

        selected = self.nodes[self.hover_index] if self.nodes and self.hover_index is not None else None
        if selected:
            hint = selected["info"]["description"]
            if not selected["unlocked"]:
                hint = "完成前置关卡后解锁"
            hint_surf = self.small_font.render(hint, True, (232, 247, 250))
            screen.blit(hint_surf, hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70)))

        self._draw_glass_button(screen, self.back_rect, hovered=False)
        back = self.hint_font.render("返回", True, (238, 250, 255))
        screen.blit(back, back.get_rect(center=self.back_rect.center))


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
