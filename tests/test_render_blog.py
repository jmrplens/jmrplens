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
