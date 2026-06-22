# Profile README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar el README autogenerado del perfil: tarjetas de blog SVG apiladas y clicables, y un panel de estadísticas con lenguajes normalizados (incl. privados) + métricas reales de actividad.

**Architecture:** Se refactoriza el monolítico `generate_stats.py` en un paquete `statsgen/` con módulos de responsabilidad única (transformaciones puras, fetch GraphQL/RSS, render de SVG, montaje del README). Las funciones puras se desarrollan con TDD; el render de SVG se testea por propiedades estructurales (well-formed XML + substrings clave). Un orquestador delgado los conecta. La verificación visual final se hace con Playwright (escritorio + móvil).

**Tech Stack:** Python 3.11, `requests`, GitHub GraphQL API v4, `pytest` (tests), Playwright MCP (verificación visual).

## Global Constraints

- Lenguajes normalizados: por cada repo, `size_lang / size_total_repo`, sumado entre repos no-fork. Display: top-8 reescalado a sumar 100%.
- Privados: solo en lenguajes (agregado). Recuentos visibles (repos, stars) usan solo datos públicos.
- Token: `os.getenv("STATS_TOKEN") or os.getenv("GITHUB_TOKEN", "")`. GraphQL header `Authorization: bearer <token>`.
- Username fijo: `jmrplens`.
- SVG temático en dos archivos: `*-dark.svg` (`#gh-dark-mode-only`) y `*-light.svg` (`#gh-light-mode-only`).
- Paleta de marca: gradiente `#667eea → #764ba2`. Fuentes `'Segoe UI', Ubuntu, sans-serif`.
- Nº de posts: 3. RSS: `https://jmrp.io/rss.xml`.
- Sin números inventados (nada de bytes÷50 ni commits×10).
- Marcadores README: `<!-- BLOG-POSTS:START -->` / `<!-- BLOG-POSTS:END -->`.

---

### Task 1: Normalización de lenguajes y porcentajes (funciones puras)

**Files:**
- Create: `statsgen/__init__.py` (vacío)
- Create: `statsgen/transform.py`
- Create: `tests/test_transform_languages.py`
- Create: `requirements-dev.txt`

**Interfaces:**
- Produces:
  - `normalize_languages(repos: list[dict]) -> dict[str, float]` — `repos` son nodos con forma `{"languages": {"edges": [{"size": int, "node": {"name": str}}]}}`.
  - `languages_to_percentages(weights: dict[str, float], top_n: int = 8) -> list[tuple[str, float]]` — ordenado desc, reescalado a sumar 100.

- [ ] **Step 1: Crear `requirements-dev.txt`**

```
pytest==8.2.0
```

- [ ] **Step 2: Escribir el test que falla**

`tests/test_transform_languages.py`:
```python
from statsgen.transform import normalize_languages, languages_to_percentages


def _repo(*langs):
    return {"languages": {"edges": [{"size": s, "node": {"name": n}} for n, s in langs]}}


def test_normalize_single_big_repo_does_not_dominate():
    # Repo A: 1MB de Go. Repo B: 1KB de MATLAB (90%) + C (10%).
    repos = [
        _repo(("Go", 1_000_000)),
        _repo(("MATLAB", 900), ("C", 100)),
    ]
    weights = normalize_languages(repos)
    # Cada repo aporta cuota 1.0 en total; Go=1.0, MATLAB=0.9, C=0.1
    assert weights["Go"] == 1.0
    assert round(weights["MATLAB"], 2) == 0.9
    assert round(weights["C"], 2) == 0.1


def test_normalize_skips_empty_repos():
    repos = [_repo(), {"languages": {"edges": []}}, _repo(("Python", 50))]
    weights = normalize_languages(repos)
    assert weights == {"Python": 1.0}


def test_percentages_sum_to_100_and_respect_top_n():
    weights = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0}
    pcts = languages_to_percentages(weights, top_n=2)
    assert [l for l, _ in pcts] == ["A", "B"]
    assert round(sum(p for _, p in pcts), 5) == 100.0
    assert round(pcts[0][1], 2) == round(4 / 7 * 100, 2)


def test_percentages_empty_input():
    assert languages_to_percentages({}, top_n=8) == []
```

- [ ] **Step 3: Ejecutar el test y verificar que falla**

Run: `python -m pytest tests/test_transform_languages.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'statsgen'`.

- [ ] **Step 4: Implementar las funciones**

`statsgen/__init__.py`: archivo vacío.

