from faster_whisper import WhisperModel

_model = None


def get_model():
    """Load whisper model once and cache it."""
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_path: str) -> str:
    """Transcribe an audio file using faster-whisper. Returns transcript text."""
    model = get_model()
    segments, _ = model.transcribe(audio_path)
    text = " ".join(segment.text.strip() for segment in segments)
    return text
