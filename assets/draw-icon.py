"""Render the Ayu Dawn icon: a sun rising over a horizon, in the Mirage palette.

Usage: python3 assets/draw-icon.py out.png  (512 px; assets/icon.png is that scaled to 256 px)
"""
import math
import struct
import sys
import zlib

SIZE = 512
SS = 3  # supersamples per axis

def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

SKY_TOP = hex2rgb('242735')     # Mirage editor background
SKY_LOW = hex2rgb('464951')     # Mirage title bar
WARM = hex2rgb('F29E74')        # Mirage operator orange
SUN = hex2rgb('FFCC66')         # Mirage accent
WATER = hex2rgb('242735')
WATER_LOW = hex2rgb('1B1E2A')

RADIUS = 104        # corner radius of the rounded square
HORIZON = 318
SUN_R = 118
SUN_X = SIZE / 2

def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))

def inside_rounded(x, y):
    r = RADIUS
    cx = min(max(x, r), SIZE - r)
    cy = min(max(y, r), SIZE - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r

def color_at(x, y):
    if y < HORIZON:
        t = y / HORIZON
        c = mix(SKY_TOP, SKY_LOW, t ** 1.6)
        # Warm glow spreading from the sun along the horizon
        d = math.hypot((x - SUN_X) / 1.6, y - HORIZON)
        glow = max(0.0, 1 - d / 300) ** 2
        c = mix(c, WARM, glow * 0.55)
        # Sun disc, above the horizon only
        if math.hypot(x - SUN_X, y - HORIZON) <= SUN_R:
            c = SUN
        return c
    # Water: darkens with depth, with reflected sun bars that narrow and fade
    t = (y - HORIZON) / (SIZE - HORIZON)
    c = mix(WATER, WATER_LOW, t)
    bars = [(338, 14, 150, 0.85), (372, 12, 104, 0.6), (402, 10, 64, 0.4), (428, 8, 30, 0.25)]
    for top, h, half, a in bars:
        # Capsule: a bar with round ends
        r = h / 2
        cy = top + r
        dx = max(abs(x - SUN_X) - (half - r), 0)
        if dx * dx + (y - cy) ** 2 <= r * r:
            c = mix(c, SUN, a)
    return c

def render():
    rows = []
    n = SS * SS
    for py in range(SIZE):
        row = bytearray([0])
        for px in range(SIZE):
            r = g = b = cov = 0.0
            for sy in range(SS):
                for sx in range(SS):
                    x = px + (sx + 0.5) / SS
                    y = py + (sy + 0.5) / SS
                    if inside_rounded(x, y):
                        cr, cg, cb = color_at(x, y)
                        r += cr; g += cg; b += cb; cov += 1
            if cov:
                row += bytes([round(r / cov * 255), round(g / cov * 255), round(b / cov * 255),
                              round(cov / n * 255)])
            else:
                row += bytes(4)
        rows.append(bytes(row))
    return b''.join(rows)

def write_png(path, data):
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    ihdr = struct.pack('>IIBBBBB', SIZE, SIZE, 8, 6, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                chunk(b'IDAT', zlib.compress(data, 9)) + chunk(b'IEND', b''))

write_png(sys.argv[1], render())
