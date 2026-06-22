"""Tema visual compartido (colores, iconos de lenguaje)."""
import os

THEMES = {
    "dark": {
        "bg": "#0d1117", "bg_stroke": "#30363d", "title": "#c9d1d9",
        "label": "#8b949e", "value": "#c9d1d9", "name": "#8b949e",
        "accent": "#c9d1d9", "divider": "#30363d", "icon_filter": "invert(1) brightness(1.2)",
    },
    "light": {
        "bg": "#ffffff", "bg_stroke": "#e1e4e8", "title": "#24292e",
        "label": "#586069", "value": "#24292e", "name": "#586069",
        "accent": "#24292e", "divider": "#e1e4e8", "icon_filter": "none",
    },
}

LANG_COLORS = {
    "C++": "#f34b7d", "C": "#555555", "Python": "#3572A5", "MATLAB": "#e16737",
    "JavaScript": "#f1e05a", "Shell": "#89e051", "TypeScript": "#2b7489",
    "HTML": "#e34c26", "CSS": "#563d7c", "Makefile": "#427819", "TeX": "#3D6117",
    "Go": "#00ADD8", "Astro": "#ff5a03", "MDX": "#fcb32c",
}

_ICON_MAP = {
    "MATLAB": "matlab_bn", "C": "c", "C++": "cpp", "Python": "python",
    "JavaScript": "javascript", "HTML": "html", "CSS": "css", "TeX": "tex",
    "Astro": "astro", "Shell": "bash_shell", "TypeScript": "typescript",
}


def load_lang_icon(lang):
    """Devuelve el contenido interno del SVG del icono, o un círculo de color."""
    name = _ICON_MAP.get(lang)
    if name:
        path = f"assets/icons/lang/{name}.svg"
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
            if "<svg" in content and "</svg>" in content:
                start = content.find(">", content.find("<svg")) + 1
                end = content.rfind("</svg>")
                return content[start:end].strip()
    color = LANG_COLORS.get(lang, "#858585")
    return f'<circle cx="12" cy="12" r="10" fill="{color}"/>'
