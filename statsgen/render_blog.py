"""Tarjeta de blog como una caja nativa de GitHub (Primer).

Eyebrow con la fecha (mono) + 'LATEST' en la más reciente, título en color de
acento (lee como enlace) y descripción en muted. Si el post tiene portada
(cover), se embebe a la derecha en base64. Altura fija para uniformidad. La
tarjeta entera es clicable vía el <a> del README.
"""
import re

from statsgen.transform import wrap_text
from statsgen.theme import THEMES, FONT_SANS, FONT_MONO

WIDTH = 800
HEIGHT = 176
PAD = 22
IMG_W = 250


def _esc(text):
    return (
        text.replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def render_blog_card_svg(post, index, theme, cover_uri=None):
    t = THEMES[theme]
    has_cover = bool(cover_uri)
    text_right = (WIDTH - IMG_W - 18) if has_cover else (WIDTH - PAD)
    title_max = 36 if has_cover else 52
    desc_max = 50 if has_cover else 78

    title_lines = wrap_text(_strip_html(post["title"]), max_chars=title_max, max_lines=2)
    desc_lines = wrap_text(_strip_html(post["description"]), max_chars=desc_max, max_lines=2)
    date = _esc(post.get("date", "")).upper()

    title_y0, title_step = 52, 25
    title_svg = "".join(
        f'<text class="b-title" x="{PAD}" y="{title_y0 + i * title_step}">{_esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    desc_top = title_y0 + len(title_lines) * title_step + 14
    desc_svg = "".join(
        f'<text class="b-desc" x="{PAD}" y="{desc_top + i * 20}">{_esc(line)}</text>'
        for i, line in enumerate(desc_lines)
    )

    latest = ""
    if index == 1:
        latest = (
            f'<rect x="{text_right - 62}" y="18" width="62" height="17" rx="8.5" '
            f'fill="none" stroke="{t["accent"]}"/>'
            f'<text class="b-latest" x="{text_right - 31}" y="30" text-anchor="middle">LATEST</text>'
        )

    cover_svg = ""
    if has_cover:
        cover_svg = (
            f'<image x="{WIDTH - IMG_W}" y="0" width="{IMG_W}" height="{HEIGHT}" '
            f'preserveAspectRatio="xMidYMid slice" clip-path="url(#bcard)" href="{cover_uri}"/>'
            f'<line x1="{WIDTH - IMG_W}" y1="0" x2="{WIDTH - IMG_W}" y2="{HEIGHT}" stroke="{t["border"]}"/>'
        )

    return f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="bcard"><rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6"/></clipPath>
  </defs>
  <style>
    .b-date {{ font: 500 11px {FONT_MONO}; fill: {t['muted']}; letter-spacing: 0.5px; }}
    .b-latest {{ font: 600 10px {FONT_MONO}; fill: {t['accent']}; letter-spacing: 0.5px; }}
    .b-title {{ font: 600 18px {FONT_SANS}; fill: {t['accent']}; }}
    .b-desc {{ font: 400 13px {FONT_SANS}; fill: {t['muted']}; }}
    .b-more {{ font: 500 13px {FONT_SANS}; fill: {t['accent']}; }}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6" fill="{t['bg']}" stroke="{t['border']}"/>
  {cover_svg}
  <text class="b-date" x="{PAD}" y="30">{date}</text>
  {latest}
  {title_svg}
  {desc_svg}
  <text class="b-more" x="{PAD}" y="{HEIGHT - 20}">Read more →</text>
</svg>'''
