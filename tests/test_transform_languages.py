from statsgen.transform import normalize_languages, languages_to_percentages


def _repo(*langs):
    return {"languages": {"edges": [{"size": s, "node": {"name": n}} for n, s in langs]}}


def test_normalize_single_big_repo_does_not_dominate():
    # Repo A: 1MB de Go. Repo B: 1KB de MATLAB (90%) + C (10%).
    repos = [
        _repo(("Go", 1_000_000)),
        _repo(("MATLAB", 900), ("C", 100)),
    ]
    weights = normalize_languages(repos)
    # Cada repo aporta cuota 1.0 en total; Go=1.0, MATLAB=0.9, C=0.1
    assert weights["Go"] == 1.0
    assert round(weights["MATLAB"], 2) == 0.9
    assert round(weights["C"], 2) == 0.1


def test_normalize_skips_empty_repos():
    repos = [_repo(), {"languages": {"edges": []}}, _repo(("Python", 50))]
    weights = normalize_languages(repos)
    assert weights == {"Python": 1.0}


def test_percentages_sum_to_100_and_respect_top_n():
    weights = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0}
    pcts = languages_to_percentages(weights, top_n=2)
    assert [l for l, _ in pcts] == ["A", "B"]
    assert round(sum(p for _, p in pcts), 5) == 100.0
    assert round(pcts[0][1], 2) == round(4 / 7 * 100, 2)


def test_percentages_empty_input():
    assert languages_to_percentages({}, top_n=8) == []
