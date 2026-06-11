#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mlx-whisper",
#   "pyannote.audio>=3.1",
#   "torch",
#   "rich",
#   "numpy",
# ]
# ///
"""Fast diarized transcription using Apple Metal (MLX Whisper + Pyannote).

Usage:
    uv run diarize.py audio.wav
    uv run diarize.py audio.wav --hf-token hf_xxx
    HF_TOKEN=hf_xxx uv run diarize.py audio.wav
    uv run diarize.py audio.wav --speakers 2 --output json

Pyannote requires a HuggingFace token and one-time model acceptance at:
  https://huggingface.co/pyannote/speaker-diarization-3.1
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Word:
    text: str
    start: float
    end: float
    speaker: Optional[str] = None


@dataclass
class Utterance:
    speaker: str
    start: float
    end: float
    text: str


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def assign_speakers(words: list[Word], diarization) -> list[Word]:
    """Map each word to a speaker by finding the segment with the most overlap at the word's midpoint."""
    for word in words:
        mid = (word.start + word.end) / 2
        best_speaker = None
        best_overlap = -1.0

        for segment, _, speaker in diarization.itertracks(yield_label=True):
            if segment.start > word.end:
                break
            if segment.end < word.start:
                continue
            overlap = min(word.end, segment.end) - max(word.start, segment.start)
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = speaker

        word.speaker = best_speaker or "UNKNOWN"

    return words


def group_into_utterances(words: list[Word], gap_threshold: float = 1.5) -> list[Utterance]:
    """Collapse consecutive same-speaker words into utterances, splitting on speaker change or long silence."""
    if not words:
        return []

    utterances: list[Utterance] = []
    current: list[Word] = [words[0]]

    for word in words[1:]:
        prev = current[-1]
        if word.speaker != prev.speaker or (word.start - prev.end) > gap_threshold:
            utterances.append(Utterance(
                speaker=current[0].speaker,
                start=current[0].start,
                end=current[-1].end,
                text=" ".join(w.text.strip() for w in current),
            ))
            current = [word]
        else:
            current.append(word)

    if current:
        utterances.append(Utterance(
            speaker=current[0].speaker,
            start=current[0].start,
            end=current[-1].end,
            text=" ".join(w.text.strip() for w in current),
        ))

    return utterances


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diarized transcription using MLX Whisper (Apple Metal) + Pyannote",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("wav_file", help="Path to WAV file")
    parser.add_argument(
        "--hf-token",
        help="HuggingFace token (or set HF_TOKEN env var)",
    )
    parser.add_argument(
        "--model",
        default="mlx-community/whisper-large-v3-turbo",
        help="MLX Whisper model repo (default: mlx-community/whisper-large-v3-turbo)",
    )
    parser.add_argument(
        "--speakers",
        type=int,
        default=None,
        help="Number of speakers — auto-detected if omitted",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    wav_path = Path(args.wav_file)
    if not wav_path.exists():
        print(f"error: {wav_path} not found", file=sys.stderr)
        sys.exit(1)

    hf_token = args.hf_token or os.environ.get("HF_TOKEN")

    from rich.console import Console
    from rich.text import Text

    console = Console(stderr=True)

    # ── Transcription via MLX Whisper ─────────────────────────────────────────
    console.print("[bold cyan]Transcribing with MLX Whisper (Apple Metal)...[/bold cyan]")

    import mlx_whisper

    result = mlx_whisper.transcribe(
        str(wav_path),
        path_or_hf_repo=args.model,
        word_timestamps=True,
    )

    words: list[Word] = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            words.append(Word(text=w["word"], start=w["start"], end=w["end"]))

    if not words:
        console.print("[yellow]No words detected in audio.[/yellow]")
        sys.exit(0)

    console.print(f"[dim]Transcribed {len(words)} words.[/dim]")

    # ── Diarization via Pyannote on MPS ───────────────────────────────────────
    if hf_token:
        console.print("[bold cyan]Running speaker diarization (Pyannote)...[/bold cyan]")

        import torch
        from pyannote.audio import Pipeline

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token,
        )

        if torch.backends.mps.is_available():
            console.print("[dim]Using Apple Metal (MPS) for diarization.[/dim]")
            pipeline.to(torch.device("mps"))
        elif torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))

        raw = pipeline(str(wav_path), num_speakers=args.speakers)

        # pyannote >= 3.3 wraps result in DiarizeOutput; older versions return Annotation directly
        if hasattr(raw, "itertracks"):
            annotation = raw
        elif hasattr(raw, "speaker_diarization"):
            annotation = raw.speaker_diarization
        else:
            raise RuntimeError(f"Unexpected diarization output type: {type(raw).__name__}, attrs: {dir(raw)}")

        words = assign_speakers(words, annotation)
    else:
        console.print(
            "[yellow]No HF_TOKEN set — skipping diarization. "
            "Pass --hf-token or set HF_TOKEN to enable speaker labels.[/yellow]"
        )
        for w in words:
            w.speaker = "SPEAKER_00"

    # ── Format output ─────────────────────────────────────────────────────────
    utterances = group_into_utterances(words)

    if args.output == "json":
        print(json.dumps(
            [
                {
                    "speaker": u.speaker,
                    "start": round(u.start, 3),
                    "end": round(u.end, 3),
                    "text": u.text,
                }
                for u in utterances
            ],
            indent=2,
        ))
        return

    # Rich colored text output — each speaker gets a consistent color
    palette = ["cyan", "magenta", "yellow", "green", "blue", "red"]
    speaker_colors: dict[str, str] = {}
    out = Console()

    out.print()
    for u in utterances:
        if u.speaker not in speaker_colors:
            speaker_colors[u.speaker] = palette[len(speaker_colors) % len(palette)]

        color = speaker_colors[u.speaker]
        header = Text(
            f"[{u.speaker}]  {format_time(u.start)} → {format_time(u.end)}",
            style=f"bold {color}",
        )
        out.print(header)
        out.print(f"  {u.text.strip()}")
        out.print()


if __name__ == "__main__":
    main()
