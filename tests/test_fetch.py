import statsgen.fetch as fetch


SAMPLE_GQL = {
    "user": {
        "followers": {"totalCount": 34},
        "contributionsCollection": {
            "totalCommitContributions": 1116,
            "contributionCalendar": {"totalContributions": 1516},
        },
        "repositories": {
            "totalCount": 18,
            "nodes": [{"stargazerCount": 200}, {"stargazerCount": 50}],
        },
    },
    "viewer": {
        "repositories": {
            "nodes": [
                {"languages": {"edges": [{"size": 100, "node": {"name": "C"}}]}},
            ]
        }
    },
}


def test_fetch_stats_maps_activity_and_languages(monkeypatch):
    monkeypatch.setattr(fetch, "graphql", lambda q, t: SAMPLE_GQL)
    activity, langs = fetch.fetch_stats("tok")
    assert activity == {
        "public_repos": 18,
        "total_stars": 250,
        "followers": 34,
        "commits_year": 1116,
        "contributions_year": 1516,
    }
    assert langs == SAMPLE_GQL["viewer"]["repositories"]["nodes"]


def test_graphql_raises_on_errors(monkeypatch):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return {"errors": [{"message": "bad"}]}
    monkeypatch.setattr(fetch.requests, "post", lambda *a, **k: FakeResp())
    import pytest
    with pytest.raises(RuntimeError):
        fetch.graphql("query", "tok")


RSS = b"""<?xml version="1.0"?><rss><channel>
<item><title>Post A</title><link>https://jmrp.io/blog/a/</link>
<description>Desc A</description><pubDate>Mon, 01 Jun 2026 00:00:00 GMT</pubDate></item>
<item><title>Post B</title><link>https://jmrp.io/blog/b/</link>
<description>Desc B</description><pubDate>Sun, 01 May 2026 00:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_fetch_blog_posts_parses_rss(monkeypatch):
    class FakeResp:
        content = RSS
        def raise_for_status(self): pass
    monkeypatch.setattr(fetch.requests, "get", lambda *a, **k: FakeResp())
    posts = fetch.fetch_blog_posts(num_posts=2)
    assert [p["title"] for p in posts] == ["Post A", "Post B"]
    assert posts[0]["link"] == "https://jmrp.io/blog/a/"
    assert posts[0]["date"] == "Jun 2026"
