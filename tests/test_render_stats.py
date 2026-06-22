from xml.dom import minidom
from statsgen.render_stats import render_stats_svg

ACTIVITY = {
    "public_repos": 18, "total_stars": 250, "total_forks": 12, "followers": 34,
    "commits_year": 1116, "prs_year": 371,
    "views_14d": 1122, "clones_14d": 25041,
}
LANGS = [("MATLAB", 40.0), ("Python", 30.0), ("C", 20.0), ("C++", 10.0)]


def test_render_stats_is_well_formed_svg():
    svg = render_stats_svg(LANGS, ACTIVITY, theme="dark")
    minidom.parseString(svg)  # lanza si no es XML válido
    assert svg.lstrip().startswith("<svg")


def test_render_stats_shows_real_metrics_no_invented():
    svg = render_stats_svg(LANGS, ACTIVITY, theme="dark")
    assert "1,116" in svg          # commits del año
    assert "371" in svg            # pull requests del año
    assert "250" in svg            # stars
    assert "12" in svg             # forks
    assert "34" in svg             # followers
    assert "18" in svg             # repos públicos
    assert "1,122" in svg          # vistas de repos 14d (tráfico)
    assert "25,041" in svg         # clones 14d (tráfico)
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
