import base64
import io

from PIL import Image

import statsgen.cover as cover


def _png_bytes(w=1200, h=630):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (10, 80, 200)).save(buf, "PNG")
    return buf.getvalue()


def test_make_cover_returns_jpeg_data_uri(monkeypatch):
    class FakeResp:
        content = _png_bytes()
        def raise_for_status(self): pass
    monkeypatch.setattr(cover.requests, "get", lambda *a, **k: FakeResp())
    uri = cover.make_cover_data_uri("https://x/cover.png", 250, 176)
    assert uri.startswith("data:image/jpeg;base64,")
    # el payload base64 decodifica a una imagen JPEG válida del tamaño pedido (x2)
    raw = base64.b64decode(uri.split(",", 1)[1])
    img = Image.open(io.BytesIO(raw))
    assert img.size == (500, 352)


def test_make_cover_none_without_url():
    assert cover.make_cover_data_uri(None, 250, 176) is None
