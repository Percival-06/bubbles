import binascii
import math
import os
import struct
import zlib


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "sprites")


def clamp(value, low=0, high=255):
    return max(low, min(high, int(value)))


def over(dst, src):
    sr, sg, sb, sa = src
    if sa <= 0:
        return dst
    dr, dg, db, da = dst
    sa_f = sa / 255.0
    da_f = da / 255.0
    out_a = sa_f + da_f * (1.0 - sa_f)
    if out_a <= 0:
        return (0, 0, 0, 0)
    out = (
        (sr * sa_f + dr * da_f * (1.0 - sa_f)) / out_a,
        (sg * sa_f + dg * da_f * (1.0 - sa_f)) / out_a,
        (sb * sa_f + db * da_f * (1.0 - sa_f)) / out_a,
        out_a * 255.0,
    )
    return tuple(clamp(v) for v in out)


def add_ellipse(px, cx, cy, rx, ry, angle, color, softness=0.18):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    for y in range(len(px)):
        for x in range(len(px[y])):
            dx = x - cx
            dy = y - cy
            xr = dx * cos_a + dy * sin_a
            yr = -dx * sin_a + dy * cos_a
            d = (xr / rx) ** 2 + (yr / ry) ** 2
            if d <= 1.0:
                fade = min(1.0, max(0.0, (1.0 - d) / softness))
                c = (*color[:3], clamp(color[3] * fade))
                px[y][x] = over(px[y][x], c)


def make_bubble(size, radius):
    cx = cy = size / 2.0
    px = [[(0, 0, 0, 0) for _ in range(size)] for _ in range(size)]

    for y in range(size):
        for x in range(size):
            dx = x + 0.5 - cx
            dy = y + 0.5 - cy
            dist = math.hypot(dx, dy)
            if dist > radius:
                continue

            t = dist / radius
            edge = max(0.0, min(1.0, (t - 0.72) / 0.28))
            center_haze = max(0.0, 1.0 - t)
            right_shadow = max(0.0, (dx / radius + dy / radius) * 0.5)
            alpha = 30 + center_haze * 36 + edge * 88
            color = (
                232 - edge * 38 - right_shadow * 30,
                246 - edge * 30 - right_shadow * 24,
                255 - edge * 20 - right_shadow * 18,
                alpha,
            )
            px[y][x] = over(px[y][x], tuple(clamp(v) for v in color))

            if 0.94 <= t <= 1.0:
                rim_alpha = (1.0 - abs(t - 0.97) / 0.03) * 150
                px[y][x] = over(px[y][x], (55, 78, 92, clamp(rim_alpha)))

    add_ellipse(
        px,
        cx - radius * 0.35,
        cy - radius * 0.34,
        radius * 0.36,
        radius * 0.12,
        math.radians(-28),
        (255, 255, 255, 165),
    )
    add_ellipse(
        px,
        cx + radius * 0.30,
        cy + radius * 0.30,
        radius * 0.34,
        radius * 0.10,
        math.radians(-45),
        (255, 255, 255, 185),
    )
    add_ellipse(
        px,
        cx + radius * 0.28,
        cy - radius * 0.20,
        radius * 0.13,
        radius * 0.13,
        0,
        (255, 255, 255, 78),
        softness=0.4,
    )

    return px


def write_png(path, px):
    height = len(px)
    width = len(px[0])
    raw = bytearray()
    for row in px:
        raw.append(0)
        for r, g, b, a in row:
            raw.extend((r, g, b, a))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
    png.extend(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    png.extend(chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def render_sprite(name, canvas_size, radius):
    write_png(os.path.join(OUT_DIR, name), make_bubble(canvas_size, radius))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    render_sprite("bubble_large.png", 160, 76)
    render_sprite("bubble_small.png", 48, 21)


if __name__ == "__main__":
    main()
