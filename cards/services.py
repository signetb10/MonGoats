import os
import tempfile

from .audio_utils import to_wav
from .models import KnowledgeCard
from .transcriber import get_transcriber
from .translator import structure_content


def _save_temp_upload(uploaded_file) -> str:
    """Write a Django UploadedFile to a real path on disk — ffmpeg needs
    an actual file, not an in-memory stream."""
    suffix = os.path.splitext(uploaded_file.name)[1]
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    return temp_path


def create_knowledge_card(uploaded_file, language_code: str, owner=None) -> KnowledgeCard:
    temp_input_path = _save_temp_upload(uploaded_file)
    wav_path = None
    try:
        wav_path = to_wav(temp_input_path)
        transcript = get_transcriber(language_code).transcribe(wav_path)
        structured = structure_content(transcript, language_code)

        # _save_temp_upload already consumed this file object's stream to
        # write the temp copy above — rewind it or Django saves 0 bytes
        # into source_media below.
        uploaded_file.seek(0)

        return KnowledgeCard.objects.create(
            language=language_code,
            transcript=transcript,
            translation=structured["translation"],
            title=structured["title"],
            summary=structured["summary"],
            key_points=structured["key_points"],
            source_media=uploaded_file,
            owner=owner if (owner is not None and owner.is_authenticated) else None,
        )
    finally:
        os.remove(temp_input_path)
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)