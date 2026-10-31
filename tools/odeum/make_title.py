"""Draws an Odeum title logo in the style of the vanilla Balatro logo: cream letters
with blue/red marbling, a slate border with depth, and a soft white glow. The text is
split around the card that the title screen places in the middle of the logo.

Needs Pillow (pip install pillow).
Usage:
  python tools/odeum/make_title.py --pack mods/Odeum/packs/vesper   (reads title = {...} from pack.lua)
  python tools/odeum/make_title.py VES PER -o some/title.png --font HARNGTON.TTF --preview
"""
import argparse
import io
import math
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Vanilla logo geometry, at 1x (the game also uses a 2x copy: every pixel doubled)
W, H = 333, 216
LEFT_MAX = 133        # left word must end here; the card covers ~135..198
RIGHT_MIN = 201       # right word starts here
MARGIN = 5            # outer margin, like vanilla
ORNAMENT = (139, 192)  # columns of the vanilla stick behind the card
TOP, BOTTOM = 56, 158  # face area of the vanilla letters (border adds the rest)

# Vanilla palette
OUTLINE = (49, 58, 60)
BORDER_LIGHT = (91, 117, 123)
BORDER = (79, 99, 103)
BORDER_DARK = (67, 81, 83)
FACE = (248, 244, 240)
FACE_HI = (255, 255, 255)
FACE_SHADE = (230, 221, 211)
FACE_SHADE_DARK = (203, 187, 167)
STREAKS = [  # (centre as fraction of letter height, colour, thickness)
    (0.16, (176, 210, 240), 2),
    (0.20, (120, 170, 225), 1),
    (0.45, (205, 190, 220), 2),
    (0.70, (243, 178, 178), 2),
    (0.74, (213, 103, 102), 1),
    (0.88, (248, 210, 211), 1),
]
GLOW = [103, 61, 30, 12, 3]  # white halo alpha, from the border outwards

DEFAULT_FONT = "BERNHC.TTF"  # Bernard MT Condensed: tall, condensed, flared
# The centre ornament is read from the installed game rather than kept in the repo
GAME_EXE = Path("D:/SteamLibrary/steamapps/common/Balatro/Balatro.exe")
VANILLA_LOGO = "game"
FONT_DIRS = [Path("C:/Windows/Fonts"), Path.home() / "AppData/Local/Microsoft/Windows/Fonts"]


def read_pack_title(pack_lua):
    """Reads `title = { left = "VES", right = "PER", font = "HARNGTON.TTF" }` from a pack.lua."""
    m = re.search(r"title\s*=\s*\{([^}]*)\}", pack_lua.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"{pack_lua}: no title = {{ left = ..., right = ... }} table")
    spec = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', m.group(1)))
    if "left" not in spec or "right" not in spec:
        raise SystemExit(f"{pack_lua}: title needs left and right")
    return spec


def find_font(name):
    p = Path(name)
    if p.exists():
        return p
    for d in FONT_DIRS:
        if (d / name).exists():
            return d / name
    raise SystemExit(f"font not found: {name}")


MAX_SQUEEZE = 0.65  # narrowest horizontal squeeze before long words shrink instead


def render_text(text, font_path, box_h):
    """Greyscale image of text whose glyphs are box_h tall."""
    # Find the font size whose glyph height fills box_h, then squeeze width if needed.
    size = box_h
    for _ in range(40):
        font = ImageFont.truetype(str(font_path), size)
        l, t, r, b = font.getbbox(text)
        if b - t >= box_h:
            break
        size += 4
    img = Image.new("L", (r - l + 4, b - t + 4), 0)
    ImageDraw.Draw(img).text((2 - l, 2 - t), text, font=font, fill=255)
    img = img.crop(img.getbbox())
    return img.resize((img.width, box_h), Image.LANCZOS)


def fit(img, box_w):
    """(squeeze, shrink) that make img fit box_w: squeeze narrows it, shrink scales it down evenly."""
    squeeze = max(MAX_SQUEEZE, min(1.0, box_w / img.width))
    return squeeze, min(1.0, box_w / (img.width * squeeze))


def text_mask(img, squeeze, shrink, box_w, box_h, align):
    """Binary mask (set of (x, y)) of the text image placed in box_w x box_h, aligned left/right."""
    w, h = max(1, round(img.width * squeeze * shrink)), max(1, round(img.height * shrink))
    img = img.resize((w, h), Image.LANCZOS)
    ox = 0 if align == "left" else box_w - w
    oy = (box_h - h) // 2
    px = img.load()
    return {(x + ox, y + oy) for x in range(w) for y in range(h) if px[x, y] >= 128}


