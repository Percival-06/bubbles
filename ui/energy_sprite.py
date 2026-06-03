import math

import pygame


_sprite_cache = {}


def draw_energy_seed(screen, center, radius):
    radius = max(8, int(radius))
    sprite = _get_energy_sprite(radius)
    screen.blit(sprite, sprite.get_rect(center=(int(center[0]), int(center[1]))))


def _get_energy_sprite(radius):
    key = radius
    if key not in _sprite_cache:
        _sprite_cache[key] = _build_energy_sprite(radius)
    return _sprite_cache[key]


def _build_energy_sprite(radius):
    size = radius * 4
    center = size // 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    ring_r = int(radius * 1.55)
    for width, alpha in ((5, 35), (3, 70), (1, 135)):
        pygame.draw.circle(surf, (224, 255, 102, alpha), (center, center), ring_r, width)

    for r in range(int(radius * 1.28), 0, -1):
        alpha = int(44 * (1 - r / (radius * 1.28)))
        pygame.draw.circle(surf, (255, 240, 92, alpha), (center, center), r)

    top = (center, center - int(radius * 1.26))
    upper_left = (center - int(radius * 0.82), center - int(radius * 0.42))
    upper_right = (center + int(radius * 0.82), center - int(radius * 0.42))
    mid_left = (center - int(radius * 0.63), center + int(radius * 0.72))
    mid_right = (center + int(radius * 0.63), center + int(radius * 0.72))
    bottom = (center, center + int(radius * 1.36))
    crystal = [top, upper_right, mid_right, bottom, mid_left, upper_left]

    pygame.draw.polygon(surf, (255, 239, 111, 235), crystal)
    pygame.draw.polygon(surf, (255, 252, 172, 190), [top, upper_left, (center, center - int(radius * 0.12))])
    pygame.draw.polygon(surf, (255, 218, 72, 155), [top, upper_right, (center, center - int(radius * 0.12))])
    pygame.draw.polygon(surf, (255, 198, 54, 145), [upper_left, mid_left, bottom, (center, center + int(radius * 0.66))])
    pygame.draw.polygon(surf, (255, 245, 134, 155), [upper_right, mid_right, bottom, (center, center + int(radius * 0.66))])
    pygame.draw.polygon(surf, (228, 255, 105, 95), [
        (center - int(radius * 0.36), center - int(radius * 0.02)),
        (center + int(radius * 0.40), center - int(radius * 0.05)),
        (center + int(radius * 0.34), center + int(radius * 0.50)),
        (center - int(radius * 0.30), center + int(radius * 0.48)),
    ])

    pygame.draw.polygon(surf, (255, 255, 210, 180), crystal, max(1, radius // 9))
    _draw_soft_line(surf, upper_left, upper_right, (255, 255, 210, 95), max(1, radius // 12))
    _draw_soft_line(surf, (center, center - int(radius * 0.12)), bottom, (255, 255, 205, 70), max(1, radius // 13))

    for dx, dy, r, alpha in (
        (-1.15, -0.24, 0.10, 155),
        (1.16, -0.05, 0.12, 145),
        (-1.04, 0.88, 0.08, 125),
    ):
        pygame.draw.circle(
            surf,
            (235, 255, 205, alpha),
            (center + int(dx * radius), center + int(dy * radius)),
            max(1, int(r * radius)),
        )

    return surf


def _draw_soft_line(surf, start, end, color, width):
    pygame.draw.line(surf, color, start, end, width)
