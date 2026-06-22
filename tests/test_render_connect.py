from xml.dom import minidom
from statsgen.render_connect import render_connect_chip_svg, LINKS, slug


def test_every_link_chip_is_well_formed_in_both_themes():
    for label, _url, spec in LINKS:
        for theme in ("dark", "light"):
            svg = render_connect_chip_svg(label, spec, theme)
            minidom.parseString(svg)
            assert svg.lstrip().startswith("<svg")
            assert label in svg


def test_chip_dark_and_light_differ():
    label, _u, spec = LINKS[0]
    assert render_connect_chip_svg(label, spec, "dark") != render_connect_chip_svg(label, spec, "light")


def test_slug_is_lowercase():
    assert slug("LinkedIn") == "linkedin"
