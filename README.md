# Eleven Labs Skill

## TL;DR

8 self-contained scripts covering ElevenLabs' full audio API + an example combining xAI/Grok with ElevenLabs for automated news delivery.

| Script | Description |
|--------|-------------|
| `narrate.py` | Convert text or markdown files to natural speech using premium voices |
| `sound-effect.py` | Generate sound effects from text prompts (dings, whooshes, ambient sounds) |
| `voice-convert.py` | Transform any voice recording into a different voice while preserving emotion |
| `isolate-audio.py` | Remove background noise and isolate speech from noisy recordings |
| `transcribe.py` | Convert speech to text with word-level timestamps (JSON, SRT, VTT) |
| `compose-music.py` | Generate music tracks from text descriptions |
| `design-voice.py` | Create custom AI voices from text descriptions |
| `xai-news-daily.sh` | Fetch AI news via xAI/Grok → narrate with ElevenLabs → send to Telegram |

```bash
./scripts/narrate.py "Hello world" -o hello.mp3
./scripts/sound-effect.py "notification ding" -d 1.5 -o ding.mp3
bash scripts/xai-news-daily.sh
```

---

Generate high-quality audio using the ElevenLabs API. This skill bundles small, UV-based scripts
that cover the core audio workflows used by ElevenLabs: text-to-speech, sound effects, voice
conversion, audio isolation, transcription, and music composition.

## Quick start

```bash
# One-off narration
./scripts/narrate.py "Hello world" -o hello.mp3

# Generate a notification ding
./scripts/sound-effect.py "short notification ding" -o ding.mp3 -d 1.5

# Transcribe audio
./scripts/transcribe.py recording.mp3
```

## Requirements

- `uv` package manager (these scripts run with inline dependencies)
- `ELEVEN_API_KEY` environment variable

## Scripts overview

All scripts are UV-based and self-contained with inline dependencies.

| Script | What it does | Example |
|--------|-------------|---------|
| `narrate.py` | Text/markdown to speech (TTS) | `./scripts/narrate.py "Hello" -o hello.mp3` |
| `sound-effect.py` | Text-to-sound effects | `./scripts/sound-effect.py "door slam" -o slam.mp3` |
| `voice-convert.py` | Speech-to-speech (voice changer) | `./scripts/voice-convert.py input.mp3 -v rachel -o out.mp3` |
| `isolate-audio.py` | Audio isolation (remove noise/ambience) | `./scripts/isolate-audio.py noisy.mp3 -o clean.mp3` |
| `transcribe.py` | Speech-to-text (Scribe v2) | `./scripts/transcribe.py input.mp3 --format srt -o subs.srt` |
| `compose-music.py` | Text-to-music | `./scripts/compose-music.py "lofi hip hop" -d 60 -o lofi.mp3` |
| `design-voice.py` | Voice design previews | `./scripts/design-voice.py "Warm British narrator" -o preview.mp3` |

## Detailed usage

### Narration (Text-to-Speech)

```bash
./scripts/narrate.py "Hello world" -o hello.mp3
./scripts/narrate.py -f article.md -o article.mp3
./scripts/narrate.py "Welcome!" -v rachel -o welcome.mp3
```

Options:
- `-v/--voice`: `sarah` (default), `rachel`, `dorothy`
- `-m/--model`: defaults to `eleven_flash_v2_5`
- `--format`: output format like `mp3_44100_128`, `pcm_16000`, `ulaw_8000`

### Sound effects (Text-to-SFX)

```bash
./scripts/sound-effect.py "short notification ding" -o ding.mp3 -d 1.5
./scripts/sound-effect.py "rain on window" -o rain.mp3 -d 10 --loop
./scripts/sound-effect.py "epic whoosh with reverb" -o whoosh.mp3
```

Options:
- `-d/--duration`: 0.5–30 seconds
- `-p/--prompt-influence`: 0–1, how literal the prompt is
- `--loop`: generate a seamless loop

### Voice conversion (Speech-to-Speech)

```bash
./scripts/voice-convert.py recording.mp3 -o sarah_version.mp3
./scripts/voice-convert.py speech.wav -v rachel -o rachel_version.mp3
./scripts/voice-convert.py noisy.mp3 -o clean.mp3 --remove-noise
```

Notes:
- Uses the ElevenLabs Voice Changer API; preserves emotion and delivery.
- `--remove-noise` runs the built-in noise removal during conversion.

### Audio isolation (Voice Isolator)

```bash
./scripts/isolate-audio.py noisy_recording.mp3 -o clean.mp3
./scripts/isolate-audio.py interview.wav -o interview_clean.mp3
```

Notes:
- Supports common audio/video formats (MP3, WAV, M4A, MP4, MOV, etc.)
- Best for separating speech from background noise and ambience

### Transcription (Speech-to-Text)

