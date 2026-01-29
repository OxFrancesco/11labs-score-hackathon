import base64
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner


class _FakeAudio:
    def __iter__(self):
        yield b"audio-data"


class _FakeTranscript:
    def __init__(self, text: str, words=None):
        self.text = text
        self.words = words or []

    def __str__(self):
        return "SRT_OUTPUT"


class _FakeElevenLabsModule:
    class ElevenLabs:  # pragma: no cover - placeholder for import
        pass


def _load_script(name: str):
    script_path = Path(__file__).resolve().parent.parent / "scripts" / f"{name}.py"
    module_name = f"elevenlabs_script_{name}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    if LIVE_TESTS:
        assert spec.loader is not None
        spec.loader.exec_module(module)
    else:
        with patch.dict(sys.modules, {"elevenlabs": _FakeElevenLabsModule()}):
            assert spec.loader is not None
            spec.loader.exec_module(module)
    return module


LIVE_TESTS = os.environ.get("ELEVENLABS_LIVE_TESTS") == "1"
SKIP_MUSIC = os.environ.get("ELEVENLABS_SKIP_MUSIC") == "1"
SKIP_VOICE_DESIGN = os.environ.get("ELEVENLABS_SKIP_VOICE_DESIGN") == "1"
SKIP_ISOLATION = os.environ.get("ELEVENLABS_SKIP_ISOLATION") == "1"
SKIP_TRANSCRIPTION = os.environ.get("ELEVENLABS_SKIP_TRANSCRIPTION") == "1"
SKIP_VOICE_CONVERT = os.environ.get("ELEVENLABS_SKIP_VOICE_CONVERT") == "1"
_OUTPUT_DIR = Path(os.environ.get("ELEVENLABS_TEST_OUTPUT_DIR", "output/elevenlabs"))


def _output_path(filename: str) -> Path:
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return _OUTPUT_DIR / filename


