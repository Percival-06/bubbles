import math

import pygame


BADGE_STARS = {
    "none": 0,
    None: 0,
    "bronze": 1,
    "silver": 2,
    "gold": 3,
}


def badge_star_count(badge):
    return BADGE_STARS.get(badge, 0)


def draw_star_row(screen, center, total=3, filled=0, radius=11, gap=6, highlight_index=None, highlight_progress=0.0):
    total = max(0, int(total))
    filled = max(0, min(int(filled), total))
    if total <= 0:
        return

    spacing = radius * 2 + gap
    start_x = center[0] - spacing * (total - 1) / 2
    for index in range(total):
        progress = highlight_progress if index == highlight_index else 0.0
        scale = 1.0 + 0.32 * _pulse(progress)
        star_radius = radius * scale
        star_center = (int(start_x + spacing * index), int(center[1]))
        is_filled = index < filled
        _draw_star(screen, star_center, star_radius, is_filled, progress)


def _pulse(progress):
    if progress <= 0.0 or progress >= 1.0:
        return 0.0
    return math.sin(progress * math.pi)


def _draw_star(screen, center, radius, filled, progress=0.0):
    outer = _star_points(center, radius, radius * 0.46)
    glow = _pulse(progress)

    if filled:
        if glow > 0:
            pygame.draw.circle(screen, (255, 229, 88), center, int(radius * (1.7 + glow * 0.8)))
        pygame.draw.polygon(screen, (255, 225, 83), outer)
        pygame.draw.polygon(screen, (255, 249, 180), _star_points((center[0] - radius * 0.12, center[1] - radius * 0.10), radius * 0.58, radius * 0.22))
        pygame.draw.polygon(screen, (149, 103, 28), outer, max(1, int(radius * 0.12)))
    else:
        pygame.draw.polygon(screen, (33, 67, 86), outer)
        pygame.draw.polygon(screen, (184, 213, 220), outer, max(1, int(radius * 0.13)))


def _star_points(center, outer_radius, inner_radius):
    points = []
    cx, cy = center
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer_radius if i % 2 == 0 else inner_radius
        points.append((int(cx + math.cos(angle) * radius), int(cy + math.sin(angle) * radius)))
    return points
