import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from news_scraper import fetch_all_articles
from github_scraper import fetch_repos
from paper_scraper import fetch_papers

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = "gemini-2.5-flash"
REPORTS_DIR = PROJECT_ROOT / "reports"

PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["data"],
    template="""반드시 한국어로 작성할 것.

You are a senior AI engineer focused on practical implementation. Write a markdown report from the provided data by strictly following all rules below.

**Filtering:** Remove all gossip-level content unrelated to engineering practice — philosophy, job market, ethics, generic policy. Keep only: new models, framework updates, technical specs, open-source tools, real-world AI product implementations, and developer-facing practical guides.

**Report Structure:**

## [ TL;DR ]
Summarize the 3 most important technical changes from today's data as bullet points.

## [ 상세 기술 리포트 ]
For each item that passed the filter, write a detailed technical explanation covering: architecture used, practical applicability, and differentiation from existing approaches. No length limit.

**Accuracy Rule (Highest Priority):**
Accuracy is paramount. If the source data does not contain sufficient detail about the architecture or technical specs, do NOT fabricate or hallucinate any information. In that case, skip the diagram and explicitly write: "수집된 원문에는 상세 아키텍처 정보가 포함되어 있지 않습니다."

**Mermaid Diagrams:**
When architecture or algorithm flow IS sufficiently described in the source data, include at least one Mermaid.js code block. Follow these syntax rules strictly:
- Start flowcharts with `flowchart TD` only. Never use `graph`.
- Node labels must contain NO special characters — no parentheses, colons, slashes, hyphens, or quotes. Use plain nouns and verbs only.
- Arrow labels must also contain NO special characters.
- Never use `A & B --> C` syntax. Write each arrow on a separate line.
- Sequence diagrams must start with `sequenceDiagram` and use only `participant` and `->>`.
- No subgraphs or styling.

[Collected Data]
{data}
""",
)


def format_data(articles, repos, papers):
    lines = ["## 글로벌 뉴스"]
    for a in articles:
        lines.append(f"[{a['tag']}] {a['title']} ({a['published']})")

    lines.append("\n## GitHub 트렌드")
    for r in repos:
        lines.append(f"- {r['name']} (★{r['stars']:,}): {r['description']}")

    lines.append("\n## 논문")
    for p in papers:
        abstract = p["abstract"][:300] + "..." if len(p["abstract"]) > 300 else p["abstract"]
        lines.append(f"- {p['title']} ({p['published']})\n  저자: {p['authors']}\n  초록: {abstract}")

    return "\n".join(lines)


def save_report(content):
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    folder_name = f"{monday.strftime('%m%d')}-{sunday.strftime('%m%d')}"
    report_dir = REPORTS_DIR / folder_name
    report_dir.mkdir(parents=True, exist_ok=True)
    date_str = now.strftime("%Y-%m-%d")
    path = report_dir / f"{date_str}_AILark_Brief.md"
    path.write_text(content, encoding="utf-8")
    return path


def main():
    print("데이터 수집 중...")
    try:
        articles = fetch_all_articles()
    except Exception as e:
        print(f"뉴스 수집 실패: {e}")
        articles = []
    try:
        repos = fetch_repos()
    except Exception as e:
        print(f"GitHub 수집 실패: {e}")
        repos = []
    try:
        papers = fetch_papers()
    except Exception as e:
        print(f"논문 수집 실패: {e}")
        papers = []

    data = format_data(articles, repos, papers)
    prompt = PROMPT_TEMPLATE.format(data=data)

    print("Gemini 분석 중...")
    llm = ChatGoogleGenerativeAI(
        model=MODEL,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )
    response = llm.invoke(prompt)

    path = save_report(response.content)
    print(f"저장 완료: {path}")
    print("\n" + response.content)


if __name__ == "__main__":
    main()
