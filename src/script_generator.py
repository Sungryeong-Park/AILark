import json
import os
from google import genai

SCRIPT_PROMPT = """당신은 AI 기술 분석가입니다. 아래 데이터를 바탕으로 동영상 슬라이드 나레이션 스크립트를 작성해주세요.

나레이션 스타일:
- 분석가 스타일: 단순 사실 나열이 아닌 인사이트와 의미 중심
- 슬라이드당 나레이션 길이: 20~30초 분량 (약 80~120자)
- 자연스러운 구어체 한국어

입력 데이터:
날짜: {date}

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
    {{"id": "intro", "narration": "...", "data": {{}}}},
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
        news=_format_news(articles),
        github=_format_repos(repos),
        papers=_format_papers(papers),
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    content = response.text.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content.strip())
