#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg for the GitHub profile README.

Edit PROFILE below, then run:  python3 generate.py
"""
import math
from xml.sax.saxutils import escape

USER = "nicholas@imruliad"

# (section title, [(key, value), ...])
PROFILE = [
    ("Main", [
        ("Occupation", "Systems Software Engineer Intern @ Intel"),
        ("Location", "Folsom, CA"),
        ("Languages", "Python, C++, TypeScript, SystemVerilog"),
        ("Frameworks", "Django"),
        ("Tools", "Git, CMake, Obsidian"),
    ]),
    ("Dev Environment", [
        ("Agents", "Claude Code"),
        ("Harnesses", "TODO"),
        ("IDE", "TODO"),
        ("Terminal", "TODO"),
    ]),
    ("About Me", [
        ("Focus", "Systems, Hardware, AI"),
        ("Interests", "Computer Architecture, Graphics, ML"),
        ("Hobbies", "TODO"),
        ("Favorite Music", "TODO"),
    ]),
    ("Contact", [
        ("LinkedIn", "TODO"),
    ]),
]

THEMES = {
    "dark": {
        "bg": "#161b22", "text": "#c9d1d9", "key": "#d2a8ff",
        "value": "#a5d6ff", "cc": "#616e7f", "art": ("#d2a8ff", "#79c0ff"),
    },
    "light": {
        "bg": "#f6f8fa", "text": "#24292f", "key": "#8250df",
        "value": "#0a3069", "cc": "#8c959f", "art": ("#8250df", "#0969da"),
    },
}

# Layout (monospace grid)
FONT_SIZE = 16
CHAR_W = 9.6          # approx advance width of a 16px monospace glyph
LINE_H = 20
PAD = 30
ART_COLS, ART_ROWS = 46, 24
GAP_COLS = 4
INFO_COLS = 60

# Animation
FRAMES = 60
FRAME_SECONDS = 0.08


def donut_frame(a, b):
    """Render one frame of a1k0n's spinning torus as a list of strings."""
    lum_chars = ".,-~:;=!*#$@"
    r1, r2, k2 = 1.0, 2.0, 5.0
    k1 = ART_COLS * k2 * 3 / (8 * (r1 + r2))
    out = [[" "] * ART_COLS for _ in range(ART_ROWS)]
    zbuf = [[0.0] * ART_COLS for _ in range(ART_ROWS)]
    ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    theta = 0.0
    while theta < 2 * math.pi:
        ct, st = math.cos(theta), math.sin(theta)
        phi = 0.0
        while phi < 2 * math.pi:
            cp, sp = math.cos(phi), math.sin(phi)
            cx, cy = r2 + r1 * ct, r1 * st
            x = cx * (cb * cp + sa * sb * sp) - cy * ca * sb
            y = cx * (sb * cp - sa * cb * sp) + cy * ca * cb
            z = k2 + ca * cx * sp + cy * sa
            ooz = 1 / z
            xp = int(ART_COLS / 2 + k1 * ooz * x)
            yp = int(ART_ROWS / 2 - k1 * ooz * y / 2)
            lum = cp * ct * sb - ca * ct * sp - sa * st + cb * (ca * st - ct * sa * sp)
            if lum > 0 and 0 <= xp < ART_COLS and 0 <= yp < ART_ROWS and ooz > zbuf[yp][xp]:
                zbuf[yp][xp] = ooz
                out[yp][xp] = lum_chars[min(int(lum * 8), len(lum_chars) - 1)]
            phi += 0.02
        theta += 0.07
    return ["".join(row).rstrip() for row in out]


def info_lines():
    """Return lines as lists of (css_class, text) spans, each INFO_COLS wide."""
    def rule(label):
        head = f"{label} "
        return [("", head), ("cc", "─" * (INFO_COLS - len(head) - 4) + "-──-")]

    lines = [rule(USER)]
    for title, rows in PROFILE:
        lines.append(rule(f"- {title}"))
        for key, value in rows:
            dots = INFO_COLS - len(key) - len(value) - 6
            lines.append([
                ("cc", ". "), ("key", key), ("", ":"),
                ("cc", " " + "." * max(dots, 1) + " "), ("value", value),
            ])
    lines.append([("cc", "─" * (INFO_COLS - 4) + "-──-")])
    return lines


def build_svg(theme, frames):
    t = THEMES[theme]
    info = info_lines()
    rows = max(ART_ROWS, len(info))
    width = round(PAD * 2 + CHAR_W * (ART_COLS + GAP_COLS + INFO_COLS))
    height = PAD * 2 + LINE_H * rows
    art_top = PAD + LINE_H * ((rows - ART_ROWS) // 2)
    info_top = PAD + LINE_H * ((rows - len(info)) // 2)
    info_x = round(PAD + CHAR_W * (ART_COLS + GAP_COLS), 1)
    total = FRAMES * FRAME_SECONDS
    step = 100 / FRAMES

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,Menlo,monospace" '
        f'width="{width}px" height="{height}px" font-size="{FONT_SIZE}px">',
        "<style>",
        f"text,tspan{{white-space:pre}} .key{{fill:{t['key']}}} .value{{fill:{t['value']}}} .cc{{fill:{t['cc']}}}",
        f".f{{opacity:0;animation:spin {total:.2f}s steps(1,end) infinite}} #f0{{opacity:1}}",
        f"@keyframes spin{{0%{{opacity:1}}{step:.4f}%{{opacity:0}}100%{{opacity:0}}}}",
        "</style>",
        f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="{PAD}" y1="{art_top}" '
        f'x2="{PAD + CHAR_W * ART_COLS:.0f}" y2="{art_top + LINE_H * ART_ROWS}">'
        f'<stop offset="0" stop-color="{t["art"][0]}"/><stop offset="1" stop-color="{t["art"][1]}"/>'
        "</linearGradient>",
        f'<rect width="{width}px" height="{height}px" fill="{t["bg"]}" rx="15"/>',
    ]
    for i, frame in enumerate(frames):
        delay = -(FRAMES - i) * FRAME_SECONDS if i else 0
        parts.append(f'<g class="f" id="f{i}" style="animation-delay:{delay:.2f}s"><text fill="url(#g)">')
        for j, line in enumerate(frame):
            if line:
                parts.append(f'<tspan x="{PAD}" y="{art_top + LINE_H * (j + 1)}">{escape(line)}</tspan>')
        parts.append("</text></g>")

    parts.append(f'<text x="{info_x}" y="{info_top}" fill="{t["text"]}">')
    for j, spans in enumerate(info):
        body = "".join(
            f'<tspan class="{cls}">{escape(txt)}</tspan>' if cls else escape(txt)
            for cls, txt in spans
        )
        parts.append(f'<tspan x="{info_x}" y="{info_top + LINE_H * (j + 1)}">{body}</tspan>')
    parts.append("</text>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    frames = [
        donut_frame(1.0 + 2 * math.pi * k / FRAMES, 0.6 + 2 * math.pi * k / FRAMES)
        for k in range(FRAMES)
    ]
    for theme in THEMES:
        with open(f"{theme}_mode.svg", "w", encoding="utf-8") as f:
            f.write(build_svg(theme, frames))


if __name__ == "__main__":
    main()
