import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SAMPLE_ARTICLES = [{"tag": "KR", "title": "삼성 갤럭시 S26 출시", "published": "2026-07-17"}]
SAMPLE_REPOS = [{"name": "microsoft/phi-4", "stars": 18200, "description": "Lightweight reasoning model"}]
SAMPLE_PAPERS = [{"title": "Attention is All You Need 2", "authors": "Vaswani et al.", "abstract": "새로운 트랜스포머 아키텍처", "published": "2026-07-17"}]

EXPECTED_SCRIPT = {
    "date": "2026-07-17",
    "slides": [
        {"id": "intro",  "narration": "인트로 나레이션", "data": {}},
        {"id": "tldr",   "narration": "요약 나레이션",   "data": {"summary": ["포인트1", "포인트2", "포인트3"]}},
        {"id": "news",   "narration": "뉴스 나레이션",   "data": {"kr": [{"title": "기사1"}], "us": [], "jp": []}},
        {"id": "github", "narration": "깃허브 나레이션", "data": {"repos": [{"name": "repo1", "stars": "1k", "description": "설명"}]}},
        {"id": "papers", "narration": "논문 나레이션",   "data": {"papers": [{"title": "논문1", "summary": "요약"}]}},
        {"id": "outro",  "narration": "아웃트로 나레이션","data": {"message": "수고하셨습니다."}},
    ],
}


def test_generate_script_returns_valid_structure():
    mock_response = MagicMock()
    mock_response.text = json.dumps(EXPECTED_SCRIPT)

    with patch("script_generator.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        import script_generator
        result = script_generator.generate_script(
            SAMPLE_ARTICLES, SAMPLE_REPOS, SAMPLE_PAPERS, "2026-07-17"
        )

    assert result["date"] == "2026-07-17"
    assert len(result["slides"]) == 6
    ids = [s["id"] for s in result["slides"]]
    assert ids == ["intro", "tldr", "news", "github", "papers", "outro"]
    for slide in result["slides"]:
        assert "narration" in slide and len(slide["narration"]) > 0
        assert "data" in slide
