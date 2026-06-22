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
