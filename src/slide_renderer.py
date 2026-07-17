import json
import subprocess
import tempfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "slides"
SLIDE_WIDTH = 1920
SLIDE_HEIGHT = 1080
DEFAULT_SLIDE_DURATION_MS = 25000  # 25초


def _get_audio_duration_ms(wav_path: Path) -> int:
    """ffprobe로 WAV 파일 재생 시간(ms) 조회"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", str(wav_path)],
        capture_output=True, text=True, check=True,
    )
    streams = json.loads(result.stdout).get("streams", [])
    for stream in streams:
        if stream.get("codec_type") == "audio":
            duration = float(stream.get("duration", 0))
            return int(duration * 1000) + 500  # 500ms 여유
    return DEFAULT_SLIDE_DURATION_MS


def record_presentation(script: dict, audio_paths: list[Path], output_path: Path) -> Path:
    """슬라이드쇼 HTML을 Playwright로 녹화"""
    timings = [_get_audio_duration_ms(p) for p in audio_paths]
    total_ms = sum(timings) + 1000  # 마지막 슬라이드 여운

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("presentation.html")
    html = template.render(
        slides=script["slides"],
        date=script["date"],
        timings_json=json.dumps(timings),
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        html_file = tmp_dir / "presentation.html"
        html_file.write_text(html, encoding="utf-8")
        video_dir = tmp_dir / "video"
        video_dir.mkdir()

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
                record_video_dir=str(video_dir),
                record_video_size={"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
            )
            page = context.new_page()
            page.goto(f"file://{html_file}")
            page.wait_for_timeout(total_ms)
            context.close()
            browser.close()

        recorded = list(video_dir.glob("*.webm"))
        if not recorded:
            raise RuntimeError("Playwright 비디오 녹화 실패")

        # webm → mp4 변환 (음성 없는 무음 영상)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(recorded[0]), "-c:v", "libx264",
             "-pix_fmt", "yuv420p", str(output_path)],
            check=True, capture_output=True,
        )
    return output_path
