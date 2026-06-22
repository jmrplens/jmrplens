"""Tema visual compartido (colores de tema y de lenguaje)."""

THEMES = {
    "dark": {
        "bg": "#0d1117", "bg_stroke": "#30363d", "title": "#c9d1d9",
        "label": "#8b949e", "value": "#c9d1d9", "name": "#8b949e",
        "accent": "#c9d1d9", "divider": "#30363d",
    },
    "light": {
        "bg": "#ffffff", "bg_stroke": "#e1e4e8", "title": "#24292e",
        "label": "#586069", "value": "#24292e", "name": "#586069",
        "accent": "#24292e", "divider": "#e1e4e8",
    },
}

# Colores oficiales de GitHub Linguist por lenguaje (para los puntos y barras).
LANG_COLORS = {
    "C++": "#f34b7d", "C": "#555555", "Python": "#3572A5", "MATLAB": "#e16737",
    "JavaScript": "#f1e05a", "Shell": "#89e051", "TypeScript": "#2b7489",
    "HTML": "#e34c26", "CSS": "#563d7c", "Makefile": "#427819", "TeX": "#3D6117",
    "Go": "#00ADD8", "Astro": "#ff5a03", "MDX": "#fcb32c",
}