`statsgen/transform.py`:
```python
"""Transformaciones puras de datos para el README autogenerado."""


def normalize_languages(repos):
    """Cuota de cada lenguaje dentro de cada repo (size/total_repo), sumada
    entre repos no-fork. Ningún repo individual puede dominar el agregado.

    repos: lista de nodos {"languages": {"edges": [{"size": int,
           "node": {"name": str}}]}}.
    Devuelve {lang: weight_float}.
    """
    weights = {}
    for repo in repos:
        edges = repo.get("languages", {}).get("edges", [])
        total = sum(e["size"] for e in edges)
        if total == 0:
            continue
        for e in edges:
            name = e["node"]["name"]
            weights[name] = weights.get(name, 0.0) + e["size"] / total
    return weights


def languages_to_percentages(weights, top_n=8):
    """Top-N lenguajes por peso, reescalados a sumar 100%.
    Devuelve [(lang, pct_float)] ordenado desc.
    """
    top = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    total = sum(w for _, w in top)
    if total == 0:
        return []
    return [(lang, w / total * 100) for lang, w in top]
```

- [ ] **Step 5: Ejecutar el test y verificar que pasa**

Run: `python -m pytest tests/test_transform_languages.py -v`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add statsgen/__init__.py statsgen/transform.py tests/test_transform_languages.py requirements-dev.txt
git commit -m "feat(stats): normalización de lenguajes y porcentajes (TDD)"
```

---

### Task 2: Wrapping de texto y montaje del bloque de blog (funciones puras)

**Files:**
- Modify: `statsgen/transform.py` (añadir `wrap_text`)
- Create: `statsgen/readme.py`
- Create: `tests/test_transform_wrap.py`
- Create: `tests/test_readme_block.py`

**Interfaces:**
- Consumes: nada de tareas previas.
- Produces:
  - `wrap_text(text: str, max_chars: int, max_lines: int) -> list[str]` — word-wrap greedy; si no cabe, añade `…` al final de la última línea.
  - `build_blog_block(posts: list[dict]) -> str` — `posts` con `{"title": str, "link": str}`. Devuelve el markdown (tarjetas clicables apiladas + badge "Read all posts").
  - `update_readme_blog(content: str, posts: list[dict]) -> str` — reemplaza el bloque entre marcadores. Lanza `ValueError` si faltan marcadores.

- [ ] **Step 1: Escribir el test que falla (wrap)**

`tests/test_transform_wrap.py`:
```python
from statsgen.transform import wrap_text


def test_wrap_fits_in_one_line():
    assert wrap_text("hello world", 20, 2) == ["hello world"]


def test_wrap_breaks_on_words():
    assert wrap_text("one two three four", 8, 3) == ["one two", "three", "four"]


def test_wrap_truncates_with_ellipsis_when_overflowing():
    out = wrap_text("alpha beta gamma delta epsilon", 11, 2)
    assert len(out) == 2
    assert out[-1].endswith("…")
    assert all(len(line) <= 11 for line in out)
```

- [ ] **Step 2: Escribir el test que falla (readme block)**

`tests/test_readme_block.py`:
```python
from statsgen.readme import build_blog_block, update_readme_blog, BLOG_START, BLOG_END


POSTS = [
    {"title": "First Post", "link": "https://jmrp.io/blog/1/"},
    {"title": 'Quote "X" Post', "link": "https://jmrp.io/blog/2/"},
]


def test_build_block_has_one_card_per_post_clickable():
    block = build_blog_block(POSTS)
    # Una tarjeta clicable por post, con par dark/light dentro del enlace
    assert block.count('<a href="https://jmrp.io/blog/1/">') == 1
    assert "generated/blog-1-dark.svg#gh-dark-mode-only" in block
    assert "generated/blog-1-light.svg#gh-light-mode-only" in block
    assert "generated/blog-2-dark.svg#gh-dark-mode-only" in block
    # El badge "Read all posts" se mantiene
    assert "jmrp.io/blog" in block


def test_build_block_escapes_alt_quotes():
    block = build_blog_block(POSTS)
    assert 'alt="Quote &quot;X&quot; Post"' in block


def test_update_readme_replaces_between_markers():
    content = f"intro\n{BLOG_START}\nOLD\n{BLOG_END}\noutro"
    out = update_readme_blog(content, POSTS)
    assert "OLD" not in out
    assert "intro" in out and "outro" in out
    assert out.count(BLOG_START) == 1 and out.count(BLOG_END) == 1


def test_update_readme_missing_markers_raises():
    import pytest
    with pytest.raises(ValueError):
        update_readme_blog("no markers here", POSTS)
