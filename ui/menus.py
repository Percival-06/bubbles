import pygame
from settings import *
from core.save_manager import LEVEL_ORDER
from ui.background import RisingBubbleField, draw_ocean_background
from ui.stars import badge_star_count, draw_star_row
from world.level_parser import Level


def _draw_liquid_glass_rect(screen, rect, radius=16, hovered=False, disabled=False, panel=False):
    glow_pad = 18 if panel else 13
    layer = pygame.Surface((rect.width + glow_pad * 2, rect.height + glow_pad * 2), pygame.SRCALPHA)
    local = pygame.Rect(glow_pad, glow_pad, rect.width, rect.height)

    if disabled:
        glow = (185, 210, 225, 18)
        top = (246, 252, 255, 34)
        middle = (170, 202, 220, 38)
        bottom = (44, 72, 92, 82)
        rim = (230, 245, 255, 72)
        inner = (255, 255, 255, 28)
    elif hovered:
        glow = (150, 222, 255, 78)
        top = (255, 255, 255, 112)
        middle = (194, 238, 255, 66)
        bottom = (62, 160, 222, 82)
        rim = (255, 255, 255, 232)
        inner = (190, 238, 255, 120)
    else:
        glow = (130, 216, 255, 42)
        top = (255, 255, 255, 78)
        middle = (196, 236, 255, 48)
        bottom = (44, 130, 194, 70)
        rim = (246, 254, 255, 168)
        inner = (200, 238, 255, 72)

    pygame.draw.rect(layer, glow, local.inflate(24, 24), border_radius=radius + 12)
    pygame.draw.rect(layer, (255, 255, 255, 24 if hovered else 14), local.inflate(7, 7), 1, border_radius=radius + 4)

    clipped = rect.clip(screen.get_rect())
    if clipped.width and clipped.height:
        backdrop = screen.subsurface(clipped).copy()
        tiny_size = (max(1, clipped.width // 6), max(1, clipped.height // 6))
        backdrop = pygame.transform.smoothscale(backdrop, tiny_size)
        backdrop = pygame.transform.smoothscale(backdrop, clipped.size)
        backdrop.set_alpha(64 if hovered else 46)
        layer.blit(backdrop, (local.left + clipped.left - rect.left, local.top + clipped.top - rect.top))

    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        if t < 0.45:
            k = t / 0.45
            color = tuple(int(top[i] + (middle[i] - top[i]) * k) for i in range(4))
        else:
            k = (t - 0.45) / 0.55
            color = tuple(int(middle[i] + (bottom[i] - middle[i]) * k) for i in range(4))
        pygame.draw.rect(layer, color, pygame.Rect(local.left, local.top + y, local.width, 1))

    mask = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), local, border_radius=radius)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    shine_height = max(14, min(44, rect.height // 3))
    shine = pygame.Rect(local.left + 9, local.top + 6, local.width - 18, shine_height)
    pygame.draw.rect(layer, (255, 255, 255, 74 if hovered else 48), shine, border_radius=max(6, radius - 2))
    pygame.draw.line(layer, (255, 255, 255, 178 if hovered else 118), (local.left + 18, local.top + 7), (local.right - 18, local.top + 7), 1)
    pygame.draw.line(layer, (255, 255, 255, 92), (local.left + 12, local.top + 17), (local.left + 34, local.bottom - 12), 1)
    pygame.draw.line(layer, (255, 255, 255, 48 if hovered else 34), (local.right - 52, local.top + 10), (local.right - 18, local.bottom - 18), 1)
    pygame.draw.arc(layer, (255, 255, 255, 86 if hovered else 54), local.inflate(-10, -10), 3.55, 5.72, 2)
    pygame.draw.rect(layer, rim, local, 2, border_radius=radius)
    pygame.draw.rect(layer, inner, local.inflate(-7, -7), 1, border_radius=max(2, radius - 5))

    screen.blit(layer, (rect.x - glow_pad, rect.y - glow_pad))


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
        _draw_liquid_glass_rect(screen, rect, radius=14, hovered=hovered, disabled=disabled)

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
        super().__init__("Bubbles", [
            {"label": "Start", "action": "start"},
            {"label": "Continue", "action": "continue"},
            {"label": "Levels", "action": "levels"},
            {"label": "Settings", "action": "settings"},
            {"label": "Quit", "action": "quit"},
        ], start_y=200)

    def render(self, screen, subtitle=None, fill_background=True):
        draw_ocean_background(screen)
        self.bubble_field.draw(screen)
        super().render(screen, subtitle, fill_background=False)


class PauseMenu(ButtonMenu):
    def __init__(self):
        super().__init__("Paused", [
            {"label": "Resume", "action": "resume"},
            {"label": "Restart", "action": "restart"},
            {"label": "Levels", "action": "levels"},
            {"label": "Main Menu", "action": "menu"},
            {"label": "Quit", "action": "quit"},
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
        self.title = "Level Map"
        self.hover_index = 0
        self.nodes = []
        self.level_previews = {}
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
            lock = self.hint_font.render("LOCK", True, (60, 68, 72))
            screen.blit(lock, lock.get_rect(center=(x, y + 1)))

        label_y = y + 36 if y < SCREEN_HEIGHT - 105 else y - 42
        title = node["info"]["title"]
        label_color = (247, 253, 237) if unlocked else (178, 188, 194)
        shadow = self.hint_font.render(title, True, (6, 23, 38))
        label = self.hint_font.render(title, True, label_color)
        screen.blit(shadow, shadow.get_rect(center=(x + 1, label_y + 2)))
        screen.blit(label, label.get_rect(center=(x, label_y)))

        if node["badge"]:
            draw_star_row(
                screen,
                (x, label_y + 25),
                total=3,
                filled=badge_star_count(node["badge"]),
                radius=7,
                gap=2,
            )

    def _get_level_preview(self, level_id):
        if level_id not in self.level_previews:
            self.level_previews[level_id] = Level(level_id)
        return self.level_previews[level_id]

    def _wrap_text(self, text, font, max_width):
        lines = []
        current = ""
        for char in text:
            candidate = current + char
            if current and font.size(candidate)[0] > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines

    def _draw_glass_panel(self, screen, rect):
        _draw_liquid_glass_rect(screen, rect, radius=16, panel=True)

    def _draw_level_thumbnail(self, screen, rect, level):
        pygame.draw.rect(screen, (9, 38, 64, 128), rect, border_radius=10)
        pygame.draw.rect(screen, (213, 242, 252, 98), rect, 1, border_radius=10)

        inset = 8
        map_rect = rect.inflate(-inset * 2, -inset * 2)

        def scale_point(x, y):
            return (
                int(map_rect.left + x / SCREEN_WIDTH * map_rect.width),
                int(map_rect.top + y / SCREEN_HEIGHT * map_rect.height),
            )

        for hazard in level.hazards:
            x, y = scale_point(hazard[0], hazard[1])
            w = max(2, int(hazard[2] / SCREEN_WIDTH * map_rect.width))
            h = max(2, int(hazard[3] / SCREEN_HEIGHT * map_rect.height))
            pygame.draw.rect(screen, (176, 58, 72, 170), pygame.Rect(x, y, w, h), border_radius=3)

        for platform in level.platforms:
            x, y = scale_point(platform[0], platform[1])
            w = max(3, int(platform[2] / SCREEN_WIDTH * map_rect.width))
            h = max(2, int(platform[3] / SCREEN_HEIGHT * map_rect.height))
            pygame.draw.rect(screen, (190, 226, 216, 210), pygame.Rect(x, y, w, h), border_radius=3)

        for collectible in level.collectibles:
            x, y = scale_point(collectible[0], collectible[1])
            if collectible[2] == "energy":
                pygame.draw.circle(screen, (255, 224, 86), (x, y), 3)
            elif collectible[2] == "bubble":
                pygame.draw.circle(screen, (142, 223, 255), (x, y), 3, 1)

        start = scale_point(*level.start_pos)
        end = scale_point(*level.end_pos)
        pygame.draw.circle(screen, (105, 230, 164), start, 5)
        pygame.draw.circle(screen, (255, 204, 96), end, 5)
        pygame.draw.circle(screen, (255, 255, 255), end, 5, 1)

    def _detail_card_rect(self, node):
        width = 346
        height = 146
        margin = 24
        x = node["pos"][0] + 44
        y = node["pos"][1] - height // 2
        x = max(margin, min(x, SCREEN_WIDTH - width - margin))
        y = max(112, min(y, SCREEN_HEIGHT - height - 92))
        return pygame.Rect(x, y, width, height)

    def _draw_level_detail_card(self, screen, node):
        rect = self._detail_card_rect(node)
        self._draw_glass_panel(screen, rect)

        level = self._get_level_preview(node["info"]["id"])
        thumb_rect = pygame.Rect(rect.left + 16, rect.top + 18, 124, rect.height - 36)
        self._draw_level_thumbnail(screen, thumb_rect, level)

        text_x = thumb_rect.right + 18
        text_width = rect.right - text_x - 16
        title_color = (255, 252, 226) if node["unlocked"] else (184, 194, 202)
        title_shadow = self.small_font.render(node["info"]["title"], True, (4, 21, 38))
        title = self.small_font.render(node["info"]["title"], True, title_color)
        screen.blit(title_shadow, (text_x + 1, rect.top + 21))
        screen.blit(title, (text_x, rect.top + 19))
        draw_star_row(
            screen,
            (rect.right - 55, rect.top + 32),
            total=3,
            filled=badge_star_count(node["badge"]),
            radius=8,
            gap=3,
        )

        description = node["info"]["description"] if node["unlocked"] else "Complete the previous level to unlock"
        lines = self._wrap_text(description, self.hint_font, text_width)
        line_y = rect.top + 58
        for line in lines[:4]:
            shadow = self.hint_font.render(line, True, (4, 21, 38))
            text = self.hint_font.render(line, True, (226, 244, 248))
            screen.blit(shadow, (text_x + 1, line_y + 1))
            screen.blit(text, (text_x, line_y))
            line_y += 23

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
            self._draw_level_detail_card(screen, selected)

        self._draw_glass_button(screen, self.back_rect, hovered=False)
        back = self.hint_font.render("Back", True, (238, 250, 255))
        screen.blit(back, back.get_rect(center=self.back_rect.center))


class SettingsMenu(ButtonMenu):
    def __init__(self, save_manager):
        self.save_manager = save_manager
        super().__init__("Settings", [], start_y=230)
        self.refresh()

    def refresh(self, return_scene="menu"):
        settings = self.save_manager.data["settings"]
        options = [
            {"label": f"Music: {'On' if settings['music'] else 'Off'}", "action": ("toggle", "music")},
            {"label": f"SFX: {'On' if settings['sfx'] else 'Off'}", "action": ("toggle", "sfx")},
        ]
        if return_scene == "game":
            options.append({"label": "Back to Game", "action": "back"})
            options.append({"label": "Main Menu", "action": "menu"})
        else:
            options.append({"label": "Main Menu", "action": "back"})
        self.set_options(options)


class ResultMenu(ButtonMenu):
    def __init__(self):
        self.result = None
        super().__init__("Results", [], start_y=250)

    def set_result(self, result):
        self.result = result
        if result["success"]:
            options = []
            if result.get("next_level"):
                options.append({"label": "Next Level", "action": "next"})
            options.extend([
                {"label": "Retry", "action": "retry"},
                {"label": "Levels", "action": "levels"},
                {"label": "Main Menu", "action": "menu"},
            ])
            self.title = "Delivery Complete"
        else:
            self.title = "Delivery Failed"
            options = [
                {"label": "Retry", "action": "retry"},
                {"label": "Levels", "action": "levels"},
                {"label": "Main Menu", "action": "menu"},
            ]
        self.set_options(options)

    def render(self, screen):
        subtitle = None
        if self.result:
            if self.result["success"]:
                subtitle = f"Energy Seeds: {self.result['energy_collected']}/{self.result['energy_total']}"
            else:
                subtitle = self.result["reason"]
        super().render(screen, subtitle)
        if self.result and self.result["success"]:
            draw_star_row(
                screen,
                (SCREEN_WIDTH // 2, 180),
                total=3,
                filled=badge_star_count(self.result["badge"]),
                radius=16,
                gap=8,
            )
