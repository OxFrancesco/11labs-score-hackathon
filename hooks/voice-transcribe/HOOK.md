---
metadata:
  clawdbot:
    emoji: "🎤"
    events:
      - message:received
    bins:
      - uv
    env:
      - ELEVEN_API_KEY
    homepage: "https://docs.molt.bot/hooks"
---

# Voice Transcribe Hook

Automatically transcribes incoming voice/audio messages using ElevenLabs Scribe v2.

When you send a voice message, this hook:
1. Downloads the audio file
2. Transcribes it using ElevenLabs
3. Replies with the transcript

Uses the transcribe.py script from the elevenlabs skill.
