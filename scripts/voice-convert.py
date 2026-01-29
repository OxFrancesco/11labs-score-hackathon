#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["elevenlabs", "click"]
# ///
"""Convert audio to use a different voice (speech-to-speech)."""

import click
from elevenlabs import ElevenLabs


FEMALE_VOICES = {
    "sarah": "EXAVITQu4vr4xnSDxMaL",
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "dorothy": "ThT5KcBeYPX3keUQqHPh",
}


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", default="converted.mp3", help="Output file path")
@click.option("-v", "--voice", default="sarah", help="Voice name or ID")
@click.option("--remove-noise", is_flag=True, help="Remove background noise")
def main(input_file: str, output: str, voice: str, remove_noise: bool):
    """Transform audio to use a different voice.
    
    Examples:
        ./voice-convert.py recording.mp3 -o sarah_version.mp3
        ./voice-convert.py speech.wav -v rachel -o rachel_version.mp3
        ./voice-convert.py noisy.mp3 -o clean.mp3 --remove-noise
    """
    client = ElevenLabs()
    
    voice_id = FEMALE_VOICES.get(voice.lower(), voice)
    
    click.echo(f"Converting to voice: {voice}...")
    
    with open(input_file, "rb") as f:
        audio_bytes = f.read()

    audio = client.speech_to_speech.convert(
        voice_id=voice_id,
        audio=audio_bytes,
        remove_background_noise=remove_noise,
    )
    
    with open(output, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    
    click.echo(f"Saved to {output}")


if __name__ == "__main__":
    main()
