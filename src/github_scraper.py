import requests
from datetime import datetime, timedelta

API_URL = "https://api.github.com/search/repositories"
REPO_LIMIT = 3


TOPICS = ["llm", "physical-ai", "embedded-ai", "robotics", "tinyml"]
MIN_STARS = 10000


def _fetch_by_topic(topic, since):
    params = {
        "q": f"topic:{topic} stars:>={MIN_STARS} pushed:>{since}",
        "sort": "stars",
        "order": "desc",
        "per_page": 10,
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["items"]


def fetch_repos(limit=REPO_LIMIT):
    since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    seen = set()
    merged = []
    for topic in TOPICS:
        for item in _fetch_by_topic(topic, since):
            if item["html_url"] not in seen:
                seen.add(item["html_url"])
                merged.append(item)
    merged.sort(key=lambda x: x["stargazers_count"], reverse=True)
    return [
        {
            "name": item["full_name"],
            "url": item["html_url"],
            "description": item["description"] or "",
            "stars": item["stargazers_count"],
        }
        for item in merged[:limit]
    ]


def print_repos(repos):
    for i, repo in enumerate(repos, 1):
        print(f"[{i}] {repo['name']}")
        print(f"    ★ {repo['stars']:,}")
        print(f"    {repo['description']}")
        print(f"    {repo['url']}")
        print()


if __name__ == "__main__":
    repos = fetch_repos()
    print_repos(repos)
