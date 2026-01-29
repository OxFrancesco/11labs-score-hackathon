#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["elevenlabs", "click"]
# ///
"""Generate original music from text prompts."""

import click
from elevenlabs import ElevenLabs


@click.command()
@click.argument("prompt")
@click.option("-o", "--output", default="music.mp3", help="Output file path")
@click.option("-d", "--duration", default=30, type=int, help="Duration in seconds (3-600)")
@click.option("--instrumental", is_flag=True, default=True, help="Force instrumental (no vocals)")
def main(prompt: str, output: str, duration: int, instrumental: bool):
    """Compose original music from a text prompt.
    
    Examples:
        ./compose-music.py "upbeat electronic background music" -o bg.mp3
        ./compose-music.py "calm piano melody" -d 60 -o piano.mp3
        ./compose-music.py "epic orchestral trailer music" -d 120 -o epic.mp3
    """
    client = ElevenLabs()
    
    click.echo(f"Composing: {prompt}...")
    click.echo(f"Duration: {duration}s")
    
    audio = client.music.compose(
        prompt=prompt,
        music_length_ms=duration * 1000,
        force_instrumental=instrumental,
    )
    
    with open(output, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    
    click.echo(f"Saved to {output}")


if __name__ == "__main__":
    main()