class ElevenLabsScriptTests(TestCase):
    @classmethod
    def setUpClass(cls):
        if LIVE_TESTS:
            narrate_module = _load_script("narrate")
            cls.sample_input = _output_path("sample_input.mp3")
            if not cls.sample_input.exists():
                client = narrate_module.ElevenLabs()
                audio = client.text_to_speech.convert(
                    text=(
                        "Hello, this is a test sample. "
                        "It is intentionally long enough to exceed the minimum duration "
                        "required for audio isolation and transcription. "
                        "We will repeat this line to ensure adequate length. "
                        "Hello, this is a test sample. "
                        "It is intentionally long enough to exceed the minimum duration "
                        "required for audio isolation and transcription."
                    ),
                    voice_id="EXAVITQu4vr4xnSDxMaL",
                    model_id="eleven_flash_v2_5",
                    output_format="mp3_44100_128",
                )
                with open(cls.sample_input, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)

    def setUp(self):
        self.runner = CliRunner()

    def test_narrate_writes_audio(self):
        module = _load_script("narrate")
        out_path = _output_path("narrate.mp3")

        if LIVE_TESTS:
            result = self.runner.invoke(module.main, ["Hello", "-o", str(out_path)])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
        else:
            client = MagicMock()
            client.text_to_speech.convert.return_value = _FakeAudio()
            with patch.object(module, "ElevenLabs", return_value=client):
                result = self.runner.invoke(module.main, ["Hello", "-o", str(out_path)])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertEqual(out_path.read_bytes(), b"audio-data")
            client.text_to_speech.convert.assert_called_once()

    def test_sound_effect_writes_audio(self):
        module = _load_script("sound-effect")
        out_path = _output_path("effect.mp3")

        if LIVE_TESTS:
            result = self.runner.invoke(module.main, ["door slam", "-o", str(out_path), "-d", "1.2"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
        else:
            client = MagicMock()
            client.text_to_sound_effects.convert.return_value = _FakeAudio()
            with patch.object(module, "ElevenLabs", return_value=client):
                result = self.runner.invoke(module.main, ["door slam", "-o", str(out_path), "-d", "1.2"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertEqual(out_path.read_bytes(), b"audio-data")
            client.text_to_sound_effects.convert.assert_called_once()

    def test_voice_convert_writes_audio(self):
        if LIVE_TESTS and SKIP_VOICE_CONVERT:
            self.skipTest("Voice conversion skipped by env")
        module = _load_script("voice-convert")
        input_path = _output_path("input.mp3")
        if LIVE_TESTS:
            input_path.write_bytes(self.sample_input.read_bytes())
        else:
            input_path.write_bytes(b"input")
        out_path = _output_path("converted.mp3")

        if LIVE_TESTS:
            result = self.runner.invoke(
                module.main,
                [str(input_path), "-v", "rachel", "-o", str(out_path), "--remove-noise"],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
        else:
            client = MagicMock()
            client.speech_to_speech.convert.return_value = _FakeAudio()
            with patch.object(module, "ElevenLabs", return_value=client):
                result = self.runner.invoke(
                    module.main,
                    [str(input_path), "-v", "rachel", "-o", str(out_path), "--remove-noise"],
                )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
            client.speech_to_speech.convert.assert_called_once()
        input_path.unlink()

    def test_isolate_audio_writes_output(self):
        if LIVE_TESTS and SKIP_ISOLATION:
            self.skipTest("Audio isolation skipped by env")
        module = _load_script("isolate-audio")
        input_path = _output_path("noisy.mp3")
        if LIVE_TESTS:
            input_path.write_bytes(self.sample_input.read_bytes())
        else:
            input_path.write_bytes(b"input")
        out_path = _output_path("isolated.mp3")

        if LIVE_TESTS:
            result = self.runner.invoke(module.main, [str(input_path), "-o", str(out_path)])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
        else:
            client = MagicMock()
            client.audio_isolation.convert.return_value = _FakeAudio()
            with patch.object(module, "ElevenLabs", return_value=client):
                result = self.runner.invoke(module.main, [str(input_path), "-o", str(out_path)])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
            client.audio_isolation.convert.assert_called_once()
        input_path.unlink()

    def test_transcribe_json_output(self):
        if LIVE_TESTS and SKIP_TRANSCRIPTION:
            self.skipTest("Transcription skipped by env")
        module = _load_script("transcribe")
        input_path = _output_path("speech.mp3")
        if LIVE_TESTS:
            input_path.write_bytes(self.sample_input.read_bytes())
        else:
            input_path.write_bytes(b"input")
        out_path = _output_path("transcript.json")

        if LIVE_TESTS:
            result = self.runner.invoke(module.main, [str(input_path), "-o", str(out_path)])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(out_path.read_text())
            self.assertIn("text", payload)
        else:
            client = MagicMock()
            fake_word = SimpleNamespace(word="hello", start=0.0, end=0.1)
            client.speech_to_text.convert.return_value = _FakeTranscript("hello", [fake_word])
            with patch.object(module, "ElevenLabs", return_value=client):
                result = self.runner.invoke(module.main, [str(input_path), "-o", str(out_path)])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(out_path.read_text())
            self.assertEqual(payload["text"], "hello")
            self.assertEqual(payload["words"][0]["word"], "hello")
        input_path.unlink()

    def test_compose_music_writes_audio(self):
        if LIVE_TESTS and SKIP_MUSIC:
            self.skipTest("Music generation skipped by env")
        module = _load_script("compose-music")
        out_path = _output_path("music.mp3")

        if LIVE_TESTS:
            result = self.runner.invoke(module.main, ["lofi beat", "-o", str(out_path), "-d", "15"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
        else:
            client = MagicMock()
            client.music.compose.return_value = _FakeAudio()
            with patch.object(module, "ElevenLabs", return_value=client):
                result = self.runner.invoke(module.main, ["lofi beat", "-o", str(out_path), "-d", "15"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
            client.music.compose.assert_called_once()

    def test_design_voice_writes_preview(self):
        if LIVE_TESTS and SKIP_VOICE_DESIGN:
            self.skipTest("Voice design skipped by env")
        module = _load_script("design-voice")
        out_path = _output_path("preview.mp3")

        if LIVE_TESTS:
            result = self.runner.invoke(
                module.main,
                [
                    "A warm, friendly narrator with a British accent and confident delivery.",
                    "-o",
                    str(out_path),
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
        else:
            preview = SimpleNamespace(
                audio_base_64=base64.b64encode(b"preview-audio").decode("ascii"),
                generated_voice_id="voice123",
            )
            client = MagicMock()
            client.text_to_voice.create_previews.return_value = SimpleNamespace(previews=[preview])
            with patch.object(module, "ElevenLabs", return_value=client):
                result = self.runner.invoke(module.main, ["Warm narrator", "-o", str(out_path)])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out_path.exists())
            self.assertEqual(out_path.read_bytes(), b"preview-audio")
            client.text_to_voice.create_previews.assert_called_once()
