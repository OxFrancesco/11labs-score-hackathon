#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["elevenlabs", "click"]
# ///
"""Generate one-shot sound effects from text descriptions."""

import click
from elevenlabs import ElevenLabs


@click.command()
@click.argument("description")
@click.option("-o", "--output", default="effect.mp3", help="Output file path")
@click.option("-d", "--duration", default=2.0, type=float, help="Duration in seconds (0.5-30)")
@click.option("-p", "--prompt-influence", default=0.5, type=float, help="How literal to interpret (0-1)")
@click.option("--loop", is_flag=True, help="Create seamless looping sound")
def main(description: str, output: str, duration: float, prompt_influence: float, loop: bool):
    """Generate a sound effect from a text description.
    
    Examples:
        ./sound-effect.py "short notification ding" -o ding.mp3 -d 1.5
        ./sound-effect.py "whoosh swoosh sound" -o whoosh.mp3
        ./sound-effect.py "rain on window" -o rain.mp3 -d 10 --loop
        ./sound-effect.py "door slam" -o slam.mp3 -d 1
    """
    client = ElevenLabs()
    
    click.echo(f"Generating: {description}...")
    
    audio = client.text_to_sound_effects.convert(
        text=description,
        duration_seconds=duration,
        prompt_influence=prompt_influence,
    )
    
    with open(output, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    
    click.echo(f"Saved to {output}")


if __name__ == "__main__":
    main()
