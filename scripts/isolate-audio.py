#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["elevenlabs", "click"]
# ///
"""Remove background noise from audio recordings."""

import click
from elevenlabs import ElevenLabs


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", default="isolated.mp3", help="Output file path")
def main(input_file: str, output: str):
    """Remove background noise from an audio file.
    
    Examples:
        ./isolate-audio.py noisy_recording.mp3 -o clean.mp3
        ./isolate-audio.py interview.wav -o interview_clean.mp3
    """
    client = ElevenLabs()
    
    click.echo(f"Isolating audio from {input_file}...")
    
    with open(input_file, "rb") as f:
        audio_bytes = f.read()

    audio = client.audio_isolation.convert(audio=audio_bytes)
    
    with open(output, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    
    click.echo(f"Saved to {output}")


if __name__ == "__main__":
    main()
