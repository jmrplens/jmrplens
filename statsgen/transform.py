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
