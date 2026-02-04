# uvicorn main:app --reload
import uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from downloader import extract_reel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# TEMP store (token → video_url)
DOWNLOADS = {}
@app.get("/prepare")
def prepare(url: str):
    try:
        data = extract_reel(url)
        token = str(uuid.uuid4())

        DOWNLOADS[token] = data["video_url"]

        return {"token": token}
    except:
        raise HTTPException(status_code=400, detail="Invalid or private Reel")


@app.get("/download/{token}")
def download(token: str, quality: str = "best"):
    video_url = DOWNLOADS.get(token)
    if not video_url:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # AUDIO ONLY (MP3)
    if quality == "audio":
        tmp_dir = tempfile.mkdtemp()
        output_template = os.path.join(tmp_dir, "audio.%(ext)s")

        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", output_template,
            video_url
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print("yt-dlp error:", result.stderr)
            raise HTTPException(status_code=500, detail="Audio extraction failed")

        audio_path = os.path.join(tmp_dir, "audio.mp3")

        if not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="MP3 file not created")

        def audio_stream():
            with open(audio_path, "rb") as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    yield chunk

        return StreamingResponse(
            audio_stream(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=audio.mp3"
            }
        )


    # VIDEO (MP4)
    r = requests.get(video_url, stream=True)

    return StreamingResponse(
        r.iter_content(chunk_size=1024 * 1024),
        media_type="video/mp4",
        headers={
            "Content-Disposition": "attachment; filename=video.mp4"
        }
    )