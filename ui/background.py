import math
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


SURFACE_COLOR = (37, 143, 174)
MID_WATER_COLOR = (13, 76, 116)
DEEP_WATER_COLOR = (4, 26, 56)


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def _mix(c1, c2, t):
    return (
        _lerp(c1[0], c2[0], t),
        _lerp(c1[1], c2[1], t),
        _lerp(c1[2], c2[2], t),
    )


def draw_ocean_background(screen, elapsed=None):
    if elapsed is None:
        elapsed = pygame.time.get_ticks() / 1000.0

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

    light_layer = pygame.Surface((width, height), pygame.SRCALPHA)
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

    caustic_layer = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(42, height, 34):
        points = []
        for x in range(-20, width + 21, 20):
            wave = math.sin(x * 0.026 + elapsed * 0.9 + y * 0.018) * 5
            points.append((x, y + wave))
        pygame.draw.lines(caustic_layer, (190, 245, 255, 18), False, points, 1)
    screen.blit(caustic_layer, (0, 0))

    floor_y = height - 42
    pygame.draw.polygon(
        screen,
        (9, 45, 53),
        [(0, height), (0, floor_y + 10), (150, floor_y - 16), (360, floor_y + 8),
         (560, floor_y - 22), (width, floor_y + 4), (width, height)],
    )

    plant_layer = pygame.Surface((width, height), pygame.SRCALPHA)
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
        bubble_layer = pygame.Surface((width, height), pygame.SRCALPHA)
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
