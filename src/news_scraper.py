import re
import requests
from bs4 import BeautifulSoup

RSS_BASE = "https://news.google.com/rss/search"
ARTICLE_LIMIT = 3

TARGETS = [
    {"tag": "KR", "params": "q=인공지능+OR+AI&hl=ko&gl=KR&ceid=KR:ko"},
    {"tag": "US", "params": "q=Artificial+Intelligence+OR+AI&hl=en-US&gl=US&ceid=US:en"},
    {"tag": "JP", "params": "q=人工知能+OR+AI&hl=ja&gl=JP&ceid=JP:ja"},
]


def fetch_articles(params, limit=ARTICLE_LIMIT):
    url = f"{RSS_BASE}?{params}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml-xml")
    items = soup.find_all("item")[:limit]
    item_blocks = re.findall(r"<item>.*?</item>", response.text, re.DOTALL)[:limit]
    raw_links = [
        m.group(1) for block in item_blocks
        if (m := re.search(r"<link>(.*?)</link>", block))
    ]
    return [
        {
            "title": item.find("title").text,
            "published": item.find("pubDate").text,
            "link": raw_links[i] if i < len(raw_links) else "",
        }
        for i, item in enumerate(items)
    ]


def fetch_all_articles():
    result = []
    for target in TARGETS:
        articles = fetch_articles(target["params"])
        for article in articles:
            article["tag"] = target["tag"]
        result.extend(articles)
    return result


def print_articles(articles):
    for i, article in enumerate(articles, 1):
        print(f"[{i}] [{article['tag']}] {article['title']}")
        print(f"    날짜: {article['published']}")
        print(f"    링크: {article['link']}")
        print()


if __name__ == "__main__":
    articles = fetch_all_articles()
    print_articles(articles)
