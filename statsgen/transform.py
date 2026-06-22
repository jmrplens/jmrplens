"""Transformaciones puras de datos para el README autogenerado."""


def normalize_languages(repos):
    """Cuota de cada lenguaje dentro de cada repo (size/total_repo), sumada
    entre repos no-fork. Ningún repo individual puede dominar el agregado.

    repos: lista de nodos {"languages": {"edges": [{"size": int,
           "node": {"name": str}}]}}.
    Devuelve {lang: weight_float}.
    """
    weights = {}
    for repo in repos:
        edges = repo.get("languages", {}).get("edges", [])
        total = sum(e["size"] for e in edges)
        if total == 0:
            continue
        for e in edges:
            name = e["node"]["name"]
            weights[name] = weights.get(name, 0.0) + e["size"] / total
    return weights


def languages_to_percentages(weights, top_n=8):
    """Top-N lenguajes por peso, reescalados a sumar 100%.
    Devuelve [(lang, pct_float)] ordenado desc.
    """
    top = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    total = sum(w for _, w in top)
    if total == 0:
        return []
    return [(lang, w / total * 100) for lang, w in top]


def wrap_text(text, max_chars, max_lines):
    """Word-wrap greedy a <=max_lines líneas de <=max_chars caracteres.
    Si el texto no cabe entero, recorta y añade '…' a la última línea.
    """
    words = text.split()
    lines = []
    current = ""
    overflow = False
    for i, word in enumerate(words):
        candidate = word if not current else current + " " + word
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word[:max_chars]
        if len(lines) == max_lines:
            current = ""
            overflow = True
            break
    if current and len(lines) < max_lines:
        lines.append(current)

    consumed_words = len(" ".join(lines).split())
    if overflow or consumed_words < len(words):
        last = lines[-1] if lines else ""
        while last and len(last) + 1 > max_chars:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines
