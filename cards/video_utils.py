"""
Re-encodes video down to a size that fits Supabase Storage's free-tier
50MB per-file cap, and keeps upload requests fast. Same ffmpeg dependency
audio_utils.py already requires.
"""

import os
import subprocess
import tempfile


def compress_video(input_path: str, target_max_mb: int = 40) -> str:
    fd, output_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", "scale=-2:720",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "28",
            "-c:a", "aac",
            "-b:a", "96k",
            "-movflags", "+faststart",
            output_path,
        ],
        capture_output=True,
    )

    if result.returncode != 0:
        os.remove(output_path)
        raise RuntimeError(
            f"ffmpeg failed compressing {input_path}:\n{result.stderr.decode()}"
        )

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    if size_mb > target_max_mb:
        raise RuntimeError(
            f"Compressed video is still {size_mb:.1f}MB, over the {target_max_mb}MB target."
        )

    return output_path