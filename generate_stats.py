#!/usr/bin/env python3
"""Orquestador: obtiene datos de GitHub/RSS, genera los SVG y actualiza el README."""
import os

from statsgen.fetch import fetch_stats, fetch_traffic, fetch_blog_posts
from statsgen.transform import normalize_languages, languages_to_percentages
from statsgen.render_stats import render_stats_svg
from statsgen.render_blog import render_blog_card_svg
from statsgen.render_techstack import render_techstack_svg
from statsgen.render_connect import render_connect_chip_svg, slug, LINKS
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

    print("Obteniendo tráfico (14d) de los repos...")
    names = [n["nameWithOwner"] for n in language_repos
             if n.get("nameWithOwner") and not n.get("isArchived")]
    activity.update(fetch_traffic(token, names))
    print(f"  Repos: {activity['public_repos']}  Stars: {activity['total_stars']}  "
          f"Commits(yr): {activity['commits_year']}  "
          f"Views(14d): {activity['views_14d']}  Clones(14d): {activity['clones_14d']}")
    print(f"  Lenguajes: {[l for l, _ in lang_pcts]}")

    for theme in ("dark", "light"):
        _write(os.path.join(outdir, f"github-stats-{theme}.svg"),
               render_stats_svg(lang_pcts, activity, theme))
        _write(os.path.join(outdir, f"tech-stack-{theme}.svg"),
               render_techstack_svg(theme))
        for label, _url, spec in LINKS:
            _write(os.path.join(outdir, f"connect-{slug(label)}-{theme}.svg"),
                   render_connect_chip_svg(label, spec, theme))
    print("✅ Panel de estadísticas, Tech Stack y Connect generados (dark + light)")

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
