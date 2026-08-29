import os
import tempfile

from django.core.files import File

from .audio_utils import to_wav
from .video_utils import compress_video
from .models import KnowledgeCard
from .transcriber import get_transcriber
from .translator import structure_content

VIDEO_EXTENSIONS = (".mp4", ".mov", ".m4v", ".webm", ".avi")


def _save_temp_upload(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1]
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    return temp_path


def create_knowledge_card(uploaded_file, language_code: str, owner=None) -> KnowledgeCard:
    temp_input_path = _save_temp_upload(uploaded_file)
    wav_path = None
    compressed_video_path = None
    try:
        wav_path = to_wav(temp_input_path)
        transcript = get_transcriber(language_code).transcribe(wav_path)
        structured = structure_content(transcript, language_code)

        is_video = os.path.splitext(uploaded_file.name)[1].lower() in VIDEO_EXTENSIONS

        common_fields = dict(
            language=language_code,
            transcript=transcript,
            translation=structured["translation"],
            title=structured["title"],
            summary=structured["summary"],
            key_points=structured["key_points"],
            owner=owner if (owner is not None and owner.is_authenticated) else None,
        )

        if is_video:
            compressed_video_path = compress_video(temp_input_path)
            media_name = os.path.splitext(uploaded_file.name)[0] + ".mp4"
            with open(compressed_video_path, "rb") as fh:
                return KnowledgeCard.objects.create(
                    source_media=File(fh, name=media_name),
                    **common_fields,
                )
        else:
            uploaded_file.seek(0)
            return KnowledgeCard.objects.create(
                source_media=uploaded_file,
                **common_fields,
            )
    finally:
        os.remove(temp_input_path)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
        if compressed_video_path and os.path.exists(compressed_video_path):
            os.remove(compressed_video_path)