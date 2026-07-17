# Project Structure
## Last Updated: 2026-07-17 (video pipeline 통합)

AILark/
├── .env                          # 환경변수 (GEMINI_API_KEY)
├── .gitignore                    # venv/reports/logs 제외
├── .claude/
│   └── settings.local.json      # Claude Code 권한 설정
├── README.md                     # 프로젝트 문서
├── requirements.txt              # Python 의존성 (버전 고정)
├── .venv/                        # Python 가상환경
├── logs/
│   ├── ailark.log                # launchd 표준 출력
│   └── ailark_error.log          # launchd 표준 에러
├── scripts/
│   ├── setup.sh                  # 초기 설치 (venv/plist/launchd 등록)
│   └── run_ailark.sh             # 실행 가드 (평일 & 9시 이후 & 미생성 시만)
├── templates/
│   └── slides/                   # CSS 애니메이션 슬라이드 HTML 템플릿
├── src/
│   ├── main.py                   # 오케스트레이터: 수집→분석→리포트→영상 저장
│   ├── paper_scraper.py          # HF Daily Papers 크롤러 (상위 5개, 중복 제거)
│   ├── news_scraper.py           # Google News RSS 크롤러 (KR/US/JP × 3개)
│   ├── github_scraper.py         # GitHub 트렌딩 레포 수집 (ai/llm 토픽)
│   ├── script_generator.py       # Gemini로 슬라이드 스크립트 JSON 생성
│   ├── tts_client.py             # Gemini TTS 음성 합성
│   ├── slide_renderer.py         # Playwright 비디오 녹화
│   └── video_generator.py        # ffmpeg 합성 + Drive 복사 오케스트레이터
├── tests/                        # 단위 테스트 (pytest)
│   ├── test_script_generator.py  # script_generator 단위 테스트 (mock 사용)
│   ├── test_tts_client.py        # tts_client 단위 테스트 (mock 사용)
│   └── test_video_generator.py   # video_generator 단위 테스트 (mock 사용)
└── reports/
    └── MMDD-MMDD/                # 주차별 폴더
        ├── YYYY-MM-DD_AILark_Brief.md  # 일일 리포트
        └── seen_papers.json      # 주간 중복 제거용 논문 ID 목록
