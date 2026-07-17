import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import script_generator
import tts_client
import slide_renderer

logger = logging.getLogger(__name__)
DRIVE_PATH = os.path.expanduser(os.getenv("GOOGLE_DRIVE_PATH", ""))


def generate(
    articles: list, repos: list, papers: list, date: str, report_dir: Path
) -> Optional[Path]:
    """동영상 생성 후 Drive 복사. 실패 시 None 반환."""
    try:
        logger.info("영상 생성 시작: %s", date)
        script = script_generator.generate_script(articles, repos, papers, date)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            audio_paths = tts_client.synthesize_all(script["slides"], tmp_dir / "audio")
            silent_mp4 = tmp_dir / "silent.mp4"
            slide_renderer.record_presentation(script, audio_paths, silent_mp4)

            output_mp4 = report_dir / f"{date}_AILark.mp4"
            _merge_audio(silent_mp4, audio_paths, output_mp4)

        if DRIVE_PATH:
            drive_dir = Path(DRIVE_PATH)
            drive_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(output_mp4, drive_dir / output_mp4.name)
            logger.info("Drive 복사 완료: %s", drive_dir / output_mp4.name)

        logger.info("영상 생성 완료: %s", output_mp4)
        return output_mp4

    except Exception as e:
        logger.error("영상 생성 실패 (리포트에 영향 없음): %s", e)
        return None


def _merge_audio(silent_mp4: Path, audio_paths: list[Path], output_mp4: Path) -> None:
    """슬라이드별 WAV를 이어 붙여 영상에 합성"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        concat_wav = tmp_dir / "all_audio.wav"
        filelist = tmp_dir / "filelist.txt"
        filelist.write_text(
            "\n".join(f"file '{p}'" for p in audio_paths), encoding="utf-8"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(filelist), str(concat_wav)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["ffmpeg", "-y",
             "-i", str(silent_mp4),
             "-i", str(concat_wav),
             "-c:v", "copy", "-c:a", "aac", "-shortest",
             str(output_mp4)],
            check=True, capture_output=True,
        )
