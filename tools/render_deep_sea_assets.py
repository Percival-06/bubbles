import math
import os
import struct
import zlib


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "backgrounds")


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c1, c2, t):
    return tuple(lerp(c1[i], c2[i], t) for i in range(3))


def blend(base, over, alpha):
    return tuple(lerp(base[i], over[i], alpha) for i in range(3))


def clamp(value, low, high):
    return max(low, min(high, value))


def add_radial(pixels, width, height, cx, cy, radius, color, strength):
    for y in range(max(0, int(cy - radius)), min(height, int(cy + radius) + 1)):
        for x in range(max(0, int(cx - radius)), min(width, int(cx + radius) + 1)):
            dist = math.hypot((x - cx) / radius, (y - cy) / radius)
            if dist >= 1:
                continue
            alpha = (1 - dist) ** 1.8 * strength
            pixels[y][x] = blend(pixels[y][x], color, alpha)


def add_light_ray(pixels, width, height, start_x, top_width, bottom_x, bottom_width, color, strength):
    for y in range(height):
        t = y / max(1, height - 1)
        center = lerp(start_x, bottom_x, t)
        half_width = lerp(top_width, bottom_width, t) / 2
        alpha_y = (1 - t) ** 1.2 * strength
        left = max(0, int(center - half_width))
        right = min(width, int(center + half_width))
        for x in range(left, right):
            dist = abs(x - center) / max(1, half_width)
            alpha = alpha_y * max(0.0, 1 - dist) ** 1.5
            pixels[y][x] = blend(pixels[y][x], color, alpha)


def add_caustics(pixels, width, height):
    for y in range(55, int(height * 0.72), 34):
        for x in range(width):
            wave = math.sin(x * 0.034 + y * 0.019) * 7
            yy = int(y + wave)
            if 0 <= yy < height:
                pixels[yy][x] = blend(pixels[yy][x], (206, 250, 255), 0.09)


def add_bubble(pixels, width, height, cx, cy, radius, alpha):
    for y in range(max(0, int(cy - radius)), min(height, int(cy + radius) + 1)):
        for x in range(max(0, int(cx - radius)), min(width, int(cx + radius) + 1)):
            dist = math.hypot(x - cx, y - cy)
            if radius - 1.6 <= dist <= radius + 0.8:
                pixels[y][x] = blend(pixels[y][x], (230, 252, 255), alpha)
            elif dist < radius:
                glow = (1 - dist / radius) * alpha * 0.12
                pixels[y][x] = blend(pixels[y][x], (185, 238, 255), glow)

    hi_r = max(1, radius * 0.16)
    hx = cx - radius * 0.32
    hy = cy - radius * 0.34
    for y in range(max(0, int(hy - hi_r)), min(height, int(hy + hi_r) + 1)):
        for x in range(max(0, int(hx - hi_r)), min(width, int(hx + hi_r) + 1)):
            if math.hypot(x - hx, y - hy) <= hi_r:
                pixels[y][x] = blend(pixels[y][x], (255, 255, 255), min(0.85, alpha + 0.2))


