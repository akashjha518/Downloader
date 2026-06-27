from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yt_dlp


@dataclass
class ReelInfo:
    title: str
    webpage_url: str


def extract_reel(url: str) -> ReelInfo:
    """
    Validate the source URL and return metadata for later download.

    The caller should keep the original webpage URL and let yt-dlp resolve the
    final media URL at download time. That keeps downloads working even when the
    direct media URL expires.
    """

    ydl_opts: dict[str, Any] = {
        "quiet": True,
        "noplaylist": True,
        "skip_download": True,
        "extract_flat": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return ReelInfo(
        title=info.get("title", "reel"),
        webpage_url=info.get("webpage_url") or url,
    )
