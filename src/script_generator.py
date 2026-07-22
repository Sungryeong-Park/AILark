import json
import os
from datetime import datetime
from google import genai
from google.genai import types

SCRIPT_PROMPT = """당신은 AI 기술 분석가입니다. 아래 데이터를 바탕으로 동영상 슬라이드 나레이션 스크립트를 작성해주세요.

나레이션 스타일:
- 분석가 스타일: 단순 사실 나열이 아닌 인사이트와 의미 중심
- 자연스러운 구어체 한국어
- 전체 스크립트는 하나의 이야기처럼 흘러가도록. tldr→뉴스→github→논문 슬라이드는 앞 슬라이드와 자연스럽게 이어지는 전환구로 시작.
  예) "이러한 흐름 속에서 글로벌 뉴스를 보면...", "뉴스에서도 확인되듯이, GitHub 트렌드를 보면..."
- outro: "내일도 함께하겠습니다", "다음에 또 만나요" 등 방송 멘트 금지. 오늘의 핵심 메시지만 간결하게.

슬라이드별 나레이션 길이:
- intro, outro: 5~10초 이내 (1~2문장)
- tldr, news, github, papers: 20~30초 (80~120자)

뉴스 슬라이드 주의사항:
- 신기술 발표, 신제품 출시, 신서비스 런치 등 '공개/발표/출시' 유형 뉴스 우선 선택
- 단순 분석·의견 기사는 제외하고 실제 발표·릴리즈 뉴스만 포함

입력 데이터:
날짜: {date} ({week_label})

뉴스:
{news}

GitHub 트렌드:
{github}

논문:
{papers}

아래 JSON 형식으로만 출력하세요. 마크다운 코드블록 없이:
{{
  "date": "{date}",
  "slides": [
    {{"id": "intro", "narration": "{week_label} 기술 동향 리포트입니다.", "data": {{}}}},
    {{"id": "tldr", "narration": "...", "data": {{"summary": ["핵심1", "핵심2", "핵심3"]}}}},
    {{"id": "news", "narration": "...", "data": {{
      "kr": [{{"title": "..."}}],
      "us": [{{"title": "..."}}],
      "jp": [{{"title": "..."}}]
    }}}},
    {{"id": "github", "narration": "...", "data": {{
      "repos": [{{"name": "...", "stars": "...", "description": "..."}}]
    }}}},
    {{"id": "papers", "narration": "...", "data": {{
      "papers": [{{"title": "...", "summary": "한 줄 핵심 인사이트"}}]
    }}}},
    {{"id": "outro", "narration": "...", "data": {{"message": "오늘의 한 줄 핵심 메시지"}}}}
  ]
}}"""


def _week_label(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    week = (d.day - 1) // 7 + 1
    return f"{d.month}월 {week}주차"


def _format_news(articles: list) -> str:
    return "\n".join(f"[{a['tag']}] {a['title']}" for a in articles)


def _format_repos(repos: list) -> str:
    return "\n".join(f"- {r['name']} (★{r['stars']:,}): {r['description']}" for r in repos)


def _format_papers(papers: list) -> str:
    return "\n".join(f"- {p['title']}: {p['abstract'][:200]}" for p in papers)


def generate_script(articles: list, repos: list, papers: list, date: str) -> dict:
    """크롤러 raw data에서 슬라이드 스크립트 JSON 생성"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = SCRIPT_PROMPT.format(
        date=date,
        week_label=_week_label(date),
        news=_format_news(articles),
        github=_format_repos(repos),
        papers=_format_papers(papers),
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text.strip())
