"""Montaje del bloque de blog dentro del README."""
import re

BLOG_START = "<!-- BLOG-POSTS:START -->"
BLOG_END = "<!-- BLOG-POSTS:END -->"

_READ_ALL_BADGE = (
    '<p align="center">\n'
    '  <a href="https://jmrp.io/blog">\n'
    '    <img src="https://img.shields.io/badge/📚_Read_all_posts-667eea?style=for-the-badge" '
    'alt="Read all posts"/>\n'
    "  </a>\n"
    "</p>"
)


def _esc(text):
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def build_blog_block(posts):
    """posts: [{"title", "link"}]. Asume que generated/blog-{i}-{theme}.svg ya existen.
    Cada tarjeta es un <a> que envuelve el par dark/light → toda la tarjeta es clicable.
    Las tarjetas se apilan (cada una en su propio párrafo).
    """
    cards = []
    for i, post in enumerate(posts, start=1):
        alt = _esc(post["title"])
        href = _esc(post["link"])
        cards.append(
            f'<a href="{href}">\n'
            f'  <img src="generated/blog-{i}-dark.svg#gh-dark-mode-only" width="100%" alt="{alt}"/>\n'
            f'  <img src="generated/blog-{i}-light.svg#gh-light-mode-only" width="100%" alt="{alt}"/>\n'
            f"</a>"
        )
    return "\n\n".join(cards) + "\n\n" + _READ_ALL_BADGE


def update_readme_blog(content, posts):
    """Reemplaza el contenido entre los marcadores. Lanza ValueError si faltan."""
    if BLOG_START not in content or BLOG_END not in content:
        raise ValueError("Marcadores de blog no encontrados en el README")
    block = build_blog_block(posts)
    pattern = re.escape(BLOG_START) + r".*?" + re.escape(BLOG_END)
    replacement = f"{BLOG_START}\n{block}\n{BLOG_END}"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)
