import yt_dlp

def extract_reel(url: str):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title", "reel"),
            "video_url": info["url"]
        }
