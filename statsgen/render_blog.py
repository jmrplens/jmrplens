"""Render de una tarjeta de blog como SVG temático y clicable (vía wrapper <a> en el README)."""
import re

from statsgen.transform import wrap_text
from statsgen.theme import THEMES

WIDTH = 800
HEIGHT = 150


def _esc(text):
    return (
        text.replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def render_blog_card_svg(post, index, theme):
    t = THEMES[theme]
    title_lines = wrap_text(_strip_html(post["title"]), max_chars=46, max_lines=2)
    desc_lines = wrap_text(_strip_html(post["description"]), max_chars=64, max_lines=2)
    date = _esc(post.get("date", ""))

    title_svg = "".join(
        f'<text class="card-title" x="78" y="{48 + i * 26}">{_esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    desc_top = 48 + len(title_lines) * 26 + 8
    desc_svg = "".join(
        f'<text class="card-desc" x="78" y="{desc_top + i * 20}">{_esc(line)}</text>'
        for i, line in enumerate(desc_lines)
    )

    return f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad{index}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="100%" style="stop-color:#764ba2"/>
    </linearGradient>
    <style>
      .card-index {{ font: 700 26px 'Segoe UI', Ubuntu, sans-serif; fill: #ffffff; }}
      .card-date {{ font: 600 11px 'Segoe UI', Ubuntu, sans-serif; fill: #ffffff; opacity: 0.85; }}
      .card-title {{ font: 700 19px 'Segoe UI', Ubuntu, sans-serif; fill: {t['title']}; }}
      .card-desc {{ font: 400 13px 'Segoe UI', Ubuntu, sans-serif; fill: {t['label']}; }}
      .card-more {{ font: 600 13px 'Segoe UI', Ubuntu, sans-serif; fill: #667eea; }}
    </style>
  </defs>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="{t['bg']}" stroke="{t['bg_stroke']}" stroke-width="1"/>
  <rect x="0" y="0" width="58" height="{HEIGHT}" rx="12" fill="url(#grad{index})"/>
  <rect x="46" y="0" width="12" height="{HEIGHT}" fill="url(#grad{index})"/>
  <text class="card-index" x="29" y="60" text-anchor="middle">{index:02d}</text>
  <text class="card-date" x="29" y="80" text-anchor="middle">{date}</text>
  {title_svg}
  {desc_svg}
  <text class="card-more" x="78" y="{HEIGHT - 18}">Read more →</text>
</svg>'''
