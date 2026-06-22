"""Tech Stack como una caja nativa de GitHub (Primer).

Caja con cabecera y, por categoría, una fila de chips (icono monocromo de la
tecnología + etiqueta) que fluyen y hacen wrap dentro del ancho. El stack es
curado (no viene de la API); vive aquí.
"""
import os
import re

from statsgen.theme import THEMES, FONT_SANS

WIDTH = 800
PAD = 22
INNER = WIDTH - 2 * PAD

# (categoría, [(etiqueta, ruta-icono relativa a assets/icons), ...])
STACK = [
    ("Languages", [
        ("C++", "lang/cpp"), ("C", "lang/c"), ("Python", "lang/python"),
        ("MATLAB", "lang/matlab"), ("JavaScript", "lang/javascript"),
        ("Bash", "lang/bash_shell"),
    ]),
    ("Frameworks & Tools", [
        ("Astro", "lang/astro"), ("Node.js", "tech/nodejs"), ("Docker", "tech/docker"),
        ("Nginx", "tech/nginx"), ("Linux", "tech/linux"), ("Git", "tech/git"),
    ]),
    ("Infrastructure & Services", [
        ("MikroTik", "tech/mikrotik"), ("Matrix", "tech/matrix"),
        ("Mastodon", "tech/mastodon"), ("Home Assistant", "tech/homeassistant"),
        ("Meshtastic", "tech/meshtastic"),
    ]),
]

ICON = 15
CHIP_H = 26
ROW_H = 34
CAT_GAP = 24
CHIP_GAP = 8


def _esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _icon_svg(rel, color):
    """Inlina el icono recoloreado a un único color (monocromo) para integrarlo
    en el tema. Quita el rect de fondo (badge de color) que algunos iconos
    traen, para que no se convierta en un cuadrado sólido. Si no existe el
    archivo, devuelve un punto."""
    path = f"assets/icons/{rel}.svg"
    if not os.path.exists(path):
        return f'<circle cx="{ICON/2}" cy="{ICON/2}" r="{ICON/2}" fill="{color}"/>'
    content = open(path, encoding="utf-8").read()
    vbm = re.search(r'viewBox="([^"]+)"', content)
    vb = vbm.group(1) if vbm else "0 0 24 24"
    wm = re.search(r'<svg[^>]*\bwidth="(\d+)"', content)
    hm = re.search(r'<svg[^>]*\bheight="(\d+)"', content)
    inner = content[content.find(">", content.find("<svg")) + 1: content.rfind("</svg>")]
    # Quitar el rect de fondo del tamaño del lienzo (en cualquier orden de attrs).
    if wm and hm:
        w, h = wm.group(1), hm.group(1)
        inner = re.sub(rf'<rect\b[^>]*\bwidth="{w}"[^>]*\bheight="{h}"[^>]*/>', "", inner)
        inner = re.sub(rf'<rect\b[^>]*\bheight="{h}"[^>]*\bwidth="{w}"[^>]*/>', "", inner)
    inner = re.sub(r'\s(?:fill|stroke)="[^"]*"', "", inner)  # quitar colores → monocromo
    return (
        f'<svg x="0" y="0" width="{ICON}" height="{ICON}" viewBox="{vb}" '
        f'fill="{color}">{inner}</svg>'
    )


def _chip_width(label):
    return 12 + ICON + 6 + int(len(label) * 7.0) + 12


def render_techstack_svg(theme):
    t = THEMES[theme]
    header_h = 46
    body = []
    y = header_h + 24
    for cat, items in STACK:
        body.append(f'<text class="ts-cat" x="{PAD}" y="{y}">{_esc(cat)}</text>')
        y += 12
        cx = 0.0
        for label, rel in items:
            cw = _chip_width(label)
            if cx + cw > INNER and cx > 0:
                cx = 0.0
                y += ROW_H
            body.append(
                f'<g transform="translate({PAD + cx:.0f}, {y})">'
                f'<rect width="{cw}" height="{CHIP_H}" rx="6" fill="{t["bg_muted"]}" stroke="{t["border"]}"/>'
                f'<g transform="translate(11, {(CHIP_H - ICON) / 2:.1f})">{_icon_svg(rel, t["fg"])}</g>'
                f'<text class="ts-label" x="32" y="17">{_esc(label)}</text>'
                f"</g>"
            )
            cx += cw + CHIP_GAP
        y += CHIP_H + CAT_GAP
    height = y - CAT_GAP + 18

    return f'''<svg width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="ts-card"><rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="6"/></clipPath>
  </defs>
  <style>
    .ts-title {{ font: 600 15px {FONT_SANS}; fill: {t['fg']}; }}
    .ts-cat {{ font: 600 11px {FONT_SANS}; fill: {t['muted']}; letter-spacing: 0.3px; }}
    .ts-label {{ font: 500 12.5px {FONT_SANS}; fill: {t['fg']}; }}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="6" fill="{t['bg']}"/>
  <g clip-path="url(#ts-card)"><rect x="0" y="0" width="{WIDTH}" height="{header_h}" fill="{t['bg_muted']}"/></g>
  <line x1="0.5" y1="{header_h}" x2="{WIDTH - 0.5}" y2="{header_h}" stroke="{t['border']}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="6" fill="none" stroke="{t['border']}"/>
  <text class="ts-title" x="{PAD}" y="29">Tech Stack</text>
  {"".join(body)}
</svg>'''