```

- [ ] **Step 3: Ejecutar y verificar que fallan**

Run: `python -m pytest tests/test_transform_wrap.py tests/test_readme_block.py -v`
Expected: FAIL (`ImportError` / función no definida).

- [ ] **Step 4: Implementar `wrap_text` en `statsgen/transform.py`**

Añadir al final de `statsgen/transform.py`:
```python
def wrap_text(text, max_chars, max_lines):
    """Word-wrap greedy a <=max_lines líneas de <=max_chars caracteres.
    Si el texto no cabe entero, recorta y añade '…' a la última línea.
    """
    words = text.split()
    lines = []
    current = ""
    overflow = False
    for i, word in enumerate(words):
        candidate = word if not current else current + " " + word
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word[:max_chars]
        if len(lines) == max_lines:
            current = ""
            overflow = True
            break
    if current and len(lines) < max_lines:
        lines.append(current)

    consumed_words = len(" ".join(lines).split())
    if overflow or consumed_words < len(words):
        last = lines[-1] if lines else ""
        while last and len(last) + 1 > max_chars:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines
```

- [ ] **Step 5: Implementar `statsgen/readme.py`**

`statsgen/readme.py`:
```python
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
        cards.append(
            f'<a href="{post["link"]}">\n'
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
```

- [ ] **Step 6: Ejecutar y verificar que pasan**

Run: `python -m pytest tests/test_transform_wrap.py tests/test_readme_block.py -v`
Expected: all passed.

- [ ] **Step 7: Commit**

```bash
git add statsgen/transform.py statsgen/readme.py tests/test_transform_wrap.py tests/test_readme_block.py
git commit -m "feat(blog): wrapping de texto y montaje del bloque de tarjetas (TDD)"
```

---

### Task 3: Capa de fetch (GraphQL + RSS) con red mockeada

**Files:**
- Create: `statsgen/fetch.py`
- Create: `tests/test_fetch.py`
- Modify: `requirements.txt` (asegurar `requests`)

**Interfaces:**
- Consumes: nada.
- Produces:
  - `graphql(query: str, token: str) -> dict` — POST a GraphQL; lanza `RuntimeError` si la respuesta trae `errors`.
  - `fetch_stats(token: str) -> tuple[dict, list[dict]]` — devuelve `(activity, language_repos)` donde `activity = {"public_repos", "total_stars", "followers", "commits_year", "contributions_year"}` y `language_repos` es la lista de nodos para `normalize_languages`.
  - `fetch_blog_posts(num_posts: int = 3) -> list[dict]` — `[{"title", "link", "description", "date"}]` desde el RSS.

- [ ] **Step 1: Asegurar `requests` en `requirements.txt`**

Contenido de `requirements.txt`:
```
requests==2.31.0
```

- [ ] **Step 2: Escribir el test que falla**

`tests/test_fetch.py`:
```python
import statsgen.fetch as fetch


SAMPLE_GQL = {
    "user": {
        "followers": {"totalCount": 34},
        "contributionsCollection": {
            "totalCommitContributions": 1116,
            "contributionCalendar": {"totalContributions": 1516},
        },
        "repositories": {
            "totalCount": 18,
            "nodes": [{"stargazerCount": 200}, {"stargazerCount": 50}],
        },
    },
    "viewer": {
        "repositories": {
            "nodes": [
                {"languages": {"edges": [{"size": 100, "node": {"name": "C"}}]}},
            ]
        }
    },
}


def test_fetch_stats_maps_activity_and_languages(monkeypatch):
    monkeypatch.setattr(fetch, "graphql", lambda q, t: SAMPLE_GQL)
    activity, langs = fetch.fetch_stats("tok")
    assert activity == {
        "public_repos": 18,
        "total_stars": 250,
        "followers": 34,
        "commits_year": 1116,
        "contributions_year": 1516,
    }
    assert langs == SAMPLE_GQL["viewer"]["repositories"]["nodes"]


def test_graphql_raises_on_errors(monkeypatch):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return {"errors": [{"message": "bad"}]}
    monkeypatch.setattr(fetch.requests, "post", lambda *a, **k: FakeResp())
    import pytest
    with pytest.raises(RuntimeError):
        fetch.graphql("query", "tok")


RSS = b"""<?xml version="1.0"?><rss><channel>
<item><title>Post A</title><link>https://jmrp.io/blog/a/</link>
<description>Desc A</description><pubDate>Mon, 01 Jun 2026 00:00:00 GMT</pubDate></item>
<item><title>Post B</title><link>https://jmrp.io/blog/b/</link>
<description>Desc B</description><pubDate>Sun, 01 May 2026 00:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_fetch_blog_posts_parses_rss(monkeypatch):
    class FakeResp:
        content = RSS
        def raise_for_status(self): pass
    monkeypatch.setattr(fetch.requests, "get", lambda *a, **k: FakeResp())
    posts = fetch.fetch_blog_posts(num_posts=2)
    assert [p["title"] for p in posts] == ["Post A", "Post B"]
    assert posts[0]["link"] == "https://jmrp.io/blog/a/"
    assert posts[0]["date"] == "Jun 2026"
```

- [ ] **Step 3: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_fetch.py -v`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 4: Implementar `statsgen/fetch.py`**

```python
"""Obtención de datos: GraphQL (stats) y RSS (blog)."""
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests

GRAPHQL_URL = "https://api.github.com/graphql"
USERNAME = "jmrplens"
BLOG_RSS_URL = "https://jmrp.io/rss.xml"

STATS_QUERY = """query {
  user(login: "jmrplens") {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
    repositories(privacy: PUBLIC, isFork: false, ownerAffiliations: OWNER, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
  }
  viewer {
    repositories(isFork: false, ownerAffiliations: OWNER, first: 100) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}"""


def graphql(query, token):
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": query},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def fetch_stats(token):
    data = graphql(STATS_QUERY, token)
    user = data["user"]
    pub = user["repositories"]
    cc = user["contributionsCollection"]
    activity = {
        "public_repos": pub["totalCount"],
        "total_stars": sum(n["stargazerCount"] for n in pub["nodes"]),
        "followers": user["followers"]["totalCount"],
        "commits_year": cc["totalCommitContributions"],
        "contributions_year": cc["contributionCalendar"]["totalContributions"],
    }
    language_repos = data["viewer"]["repositories"]["nodes"]
    return activity, language_repos


def _fmt_date(raw):
    try:
        return parsedate_to_datetime(raw).strftime("%b %Y")
    except (TypeError, ValueError):
        return ""


def fetch_blog_posts(num_posts=3):
    try:
        resp = requests.get(BLOG_RSS_URL, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except (requests.RequestException, ET.ParseError) as e:
        print(f"⚠️  Error obteniendo RSS: {e}")
        return []

    posts = []
    for item in root.findall(".//item")[:num_posts]:
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        desc = item.findtext("description", "") or ""
        date = _fmt_date(item.findtext("pubDate", ""))
        if title and link:
            posts.append({"title": title, "link": link, "description": desc, "date": date})
    return posts
```

- [ ] **Step 5: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_fetch.py -v`
Expected: all passed.

- [ ] **Step 6: Commit**

```bash
git add statsgen/fetch.py tests/test_fetch.py requirements.txt
git commit -m "feat(fetch): capa GraphQL + RSS con tests mockeados"
```

---

### Task 4: Render del panel de estadísticas SVG

**Files:**
- Create: `statsgen/render_stats.py`
- Create: `statsgen/theme.py`
- Create: `tests/test_render_stats.py`

**Interfaces:**
- Consumes: salida de `languages_to_percentages` (`[(lang, pct)]`) y `activity` dict de `fetch_stats`.
- Produces:
  - `statsgen/theme.py`: `THEMES: dict[str, dict]`, `LANG_COLORS: dict[str, str]`, `load_lang_icon(lang) -> str`.
  - `render_stats_svg(lang_pcts: list[tuple[str, float]], activity: dict, theme: str) -> str` — SVG well-formed.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_render_stats.py`:
```python
from xml.dom import minidom
from statsgen.render_stats import render_stats_svg

ACTIVITY = {
    "public_repos": 18, "total_stars": 250, "followers": 34,
    "commits_year": 1116, "contributions_year": 1516,
}
LANGS = [("MATLAB", 40.0), ("Python", 30.0), ("C", 20.0), ("C++", 10.0)]


def test_render_stats_is_well_formed_svg():
    svg = render_stats_svg(LANGS, ACTIVITY, theme="dark")
    minidom.parseString(svg)  # lanza si no es XML válido
    assert svg.lstrip().startswith("<svg")


def test_render_stats_shows_real_metrics_no_invented():
    svg = render_stats_svg(LANGS, ACTIVITY, theme="dark")
    assert "1,116" in svg          # commits del año, con separador de miles
    assert "1,516" in svg          # contribuciones
    assert "250" in svg            # stars
    assert "34" in svg             # followers
    assert "18" in svg             # repos públicos
    assert "lines" not in svg.lower()   # sin "lines" inventadas


def test_render_stats_shows_language_percentages():
    svg = render_stats_svg(LANGS, ACTIVITY, theme="light")
    assert "MATLAB" in svg
    assert "40%" in svg


def test_render_stats_dark_and_light_differ():
    dark = render_stats_svg(LANGS, ACTIVITY, theme="dark")
    light = render_stats_svg(LANGS, ACTIVITY, theme="light")
    assert dark != light
    assert "#0d1117" in dark       # fondo oscuro
    assert "#ffffff" in light      # fondo claro
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_render_stats.py -v`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implementar `statsgen/theme.py`**

```python
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
```

- [ ] **Step 4: Implementar `statsgen/render_stats.py`**

```python
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
```

- [ ] **Step 5: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_render_stats.py -v`
Expected: all passed.

- [ ] **Step 6: Commit**

```bash
git add statsgen/theme.py statsgen/render_stats.py tests/test_render_stats.py
git commit -m "feat(stats): render del panel SVG (lenguajes % + métricas reales)"
```

---

### Task 5: Render de tarjeta de blog SVG

**Files:**
- Create: `statsgen/render_blog.py`
- Create: `tests/test_render_blog.py`

**Interfaces:**
- Consumes: `wrap_text` (Task 2), `THEMES` (Task 4), un post `{"title", "description", "date"}`.
- Produces: `render_blog_card_svg(post: dict, index: int, theme: str) -> str` — SVG well-formed, ancho 800, alto fijo.

- [ ] **Step 1: Escribir el test que falla**

`tests/test_render_blog.py`:
```python
from xml.dom import minidom
from statsgen.render_blog import render_blog_card_svg

POST = {
    "title": "Your 4-Digit PIN Is Fine: Device-Bound Keys on ESP32-S3",
    "description": "Why PBKDF2 iterations can't protect a 4-digit PIN on a microcontroller.",
    "date": "Jun 2026",
}


def test_card_is_well_formed_svg():
    svg = render_blog_card_svg(POST, index=1, theme="dark")
    minidom.parseString(svg)
    assert svg.lstrip().startswith("<svg")


def test_card_contains_index_and_read_more():
    svg = render_blog_card_svg(POST, index=1, theme="dark")
    assert "01" in svg
    assert "Jun 2026" in svg
    assert "Read more" in svg


def test_card_escapes_xml_special_chars():
    post = {"title": "A & B <C>", "description": 'He said "hi"', "date": ""}
    svg = render_blog_card_svg(post, index=2, theme="light")
    minidom.parseString(svg)  # no debe romper el XML
    assert "&amp;" in svg


def test_card_dark_and_light_differ():
    assert render_blog_card_svg(POST, 1, "dark") != render_blog_card_svg(POST, 1, "light")
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_render_blog.py -v`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implementar `statsgen/render_blog.py`**

```python
"""Render de una tarjeta de blog como SVG temático y clicable (vía wrapper <a> en el README)."""
import re

from statsgen.transform import wrap_text
from statsgen.theme import THEMES

WIDTH = 800
HEIGHT = 150


def _esc(text):
    return (
        text.replace("&", "&amp;").replace("<", "&lt;")
        .replace(">", "&gt;").replace('"', "&quot;")
    )


def _strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def render_blog_card_svg(post, index, theme):
    t = THEMES[theme]
    title_lines = wrap_text(_strip_html(post["title"]), max_chars=46, max_lines=2)
    desc_lines = wrap_text(_strip_html(post["description"]), max_chars=64, max_lines=2)
    date = _esc(post.get("date", ""))

    title_svg = "".join(
        f'<text class="card-title" x="78" y="{48 + i * 26}">{_esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    desc_top = 48 + len(title_lines) * 26 + 8
    desc_svg = "".join(
        f'<text class="card-desc" x="78" y="{desc_top + i * 20}">{_esc(line)}</text>'
        for i, line in enumerate(desc_lines)
    )

    return f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad{index}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="100%" style="stop-color:#764ba2"/>
    </linearGradient>
    <style>
      .card-index {{ font: 700 26px 'Segoe UI', Ubuntu, sans-serif; fill: #ffffff; }}
      .card-date {{ font: 600 11px 'Segoe UI', Ubuntu, sans-serif; fill: #ffffff; opacity: 0.85; }}
      .card-title {{ font: 700 19px 'Segoe UI', Ubuntu, sans-serif; fill: {t['title']}; }}
      .card-desc {{ font: 400 13px 'Segoe UI', Ubuntu, sans-serif; fill: {t['label']}; }}
      .card-more {{ font: 600 13px 'Segoe UI', Ubuntu, sans-serif; fill: #667eea; }}
    </style>
  </defs>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="{t['bg']}" stroke="{t['bg_stroke']}" stroke-width="1"/>
  <rect x="0" y="0" width="58" height="{HEIGHT}" rx="12" fill="url(#grad{index})"/>
  <rect x="46" y="0" width="12" height="{HEIGHT}" fill="url(#grad{index})"/>
  <text class="card-index" x="29" y="60" text-anchor="middle">{index:02d}</text>
  <text class="card-date" x="29" y="80" text-anchor="middle">{date}</text>
  {title_svg}
  {desc_svg}
  <text class="card-more" x="78" y="{HEIGHT - 18}">Read more →</text>
</svg>'''
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_render_blog.py -v`
Expected: all passed.

- [ ] **Step 5: Commit**

```bash
git add statsgen/render_blog.py tests/test_render_blog.py
git commit -m "feat(blog): render de tarjeta SVG temática"
```

---

### Task 6: Orquestador `generate_stats.py`

**Files:**
- Modify (reescribir): `generate_stats.py`
- Create: `tests/test_generate_smoke.py`

**Interfaces:**
- Consumes: `fetch_stats`, `fetch_blog_posts`, `normalize_languages`, `languages_to_percentages`, `render_stats_svg`, `render_blog_card_svg`, `update_readme_blog`.
- Produces: `main(token: str, outdir: str = "generated", readme_path: str = "README.md") -> None` — escribe los SVG y actualiza el README.

- [ ] **Step 1: Escribir el test de humo que falla**

`tests/test_generate_smoke.py`:
```python
import os
import generate_stats


def test_main_writes_all_svgs_and_updates_readme(tmp_path, monkeypatch):
    activity = {
        "public_repos": 18, "total_stars": 250, "followers": 34,
        "commits_year": 1116, "contributions_year": 1516,
    }
    repos = [{"languages": {"edges": [{"size": 100, "node": {"name": "C"}}]}}]
    posts = [
        {"title": "P1", "link": "https://jmrp.io/blog/1/", "description": "d1", "date": "Jun 2026"},
        {"title": "P2", "link": "https://jmrp.io/blog/2/", "description": "d2", "date": "May 2026"},
        {"title": "P3", "link": "https://jmrp.io/blog/3/", "description": "d3", "date": "Apr 2026"},
    ]
    monkeypatch.setattr(generate_stats, "fetch_stats", lambda tok: (activity, repos))
    monkeypatch.setattr(generate_stats, "fetch_blog_posts", lambda n=3: posts)

    outdir = tmp_path / "generated"
    readme = tmp_path / "README.md"
    readme.write_text("x\n<!-- BLOG-POSTS:START -->\nOLD\n<!-- BLOG-POSTS:END -->\ny")

    generate_stats.main(token="tok", outdir=str(outdir), readme_path=str(readme))

    for name in ["github-stats-dark.svg", "github-stats-light.svg",
                 "blog-1-dark.svg", "blog-3-light.svg"]:
        assert (outdir / name).exists()
    assert "OLD" not in readme.read_text()
    assert "generated/blog-1-dark.svg" in readme.read_text()
```

- [ ] **Step 2: Ejecutar y verificar que falla**

Run: `python -m pytest tests/test_generate_smoke.py -v`
Expected: FAIL (`AttributeError: main` o `fetch_stats` no importable).

- [ ] **Step 3: Reescribir `generate_stats.py`**

```python
#!/usr/bin/env python3
"""Orquestador: obtiene datos de GitHub/RSS, genera los SVG y actualiza el README."""
import os

from statsgen.fetch import fetch_stats, fetch_blog_posts
from statsgen.transform import normalize_languages, languages_to_percentages
from statsgen.render_stats import render_stats_svg
from statsgen.render_blog import render_blog_card_svg
from statsgen.readme import update_readme_blog

NUM_POSTS = 3


def _write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main(token, outdir="generated", readme_path="README.md"):
    os.makedirs(outdir, exist_ok=True)

    print("Obteniendo estadísticas de GitHub...")
    activity, language_repos = fetch_stats(token)
    lang_pcts = languages_to_percentages(normalize_languages(language_repos))
    print(f"  Repos: {activity['public_repos']}  Stars: {activity['total_stars']}  "
          f"Commits(yr): {activity['commits_year']}")
    print(f"  Lenguajes: {[l for l, _ in lang_pcts]}")

    for theme in ("dark", "light"):
        _write(os.path.join(outdir, f"github-stats-{theme}.svg"),
               render_stats_svg(lang_pcts, activity, theme))
    print("✅ Panel de estadísticas generado (dark + light)")

    print("Obteniendo posts del blog...")
    posts = fetch_blog_posts(num_posts=NUM_POSTS)
    if posts:
        for i, post in enumerate(posts, start=1):
            for theme in ("dark", "light"):
                _write(os.path.join(outdir, f"blog-{i}-{theme}.svg"),
                       render_blog_card_svg(post, i, theme))
        print(f"✅ {len(posts)} tarjetas de blog generadas")

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        _write(readme_path, update_readme_blog(content, posts))
        print("✅ README actualizado con las tarjetas de blog")
    else:
        print("⚠️  Sin posts; README de blog sin cambios")


if __name__ == "__main__":
    token = os.getenv("STATS_TOKEN") or os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("Falta STATS_TOKEN/GITHUB_TOKEN")
    main(token)
```

- [ ] **Step 4: Ejecutar y verificar que pasa**

Run: `python -m pytest tests/test_generate_smoke.py -v`
Expected: passed.

- [ ] **Step 5: Ejecutar toda la suite**

Run: `python -m pytest -v`
Expected: todos los tests passed.

- [ ] **Step 6: Commit**

```bash
git add generate_stats.py tests/test_generate_smoke.py
git commit -m "feat: orquestador modular generate_stats"
```

---

### Task 7: Limpieza de artefactos y actualización del README inicial

**Files:**
- Delete: `generated/github-stats.svg`, `generated/github-stats-backup.svg`
- Delete: `.github/workflows/update-blog.yml.disabled`
- Modify: `README.md` (regenerar bloque de blog con tarjetas reales)

**Interfaces:**
- Consumes: el orquestador de la Task 6 con el `STATS_TOKEN` real.

- [ ] **Step 1: Borrar artefactos obsoletos y el workflow del mirror**

```bash
git rm generated/github-stats.svg generated/github-stats-backup.svg .github/workflows/update-blog.yml.disabled
```

- [ ] **Step 2: Generar los assets reales en local**

Run:
```bash
STATS_TOKEN="$(cat /tmp/ghtok)" python generate_stats.py
```
Expected: imprime repos/stars/commits, lista de lenguajes con MATLAB/Python/C/C++ arriba (no Go/C dominando), y crea `generated/github-stats-*.svg` + `generated/blog-{1,2,3}-{dark,light}.svg`. El README queda con `<a href=...><img src="generated/blog-1-dark.svg#gh-dark-mode-only".../></a>` entre los marcadores.

- [ ] **Step 3: Verificar el README a ojo**

Run: `git diff README.md`
Expected: el bloque entre marcadores ya no tiene `<table>` de 3 columnas, sino 3 tarjetas `<a><img/></a>` apiladas + el badge "Read all posts".

- [ ] **Step 4: Commit**

```bash
git add -A generated README.md
git commit -m "chore: regenerar assets reales, eliminar obsoletos y mirror Gitea"
```

---

### Task 8: Actualizar el workflow de CI

**Files:**
- Modify: `.github/workflows/generate-stats.yml`

**Interfaces:**
- Consumes: secret `GH_STATS_TOKEN` (ya añadido por el usuario), `requirements.txt`.

- [ ] **Step 1: Reemplazar el paso de generación y el `git add`**

En `.github/workflows/generate-stats.yml`, sustituir el step "Generate stats SVGs and update blog posts" por:
```yaml
      - name: Generate stats SVGs and blog cards
        env:
          STATS_TOKEN: ${{ secrets.GH_STATS_TOKEN || secrets.GITHUB_TOKEN }}
        run: python generate_stats.py
```
Y en el step de commit, cambiar la línea `git add` por:
```bash
          git add generated/*.svg README.md
```

- [ ] **Step 2: Validar la sintaxis YAML**

Run: `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/generate-stats.yml')); print('YAML OK')"`
Expected: `YAML OK` (si falta PyYAML: `pip install pyyaml` primero).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/generate-stats.yml
git commit -m "ci: usar STATS_TOKEN (privados en lenguajes) y commitear tarjetas de blog"
```

---

### Task 9: Script de preview con Playwright

**Files:**
- Create: `preview_readme.py`
- Modify: `.gitignore` (ignorar `preview/`)

**Interfaces:**
- Consumes: `README.md` + `generated/*.svg` ya generados. Token para la API de markdown (opcional pero recomendado para no chocar con rate limit).
- Produces: `preview/index.html` (README renderizado) que luego se abre con Playwright.

- [ ] **Step 1: Añadir `preview/` a `.gitignore`**

Añadir línea `preview/` a `.gitignore`.

- [ ] **Step 2: Crear `preview_readme.py`**

```python
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
    body = re.sub(r'src="\.\./generated/([^"]+)-light\.svg[^"]*"[^>]*>', "", body)
    os.makedirs("preview", exist_ok=True)
    html = (
        f'<!doctype html><html><head><meta charset="utf-8">'
        f'<link rel="stylesheet" href="{GH_MD_CSS}">'
        f'<style>body{{background:#0d1117;margin:0;display:flex;justify-content:center}}'
        f'.markdown-body{{box-sizing:border-box;max-width:880px;padding:32px}}</style>'
        f'</head><body><article class="markdown-body">{body}</article></body></html>'
    )
    with open("preview/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ preview/index.html generado. Ábrelo con Playwright (file://...) "
          "y captura a 1280px y 390px.")


if __name__ == "__main__":
    render()
```

- [ ] **Step 3: Ejecutar el preview**

Run:
```bash
STATS_TOKEN="$(cat /tmp/ghtok)" python preview_readme.py
```
Expected: `✅ preview/index.html generado`.

- [ ] **Step 4: Commit**

```bash
git add preview_readme.py .gitignore
git commit -m "tooling: preview local del README para verificación con Playwright"
```

---

### Task 10: Verificación visual final (Playwright, escritorio + móvil)

**Files:** ninguno (verificación).

**Interfaces:** Consumes `preview/index.html` (Task 9).

- [ ] **Step 1: Abrir el preview en Playwright a 1280px**

Navegar a `file:///opt/jmrplens/preview/index.html`, resize 1280×900, screenshot `preview-desktop.png`.

- [ ] **Step 2: Capturar a 390px (móvil)**

Resize 390×844, screenshot `preview-mobile.png`.

- [ ] **Step 3: Verificar criterios de éxito (a ojo, contra el spec)**

Comprobar en las capturas:
- Las 3 tarjetas de blog se apilan, completas, sin desborde horizontal, legibles también en 390px.
- El panel muestra lenguajes con % (MATLAB/Python/C/C++ representativos), métricas reales (1.116 commits, etc.), sin "lines" inventadas.
- Estética coherente (gradiente, esquinas) entre tarjetas y panel.

Si algo no encaja, ajustar `render_blog.py` / `render_stats.py` (tamaños de fuente, alto de tarjeta para que el texto sobreviva al escalado en móvil), regenerar (`python generate_stats.py`), re-preview y volver a capturar.

- [ ] **Step 4: Commit de ajustes (si los hubo)**

```bash
git add -A
git commit -m "polish: ajustes visuales tras verificación con Playwright"
```

---

## Self-Review

**Spec coverage:**
- Tarjetas blog SVG apiladas clicables → Tasks 2, 5, 6, 7. ✓
- Lenguajes normalizados + privados → Tasks 1, 3 (`viewer` incl. privados), 4. ✓
- Métricas reales, sin inventados → Tasks 3, 4 (test `no "lines"`). ✓
- Privados solo en lenguajes; recuentos públicos → Task 3 (`user.repositories(privacy: PUBLIC)` para counts; `viewer` para lenguajes). ✓
- Dos archivos dark/light → Tasks 4, 5, 6. ✓
- Token `STATS_TOKEN`/`GITHUB_TOKEN` fallback → Tasks 6, 8. ✓
- Eliminar mirror → Task 7. ✓
- Verificación Playwright escritorio/móvil → Tasks 9, 10. ✓
- Refactor modular → Tasks 1–6. ✓

**Placeholder scan:** sin TODO/TBD; todo el código está completo. ✓

**Type consistency:** `fetch_stats → (activity dict, language_repos list)` consumido en Task 6; `normalize_languages(repos) → dict` → `languages_to_percentages(dict) → [(lang,pct)]` → `render_stats_svg([(lang,pct)], activity, theme)`. `render_blog_card_svg(post, index, theme)` y `build_blog_block(posts)` usan `post["title"/"link"/"description"/"date"]`, claves producidas por `fetch_blog_posts`. Consistente. ✓
