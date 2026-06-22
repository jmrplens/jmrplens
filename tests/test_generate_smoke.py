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
    monkeypatch.setattr(generate_stats, "fetch_blog_posts", lambda num_posts=3: posts)

    outdir = tmp_path / "generated"
    readme = tmp_path / "README.md"
    readme.write_text("x\n<!-- BLOG-POSTS:START -->\nOLD\n<!-- BLOG-POSTS:END -->\ny")

    generate_stats.main(token="tok", outdir=str(outdir), readme_path=str(readme))

    for name in ["github-stats-dark.svg", "github-stats-light.svg",
                 "blog-1-dark.svg", "blog-3-light.svg"]:
        assert (outdir / name).exists()
    assert "OLD" not in readme.read_text()
    assert "generated/blog-1-dark.svg" in readme.read_text()
