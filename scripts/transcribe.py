#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["elevenlabs", "click"]
# ///
"""Transcribe audio to text with timestamps."""

import click
import json
from elevenlabs import ElevenLabs


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output file (omit for stdout)")
@click.option("--format", "output_format", default="json", type=click.Choice(["json", "srt", "vtt", "text"]), help="Output format")
@click.option("--timestamps", default="word", type=click.Choice(["word", "segment"]), help="Timestamp granularity")
def main(input_file: str, output: str | None, output_format: str, timestamps: str):
    """Transcribe audio to text.
    
    Examples:
        ./transcribe.py recording.mp3
        ./transcribe.py podcast.mp3 -o transcript.json
        ./transcribe.py video.mp4 --format srt -o subtitles.srt
        ./transcribe.py interview.wav --format text
    """
    client = ElevenLabs()
    
    click.echo(f"Transcribing {input_file}...", err=True)
    
    with open(input_file, "rb") as f:
        audio_bytes = f.read()

    result = client.speech_to_text.convert(
        model_id="scribe_v2",
        file=audio_bytes,
        timestamps_granularity=timestamps,
    )
    
    if output_format == "json":
        content = json.dumps({"text": result.text, "words": [w.__dict__ for w in (result.words or [])]}, indent=2)
    elif output_format == "text":
        content = result.text
    else:
        content = str(result)
    
    if output:
        with open(output, "w") as f:
            f.write(content)
        click.echo(f"Saved to {output}", err=True)
    else:
        click.echo(content)


if __name__ == "__main__":
    main()
