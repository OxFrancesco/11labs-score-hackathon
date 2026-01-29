#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["elevenlabs", "click"]
# ///
"""Generate new synthetic voices from text descriptions."""

import click
from elevenlabs import ElevenLabs


@click.command()
@click.argument("description")
@click.option(
    "-t",
    "--text",
    default=(
        "Hello! This is a preview of the generated voice. "
        "It is long enough to satisfy the minimum length requirements "
        "for the voice design API preview."
    ),
    help="Preview text",
)
@click.option("-o", "--output", default="voice_preview.mp3", help="Output file for preview")
@click.option("--loudness", default=0.0, type=float, help="Volume control (-1 to 1)")
@click.option("--quality", default=0.5, type=float, help="Quality vs variety (0-1)")
def main(description: str, text: str, output: str, loudness: float, quality: float):
    """Generate a new voice from a text description.
    
    Examples:
        ./design-voice.py "A warm, friendly female voice with a slight British accent"
        ./design-voice.py "Deep male narrator voice" -t "Welcome to the show"
        ./design-voice.py "Energetic young female podcaster" -o podcaster.mp3
    """
    client = ElevenLabs()
    
    click.echo(f"Designing voice: {description}...")
    
    previews = client.text_to_voice.create_previews(
        voice_description=description,
        text=text,
        loudness=loudness,
        quality=quality,
    )
    
    if previews.previews:
        preview = previews.previews[0]
        
        # Save the audio preview
        if preview.audio_base_64:
            import base64
            audio_data = base64.b64decode(preview.audio_base_64)
            with open(output, "wb") as f:
                f.write(audio_data)
            click.echo(f"Preview saved to {output}")
        
        click.echo(f"Generated Voice ID: {preview.generated_voice_id}")
        click.echo("Use this ID to create the voice permanently")
    else:
        click.echo("No previews generated")


if __name__ == "__main__":
    main()
