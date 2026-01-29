#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["elevenlabs", "click"]
# ///
"""Narrate text or markdown with a female voice."""

import click
from pathlib import Path
from elevenlabs import ElevenLabs


FEMALE_VOICES = {
    "sarah": "EXAVITQu4vr4xnSDxMaL",
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "dorothy": "ThT5KcBeYPX3keUQqHPh",
}


@click.command()
@click.argument("text", required=False)
@click.option("-f", "--file", "input_file", type=click.Path(exists=True), help="Read text from file (markdown or plain text)")
@click.option("-o", "--output", default="narration.mp3", help="Output file path")
@click.option("-v", "--voice", default="sarah", type=click.Choice(list(FEMALE_VOICES.keys())), help="Female voice to use")
@click.option("-m", "--model", default="eleven_flash_v2_5", help="Model ID")
@click.option("--format", "output_format", default="mp3_44100_128", help="Audio format")
def main(text: str | None, input_file: str | None, output: str, voice: str, model: str, output_format: str):
    """Convert text or markdown to speech.
    
    Examples:
        ./narrate.py "Hello world" -o hello.mp3
        ./narrate.py -f article.md -o article.mp3
        ./narrate.py "Welcome!" -v rachel -o welcome.mp3
    """
    if input_file:
        text = Path(input_file).read_text()
    
    if not text:
        raise click.UsageError("Provide TEXT argument or --file option")
    
    client = ElevenLabs()
    voice_id = FEMALE_VOICES[voice]
    
    click.echo(f"Narrating with {voice} voice...")
    
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model,
        output_format=output_format,
    )
    
    with open(output, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    
    click.echo(f"Saved to {output}")


if __name__ == "__main__":
    main()
