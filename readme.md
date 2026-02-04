# ViralDownloader 🚀

A high-speed video downloader for Instagram Reels, YouTube Shorts, and TikTok.

## Features
- MP4 video downloads
- Audio-only downloads (M4A)
- Token-based secure downloads
- No watermark
- FastAPI backend
- Static frontend (Tailwind)

## Tech Stack
- Backend: FastAPI, yt-dlp
- Frontend: HTML + Tailwind CSS
- Streaming: HTTP streaming
- Optional: FFmpeg for MP3

## Local Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
