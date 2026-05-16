import requests
from datetime import datetime, timedelta

API_URL = "https://api.github.com/search/repositories"
REPO_LIMIT = 3


def fetch_repos(limit=REPO_LIMIT):
    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    params = {
        "q": f'ai OR "machine learning" OR llm pushed:>{since}',
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    items = response.json()["items"]
    return [
        {
            "name": item["full_name"],
            "url": item["html_url"],
            "description": item["description"] or "",
            "stars": item["stargazers_count"],
        }
        for item in items
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
