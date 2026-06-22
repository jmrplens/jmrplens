"""Tokens de tema alineados con GitHub Primer (claro y oscuro).

Los valores se extrajeron de las variables CSS reales de github.com
(--bgColor-*, --borderColor-*, --fgColor-*) para que los paneles generados
se integren como una caja nativa más de GitHub en ambos temas.
"""

# Stacks de fuente de GitHub. En un SVG renderizado como <img> no se carga
# la webfont "Mona Sans", así que se cae al mismo stack de sistema que usa
# GitHub como fallback; los datos van en monoespaciada (estética de readout).
FONT_SANS = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', "
    "Helvetica, Arial, sans-serif"
)
FONT_MONO = (
    "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
    "'Liberation Mono', monospace"
)

THEMES = {
    "dark": {
        "bg": "#0d1117", "bg_muted": "#151b23", "border": "#3d444d",
        "fg": "#f0f6fc", "muted": "#9198a1", "accent": "#4493f8",
        "success": "#3fb950",
    },
    "light": {
        "bg": "#ffffff", "bg_muted": "#f6f8fa", "border": "#d1d9e0",
        "fg": "#1f2328", "muted": "#59636e", "accent": "#0969da",
        "success": "#1a7f37",
    },
}

# Colores oficiales de GitHub Linguist por lenguaje (puntos y barra).
LANG_COLORS = {
    "C++": "#f34b7d", "C": "#555555", "Python": "#3572A5", "MATLAB": "#e16737",
    "JavaScript": "#f1e05a", "Shell": "#89e051", "TypeScript": "#2b7489",
    "HTML": "#e34c26", "CSS": "#563d7c", "Makefile": "#427819", "TeX": "#3D6117",
    "Go": "#00ADD8", "Astro": "#ff5a03", "MDX": "#fcb32c",
}