```bash
./scripts/transcribe.py recording.mp3
./scripts/transcribe.py podcast.mp3 -o transcript.json
./scripts/transcribe.py video.mp4 --format srt -o subtitles.srt
./scripts/transcribe.py interview.wav --format text
```

Options:
- `--format`: `json`, `srt`, `vtt`, `text`
- `--timestamps`: `word` (default) or `segment`

### Music generation (Text-to-Music)

```bash
./scripts/compose-music.py "upbeat electronic background music" -o bg.mp3
./scripts/compose-music.py "calm piano melody" -d 60 -o piano.mp3
./scripts/compose-music.py "epic orchestral trailer music" -d 120 -o epic.mp3
```

Notes:
- Eleven Music API access may be plan/feature gated and is still rolling out.

### Voice design (Text-to-Voice)

```bash
./scripts/design-voice.py "A warm, friendly female voice with a slight British accent"
./scripts/design-voice.py "Deep male narrator voice" -t "Welcome to the show"
./scripts/design-voice.py "Energetic young female podcaster" -o podcaster.mp3
```

Notes:
- Generates previews and prints a `generated_voice_id` you can use to create a permanent voice.

## Voice IDs

Popular female voices:
- `EXAVITQu4vr4xnSDxMaL` — Sarah (soft, warm)
- `21m00Tcm4TlvDq8ikWAM` — Rachel (calm, clear)
- `ThT5KcBeYPX3keUQqHPh` — Dorothy (pleasant)

## Models

- `eleven_flash_v2_5` — Fastest, 32 languages, lowest cost
- `eleven_multilingual_v2` — Best quality, 29 languages
- `eleven_turbo_v2_5` — Balanced speed/quality

## Output formats

- `mp3_44100_128` — Good quality (default)
- `mp3_22050_32` — Smallest file size
- `pcm_16000` — Raw PCM for processing
- `ulaw_8000` — Telephony compatible

## Documentation references

- ElevenLabs API reference: https://elevenlabs.io/docs/api-reference/introduction
- Text-to-Speech (TTS): https://elevenlabs.io/docs/overview/capabilities/text-to-speech
- Speech-to-Text (Scribe v2): https://elevenlabs.io/docs/overview/capabilities/speech-to-text
- Sound Effects: https://elevenlabs.io/docs/overview/capabilities/sound-effects
- Voice Changer (Speech-to-Speech): https://elevenlabs.io/docs/overview/capabilities/voice-changer
- Voice Isolator (Audio Isolation): https://elevenlabs.io/docs/overview/capabilities/voice-isolator
- Dubbing: https://elevenlabs.io/docs/overview/capabilities/dubbing
- Voices & Voice Cloning: https://elevenlabs.io/docs/overview/capabilities/voices
- Voice Remixing: https://elevenlabs.io/docs/overview/capabilities/voice-remixing
- Text-to-Dialogue: https://elevenlabs.io/docs/overview/capabilities/text-to-dialogue
- Forced Alignment: https://elevenlabs.io/docs/overview/capabilities/forced-alignment
- Eleven Music: https://elevenlabs.io/docs/overview/capabilities/music

## Missing coverage in this skill

This skill currently does **not** implement scripts for several ElevenLabs capabilities:

- **Dubbing** (translate audio/video while preserving emotion and timing)
- **Text-to-Dialogue** (multi-speaker expressive dialogue using Eleven v3)
- **Voice Remixing** (transform voices you own via prompt-based edits)
- **Forced Alignment** (align known transcripts to audio with timestamps)
- **Voice Library / Voice Management** (search, list, and manage voices)
- **Audio Native / Embeddable Players** (publish audio players)
- **Streaming APIs** (low-latency TTS and streaming STT)

If you want, I can add scripts for any of these missing features.

---

## xAI News Daily

A complete example script that combines ElevenLabs TTS with xAI/Grok for automated AI news delivery.

### What it does

1. **Fetches AI news** from X/Twitter using xAI's `x_search` tool and Grok model
2. **Generates voice narration** using ElevenLabs (`sag` CLI with `eleven_flash_v2_5`)
3. **Sends to Telegram** via clawdbot (text summary + audio file)

### Usage

```bash
# Run directly (requires environment variables)
doppler run --project mao-mao --config prd --command 'bash scripts/xai-news-daily.sh'

# Or set env vars manually
export XAI_API_KEY="your-xai-key"
export ELEVEN_API_KEY="your-elevenlabs-key"
bash scripts/xai-news-daily.sh
```

### Requirements

- `XAI_API_KEY` — xAI API key for Grok access
- `ELEVEN_API_KEY` — ElevenLabs API key
- `sag` — ElevenLabs CLI tool
- `clawdbot` — Telegram bot CLI for sending messages
- `jq`, `curl` — Standard CLI tools

### Cron setup

```bash
# Daily at 9 AM CET
0 8 * * * doppler run --project mao-mao --config prd --command 'bash /path/to/xai-news-daily.sh'
```
