import io
import os
import wave
from pathlib import Path
from google import genai
from google.genai import types

# Gemini TTS returns raw PCM at 24kHz, 16-bit, mono
_PCM_SAMPLE_RATE = 24000
_PCM_CHANNELS = 1
_PCM_SAMPLE_WIDTH = 2  # 16-bit


def _wrap_pcm_as_wav(pcm_data: bytes) -> bytes:
    """raw PCM 바이트에 WAV 헤더 추가"""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(_PCM_CHANNELS)
        wf.setsampwidth(_PCM_SAMPLE_WIDTH)
        wf.setframerate(_PCM_SAMPLE_RATE)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def synthesize_speech(text: str, output_path: Path) -> Path:
    """텍스트를 한국어 음성(WAV)으로 변환해 저장"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                )
            ),
        ),
    )
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    # Gemini TTS returns raw PCM without WAV header — wrap it
    if not audio_data[:4] == b"RIFF":
        audio_data = _wrap_pcm_as_wav(audio_data)
    output_path.write_bytes(audio_data)
    return output_path


def synthesize_all(slides: list, output_dir: Path) -> list[Path]:
    """전체 슬라이드 나레이션을 음성 파일로 합성"""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, slide in enumerate(slides):
        wav_path = output_dir / f"slide_{i + 1:02d}_{slide['id']}.wav"
        synthesize_speech(slide["narration"], wav_path)
        paths.append(wav_path)
    return paths
