"""
Normalizes any audio or video file to mono 16kHz WAV before it reaches
either transcriber. Don't trust per-provider format support claims —
run everything through this first so behavior is identical regardless
of what format a clip actually arrives in.

REQUIRES ffmpeg on PATH.
  - Local (Mac): brew install ffmpeg
  - Railway: ffmpeg is NOT there by default. You need to make sure your
    deploy target installs it (e.g. a nixpacks.toml with ffmpeg in the
    package list, or an apt buildpack step). This is the classic
    "works on my machine, breaks in prod" gap — handle it before you
    deploy, not after something fails silently on Railway.
"""

import os
import subprocess
import tempfile


def to_wav(input_path: str) -> str:
    """
    Convert any audio/video file to a temporary mono 16kHz WAV file.
    Returns the path to the temp file — caller is responsible for
    deleting it after use.
    """
    fd, output_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ac", "1",       # mono
            "-ar", "16000",   # 16kHz — plenty for speech, keeps files small
            output_path,
        ],
        capture_output=True,
    )

    if result.returncode != 0:
        os.remove(output_path)
        raise RuntimeError(
            f"ffmpeg failed converting {input_path}:\n{result.stderr.decode()}"
        )

    return output_path