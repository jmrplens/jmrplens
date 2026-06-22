"""Enlaces sociales como chips nativos de GitHub (Primer), clicables.

Cada enlace se renderiza como un chip independiente (icono monocromo + label,
estética de botón de GitHub) en su propio SVG, para envolverlo en un <a> en el
README y que sea clicable. Tamaño fijo: en móvil no se encogen a ilegible.
"""
import os
import re

from statsgen.theme import THEMES, FONT_SANS

H = 36
ICON = 16

# Globo dibujado con primitivas (válido y reconocible, sin depender de un path).
_GLOBE = (
    '<circle cx="8" cy="8" r="7.1" fill="none" stroke-width="1.25"/>'
    '<ellipse cx="8" cy="8" rx="3" ry="7.1" fill="none" stroke-width="1.25"/>'
    '<path d="M1 8h14M2.4 4.4h11.2M2.4 11.6h11.2" stroke-width="1.1" fill="none"/>'
)
# LinkedIn (simple-icons, viewBox 0 0 24 24).
_LINKEDIN = (
    '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 '
    '1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 '
    '4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 '
    '2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 '
    '0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 '
    '22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'
)

# (label, url, (viewBox, inner) | ("asset", rel))
LINKS = [
    ("Website", "https://jmrp.io", ("0 0 16 16", _GLOBE)),
    ("LinkedIn", "https://www.linkedin.com/in/jmrplens/", ("0 0 24 24", _LINKEDIN)),
    ("Mastodon", "https://mstdn.jmrp.io/@jmrplens", ("asset", "tech/mastodon")),
]


def _mono_asset(rel, color):
    """Inlina un icono de assets recoloreado a monocromo, quitando el rect de fondo."""
    path = f"assets/icons/{rel}.svg"
    if not os.path.exists(path):
        return f'<rect width="{ICON}" height="{ICON}" rx="3" fill="{color}"/>'
    content = open(path, encoding="utf-8").read()
    vbm = re.search(r'viewBox="([^"]+)"', content)
    vb = vbm.group(1) if vbm else "0 0 24 24"
    wm = re.search(r'<svg[^>]*\bwidth="(\d+)"', content)
    hm = re.search(r'<svg[^>]*\bheight="(\d+)"', content)
    inner = content[content.find(">", content.find("<svg")) + 1: content.rfind("</svg>")]
    if wm and hm:
        w, h = wm.group(1), hm.group(1)
        inner = re.sub(rf'<rect\b[^>]*\bwidth="{w}"[^>]*\bheight="{h}"[^>]*/>', "", inner)
        inner = re.sub(rf'<rect\b[^>]*\bheight="{h}"[^>]*\bwidth="{w}"[^>]*/>', "", inner)
    inner = re.sub(r'\s(?:fill|stroke)="[^"]*"', "", inner)
    return f'<svg width="{ICON}" height="{ICON}" viewBox="{vb}" fill="{color}">{inner}</svg>'


def _icon(spec, color):
    if spec[0] == "asset":
        return _mono_asset(spec[1], color)
    vb, inner = spec
    return (
        f'<svg width="{ICON}" height="{ICON}" viewBox="{vb}" '
        f'fill="{color}" stroke="{color}">{inner}</svg>'
    )


def render_connect_chip_svg(label, spec, theme):
    t = THEMES[theme]
    width = 14 + ICON + 8 + int(len(label) * 7.4) + 14
    return f'''<svg width="{width}" height="{H}" viewBox="0 0 {width} {H}" xmlns="http://www.w3.org/2000/svg">
  <style>.c-label {{ font: 500 13px {FONT_SANS}; fill: {t['fg']}; }}</style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{H - 1}" rx="6" fill="{t['bg_muted']}" stroke="{t['border']}"/>
  <g transform="translate(14, {(H - ICON) // 2})">{_icon(spec, t['accent'])}</g>
  <text class="c-label" x="{14 + ICON + 8}" y="23">{label}</text>
</svg>'''


def slug(label):
    return label.lower()
