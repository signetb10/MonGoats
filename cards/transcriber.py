"""
Transcription backends for MonGoats.

Every backend implements Transcriber.transcribe(audio_path) -> str.
Callers never need to know whether a provider polls, streams, or answers
in one call — that's each subclass's problem to hide.
"""

import os
import time
from abc import ABC, abstractmethod

import requests


class Transcriber(ABC):
    """Abstract base. Contract: audio path in, plain-text transcript out.
    No timestamps, no confidence scores, no speaker labels — this project
    doesn't need subtitle-level detail (decided this session).
    """

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """Return the transcript for the audio file at audio_path."""
        raise NotImplementedError


class ChimegeTranscriber(Transcriber):
    """
    Always uses Chimege's long-audio push+poll flow, even for short clips
    (Option B — one code path, no pydub duration-detection dependency,
    accepted fixed overhead on short audio). Validated end-to-end this
    session against a real 52s Mongolian clip.
    """

    PUSH_URL = "https://api.chimege.com/v1.2/stt-long"
    POLL_URL = "https://api.chimege.com/v1.2/stt-long-transcript"
    POLL_INTERVAL_SECONDS = 1.5
    MAX_POLL_SECONDS = 240

    TRANSCRIPT_FIELD = "transcription"

    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("CHIMEGE_API_KEY")
        if not self.token:
            raise RuntimeError(
                "CHIMEGE_API_KEY is not set. Never hardcode it — "
                "we already leaked one real token into this chat."
            )

    def transcribe(self, audio_path: str) -> str:
        job = self._push_audio(audio_path)
        return self._poll_transcript(job["uuid"])

    def _push_audio(self, audio_path: str) -> dict:
        with open(audio_path, "rb") as f:
            response = requests.post(
                self.PUSH_URL,
                headers={
                    "Token": self.token,
                    "Content-Type": "application/octet-stream",
                },
                data=f.read(),
            )
        response.raise_for_status()
        return response.json()  # {"uuid": ..., "duration": ...}

    def _poll_transcript(self, uuid: str) -> str:
        elapsed = 0.0
        while elapsed < self.MAX_POLL_SECONDS:
            response = requests.get(
                self.POLL_URL,
                headers={"Token": self.token, "UUID": uuid},
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("done"):
                return payload[self.TRANSCRIPT_FIELD]
            time.sleep(self.POLL_INTERVAL_SECONDS)
            elapsed += self.POLL_INTERVAL_SECONDS
        raise TimeoutError(
            f"Chimege transcript for {uuid} did not finish within "
            f"{self.MAX_POLL_SECONDS}s"
        )


class ElevenLabsTranscriber(Transcriber):
    """
    Single synchronous call — ElevenLabs' Speech-to-Text endpoint handles
    long audio internally (chunks clips over 8min into parallel segments
    server-side) and returns the finished transcript in the same response.
    No push/poll needed, unlike Chimege.
    """

    URL = "https://api.elevenlabs.io/v1/speech-to-text"
    MODEL_ID = "scribe_v2"  

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set.")

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as f:
            response = requests.post(
                self.URL,
                headers={"xi-api-key": self.api_key},
                files={"file": f},
                data={"model_id": self.MODEL_ID},
            )
        response.raise_for_status()
        return response.json()["text"]


LANGUAGE_TRANSCRIBERS = {
    "mn": ChimegeTranscriber,  # Mongolian — Chimege is Mongolian-specific
    "ja": ElevenLabsTranscriber,
    "ru": ElevenLabsTranscriber,
}


def get_transcriber(language_code: str) -> Transcriber:
    """Return the right Transcriber instance for an ISO-639-1 language code.

    Callers (views, tasks) should route through this instead of
    instantiating a provider directly — adding a 4th language later is a
    one-line change here instead of a hunt through the codebase.
    """
    try:
        transcriber_cls = LANGUAGE_TRANSCRIBERS[language_code]
    except KeyError:
        raise ValueError(
            f"No transcriber configured for language '{language_code}'. "
            f"Supported: {list(LANGUAGE_TRANSCRIBERS)}"
        )
    return transcriber_cls()