#!/usr/bin/env python3
"""Draw the 21 November 2026 world-news infographic (1024x1024 PNG).

Everything on the page is rendered as real text with PIL, so nothing can
come out garbled the way AI-generated lettering can. The page is a
newspaper front page in miniature: a navy masthead, six story cards in a
two-by-three grid, and a short footer line. Re-running this script
reproduces entry.png byte for byte.
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------

PAGE_W = 1024
PAGE_H = 1024

MASTHEAD_H = 148          # navy band at the top
GRID_TOP = 168            # first row of story cards
GRID_LEFT = 28
GRID_GAP_X = 20
GRID_GAP_Y = 18
CARD_W = 474
CARD_H = 244
CARD_PAD = 22             # inner padding inside a card
FOOTER_Y = 956            # footer text baseline area

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

PAPER = (247, 244, 236)    # warm off-white page
NAVY = (20, 38, 74)        # masthead + footer ink
NAVY_SOFT = (31, 55, 99)   # panel borders / secondary navy
GOLD = (232, 200, 106)     # masthead rule + date line
INK = (24, 24, 24)         # headline ink
BODY_INK = (74, 74, 74)    # caption ink
CARD_FILL = (255, 255, 255)
CARD_EDGE = (214, 210, 198)
FOOTER_INK = (120, 116, 104)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a DejaVu face; fall back to PIL's built-in bitmap font."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


TITLE_FONT = load_font("DejaVuSerif-Bold.ttf", 52)
DATE_FONT = load_font("DejaVuSans.ttf", 21)
TAG_FONT = load_font("DejaVuSans-Bold.ttf", 17)
HEAD_FONT = load_font("DejaVuSans-Bold.ttf", 31)
CAPTION_FONT = load_font("DejaVuSans.ttf", 20)
FOOTER_FONT = load_font("DejaVuSans.ttf", 17)

# ---------------------------------------------------------------------------
# The six stories of Saturday 21 November 2026
# ---------------------------------------------------------------------------
# tag: the coloured chip at the top of the card
# tint: chip + icon colour for the story
# headline: short, newspaper-style
# blurb: one sentence of detail
# glyph: which little pictogram to draw in the card's icon disc

STORIES = [
    {
        "tag": "CLIMATE",
        "tint": (31, 122, 90),
        "headline": "COP31 talks run into overtime",
        "blurb": "Antalya negotiations drag past the deadline; the draft deal "
                 "still omits fossil fuels, with a third text due Saturday morning.",
        "glyph": "globe",
    },
    {
        "tag": "SPORT",
        "tint": (176, 92, 24),
        "headline": "Rahul completes the SENA set",
        "blurb": "First Indian opener with Test centuries in all four SENA "
                 "countries, sealed in Wellington.",
        "glyph": "ball",
    },
    {
        "tag": "DISASTER",
        "tint": (140, 52, 52),
        "headline": "6.8 quake shakes central Peru",
        "blurb": "Tremors felt in Lima after the 00:09 UTC shock; "
                 "no casualties reported.",
        "glyph": "quake",
    },
    {
        "tag": "WAR",
        "tint": (94, 58, 130),
        "headline": "Double-tap strike hits Kryvyi Rih",
        "blurb": "A 7-year-old boy and a 20-year-old paramedic killed, 42 hurt; "
                 "a missile also lands in Poland.",
        "glyph": "burst",
    },
    {
        "tag": "U.S. / TECH",
        "tint": (26, 92, 150),
        "headline": "Trump threatens AI data-centre tax",
        "blurb": "\u201cTremendous tax\u201d or a ban on US firms building AI data "
                 "centres abroad: \u201cChina will take all of them.\u201d",
        "glyph": "chip",
    },
    {
        "tag": "DIPLOMACY",
        "tint": (120, 84, 20),
        "headline": "Nepal PM heads to Delhi",
        "blurb": "Balendra Shah\u2019s first foreign trip: a two-day state visit "
                 "to India starting Sunday.",
        "glyph": "flags",
    },
]

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def wrap_words(draw: ImageDraw.ImageDraw, text: str,
               font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word wrap: pack as many whole words per line as fit."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def centred(draw: ImageDraw.ImageDraw, cx: int, y: int, text: str,
            font: ImageFont.FreeTypeFont, fill) -> None:
    """Draw one line of text centred on x=cx."""
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------------------
# Pictograms (all drawn with plain PIL shapes, in white on a tinted disc)
# ---------------------------------------------------------------------------


def paint_globe(draw, cx, cy, r, ink):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=3)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=ink, width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=ink, width=2)
    draw.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
             start=200, end=340, fill=ink, width=2)


def paint_ball(draw, cx, cy, r, ink):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=3)
    draw.arc([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7],
             start=300, end=120, fill=ink, width=2)
    draw.line([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55],
              fill=ink, width=2)


def paint_quake(draw, cx, cy, r, ink):
    pts = [
        (cx - r, cy + r * 0.25),
        (cx - r * 0.55, cy + r * 0.25),
        (cx - r * 0.3, cy - r * 0.6),
        (cx, cy + r * 0.55),
        (cx + r * 0.3, cy - r * 0.35),
        (cx + r * 0.55, cy + r * 0.25),
        (cx + r, cy + r * 0.25),
    ]
    draw.line(pts, fill=ink, width=3, joint="curve")


def paint_burst(draw, cx, cy, r, ink):
    import math
    outer = [(cx + r * math.cos(a), cy + r * math.sin(a))
             for a in [i * math.pi / 4 for i in range(8)]]
    inner = [(cx + r * 0.45 * math.cos(a + math.pi / 8),
              cy + r * 0.45 * math.sin(a + math.pi / 8))
             for a in [i * math.pi / 4 for i in range(8)]]
    star = []
    for o, i in zip(outer, inner):
        star.extend([o, i])
    draw.polygon(star, fill=ink)


def paint_chip(draw, cx, cy, r, ink):
    s = r * 0.95
    draw.rectangle([cx - s, cy - s, cx + s, cy + s], outline=ink, width=3)
    draw.rectangle([cx - s * 0.45, cy - s * 0.45, cx + s * 0.45, cy + s * 0.45],
                   outline=ink, width=2)
    for dx in (-0.55, 0.0, 0.55):
        draw.line([cx + dx * s, cy - s - r * 0.3, cx + dx * s, cy - s],
                  fill=ink, width=2)
        draw.line([cx + dx * s, cy + s, cx + dx * s, cy + s + r * 0.3],
                  fill=ink, width=2)
    for dy in (-0.55, 0.0, 0.55):
        draw.line([cx - s - r * 0.3, cy + dy * s, cx - s, cy + dy * s],
                  fill=ink, width=2)
        draw.line([cx + s, cy + dy * s, cx + s + r * 0.3, cy + dy * s],
                  fill=ink, width=2)


def paint_flags(draw, cx, cy, r, ink):
    draw.line([cx - r * 0.45, cy - r, cx - r * 0.45, cy + r], fill=ink, width=3)
    draw.line([cx + r * 0.45, cy - r, cx + r * 0.45, cy + r], fill=ink, width=3)
    draw.polygon([(cx - r * 0.45, cy - r), (cx + r * 0.25, cy - r * 0.62),
                  (cx - r * 0.45, cy - r * 0.24)], fill=ink)
    draw.polygon([(cx + r * 0.45, cy - r), (cx - r * 0.25, cy - r * 0.62),
                  (cx + r * 0.45, cy - r * 0.24)], fill=ink)


GLYPHS = {
    "globe": paint_globe,
    "ball": paint_ball,
    "quake": paint_quake,
    "burst": paint_burst,
    "chip": paint_chip,
    "flags": paint_flags,
}

# ---------------------------------------------------------------------------
# Page sections
# ---------------------------------------------------------------------------


def paint_masthead(draw: ImageDraw.ImageDraw) -> None:
    """Navy band: paper name, gold rule, date line."""
    draw.rectangle([0, 0, PAGE_W, MASTHEAD_H], fill=NAVY)
    centred(draw, PAGE_W // 2, 26, "THE WORLD IN ONE IMAGE", TITLE_FONT,
            (255, 255, 255))
    draw.rectangle([0, MASTHEAD_H - 5, PAGE_W, MASTHEAD_H], fill=GOLD)
    centred(draw, PAGE_W // 2, MASTHEAD_H - 42,
            "SATURDAY  \u00b7  21 NOVEMBER 2026  \u00b7  SIX STORIES, ONE PAGE",
            DATE_FONT, GOLD)


def paint_card(draw: ImageDraw.ImageDraw, story: dict,
               x: int, y: int) -> None:
    """One story card: tag chip, icon disc, headline, caption."""
    tint = story["tint"]
    draw.rounded_rectangle([x, y, x + CARD_W, y + CARD_H], radius=10,
                           fill=CARD_FILL, outline=CARD_EDGE, width=2)

    # Icon disc, top right.
    disc_r = 27
    disc_cx = x + CARD_W - CARD_PAD - disc_r
    disc_cy = y + CARD_PAD + disc_r
    draw.ellipse([disc_cx - disc_r, disc_cy - disc_r,
                  disc_cx + disc_r, disc_cy + disc_r], fill=tint)
    GLYPHS[story["glyph"]](draw, disc_cx, disc_cy, disc_r * 0.62,
                           (255, 255, 255))

    # Tag chip, top left.
    tag = story["tag"]
    chip_w = draw.textlength(tag, font=TAG_FONT) + 24
    chip_h = 30
    chip_x = x + CARD_PAD
    chip_y = y + CARD_PAD
    draw.rounded_rectangle([chip_x, chip_y, chip_x + chip_w, chip_y + chip_h],
                           radius=15, fill=tint)
    draw.text((chip_x + 12, chip_y + 6), tag, font=TAG_FONT,
              fill=(255, 255, 255))

    # Headline: two lines max, kept clear of the icon disc.
    text_x = x + CARD_PAD
    text_w = CARD_W - 2 * CARD_PAD - 2 * disc_r - 14
    head_lines = wrap_words(draw, story["headline"], HEAD_FONT, text_w)[:2]
    line_y = chip_y + chip_h + 14
    for line in head_lines:
        draw.text((text_x, line_y), line, font=HEAD_FONT, fill=INK)
        line_y += 38

    # Short tinted rule under the headline, then the caption.
    draw.rectangle([text_x, line_y + 2, text_x + 46, line_y + 5], fill=tint)

    # Caption: up to three lines across the full card width.
    caption_lines = wrap_words(draw, story["blurb"], CAPTION_FONT,
                               CARD_W - 2 * CARD_PAD)[:3]
    line_y += 16
    for line in caption_lines:
        draw.text((text_x, line_y), line, font=CAPTION_FONT, fill=BODY_INK)
        line_y += 27


def paint_footer(draw: ImageDraw.ImageDraw) -> None:
    centred(draw, PAGE_W // 2, FOOTER_Y,
            "Drawn programmatically with PIL \u2014 every word rendered as "
            "text, no AI image generation.",
            FOOTER_FONT, FOOTER_INK)
    centred(draw, PAGE_W // 2, FOOTER_Y + 24,
            "make.fun \u00b7 news-image-20261121",
            FOOTER_FONT, FOOTER_INK)


# ---------------------------------------------------------------------------
# Build the page
# ---------------------------------------------------------------------------


def build_page() -> Image.Image:
    canvas = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(canvas)
    paint_masthead(draw)
    for index, story in enumerate(STORIES):
        col = index % 2
        row = index // 2
        x = GRID_LEFT + col * (CARD_W + GRID_GAP_X)
        y = GRID_TOP + row * (CARD_H + GRID_GAP_Y)
        paint_card(draw, story, x, y)
    paint_footer(draw)
    return canvas


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "entry.png")
    build_page().save(out_path, format="PNG")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
