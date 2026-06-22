"""Montaje del bloque de blog dentro del README."""
import re

BLOG_START = "<!-- BLOG-POSTS:START -->"
BLOG_END = "<!-- BLOG-POSTS:END -->"


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
        # <picture> + prefers-color-scheme: el truco "#gh-dark-mode-only" NO
        # oculta variantes cuando el <img> va dentro de un <a>; <picture> sí.
        cards.append(
            f'<a href="{href}">\n'
            f"  <picture>\n"
            f'    <source media="(prefers-color-scheme: dark)" srcset="generated/blog-{i}-dark.svg"/>\n'
            f'    <img src="generated/blog-{i}-light.svg" width="100%" alt="{alt}"/>\n'
            f"  </picture>\n"
            f"</a>"
        )
    # Sin botón "Read all posts": cada tarjeta ya enlaza a su post.
    return "\n\n".join(cards)


def update_readme_blog(content, posts):
    """Reemplaza el contenido entre los marcadores. Lanza ValueError si faltan."""
    if BLOG_START not in content or BLOG_END not in content:
        raise ValueError("Marcadores de blog no encontrados en el README")
    block = build_blog_block(posts)
    pattern = re.escape(BLOG_START) + r".*?" + re.escape(BLOG_END)
    replacement = f"{BLOG_START}\n{block}\n{BLOG_END}"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)
