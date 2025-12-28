#!/usr/bin/env python3
"""
Generate GitHub statistics SVG
Fetches real data from GitHub API and creates a custom SVG visualization
"""

import os
import requests
from datetime import datetime

# GitHub API configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
USERNAME = 'jmrplens'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

def fetch_github_stats():
    """Fetch comprehensive GitHub statistics"""
    
    # Get user data
    user_url = f'https://api.github.com/users/{USERNAME}'
    user_data = requests.get(user_url, headers=HEADERS).json()
    
    # Get all repos (including contributions)
    repos_url = f'https://api.github.com/users/{USERNAME}/repos?per_page=100&type=all'
    repos = requests.get(repos_url, headers=HEADERS).json()
    
    # Calculate statistics
    total_stars = sum(repo['stargazers_count'] for repo in repos if not repo['fork'])
    total_repos = len([repo for repo in repos if not repo['fork']])
    
    # Get languages statistics
    languages_bytes = {}
    for repo in repos:
        if repo['fork']:
            continue
        lang_url = repo['languages_url']
        lang_data = requests.get(lang_url, headers=HEADERS).json()
        for lang, bytes_count in lang_data.items():
            languages_bytes[lang] = languages_bytes.get(lang, 0) + bytes_count
    
    # Sort and get top 8 languages with lines of code, filtering out Pascal
    sorted_langs = sorted(languages_bytes.items(), key=lambda x: x[1], reverse=True)
    # Filter out Pascal and get top 8
    sorted_langs = [(lang, bytes) for lang, bytes in sorted_langs if lang != 'Pascal'][:8]
    total_bytes = sum(languages_bytes.values())
    
    # Estimate lines (50 bytes per line average)
    languages_with_lines = [
        (lang, bytes_count, bytes_count // 50, (bytes_count / total_bytes * 100)) 
        for lang, bytes_count in sorted_langs
    ]
    
    # Get contribution data (approximate from events)
    events_url = f'https://api.github.com/users/{USERNAME}/events/public?per_page=100'
    events = requests.get(events_url, headers=HEADERS).json()
    recent_commits = len([e for e in events if e['type'] == 'PushEvent'])
    
    return {
        'total_stars': total_stars,
        'total_repos': total_repos,
        'public_repos': user_data.get('public_repos', 0),
        'total_commits': recent_commits * 10,  # Rough estimate
        'languages': languages_with_lines,  # (lang, bytes, lines, percent)
        'total_lines': total_bytes // 50,  # Rough estimate: 50 bytes per line average
    }

# Language colors (official GitHub colors)
LANG_COLORS = {
    'C++': '#f34b7d',
    'C': '#555555',
    'Python': '#3572A5',
    'MATLAB': '#e16737',
    'JavaScript': '#f1e05a',
    'Shell': '#89e051',
    'TypeScript': '#2b7489',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'Makefile': '#427819',
}

def load_lang_icon(lang):
    """Load language icon from file and return as embedded SVG"""
    icon_map = {
        'MATLAB': 'matlab_bn',  # Black and white version for stats
        'C': 'c',
        'C++': 'cpp',
        'Python': 'python',
        'JavaScript': 'javascript',
        'HTML': 'html',
        'CSS': 'css',
        'TeX': 'tex',
        'Astro': 'astro',
        'Shell': 'bash_shell',  # Bash shell icon
        'TypeScript': 'typescript',
    }
    
    if lang in icon_map:
        icon_file = f'assets/icons/lang/{icon_map[lang]}.svg'
        if os.path.exists(icon_file):
            try:
                with open(icon_file, 'r') as f:
                    content = f.read()
                    # Extract only inner content without svg wrapper
                    if '<svg' in content and '</svg>' in content:
                        svg_start = content.find('<svg')
                        tag_end = content.find('>', svg_start) + 1
                        svg_close = content.rfind('</svg>')
                        inner = content[tag_end:svg_close].strip()
                        return inner
            except Exception as e:
                print(f"Error loading icon for {lang}: {e}")
    
    # Fallback: simple colored circle
    color = LANG_COLORS.get(lang, '#858585')
    return f'<circle cx="12" cy="12" r="10" fill="{color}"/>'

def generate_svg(stats, theme='dark'):
    """Generate SVG with GitHub statistics for specified theme"""
    
    width = 800
    height = 500  # Increased for 8 languages
    
    
    # Theme-specific colors
    if theme == 'dark':
        bg_fill = '#0d1117'
        bg_stroke = '#30363d'
        title_fill = '#c9d1d9'
        stat_label_fill = '#8b949e'
        stat_value_fill = '#c9d1d9'
        lang_name_fill = '#8b949e'
        lang_lines_fill = '#c9d1d9'
        divider_stroke = '#30363d'
        icon_filter = 'invert(1) brightness(1.2)'
    else:  # light
        bg_fill = '#ffffff'
        bg_stroke = '#e1e4e8'
        title_fill = '#24292e'
        stat_label_fill = '#586069'
        stat_value_fill = '#24292e'
        lang_name_fill = '#586069'
        lang_lines_fill = '#24292e'
        divider_stroke = '#e1e4e8'
        icon_filter = 'none'
    
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
    <style>
      .title {{ font: 600 18px 'Segoe UI', Ubuntu, sans-serif; fill: {title_fill}; }}
      .stat-label {{ font: 400 14px 'Segoe UI', Ubuntu, sans-serif; fill: {stat_label_fill}; }}
      .stat-value {{ font: 700 24px 'Segoe UI', Ubuntu, sans-serif; fill: {stat_value_fill}; }}
      .lang-name {{ font: 400 13px 'Segoe UI', Ubuntu, sans-serif; fill: {lang_name_fill}; }}
      .lang-lines {{ font: 600 12px 'Segoe UI', Ubuntu, sans-serif; fill: {lang_lines_fill}; }}
      .lang-icon {{ filter: {icon_filter}; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" rx="10" fill="{bg_fill}" stroke="{bg_stroke}" stroke-width="1" fill-opacity="0.8"/>
  
  <!-- Title -->
  <text class="title" x="25" y="35">📊 GitHub Statistics</text>
  
  <!-- Stats Grid -->
  <g transform="translate(25, 60)">
    <!-- Total Repos -->
    <text class="stat-label" x="0" y="0">Total Repositories</text>
    <text class="stat-value" x="0" y="28">{stats['total_repos']}</text>
    
    <!-- Total Stars -->
    <text class="stat-label" x="190" y="0">Total Stars</text>
    <text class="stat-value" x="190" y="28">{stats['total_stars']}</text>
    
    <!-- Total Commits (estimate) -->
    <text class="stat-label" x="380" y="0">Commits (est.)</text>
    <text class="stat-value" x="380" y="28">{stats['total_commits']:,}</text>
    
    <!-- Lines of Code (estimate) -->
    <text class="stat-label" x="570" y="0">Lines of Code (est.)</text>
    <text class="stat-value" x="570" y="28">{stats['total_lines']:,}</text>
  </g>
  
  <!-- Divider -->
  <line x1="25" y1="130" x2="{width-25}" y2="130" stroke="{divider_stroke}" stroke-width="1"/>
  
  <!-- Languages Title -->
  <text class="title" x="25" y="165">💻 Most Used Languages</text>
  
  <!-- Languages List -->
  <g transform="translate(25, 180)">
'''
    
    y_offset = 0
    for i, (lang, bytes_count, lines, percent) in enumerate(stats['languages']):
        color = LANG_COLORS.get(lang, '#858585')
        bar_width = (percent / 100) * 500
        
        # Load icon from file or use fallback
        icon_svg = load_lang_icon(lang)
        
        svg += f'''    <!-- {lang} -->
    <g transform="translate(0, {y_offset})">
      <svg x="0" y="-2" width="32" height="32" viewBox="0 0 24 24">
        {icon_svg}
      </svg>
      <text class="lang-name" x="38" y="16">{lang}</text>
      <rect x="120" y="6" width="{bar_width}" height="12" rx="6" fill="{color}" opacity="0.8"/>
      <text class="lang-lines" x="{120 + bar_width + 10}" y="16">{lines:,} lines</text>
    </g>
'''
        y_offset += 35
    
    svg += f'''  </g>
  
  <!-- Footer -->
  <text class="stat-label" x="{width//2}" y="{height-15}" text-anchor="middle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>'''
    
    return svg

if __name__ == '__main__':
    print("Fetching GitHub statistics...")
    stats = fetch_github_stats()
    
    print(f"  - Repos: {stats['total_repos']}")
    print(f"  - Stars: {stats['total_stars']}")
    print(f"  - Top Languages: {[lang for lang, _, _, _ in stats['languages']]}")
    
    os.makedirs('generated', exist_ok=True)
    
    # Generate dark theme
    print("\nGenerating dark theme SVG...")
    dark_svg = generate_svg(stats, theme='dark')
    with open('generated/github-stats-dark.svg', 'w') as f:
        f.write(dark_svg)
    print("✅ Created generated/github-stats-dark.svg")
    
    # Generate light theme
    print("Generating light theme SVG...")
    light_svg = generate_svg(stats, theme='light')
    with open('generated/github-stats-light.svg', 'w') as f:
        f.write(light_svg)
    print("✅ Created generated/github-stats-light.svg")
    
    print("\n✨ Both stat themes generated successfully!")
