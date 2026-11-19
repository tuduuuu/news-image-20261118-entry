"""Sum up 18 November 2026 world news in one image.

Pure Python standard library only. Draws a 1024x1024 newspaper
front page with a small bitmap font and writes a deterministic PNG
to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
No network, no randomness, no timestamps in the output.
"""
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 232)
INK = (17, 24, 39)
NAVY = (15, 42, 92)
RED = (185, 28, 28)
TEAL = (13, 110, 110)
GOLD = (180, 130, 20)
GREY = (90, 95, 105)
LIGHT = (232, 226, 210)
WHITE = (255, 255, 255)

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "00000", "00000", "01100", "00000", "00000"),
    "%": ("10001", "00010", "00100", "01000", "10001", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(pixels, text, x, y, color, scale=2):
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            px = cx + col * scale + dx
                            py = y + row * scale + dy
                            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                                pixels[py][px] = color
        cx += 6 * scale
    return cx


def draw_text_centered(pixels, text, cx, y, color, scale=2):
    x = cx - text_width(text, scale) // 2
    draw_text(pixels, text, x, y, color, scale)


def wrap(text, width_chars):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        if cur and len(cur) + 1 + len(word) > width_chars:
            lines.append(cur)
            cur = word
        else:
            cur = cur + " " + word if cur else word
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(pixels, text, x, y, width_chars, color, scale=1, leading=12):
    lines = wrap(text, width_chars)
    for line in lines:
        draw_text(pixels, line, x, y, color, scale)
        y += leading
    return y


def rect(pixels, x, y, w, h, color):
    for py in range(max(0, y), min(HEIGHT, y + h)):
        for px in range(max(0, x), min(WIDTH, x + w)):
            pixels[py][px] = color


def hline(pixels, x, y, w, color, thick=2):
    rect(pixels, x, y, w, thick, color)


def draw_globe(pixels, cx, cy, r):
    for py in range(cy - r, cy + r + 1):
        for px in range(cx - r, cx + r + 1):
            dx = px - cx
            dy = py - cy
            d2 = dx * dx + dy * dy
            if d2 <= r * r:
                if d2 > (r - 3) * (r - 3):
                    pixels[py][px] = NAVY
                elif (dx * 7 + dy * 3) % 23 < 4:
                    pixels[py][px] = TEAL
                else:
                    pixels[py][px] = (190, 220, 225)
    hline(pixels, cx - r, cy, 2 * r, NAVY, 2)
    for k in range(-2, 3):
        x = cx + k * r // 3
        for py in range(cy - r, cy + r + 1):
            dx = x - cx
            if dx * dx + (py - cy) ** 2 <= r * r:
                pixels[py][x] = NAVY


def build():
    pixels = [[PAPER for _ in range(WIDTH)] for _ in range(HEIGHT)]
    rect(pixels, 0, 0, WIDTH, 10, NAVY)
    rect(pixels, 0, HEIGHT - 10, WIDTH, 10, NAVY)
    draw_text_centered(pixels, "WORLD NEWS", WIDTH // 2, 28, INK, 7)
    draw_text_centered(
        pixels, "WEDNESDAY 18 NOVEMBER 2026", WIDTH // 2, 92, RED, 3
    )
    hline(pixels, 40, 128, WIDTH - 80, INK, 3)
    hline(pixels, 40, 136, WIDTH - 80, INK, 1)

    # Lead story: Shenzhen summit
    y = 156
    draw_text(pixels, "THE THREE LEADERS MEET", 40, y, NAVY, 4)
    y += 40
    draw_text(pixels, "TRUMP, XI AND PUTIN", 40, y, INK, 4)
    y += 40
    draw_text(pixels, "IN SHENZHEN", 40, y, INK, 4)
    y += 52
    draw_globe(pixels, 880, 250, 78)
    draw_text_centered(pixels, "APEC", 880, 330, NAVY, 2)
    y = draw_paragraph(
        pixels,
        "Donald Trump, Xi Jinping and Vladimir Putin exchanged "
        "greetings at the APEC welcome banquet in Shenzhen on "
        "Wednesday, a day before their first-ever trilateral "
        "summit. Xi welcomed Trump on the tarmac, then met Putin "
        "for talks on Ukraine, Iran and nuclear arms.",
        40,
        y,
        58,
        INK,
        2,
        24,
    )
    y += 8
    hline(pixels, 40, y, WIDTH - 80, GREY, 2)
    y += 18

    # Second row: Hormuz and Cyclone, two columns
    col_w = 440
    left_y = y
    draw_text(pixels, "US STRIKES IRAN", 40, left_y, RED, 3)
    left_y += 34
    left_y = draw_paragraph(
        pixels,
        "US jets hit a Revolutionary Guards missile site on "
        "Qeshm Island in the Strait of Hormuz after Iranian "
        "drones targeted US bases in Kuwait and Bahrain.",
        40,
        left_y,
        36,
        INK,
        2,
        22,
    )
    right_y = y
    draw_text(pixels, "CYCLONE AKVAN", 540, right_y, TEAL, 3)
    right_y += 34
    right_y = draw_paragraph(
        pixels,
        "A severe cyclone strengthens in the Bay of Bengal. "
        "Odisha and Andhra Pradesh brace for landfall on Friday "
        "as shelters fill and flights are watched.",
        540,
        right_y,
        36,
        INK,
        2,
        22,
    )
    y = max(left_y, right_y) + 10
    hline(pixels, 40, y, WIDTH - 80, GREY, 2)
    y += 18

    # Third row: Gaza and Nvidia
    left_y = y
    draw_text(pixels, "GAZA OPERATION", 40, left_y, RED, 3)
    left_y += 34
    left_y = draw_paragraph(
        pixels,
        "Israel begins a concentrated operation in three areas "
        "of central Gaza, west of the yellow line, as the war "
        "enters another winter.",
        40,
        left_y,
        36,
        INK,
        2,
        22,
    )
    right_y = y
    draw_text(pixels, "NVIDIA DOUBLES", 540, right_y, NAVY, 3)
    right_y += 34
    right_y = draw_paragraph(
        pixels,
        "Nvidia revenue hits $115.8 billion, up 103 percent, "
        "on data-centre sales. Its board rules out bringing "
        "back ousted chief Jensen Huang.",
        540,
        right_y,
        36,
        INK,
        2,
        22,
    )
    y = max(left_y, right_y) + 10
    hline(pixels, 40, y, WIDTH - 80, GREY, 2)
    y += 18

    # Bottom strip: Senate and Quad
    draw_text(pixels, "SENATE FLIPS IN ALASKA", 40, y, NAVY, 3)
    y += 34
    y = draw_paragraph(
        pixels,
        "Democrat Mary Peltola defeats Republican Dan Sullivan, "
        "giving Democrats a projected 56-44 Senate majority. "
        "The Quad meets in Manila, and the US loses its "
        "measles-free status as cases spike.",
        40,
        y,
        76,
        INK,
        2,
        22,
    )
    y += 14
    hline(pixels, 40, y, WIDTH - 80, INK, 3)
    draw_text_centered(
        pixels, "WORLD NEWS  -  18 NOVEMBER 2026", WIDTH // 2, y + 14, GREY, 2
    )
    return pixels


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(pixels, path):
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b in row:
            raw.extend((r, g, b))
    compressed = zlib.compress(bytes(raw), 6)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    pixels = build()
    size = write_png(pixels, os.path.join(out_dir, "entry.png"))
    print(f"wrote entry.png {size} bytes")


if __name__ == "__main__":
    main()
