"""Tarjeta de blog como una caja nativa de GitHub (Primer).

Sin el número 01/02/03 (el orden solo es recencia, que ya indica la fecha):
eyebrow con la fecha en monoespaciada + 'LATEST' en la más reciente, título
en color de acento (lee como enlace), descripción en muted. La tarjeta entera
es clicable vía el <a> que la envuelve en el README.
"""
import re

from statsgen.transform import wrap_text
from statsgen.theme import THEMES, FONT_SANS, FONT_MONO

WIDTH = 800
PAD = 22


def _esc(text):
    return (
        text.replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def render_blog_card_svg(post, index, theme):
    t = THEMES[theme]
    title_lines = wrap_text(_strip_html(post["title"]), max_chars=52, max_lines=2)
    desc_lines = wrap_text(_strip_html(post["description"]), max_chars=78, max_lines=2)
    date = _esc(post.get("date", "")).upper()

    eyebrow_y = 30
    title_y0 = 56
    title_step = 25
    title_svg = "".join(
        f'<text class="b-title" x="{PAD}" y="{title_y0 + i * title_step}">{_esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    desc_top = title_y0 + len(title_lines) * title_step + 12
    desc_svg = "".join(
        f'<text class="b-desc" x="{PAD}" y="{desc_top + i * 20}">{_esc(line)}</text>'
        for i, line in enumerate(desc_lines)
    )
    more_y = desc_top + (len(desc_lines) - 1) * 20 + 30
    height = more_y + 16

    # 'LATEST' eyebrow-pill sólo en la entrada más reciente (index == 1).
    latest = ""
    if index == 1:
        latest = (
            f'<rect x="{WIDTH - PAD - 62}" y="18" width="62" height="17" rx="8.5" '
            f'fill="none" stroke="{t["accent"]}"/>'
            f'<text class="b-latest" x="{WIDTH - PAD - 31}" y="30" text-anchor="middle">LATEST</text>'
        )

    return f'''<svg width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .b-date {{ font: 500 11px {FONT_MONO}; fill: {t['muted']}; letter-spacing: 0.5px; }}
    .b-latest {{ font: 600 10px {FONT_MONO}; fill: {t['accent']}; letter-spacing: 0.5px; }}
    .b-title {{ font: 600 18px {FONT_SANS}; fill: {t['accent']}; }}
    .b-desc {{ font: 400 13px {FONT_SANS}; fill: {t['muted']}; }}
    .b-more {{ font: 500 13px {FONT_SANS}; fill: {t['accent']}; }}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="6" fill="{t['bg']}" stroke="{t['border']}"/>
  <text class="b-date" x="{PAD}" y="{eyebrow_y}">{date}</text>
  {latest}
  {title_svg}
  {desc_svg}
  <text class="b-more" x="{PAD}" y="{more_y}">Read more →</text>
</svg>'''
