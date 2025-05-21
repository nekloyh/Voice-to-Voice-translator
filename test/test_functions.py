from yt_dlp import YoutubeDL

url = input("Enter YouTube video URL: ")

with YoutubeDL() as ydl:
    info = ydl.extract_info(url, download=False)
    print("Video title:", info.get("title"))
