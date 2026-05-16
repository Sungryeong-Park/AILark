import requests
import xml.etree.ElementTree as ET

API_URL = "http://export.arxiv.org/api/query"
PAPER_LIMIT = 3
NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_papers(limit=PAPER_LIMIT):
    params = {
        "search_query": "cat:cs.AI OR cat:cs.CL",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": limit,
    }
    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    entries = root.findall("atom:entry", NS)
    return [
        {
            "title": entry.find("atom:title", NS).text.strip(),
            "authors": ", ".join(
                a.find("atom:name", NS).text
                for a in entry.findall("atom:author", NS)
            ),
            "published": entry.find("atom:published", NS).text[:10],
            "abstract": entry.find("atom:summary", NS).text.strip(),
            "pdf": next(
                (link.get("href") for link in entry.findall("atom:link", NS)
                 if link.get("type") == "application/pdf"),
                "",
            ),
        }
        for entry in entries
    ]


def print_papers(papers):
    for i, paper in enumerate(papers, 1):
        abstract = paper["abstract"][:200] + "..." if len(paper["abstract"]) > 200 else paper["abstract"]
        print(f"[{i}] {paper['title']}")
        print(f"    저자 : {paper['authors']}")
        print(f"    날짜 : {paper['published']}")
        print(f"    초록 : {abstract}")
        print(f"    PDF  : {paper['pdf']}")
        print()


if __name__ == "__main__":
    papers = fetch_papers()
    print_papers(papers)
