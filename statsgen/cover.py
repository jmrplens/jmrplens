"""Descarga la imagen de portada de un post y la devuelve como data URI JPEG
(base64) recortada al tamaño del panel derecho de la tarjeta. Embeber en base64
es necesario porque GitHub no carga recursos remotos dentro de un SVG-imagen.
"""
import base64
import io

import requests

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


def make_cover_data_uri(image_url, width, height, scale=2, quality=78):
    """Devuelve 'data:image/jpeg;base64,...' recortado a width×height (con
    supersampling x`scale` para nitidez en retina), o None si falla/no hay PIL."""
    if not image_url or Image is None:
        return None
    try:
        resp = requests.get(image_url, timeout=20)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")

        tw, th = width * scale, height * scale
        target = tw / th
        w, h = img.size
        ratio = w / h
        if ratio > target:  # demasiado ancha → recortar laterales
            nw = int(h * target)
            x0 = (w - nw) // 2
            img = img.crop((x0, 0, x0 + nw, h))
        else:  # demasiado alta → recortar arriba/abajo
            nh = int(w / target)
            y0 = (h - nh) // 2
            img = img.crop((0, y0, w, y0 + nh))
        img = img.resize((tw, th), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    except (requests.RequestException, OSError):
        return None
