#!/usr/bin/env python3
"""
Generate GitHub profile header/banner in both light and dark themes
"""

def generate_banner(theme='dark'):
    """Generate banner SVG for specified theme"""
    
    # Theme-specific colors
    if theme == 'dark':
        bg_color = '#0d1117'
        title_color = '#c9d1d9'
        subtitle_color = '#8b949e'
        accent_color = '#8b949e'
        grad_id = 'grad-dark'
        grad_start = '#667eea'
        grad_end = '#764ba2'
    else:  # light
        bg_color = '#ffffff'
        title_color = '#24292e'
        subtitle_color = '#586069'
        accent_color = '#6a737d'
        grad_id = 'grad-light'
        grad_start = '#667eea'
        grad_end = '#764ba2'
    
    svg = f'''<svg width="1200" height="180" viewBox="0 0 1200 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{grad_start};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{grad_end};stop-opacity:1" />
    </linearGradient>
    <style>
      .title {{ font: bold 64px 'Segoe UI', Ubuntu, sans-serif; fill: {title_color}; }}
      .subtitle {{ font: 400 28px 'Segoe UI', Ubuntu, sans-serif; fill: {subtitle_color}; }}
      .accent {{ font: 300 20px 'Segoe UI', Ubuntu, sans-serif; fill: {accent_color}; opacity: 0.8; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="180" rx="10" fill="{bg_color}"/>
  
  <!-- Gradient accent bar -->
  <rect x="0" y="0" width="8" height="180" rx="10" fill="url(#{grad_id})"/>
  
  <!-- Content -->
  <g transform="translate(40, 60)">
    <text class="title" x="0" y="0">José M. Requena Plens</text>
    <text class="subtitle" x="0" y="45">Full Stack Developer &amp; IoT Specialist</text>
    <text class="accent" x="0" y="75">🚀 Building scalable solutions | 🔧 Open Source Contributor</text>
  </g>
</svg>'''
    
    return svg

if __name__ == '__main__':
    import os
    
    # Ensure assets directory exists
    os.makedirs('assets', exist_ok=True)
    
    # Generate dark theme banner
    print("Generating dark theme banner...")
    dark_svg = generate_banner('dark')
    with open('assets/header-dark.svg', 'w') as f:
        f.write(dark_svg)
    print("✅ Created assets/header-dark.svg")
    
    # Generate light theme banner
    print("Generating light theme banner...")
    light_svg = generate_banner('light')
    with open('assets/header-light.svg', 'w') as f:
        f.write(light_svg)
    print("✅ Created assets/header-light.svg")
    
    print("\n✨ Both banner themes generated successfully!")
