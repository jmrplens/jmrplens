"""Obtención de datos: GraphQL (stats) y RSS (blog)."""
import xml.etree.ElementTree as ET
from datetime import datetime
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
