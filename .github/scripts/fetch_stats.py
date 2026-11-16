#!/usr/bin/env python3
"""Fetch aggregate GitHub stats for the profile cards.

Only totals and language shares are written (no private repo names).
Env: GH_TOKEN (needs repo + read:user to include private contributions), GH_USER.
Usage: python fetch_stats.py [out.json]
"""
import datetime
import json
import os
import re
import sys
import urllib.request

USER = os.environ.get("GH_USER", "amansquadstack")
TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    repositories(ownerAffiliations: OWNER) { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY], includeUserRepositories: true) { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
      commitContributionsByRepository(maxRepositories: 100) {
        contributions { totalCount }
        repository { languages(first: 6, orderBy: {field: SIZE, direction: DESC}) { totalSize edges { size node { name color } } } }
      }
    }
  }
}
"""


def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not counted yet doesn't break the streak
        i -= 1
    while i >= 0 and counts[i]:
        current += 1
        i -= 1
    return current, longest


def views():
    try:
        req = urllib.request.Request(f"https://komarev.com/ghpvc/?username={USER}&style=flat",
                                     headers={"User-Agent": "profile-stats"})
        with urllib.request.urlopen(req, timeout=20) as r:
            nums = re.findall(r">([\d,]+)<", r.read().decode())
        return int(nums[-1].replace(",", "")) if nums else None
    except Exception:
        return None


def main():
    u = gql(QUERY, {"login": USER})["user"]
    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cc["contributionCalendar"]["weeks"]]
    current, longest = streaks(days)

    langs = {}
    for item in cc["commitContributionsByRepository"]:
        L = item["repository"]["languages"]
        total = L["totalSize"] or 0
        if not total:
            continue
        for e in L["edges"]:
            name, color = e["node"]["name"], e["node"]["color"] or "#8b949e"
            share = item["contributions"]["totalCount"] * e["size"] / total
            prev = langs.get(name, (0, color))
            langs[name] = (prev[0] + share, color)
    total_w = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    languages = [{"name": n, "color": c, "pct": round(100 * w / total_w, 1)} for n, (w, c) in top]

    stats = {
        "updated": datetime.date.today().isoformat(),
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs": cc["totalPullRequestContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "issues": cc["totalIssueContributions"],
        "repos": u["repositoriesContributedTo"]["totalCount"],
        "current_streak": current,
        "longest_streak": longest,
        "weekly": weekly,
        "languages": languages,
        "views": views(),
    }
    out = sys.argv[1] if len(sys.argv) > 1 else ".github/data/stats.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(stats, f, indent=2)
    print(json.dumps({k: v for k, v in stats.items() if k != "weekly"}, indent=2))


if __name__ == "__main__":
    main()
