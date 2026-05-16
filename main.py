import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from news_scraper import fetch_all_articles
from github_scraper import fetch_repos
from paper_scraper import fetch_papers

load_dotenv()

MODEL = "gemini-2.5-flash"
REPORTS_DIR = Path("reports")

PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["data"],
    template="""너는 실무 중심의 시니어 AI 엔지니어다. 제공된 데이터에서 다음 규칙을 엄격히 지켜서 마크다운 리포트를 작성해.

**철저한 필터링**: 철학, 일자리, 윤리, 단순 정책 등 실무와 무관한 가십성 기사는 완전히 삭제해. 오직 신규 모델(LLM 등), 프레임워크 업데이트, 기술 스펙, 오픈소스 툴에 관련된 내용만 남겨.

**리포트 구조**:

## [ TL;DR ]
오늘 수집된 정보 중 가장 중요한 기술적 변화 3가지만 글머리 기호로 요약해.

## [ 상세 기술 리포트 ]
필터링하고 남은 각 뉴스, GitHub 트렌드, 논문에 대해 매우 상세하게 서술해.
GitHub와 논문은 '어떤 아키텍처를 썼는지', '실무에 어떻게 적용 가능한지', '기존 기술 대비 차별점'을 위주로 개발자가 이해할 수 있는 깊이로 길게 설명해. 분량 제한은 두지 마.
리뷰하는 GitHub 프로젝트의 아키텍처나, 논문의 핵심 알고리즘 흐름을 설명할 때는 반드시 마크다운 내에서 렌더링되는 Mermaid.js 코드 블록(플로우차트 또는 시퀀스 다이어그램)을 하나 이상 포함하여 시각적으로 이해하기 쉽게 구성할 것.
Mermaid 문법 규칙을 반드시 준수할 것:
- 플로우차트는 반드시 `flowchart TD` 로 시작할 것 (`graph` 키워드 사용 금지)
- 노드 레이블에 괄호, 콜론, 슬래시, 하이픈, 따옴표 등 특수문자를 절대 사용하지 말 것. 예시 표기나 부연 설명은 레이블에서 제거하고 순수한 명사/동사만 남길 것
- 화살표 레이블에도 괄호, 따옴표, 슬래시 등 특수문자를 절대 사용하지 말 것
- `A & B --> C` 형태의 다중 출처 문법은 사용 금지. 반드시 각각의 화살표로 분리할 것
- 시퀀스 다이어그램은 `sequenceDiagram` 으로 시작하고 `participant`, `->>` 문법만 사용할 것
- 서브그래프, 스타일링 등 고급 문법은 사용하지 말 것

[수집 데이터]
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
    REPORTS_DIR.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = REPORTS_DIR / f"{date_str}_AILark_Brief.md"
    path.write_text(content, encoding="utf-8")
    return path


def main():
    print("데이터 수집 중...")
    articles = fetch_all_articles()
    repos = fetch_repos()
    papers = fetch_papers()

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
