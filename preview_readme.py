#!/usr/bin/env python3
"""Renderiza README.md a HTML usando la API de markdown de GitHub para
previsualizarlo fiel al perfil real. Reescribe las rutas de imagen a locales
para que los SVG se vean. Luego se captura con Playwright (escritorio/móvil)."""
import os
import re
import requests

GH_MD_CSS = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css"


def render():
    token = os.getenv("STATS_TOKEN") or os.getenv("GITHUB_TOKEN", "")
    headers = {"Authorization": f"bearer {token}"} if token else {}
    md = open("README.md", encoding="utf-8").read()
    resp = requests.post(
        "https://api.github.com/markdown",
        json={"text": md, "mode": "gfm", "context": "jmrplens/jmrplens"},
        headers=headers, timeout=30,
    )
    resp.raise_for_status()
    body = resp.text
    # Resolver rutas relativas y forzar la variante dark (el preview es dark)
    body = body.replace('src="generated/', 'src="../generated/')
    body = re.sub(r'<img[^>]*src="\.\./generated/[^"]+-light\.svg[^"]*"[^>]*>', "", body)
    # Eliminar el fragmento #gh-dark-mode-only para que el navegador muestre el SVG
    body = body.replace("-dark.svg#gh-dark-mode-only", "-dark.svg")
    os.makedirs("preview", exist_ok=True)
    html = (
        f'<!doctype html><html><head><meta charset="utf-8">'
        f'<link rel="stylesheet" href="{GH_MD_CSS}">'
        f'<style>body{{background:#0d1117;margin:0;display:flex;justify-content:center}}'
        f'.markdown-body{{box-sizing:border-box;max-width:880px;padding:32px;width:100%}}</style>'
        f'</head><body><article class="markdown-body">{body}</article></body></html>'
    )
    with open("preview/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ preview/index.html generado. Ábrelo con Playwright (file://...) "
          "y captura a 1280px y 390px.")


if __name__ == "__main__":
    render()
