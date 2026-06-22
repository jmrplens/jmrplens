"""Obtención de datos: GraphQL (stats) y RSS (blog)."""
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests

GRAPHQL_URL = "https://api.github.com/graphql"
USERNAME = "jmrplens"
BLOG_RSS_URL = "https://jmrp.io/rss.xml"

STATS_QUERY = """query {
  user(login: "jmrplens") {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
    repositories(privacy: PUBLIC, isFork: false, ownerAffiliations: OWNER, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
  }
  viewer {
    repositories(isFork: false, ownerAffiliations: OWNER, first: 100) {
      nodes {
        nameWithOwner
        isArchived
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}"""


def graphql(query, token):
    resp = requests.post(
        GRAPHQL_URL,
        json={"query": query},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def fetch_stats(token):
    data = graphql(STATS_QUERY, token)
    user = data["user"]
    pub = user["repositories"]
    cc = user["contributionsCollection"]
    activity = {
        "public_repos": pub["totalCount"],
        "total_stars": sum(n["stargazerCount"] for n in pub["nodes"]),
        "followers": user["followers"]["totalCount"],
        "commits_year": cc["totalCommitContributions"],
        "contributions_year": cc["contributionCalendar"]["totalContributions"],
    }
    language_repos = data["viewer"]["repositories"]["nodes"]
    return activity, language_repos


def fetch_traffic(token, repo_full_names):
    """Suma vistas y clones de los últimos 14 días (GitHub Traffic API) entre
    todos los repos dados. Requiere push (el token admin lo tiene). Los repos
    inaccesibles se ignoran sin romper el agregado.

    Devuelve {"views_14d": int, "clones_14d": int}.
    """
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    totals = {"views_14d": 0, "clones_14d": 0}
    for full in repo_full_names:
        for kind, key in (("views", "views_14d"), ("clones", "clones_14d")):
            try:
                r = requests.get(
                    f"https://api.github.com/repos/{full}/traffic/{kind}",
                    headers=headers, timeout=20,
                )
                if r.status_code == 200:
                    totals[key] += r.json().get("count", 0)
            except requests.RequestException:
                continue
    return totals


def _fmt_date(raw):
    try:
        return parsedate_to_datetime(raw).strftime("%b %Y")
    except (TypeError, ValueError):
        return ""


def fetch_blog_posts(num_posts=3):
    try:
        resp = requests.get(BLOG_RSS_URL, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except (requests.RequestException, ET.ParseError) as e:
        print(f"⚠️  Error obteniendo RSS: {e}")
        return []

    posts = []
    for item in root.findall(".//item")[:num_posts]:
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        desc = item.findtext("description", "") or ""
        date = _fmt_date(item.findtext("pubDate", ""))
        if title and link:
            posts.append({"title": title, "link": link, "description": desc, "date": date})
    return posts
