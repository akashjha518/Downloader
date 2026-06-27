# uvicorn main:app --reload

from __future__ import annotations

import glob
import os
import shutil
import tempfile
import uuid
from pathlib import Path

import yt_dlp
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from downloader import extract_reel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# token -> {"url": original webpage url, "title": reel title}
DOWNLOADS: dict[str, dict[str, str]] = {}


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Reels Downloader API</title>
        <style>
          body { font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.5; }
          code { background: #f3f4f6; padding: 0.15rem 0.35rem; border-radius: 0.25rem; }
        </style>
      </head>
      <body>
        <h1>Reels Downloader API</h1>
        <p>Service is running.</p>
        <ul>
          <li><code>/prepare?url=...</code></li>
          <li><code>/download/{token}</code></li>
          <li><code>/health</code></li>
        </ul>
      </body>
    </html>
    """


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _cleanup_dir(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _download_media(source_url: str, quality: str) -> tuple[str, str, str, str]:
    tmp_dir = tempfile.mkdtemp(prefix="reelsdownloader-")
    outtmpl = os.path.join(tmp_dir, "media.%(ext)s")

    if quality == "audio":
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0",
                }
            ],
        }
        expected_pattern = os.path.join(tmp_dir, "media.mp3")
        media_type = "audio/mpeg"
        filename = "audio.mp3"
    else:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": "bestvideo*+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": outtmpl,
        }
        expected_pattern = os.path.join(tmp_dir, "media.mp4")
        media_type = "video/mp4"
        filename = "video.mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([source_url])
    except yt_dlp.utils.DownloadError as exc:
        _cleanup_dir(tmp_dir)
        raise HTTPException(status_code=500, detail="Media download failed") from exc
    except Exception as exc:
        _cleanup_dir(tmp_dir)
        raise HTTPException(status_code=500, detail="Media download failed") from exc

    if os.path.exists(expected_pattern):
        media_path = expected_pattern
    else:
        matches = glob.glob(os.path.join(tmp_dir, "*"))
        media_files = [path for path in matches if Path(path).suffix.lower() in {".mp4", ".mp3", ".m4a", ".webm", ".mkv"}]
        if not media_files:
            _cleanup_dir(tmp_dir)
            raise HTTPException(status_code=500, detail="Downloaded file not found")
        media_path = media_files[0]
        if quality == "audio" and Path(media_path).suffix.lower() != ".mp3":
            filename = f"{Path(media_path).stem}.mp3"

    return media_path, media_type, filename, tmp_dir


@app.get("/prepare")
def prepare(url: str):
    try:
        reel = extract_reel(url)
        token = str(uuid.uuid4())
        DOWNLOADS[token] = {"url": reel.webpage_url, "title": reel.title}
        return {"token": token, "title": reel.title}
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid or private Reel") from exc


@app.get("/download/{token}")
def download(token: str, background_tasks: BackgroundTasks, quality: str = "best"):
    payload = DOWNLOADS.get(token)
    if not payload:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    if quality not in {"best", "audio"}:
        raise HTTPException(status_code=400, detail="quality must be 'best' or 'audio'")

    media_path, media_type, filename, tmp_dir = _download_media(payload["url"], quality)

    background_tasks.add_task(_cleanup_dir, tmp_dir)

    return FileResponse(
        media_path,
        media_type=media_type,
        filename=filename,
        background=background_tasks,
    )
