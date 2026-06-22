"""Panel de estadísticas como una caja nativa de GitHub (Primer).

Cabecera con título, fila de métricas reales con los números en monoespaciada
(estética de readout de instrumento), y los lenguajes como barra segmentada
full-width + leyenda en dos columnas. Sin números inventados.
"""
from datetime import datetime

from statsgen.theme import THEMES, LANG_COLORS, FONT_SANS, FONT_MONO

WIDTH = 800
PAD = 22
INNER = WIDTH - 2 * PAD


def _metric(x, label, value):
    return (
        f'<text class="m-val" x="{x}" y="0">{value}</text>'
        f'<text class="m-lbl" x="{x}" y="18">{label}</text>'
    )


def render_stats_svg(lang_pcts, activity, theme):
    t = THEMES[theme]

    header_h = 50
    metrics = [
        ("Repositories", f"{activity['public_repos']:,}"),
        ("Stars", f"{activity['total_stars']:,}"),
        ("Followers", f"{activity['followers']:,}"),
        ("Commits / yr", f"{activity['commits_year']:,}"),
        ("Contributions / yr", f"{activity['contributions_year']:,}"),
        ("Repo views / 14d", f"{activity['views_14d']:,}"),
        ("Clones / 14d", f"{activity['clones_14d']:,}"),
    ]
    cols = 4
    mcol = INNER / cols
    m_row_h = 46
    metrics_y = header_h + 32
    metric_svg = "".join(
        f'<g transform="translate({(i % cols) * mcol:.0f}, {(i // cols) * m_row_h})">'
        f"{_metric(0, lbl, val)}</g>"
        for i, (lbl, val) in enumerate(metrics)
    )
    m_rows = (len(metrics) + cols - 1) // cols

    lang_title_y = metrics_y + (m_rows - 1) * m_row_h + 54
    bar_y = lang_title_y + 34
    bar_h = 14
    segs, x = [], 0.0
    for lang, pct in lang_pcts:
        w = pct / 100 * INNER
        color = LANG_COLORS.get(lang, "#858585")
        segs.append(
            f'<rect x="{x:.1f}" y="0" width="{max(w - 2, 1):.1f}" '
            f'height="{bar_h}" rx="3" fill="{color}"/>'
        )
        x += w
    bar_svg = "".join(segs)

    legend_top = bar_y + bar_h + 26
    col_w = INNER / 2
    row_h = 25
    half = (len(lang_pcts) + 1) // 2
    legend = []
    for i, (lang, pct) in enumerate(lang_pcts):
        col, row = (0, i) if i < half else (1, i - half)
        color = LANG_COLORS.get(lang, "#858585")
        legend.append(
            f'<g transform="translate({col * col_w:.0f}, {row * row_h})">'
            f'<circle cx="6" cy="-4" r="6" fill="{color}"/>'
            f'<text class="lg-name" x="20" y="0">{lang}</text>'
            f'<text class="lg-pct" x="{col_w - 20:.0f}" y="0" text-anchor="end">{pct:.0f}%</text>'
            f"</g>"
        )
    legend_svg = "".join(legend)
    height = legend_top + half * row_h + 22

    return f'''<svg width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="card"><rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="6"/></clipPath>
  </defs>
  <style>
    .h-title {{ font: 600 15px {FONT_SANS}; fill: {t['fg']}; }}
    .s-title {{ font: 600 14px {FONT_SANS}; fill: {t['fg']}; }}
    .s-sub {{ font: 400 11px {FONT_SANS}; fill: {t['muted']}; }}
    .m-val {{ font: 600 22px {FONT_MONO}; fill: {t['fg']}; }}
    .m-lbl {{ font: 400 11px {FONT_SANS}; fill: {t['muted']}; }}
    .lg-name {{ font: 400 13px {FONT_SANS}; fill: {t['fg']}; }}
    .lg-pct {{ font: 500 13px {FONT_MONO}; fill: {t['muted']}; }}
    .foot {{ font: 400 10px {FONT_MONO}; fill: {t['muted']}; }}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="6" fill="{t['bg']}"/>
  <g clip-path="url(#card)"><rect x="0" y="0" width="{WIDTH}" height="{header_h}" fill="{t['bg_muted']}"/></g>
  <line x1="0.5" y1="{header_h}" x2="{WIDTH - 0.5}" y2="{header_h}" stroke="{t['border']}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="6" fill="none" stroke="{t['border']}"/>
  <text class="h-title" x="{PAD}" y="31">GitHub Statistics</text>
  <g transform="translate({PAD}, {metrics_y})">{metric_svg}</g>
  <text class="s-title" x="{PAD}" y="{lang_title_y}">Most Used Languages</text>
  <text class="s-sub" x="{PAD}" y="{lang_title_y + 17}">Normalized share across repositories · public + private</text>
  <g transform="translate({PAD}, {bar_y})">{bar_svg}</g>
  <g transform="translate({PAD}, {legend_top})">{legend_svg}</g>
  <text class="foot" x="{WIDTH // 2}" y="{height - 11}" text-anchor="middle">updated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>'''