def add_reef(pixels, width, height):
    floor = int(height * 0.86)
    for y in range(floor, height):
        t = (y - floor) / max(1, height - floor)
        for x in range(width):
            ridge = (
                math.sin(x * 0.012) * height * 0.035
                + math.sin(x * 0.031 + 1.7) * height * 0.018
            )
            edge = floor + ridge
            if y >= edge:
                color = mix((6, 28, 43), (2, 8, 17), t)
                pixels[y][x] = blend(pixels[y][x], color, 0.92)

    for i, x in enumerate(range(int(width * 0.06), width, max(32, width // 17))):
        base = height - int(height * 0.035)
        blade = int(height * (0.065 + (i % 5) * 0.012))
        sway = math.sin(i * 1.3) * width * 0.009
        for step in range(blade):
            y = base - step
            xx = int(x + sway * (step / blade) + math.sin(step * 0.15 + i) * 2)
            for dx in range(-1, 2):
                if 0 <= xx + dx < width and 0 <= y < height:
                    pixels[y][xx + dx] = blend(pixels[y][xx + dx], (28, 115, 99), 0.45)


def add_vignette(pixels, width, height):
    cx = width / 2
    cy = height / 2
    max_dist = math.hypot(cx, cy)
    for y in range(height):
        for x in range(width):
            edge = math.hypot(x - cx, y - cy) / max_dist
            side = abs((x / width) - 0.5) * 2
            alpha = clamp(edge ** 2.2 * 0.42 + side ** 2.5 * 0.16, 0, 0.58)
            pixels[y][x] = blend(pixels[y][x], (0, 2, 8), alpha)


def make_background(width, height):
    top = (18, 67, 111)
    mid = (8, 39, 76)
    bottom = (2, 8, 20)
    pixels = []
    for y in range(height):
        depth = y / max(1, height - 1)
        if depth < 0.43:
            color = mix(top, mid, depth / 0.43)
        else:
            color = mix(mid, bottom, (depth - 0.43) / 0.57)
        row = [color for _ in range(width)]
        pixels.append(row)

    add_radial(pixels, width, height, width * 0.2, height * 0.24, width * 0.25, (85, 172, 213), 0.28)
    add_radial(pixels, width, height, width * 0.52, height * 0.82, width * 0.28, (28, 150, 142), 0.18)
    add_light_ray(pixels, width, height, int(width * 0.02), int(width * 0.15), int(width * 0.26), int(width * 0.34), (206, 245, 255), 0.24)
    add_light_ray(pixels, width, height, int(width * 0.36), int(width * 0.12), int(width * 0.48), int(width * 0.28), (180, 232, 252), 0.16)
    add_light_ray(pixels, width, height, int(width * 0.72), int(width * 0.15), int(width * 0.58), int(width * 0.26), (170, 226, 250), 0.14)
    add_caustics(pixels, width, height)
    add_reef(pixels, width, height)

    bubble_specs = [
        (0.08, 0.68, 0.035, 0.42),
        (0.17, 0.4, 0.016, 0.52),
        (0.28, 0.73, 0.025, 0.38),
        (0.44, 0.31, 0.012, 0.48),
        (0.58, 0.62, 0.03, 0.34),
        (0.72, 0.42, 0.018, 0.45),
        (0.84, 0.72, 0.04, 0.28),
        (0.92, 0.28, 0.014, 0.5),
    ]
    for bx, by, br, alpha in bubble_specs:
        add_bubble(pixels, width, height, bx * width, by * height, br * min(width, height), alpha)

    add_vignette(pixels, width, height)
    return pixels


def add_cover_title(pixels, width, height):
    # Keep the generated cover useful even without font dependencies: a soft title plate
    # leaves room for the Remotion version to render real Chinese text.
    plate_top = int(height * 0.36)
    plate_bottom = int(height * 0.57)
    for y in range(plate_top, plate_bottom):
        t = 1 - abs((y - (plate_top + plate_bottom) / 2) / ((plate_bottom - plate_top) / 2))
        for x in range(int(width * 0.17), int(width * 0.83)):
            pixels[y][x] = blend(pixels[y][x], (3, 14, 30), 0.22 * t)


def write_png(path, pixels):
    height = len(pixels)
    width = len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b in row:
            raw.extend((r, g, b, 255))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as file:
        file.write(png)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    menu = make_background(800, 600)
    write_png(os.path.join(OUT_DIR, "main_menu_deep_sea.png"), menu)

    cover = make_background(1280, 720)
    add_cover_title(cover, 1280, 720)
    write_png(os.path.join(OUT_DIR, "cover_deep_sea.png"), cover)
    print(os.path.join(OUT_DIR, "main_menu_deep_sea.png"))
    print(os.path.join(OUT_DIR, "cover_deep_sea.png"))


if __name__ == "__main__":
    main()
