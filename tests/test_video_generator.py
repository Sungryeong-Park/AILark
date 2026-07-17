import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SAMPLE_SCRIPT = {
    "date": "2026-07-17",
    "slides": [
        {"id": "intro",  "narration": "인트로", "data": {}},
        {"id": "outro",  "narration": "아웃트로","data": {"message": "수고"}},
    ],
}


def test_generate_returns_none_on_script_failure(tmp_path):
    import video_generator
    with patch("video_generator.script_generator.generate_script",
               side_effect=Exception("API 오류")):
        result = video_generator.generate([], [], [], "2026-07-17", tmp_path)
    assert result is None


def test_generate_returns_mp4_on_success(tmp_path):
    def fake_render(script, audio_paths, output_path):
        output_path.write_bytes(b"fake-mp4")
        return output_path

    def fake_tts_all(slides, audio_dir):
        audio_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for i, s in enumerate(slides):
            p = audio_dir / f"slide_{i+1:02d}.wav"
            p.write_bytes(b"fake-wav")
            paths.append(p)
        return paths

    import video_generator
    fake_drive = str(tmp_path / "drive")
    with patch("video_generator.script_generator.generate_script",
               return_value=SAMPLE_SCRIPT), \
         patch("video_generator.tts_client.synthesize_all", side_effect=fake_tts_all), \
         patch("video_generator.slide_renderer.record_presentation", side_effect=fake_render), \
         patch("video_generator._merge_audio") as mock_merge, \
         patch("video_generator.DRIVE_PATH", fake_drive), \
         patch("video_generator.shutil.copy2") as mock_copy:
        mock_merge.side_effect = lambda silent, audio_paths, out: out.write_bytes(b"merged-mp4")
        result = video_generator.generate([], [], [], "2026-07-17", tmp_path)

    assert result is not None
    assert result.suffix == ".mp4"
    mock_copy.assert_called_once()
