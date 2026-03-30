import tempfile
import os
import yt_dlp


def download_reel_audio(url: str) -> str:
    """Download a Facebook reel and extract audio. Returns path to audio file."""
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "cookiefile": None,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    audio_file = os.path.join(temp_dir, "audio.mp3")
    if not os.path.exists(audio_file):
        for f in os.listdir(temp_dir):
            if f.startswith("audio"):
                audio_file = os.path.join(temp_dir, f)
                break

    if not os.path.exists(audio_file):
        raise FileNotFoundError("Failed to download or extract audio from the reel.")

    return audio_file
