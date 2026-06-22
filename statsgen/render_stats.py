"""Render del panel de estadísticas como SVG temático."""
from datetime import datetime

from statsgen.theme import THEMES, LANG_COLORS, load_lang_icon

WIDTH = 800


def _metric(x, label, value):
    return (
        f'<text class="stat-label" x="{x}" y="0">{label}</text>'
        f'<text class="stat-value" x="{x}" y="28">{value}</text>'
    )


def render_stats_svg(lang_pcts, activity, theme):
    t = THEMES[theme]
    rows = len(lang_pcts)
    langs_top = 215
    height = langs_top + rows * 34 + 40

    metrics = [
        ("Repositories", f"{activity['public_repos']:,}"),
        ("Stars", f"{activity['total_stars']:,}"),
        ("Followers", f"{activity['followers']:,}"),
        ("Commits (yr)", f"{activity['commits_year']:,}"),
        ("Contributions (yr)", f"{activity['contributions_year']:,}"),
    ]
    metric_svg = "".join(
        f'<g transform="translate({i * 152}, 0)">{_metric(0, lbl, val)}</g>'
        for i, (lbl, val) in enumerate(metrics)
    )

    lang_rows = []
    y = 0
    for lang, pct in lang_pcts:
        color = LANG_COLORS.get(lang, "#858585")
        bar = (pct / 100) * 480
        icon = load_lang_icon(lang)
        lang_rows.append(
            f'<g transform="translate(0, {y})">'
            f'<svg class="lang-icon" x="0" y="0" width="22" height="22" viewBox="0 0 24 24">{icon}</svg>'
            f'<text class="lang-name" x="30" y="15">{lang}</text>'
            f'<rect x="130" y="5" width="{bar:.1f}" height="12" rx="6" fill="{color}" opacity="0.85"/>'
            f'<text class="lang-pct" x="{130 + bar + 8:.1f}" y="15">{pct:.0f}%</text>'
            f"</g>"
        )
        y += 34

    return f'''<svg width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="100%" style="stop-color:#764ba2"/>
    </linearGradient>
    <style>
      .title {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {t['title']}; }}
      .stat-label {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: {t['label']}; }}
      .stat-value {{ font: 700 22px 'Segoe UI', Ubuntu, sans-serif; fill: {t['value']}; }}
      .lang-name {{ font: 400 13px 'Segoe UI', Ubuntu, sans-serif; fill: {t['name']}; }}
      .lang-pct {{ font: 600 12px 'Segoe UI', Ubuntu, sans-serif; fill: {t['accent']}; }}
      .footer {{ font: 400 11px 'Segoe UI', Ubuntu, sans-serif; fill: {t['label']}; }}
      .lang-icon {{ filter: {t['icon_filter']}; }}
    </style>
  </defs>
  <rect width="{WIDTH}" height="{height}" rx="10" fill="{t['bg']}" stroke="{t['bg_stroke']}" stroke-width="1"/>
  <rect x="0" y="0" width="6" height="{height}" rx="3" fill="url(#grad)"/>
  <text class="title" x="25" y="38">GitHub Statistics</text>
  <g transform="translate(25, 70)">{metric_svg}</g>
  <line x1="25" y1="120" x2="{WIDTH - 25}" y2="120" stroke="{t['divider']}" stroke-width="1"/>
  <text class="title" x="25" y="160">Most Used Languages</text>
  <text class="stat-label" x="25" y="180">Normalized share across repositories (public + private)</text>
  <g transform="translate(25, {langs_top})">
    {"".join(lang_rows)}
  </g>
  <text class="footer" x="{WIDTH // 2}" y="{height - 14}" text-anchor="middle">Updated {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>'''
