import os
import tempfile
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from deep_translator import GoogleTranslator
from urllib.parse import urlparse, parse_qs


def sanitize_title(title):
    valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    cleaned = "".join(c if c in valid_chars else "-" for c in title)
    return cleaned.replace(" ", "-")


def download_audio_wav(yt_url):
    print("Downloading audio...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_file:
        temp_path = temp_file.name
    temp_base = os.path.splitext(temp_path)[0] 

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": temp_base,  
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(yt_url, download=True)
            yt_title = info.get("title", "output_audio")
            print(f"Downloaded from: {yt_title}")
    except Exception as e:
        print(f"[Download error: {e}]")
        return None, None

    actual_path = temp_base + ".m4a"  # actual output file
    audio_folder = "audio"
    os.makedirs(audio_folder, exist_ok=True)

    safe_title = sanitize_title(yt_title)
    output_path = os.path.join(audio_folder, safe_title + ".wav")

    print("Converting to WAV...")
    try:
        audio = AudioSegment.from_file(actual_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_path, format="wav")
    except Exception as e:
        print(f"[Error converting audio: {e}]")
        output_path = None
    finally:
        if os.path.exists(actual_path):
            os.remove(actual_path)

    if output_path:
        print(f"Saved audio to: {output_path}")
    return output_path, safe_title


def get_video_id(yt_url):
    try:
        query = urlparse(yt_url)
        if query.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(query.query).get("v", [None])[0]
        elif query.hostname == "youtu.be":
            return query.path[1:]
    except Exception:
        pass
    return None


def fetch_youtube_transcript(yt_url, src_lang="en"):
    video_id = get_video_id(yt_url)
    if not video_id:
        return "[Invalid YouTube URL]"

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[src_lang])
        lines = [
            entry["text"]
            for entry in transcript
            if entry["text"].strip() and not entry["text"].strip().startswith("[")
        ]
        return " ".join(lines)
    except TranscriptsDisabled:
        return "[Transcript not available for this video.]"
    except Exception as e:
        return f"[Error fetching transcript: {e}]"


def translate_text(text, target_lang="vi"):
    if "[Transcript" in text or "[Error" in text:
        return text
    try:
        print("Translating transcript...")
        chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
        translated_chunks = [
            GoogleTranslator(source="auto", target=target_lang).translate(chunk)
            for chunk in chunks
        ]
        return " ".join(translated_chunks)
    except Exception as e:
        return f"[Error translating: {e}]"


if __name__ == "__main__":
    yt_link = input("Enter YouTube video URL: ").strip()
    lang_code = input("Translate to (vi/en/...): ").strip()

    audio_path, safe_title = download_audio_wav(yt_link)
    if not audio_path:
        print("[Failed to download audio]")
        exit(1)

    transcript = fetch_youtube_transcript(yt_link)
    translated = translate_text(transcript, target_lang=lang_code)

    scripts_folder = "scripts"
    os.makedirs(scripts_folder, exist_ok=True)

    transcript_path = os.path.join(scripts_folder, safe_title + "_transcript.txt")
    translation_path = os.path.join(scripts_folder, safe_title + "_translation.txt")

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    with open(translation_path, "w", encoding="utf-8") as f:
        f.write(translated)

    print(f"\nTranscript saved to: {transcript_path}")
    print(f"Translation saved to: {translation_path}")
