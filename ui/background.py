import math
import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP_SEA_BACKGROUND = os.path.join(ROOT_DIR, "assets", "backgrounds", "main_menu_deep_sea.png")
SURFACE_COLOR = (37, 143, 174)
MID_WATER_COLOR = (13, 76, 116)
DEEP_WATER_COLOR = (4, 26, 56)
_background_source = None
_scaled_backgrounds = {}
_dynamic_layers = {}


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def _mix(c1, c2, t):
    return (
        _lerp(c1[0], c2[0], t),
        _lerp(c1[1], c2[1], t),
        _lerp(c1[2], c2[2], t),
    )


def _get_background_image(size):
    global _background_source
    if not os.path.exists(DEEP_SEA_BACKGROUND):
        return None

    if _background_source is None:
        _background_source = pygame.image.load(DEEP_SEA_BACKGROUND)

    if size not in _scaled_backgrounds:
        _scaled_backgrounds[size] = pygame.transform.smoothscale(_background_source, size)
    return _scaled_backgrounds[size]


def _get_dynamic_layer(name, size):
    key = (name, size)
    if key not in _dynamic_layers:
        _dynamic_layers[key] = pygame.Surface(size, pygame.SRCALPHA)
    layer = _dynamic_layers[key]
    layer.fill((0, 0, 0, 0))
    return layer


def _draw_generated_ocean(screen, elapsed):
    width, height = screen.get_size()
    horizon = int(height * 0.42)
    for y in range(height):
        depth = y / max(1, height - 1)
        if y < horizon:
            t = y / max(1, horizon)
            color = _mix(SURFACE_COLOR, MID_WATER_COLOR, t)
        else:
            t = (y - horizon) / max(1, height - horizon)
            color = _mix(MID_WATER_COLOR, DEEP_WATER_COLOR, t)
        screen.fill(color, (0, y, width, 1))


def draw_ocean_background(screen, elapsed=None):
    if elapsed is None:
        elapsed = pygame.time.get_ticks() / 1000.0

    width, height = screen.get_size()
    background = _get_background_image((width, height))
    if background:
        screen.blit(background, (0, 0))
    else:
        _draw_generated_ocean(screen, elapsed)

    light_layer = _get_dynamic_layer("light", (width, height))
    for i, x in enumerate((-90, 130, 340, 570)):
        drift = math.sin(elapsed * 0.28 + i * 1.7) * 34
        points = [
            (x + drift, 0),
            (x + 92 + drift, 0),
            (x + 275 + drift * 0.35, height),
            (x + 110 + drift * 0.3, height),
        ]
        pygame.draw.polygon(light_layer, (170, 230, 255, 20), points)
    screen.blit(light_layer, (0, 0))

    caustic_layer = _get_dynamic_layer("caustic", (width, height))
    for y in range(42, height, 34):
        points = []
        for x in range(-20, width + 21, 20):
            wave = math.sin(x * 0.026 + elapsed * 0.9 + y * 0.018) * 5
            points.append((x, y + wave))
        pygame.draw.lines(caustic_layer, (190, 245, 255, 18), False, points, 1)
    screen.blit(caustic_layer, (0, 0))

    if not background:
        floor_y = height - 42
        pygame.draw.polygon(
            screen,
            (9, 45, 53),
            [(0, height), (0, floor_y + 10), (150, floor_y - 16), (360, floor_y + 8),
             (560, floor_y - 22), (width, floor_y + 4), (width, height)],
        )

        plant_layer = _get_dynamic_layer("plants", (width, height))
        for i, x in enumerate(range(24, width, 58)):
            base = height - 34 + (i % 3) * 4
            blade_h = 38 + (i % 5) * 11
            sway = math.sin(elapsed * 0.8 + i) * 8
            pygame.draw.line(plant_layer, (28, 126, 106, 105), (x, base), (x + sway, base - blade_h), 4)
            pygame.draw.line(plant_layer, (42, 158, 126, 90), (x + 8, base), (x + 5 + sway * 0.5, base - blade_h * 0.75), 3)
        screen.blit(plant_layer, (0, 0))


class RisingBubbleField:
    def __init__(self, count=38):
        self.bubbles = []
        for i in range(count):
            self.bubbles.append({
                "x": (i * 53 + 19) % SCREEN_WIDTH,
                "y": (i * 97 + 23) % SCREEN_HEIGHT,
                "r": 4 + (i * 7) % 15,
                "speed": 24 + (i * 11) % 58,
                "phase": i * 0.73,
            })

    def draw(self, screen, elapsed=None):
        if elapsed is None:
            elapsed = pygame.time.get_ticks() / 1000.0

        width, height = screen.get_size()
        bubble_layer = _get_dynamic_layer("rising_bubbles", (width, height))
        for bubble in self.bubbles:
            y = (bubble["y"] - elapsed * bubble["speed"]) % (height + 70) - 40
            x = bubble["x"] + math.sin(elapsed * 1.4 + bubble["phase"]) * (10 + bubble["r"] * 0.35)
            radius = bubble["r"]
            alpha = 72 + min(82, radius * 5)
            center = (int(x), int(y))
            pygame.draw.circle(bubble_layer, (210, 246, 255, alpha), center, radius, 1)
            pygame.draw.circle(bubble_layer, (255, 255, 255, min(180, alpha + 45)),
                               (int(x - radius * 0.34), int(y - radius * 0.36)),
                               max(1, radius // 4))
        screen.blit(bubble_layer, (0, 0))
