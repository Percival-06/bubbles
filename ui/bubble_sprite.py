import pygame


_sprite_cache = {}


def draw_photo_bubble(screen, center, radius, pollution_ratio=0.0, alpha=210):
    """Draw a glassy bubble inspired by the reference image."""
    radius = max(3, int(radius))
    pollution_ratio = max(0.0, min(1.0, pollution_ratio))
    alpha = max(0, min(255, int(alpha)))
    sprite = _get_bubble_sprite(radius, round(pollution_ratio, 2), alpha)
    screen.blit(sprite, (int(center[0] - radius), int(center[1] - radius)))


def _get_bubble_sprite(radius, pollution_ratio, alpha):
    key = (radius, pollution_ratio, alpha)
    if key not in _sprite_cache:
        _sprite_cache[key] = _build_bubble_sprite(radius, pollution_ratio, alpha)
    return _sprite_cache[key]


def _mix(a, b, ratio):
    return int(a * (1.0 - ratio) + b * ratio)


def _build_bubble_sprite(radius, pollution_ratio, alpha):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (radius, radius)

    tint = (
        _mix(224, 180, pollution_ratio),
        _mix(244, 70, pollution_ratio),
        _mix(255, 220, pollution_ratio),
    )
    rim_dark = (
        _mix(82, 118, pollution_ratio),
        _mix(116, 36, pollution_ratio),
        _mix(132, 150, pollution_ratio),
    )

    pygame.draw.circle(surf, (255, 255, 255, 34), center, radius)
    for i in range(radius, 0, -1):
        t = i / radius
        edge = 1.0 - t
        fill_alpha = int(alpha * (0.10 + edge * 0.30))
        color = (
            _mix(tint[0], 255, edge * 0.65),
            _mix(tint[1], 255, edge * 0.65),
            _mix(tint[2], 255, edge * 0.65),
            fill_alpha,
        )
        pygame.draw.circle(surf, color, center, i)

    rim_width = max(2, radius // 16)
    pygame.draw.circle(surf, (*rim_dark, 120), center, radius - 1, rim_width)
    pygame.draw.circle(
        surf,
        (26, 38, 46, 72),
        (radius + max(1, radius // 15), radius + max(1, radius // 24)),
        radius - max(2, radius // 28),
        max(1, rim_width),
    )
    pygame.draw.circle(
        surf,
        (255, 255, 255, 150),
        (radius - max(1, radius // 18), radius - max(1, radius // 18)),
        radius - max(3, radius // 9),
        max(1, rim_width // 2),
    )

    _draw_ellipse_highlight(
        surf,
        radius * 0.24,
        radius * 0.17,
        radius * 0.56,
        radius * 0.20,
        18,
        (255, 255, 255, 150),
    )
    _draw_ellipse_highlight(
        surf,
        radius * 1.05,
        radius * 1.08,
        radius * 0.50,
        radius * 0.17,
        -42,
        (255, 255, 255, 172),
    )
    pygame.draw.circle(
        surf,
        (255, 255, 255, 90),
        (int(radius * 1.28), int(radius * 0.78)),
        max(2, radius // 7),
        max(1, radius // 28),
    )
    pygame.draw.circle(
        surf,
        (255, 255, 255, 115),
        (int(radius * 0.34), int(radius * 1.64)),
        max(2, radius // 8),
        max(1, radius // 26),
    )

    return surf


def _draw_ellipse_highlight(surf, x, y, w, h, angle, color):
    w = max(2, int(w))
    h = max(2, int(h))
    highlight = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(highlight, color, (0, 0, w, h))
    highlight = pygame.transform.rotate(highlight, angle)
    surf.blit(highlight, highlight.get_rect(center=(int(x + w / 2), int(y + h / 2))))
