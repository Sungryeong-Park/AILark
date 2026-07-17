import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_synthesize_speech_writes_wav(tmp_path):
    output_path = tmp_path / "slide_01.wav"
    fake_audio = b"\x52\x49\x46\x46" + b"\x00" * 100  # fake WAV bytes

    mock_response = MagicMock()
    mock_response.candidates[0].content.parts[0].inline_data.data = fake_audio

    with patch("tts_client.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        import tts_client
        result = tts_client.synthesize_speech("안녕하세요.", output_path)

    assert result == output_path
    assert output_path.read_bytes() == fake_audio


def test_synthesize_all_returns_correct_count(tmp_path):
    slides = [
        {"id": "intro",  "narration": "인트로"},
        {"id": "tldr",   "narration": "요약"},
        {"id": "outro",  "narration": "아웃트로"},
    ]

    import tts_client
    with patch.object(tts_client, "synthesize_speech") as mock_synth:
        def fake_synth(text, path):
            path.write_bytes(b"fake")
            return path
        mock_synth.side_effect = fake_synth
        paths = tts_client.synthesize_all(slides, tmp_path)

    assert len(paths) == 3
    assert mock_synth.call_count == 3
