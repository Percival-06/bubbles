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
    return tuple(
        clamp(v)
        for v in (
            (sr * sa_f + dr * da_f * (1.0 - sa_f)) / out_a,
            (sg * sa_f + dg * da_f * (1.0 - sa_f)) / out_a,
            (sb * sa_f + db * da_f * (1.0 - sa_f)) / out_a,
            out_a * 255,
        )
    )


def point_in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i, point in enumerate(poly):
        xi, yi = point
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            cross = (xj - xi) * (y - yi) / max(0.0001, yj - yi) + xi
            if x < cross:
                inside = not inside
        j = i
    return inside


def add_poly(px, poly, color):
    min_x = max(0, int(min(p[0] for p in poly)))
    max_x = min(len(px[0]) - 1, int(max(p[0] for p in poly)) + 1)
    min_y = max(0, int(min(p[1] for p in poly)))
    max_y = min(len(px) - 1, int(max(p[1] for p in poly)) + 1)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if point_in_poly(x + 0.5, y + 0.5, poly):
                px[y][x] = over(px[y][x], color)


def add_circle(px, cx, cy, radius, color, ring_width=None):
    for y in range(max(0, int(cy - radius)), min(len(px), int(cy + radius) + 1)):
        for x in range(max(0, int(cx - radius)), min(len(px[0]), int(cx + radius) + 1)):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if ring_width is None:
                if d <= radius:
                    fade = max(0.0, 1.0 - d / max(1, radius))
                    px[y][x] = over(px[y][x], (*color[:3], clamp(color[3] * fade)))
            elif radius - ring_width <= d <= radius:
                fade = 1.0 - abs(d - (radius - ring_width / 2)) / max(1, ring_width / 2)
                px[y][x] = over(px[y][x], (*color[:3], clamp(color[3] * max(0, fade))))


def make_energy_seed(size=64):
    px = [[(0, 0, 0, 0) for _ in range(size)] for _ in range(size)]
    c = size / 2
    r = size * 0.24

    add_circle(px, c, c, size * 0.37, (225, 255, 104, 150), ring_width=size * 0.035)
    add_circle(px, c, c, size * 0.28, (255, 236, 90, 72))

    top = (c, c - r * 1.28)
    upper_left = (c - r * 0.82, c - r * 0.42)
    upper_right = (c + r * 0.82, c - r * 0.42)
    mid_left = (c - r * 0.63, c + r * 0.72)
    mid_right = (c + r * 0.63, c + r * 0.72)
    bottom = (c, c + r * 1.36)
    crystal = [top, upper_right, mid_right, bottom, mid_left, upper_left]

    add_poly(px, crystal, (255, 235, 98, 238))
    add_poly(px, [top, upper_left, (c, c - r * 0.12)], (255, 255, 185, 170))
    add_poly(px, [top, upper_right, (c, c - r * 0.12)], (255, 211, 61, 145))
    add_poly(px, [upper_left, mid_left, bottom, (c, c + r * 0.66)], (244, 177, 48, 125))
    add_poly(px, [upper_right, mid_right, bottom, (c, c + r * 0.66)], (255, 247, 135, 145))
    add_poly(px, [
        (c - r * 0.36, c - r * 0.02),
        (c + r * 0.40, c - r * 0.05),
        (c + r * 0.34, c + r * 0.50),
        (c - r * 0.30, c + r * 0.48),
    ], (218, 255, 112, 105))

    for dx, dy, rr, alpha in ((-1.16, -0.24, 0.10, 170), (1.16, -0.05, 0.12, 150), (-1.04, 0.88, 0.08, 125)):
        add_circle(px, c + dx * r, c + dy * r, rr * r, (238, 255, 205, alpha))

    return px


def write_png(path, px):
    height = len(px)
    width = len(px[0])
    raw = bytearray()
    for row in px:
        raw.append(0)
        for rgba in row:
            raw.extend(rgba)

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
    png.extend(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    png.extend(chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    write_png(os.path.join(OUT_DIR, "energy_seed.png"), make_energy_seed())


if __name__ == "__main__":
    main()
