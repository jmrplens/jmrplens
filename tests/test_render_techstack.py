from xml.dom import minidom
from statsgen.render_techstack import render_techstack_svg


def test_techstack_is_well_formed_svg():
    svg = render_techstack_svg("dark")
    minidom.parseString(svg)
    assert svg.lstrip().startswith("<svg")


def test_techstack_has_title_and_labels():
    svg = render_techstack_svg("light")
    assert "Tech Stack" in svg
    assert "Python" in svg
    assert "Docker" in svg
    assert "Home Assistant" in svg


def test_techstack_dark_and_light_differ():
    assert render_techstack_svg("dark") != render_techstack_svg("light")