def dilate(mask, r):
    out = set(mask)
    offsets = [(dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r * r + r]
    for x, y in mask:
        for dx, dy in offsets:
            out.add((x + dx, y + dy))
    return out


def shift(mask, dx, dy):
    return {(x + dx, y + dy) for x, y in mask}


def draw(left, right, font_path, ornament_from=None):
    face_h = BOTTOM - TOP
    sides = [(t, x0, x1, align) for t, x0, x1, align in (
        (left, MARGIN + 6, LEFT_MAX - 6, "right"),
        (right, RIGHT_MIN + 6, W - MARGIN - 6, "left"),
    ) if t]
    images = [render_text(t, font_path, face_h) for t, *_ in sides]
    fits = [fit(img, x1 - x0) for img, (_, x0, x1, _) in zip(images, sides)]
    shrink = min(s for _, s in fits)  # both halves shrink together so the letters match
    face = set()
    for img, (squeeze, _), (_, x0, x1, align) in zip(images, fits, sides):
        face |= shift(text_mask(img, squeeze, shrink, x1 - x0, face_h, align), x0, TOP)

    border = dilate(face, 3)
    depth = set()
    for d in range(1, 5):  # extrusion: the border continues downwards
        depth |= shift(border, 0, d)
    shell = border | depth
    outline = dilate(shell, 1) - shell
    halo = [dilate(shell | outline, i + 1) for i in range(len(GLOW))]

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if ornament_from:  # keep the vanilla centre ornament (the stick behind the card)
        if ornament_from == "game":
            with zipfile.ZipFile(GAME_EXE) as z:
                ornament_from = io.BytesIO(z.read("resources/textures/1x/balatro.png"))
        orn = Image.open(ornament_from).convert("RGBA").resize((W, H), Image.NEAREST)
        img.paste(orn.crop((ORNAMENT[0], 0, ORNAMENT[1], H)), (ORNAMENT[0], 0))
    px = img.load()

    def put(x, y, c, a=255):
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = (*c, a)

    prev = set(shell | outline)
    for ring, alpha in zip(halo, GLOW):
        for x, y in ring - prev:
            if 0 <= x < W and 0 <= y < H and px[x, y][3] == 0:
                put(x, y, (255, 255, 255), alpha)
        prev = ring
    for x, y in outline:
        put(x, y, OUTLINE)
    for x, y in shell:
        if (x, y) in border:
            put(x, y, BORDER_LIGHT if (x, y - 2) not in border else BORDER)
        else:
            put(x, y, BORDER_DARK if (x, y + 1) not in shell else BORDER)

    top = min(y for _, y in face)
    height = max(y for _, y in face) - top
    for x, y in face:
        c = FACE
        # marbling: thin wavy streaks across the letters
        for centre, colour, thick in STREAKS:
            wave = centre * height + 4 * math.sin(x / 9 + centre * 7) + 2 * math.sin(x / 3.7)
            if abs((y - top) - wave) < thick * 0.6:
                c = colour
        # lighting: highlight on top edges, shading on bottom/right edges
        if (x, y - 1) not in face:
            c = FACE_HI
        if (x, y + 1) not in face or (x + 1, y) not in face:
            c = FACE_SHADE_DARK
        elif (x, y + 2) not in face or (x + 2, y) not in face:
            c = FACE_SHADE
        put(x, y, c)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("left", nargs="?", help="text left of the card")
    ap.add_argument("right", nargs="?", help="text right of the card")
    ap.add_argument("--pack", help="pack folder: read title = { left, right, font } from its pack.lua, write its title.png")
    ap.add_argument("-o", "--out", default="title.png", help="output PNG (2x, 666x432)")
    ap.add_argument("--font", default=DEFAULT_FONT)
    ap.add_argument("--ornament", default=VANILLA_LOGO,
                    help="where to copy the centre ornament from: 'game' (Balatro.exe), a balatro.png, or '' for none")
    ap.add_argument("--preview", action="store_true", help="also write <out>_preview.png on a dark background")
    args = ap.parse_args()

    if args.pack:
        spec = read_pack_title(Path(args.pack) / "pack.lua")
        args.left, args.right = spec["left"], spec["right"]
        args.font = spec.get("font", args.font)
        args.out = str(Path(args.pack) / "title.png")
    if args.left is None or args.right is None:
        ap.error("give LEFT RIGHT, or --pack")

    img = draw(args.left, args.right, find_font(args.font), args.ornament or None)
    big = img.resize((W * 2, H * 2), Image.NEAREST)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    big.save(out)
    if args.preview:
        bg = Image.new("RGBA", big.size, (38, 50, 56, 255))
        bg.alpha_composite(big)
        bg.save(out.with_name(out.stem + "_preview.png"))
    print(out)


if __name__ == "__main__":
    main()
