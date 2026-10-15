#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg for the GitHub profile README.

Edit PROFILE below, then run:  python3 generate.py  (requires Pillow)
"""
from xml.sax.saxutils import escape

USER = "nicholas@imruliad"

# (section title, [(key, value), ...])
PROFILE = [
    ("Main", [
        ("Occupation", "Systems Software Engineer Intern @ Intel"),
        ("Location", "Sacramento, California"),
        ("Languages", "Python, Java, C++, PowerShell"),
        ("Frameworks/Libraries", "Django, FastAPI, SQLAlchemy, Alembic"),
        ("Tools", "Git, Postman"),
    ]),
    ("Dev Environment", [
        ("Agents", "Claude, Codex"),
        ("Harnesses", "Monocode"),
        ("IDE", "Zed, VS Code"),
        ("Terminal", "Ghostty"),
    ]),
    ("About Me", [
        ("Focus", "AI, Automation, Systems Software, Operating Systems"),
        ("Interests", "AI/ML, Computer Architecture, Database Internals, Compilers, Operating Systems"),
        ("Hobbies", "Camping, Hiking, Coffee Runs"),
        ("Favorite Music", "Sade, Deftones, LAUNDRY DAY"),
    ]),
    ("Contact", [
        ("LinkedIn", "linkedin.com/in/nicholaseovva"),
    ]),
]

THEMES = {
    "dark": {
        "bg": "#161b22", "text": "#c9d1d9", "key": "#d2a8ff",
        "value": "#a5d6ff", "cc": "#616e7f", "art": ("#e6edf3", "#79c0ff"),
    },
    "light": {
        "bg": "#f6f8fa", "text": "#24292f", "key": "#8250df",
        "value": "#0a3069", "cc": "#8c959f", "art": ("#57606a", "#0a3069"),
    },
}

# Layout (monospace grid)
FONT_SIZE = 16
CHAR_W = 9.6          # approx advance width of a 16px monospace glyph
LINE_H = 20
PAD = 30
GAP = 40
INFO_COLS = 64

# ASCII art: a painting rendered as dithered shade blocks in a small font
ART_IMAGE = "art/painting.jpg"
ART_ROWS = 70
ART_FONT_SIZE = 8
ART_CHAR_W = 4.8
ART_LINE_H = 8
SHADES = " ░▒▓█"


def image_to_ascii(path, invert):
    """Convert an image to ART_ROWS lines of shade blocks, keeping its aspect ratio."""
    from PIL import Image, ImageOps

    img = ImageOps.autocontrast(Image.open(path).convert("L"), cutoff=1)
    if invert:
        img = ImageOps.invert(img)
    cols = round(ART_ROWS * ART_LINE_H * img.width / img.height / ART_CHAR_W)
    img = img.resize((cols, ART_ROWS), Image.LANCZOS)
    # Floyd-Steinberg dither down to one gray level per shade glyph
    levels = [round(i * 255 / (len(SHADES) - 1)) for i in range(len(SHADES))]
    palette = Image.new("P", (1, 1))
    palette.putpalette([c for level in levels for c in (level, level, level)])
    px = img.convert("RGB").quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG).load()
    lines = ["".join(SHADES[px[x, y]] for x in range(cols)).rstrip() for y in range(ART_ROWS)]
    return lines, cols


def info_lines():
    """Return lines as lists of (css_class, text) spans, each INFO_COLS wide."""
    def rule(label):
        head = f"{label} "
        return [("", head), ("cc", "─" * (INFO_COLS - len(head) - 4) + "-──-")]

    lines = [rule(USER)]
    for title, rows in PROFILE:
        lines.append(rule(f"- {title}"))
        for key, value in rows:
            # Wrap long comma-separated values onto right-aligned continuation lines
            chunks, budget = [], INFO_COLS - len(key) - 8
            for item in value.split(", "):
                if chunks and len(chunks[-1]) + len(item) + 2 <= budget:
                    chunks[-1] += ", " + item
                else:
                    if chunks:
                        chunks[-1] += ","
                        budget = INFO_COLS - 2
                    chunks.append(item)
            dots = INFO_COLS - len(key) - len(chunks[0]) - 5
            lines.append([
                ("cc", ". "), ("key", key), ("", ":"),
                ("cc", " " + "." * max(dots, 1) + " "), ("value", chunks[0]),
            ])
            for chunk in chunks[1:]:
                lines.append([("", " " * (INFO_COLS - len(chunk))), ("value", chunk)])
    lines.append([("cc", "─" * (INFO_COLS - 4) + "-──-")])
    return lines


def build_svg(theme):
    t = THEMES[theme]
    info = info_lines()
    info_h = LINE_H * len(info)
    art_h = ART_LINE_H * ART_ROWS
    # Dark theme: bright pixels get dense glyphs; light theme: dark pixels do
    art, art_cols = image_to_ascii(ART_IMAGE, invert=(theme == "light"))
    art_w = ART_CHAR_W * art_cols
    width = round(PAD * 2 + art_w + GAP + CHAR_W * INFO_COLS)
    height = PAD * 2 + max(art_h, info_h)
    art_top = PAD + (height - PAD * 2 - art_h) // 2
    info_top = PAD + (height - PAD * 2 - info_h) // 2
    info_x = round(PAD + art_w + GAP, 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,Menlo,monospace" '
        f'width="{width}px" height="{height}px" font-size="{FONT_SIZE}px">',
        "<style>",
        f"text,tspan{{white-space:pre}} .key{{fill:{t['key']}}} .value{{fill:{t['value']}}} .cc{{fill:{t['cc']}}}",
        "</style>",
        f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="{art_top}" x2="0" y2="{art_top + art_h}">'
        f'<stop offset="0" stop-color="{t["art"][0]}"/><stop offset="1" stop-color="{t["art"][1]}"/>'
        "</linearGradient>",
        f'<rect width="{width}px" height="{height}px" fill="{t["bg"]}" rx="15"/>',
        f'<text x="{PAD}" y="{art_top}" fill="url(#g)" font-size="{ART_FONT_SIZE}px">',
    ]
    for j, line in enumerate(art):
        if line:
            parts.append(f'<tspan x="{PAD}" y="{art_top + ART_LINE_H * (j + 1) - 1}">{escape(line)}</tspan>')
    parts.append("</text>")

    parts.append(f'<text x="{info_x}" y="{info_top}" fill="{t["text"]}">')
    for j, spans in enumerate(info):
        body = "".join(
            f'<tspan class="{cls}">{escape(txt)}</tspan>' if cls else escape(txt)
            for cls, txt in spans
        )
        parts.append(f'<tspan x="{info_x}" y="{info_top + LINE_H * (j + 1) - 5}">{body}</tspan>')
    parts.append("</text>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    for theme in THEMES:
        with open(f"{theme}_mode.svg", "w", encoding="utf-8") as f:
            f.write(build_svg(theme))


if __name__ == "__main__":
    main()
