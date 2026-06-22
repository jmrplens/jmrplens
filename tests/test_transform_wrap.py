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
