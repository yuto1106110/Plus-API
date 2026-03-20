import yt_dlp

BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["web", "android"],
        }
    },
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
}

# ──────────────────────────────
# 動画情報
# ──────────────────────────────
def get_video_info(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
        return ydl.extract_info(url, download=False)

def get_stream_urls(video_id: str) -> list:
    info = get_video_info(video_id)
    return [
        {
            "format_id": f.get("format_id"),
            "ext": f.get("ext"),
            "resolution": f.get("resolution"),
            "fps": f.get("fps"),
            "vcodec": f.get("vcodec"),
            "acodec": f.get("acodec"),
            "filesize": f.get("filesize"),
            "url": f.get("url"),
        }
        for f in info.get("formats", [])
        if f.get("url")
    ]

# ──────────────────────────────
# 検索（ソート対応）
# ──────────────────────────────
SORT_MAP = {
    "relevance":  "ytsearch",
    "date":       "ytsearchdate",
    "viewCount":  "ytsearchviews",
}

def search_videos(query: str, max_results: int = 10, sort: str = "relevance") -> list:
    prefix = SORT_MAP.get(sort, "ytsearch")
    opts = {**BASE_OPTS, "extract_flat": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        results = ydl.extract_info(f"{prefix}{max_results}:{query}", download=False)
        entries = results.get("entries", [])
        return [_format_entry(e) for e in entries if e]

def _format_entry(e: dict) -> dict:
    return {
        "id": e.get("id"),
        "title": e.get("title"),
        "thumbnail": e.get("thumbnail"),
        "duration": e.get("duration"),
        "view_count": e.get("view_count"),
        "channel": e.get("channel"),
        "channel_id": e.get("channel_id"),
        "is_short": e.get("duration", 999) <= 60,
    }

# ──────────────────────────────
# チャンネル
# ──────────────────────────────
def get_channel_info(channel_id: str) -> dict:
    url = f"https://www.youtube.com/channel/{channel_id}"
    opts = {**BASE_OPTS, "extract_flat": True, "playlistend": 1}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "thumbnail": info.get("thumbnails", [{}])[-1].get("url"),
            "channel_url": info.get("webpage_url"),
            "subscriber_count": info.get("channel_follower_count"),
        }

CHANNEL_SORT_MAP = {
    "date":      "/videos?view=0&sort=dd",
    "viewCount": "/videos?view=0&sort=p",
}

def get_channel_videos(channel_id: str, sort: str = "date", max_results: int = 10) -> list:
    path = CHANNEL_SORT_MAP.get(sort, CHANNEL_SORT_MAP["date"])
    url = f"https://www.youtube.com/channel/{channel_id}{path}"
    opts = {
        **BASE_OPTS,
        "extract_flat": True,
        "playlistend": max_results,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get("entries", [])
        return [_format_entry(e) for e in entries if e]

# ──────────────────────────────
# YouTube Music
# ──────────────────────────────
def get_music_info(video_id: str) -> dict:
    url = f"https://music.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_formats = [
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "abr": f.get("abr"),
                "acodec": f.get("acodec"),
                "filesize": f.get("filesize"),
                "url": f.get("url"),
            }
            for f in info.get("formats", [])
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ]
        return {
            "id": info.get("id"),
            "title": info.get("title"),
            "artist": info.get("artist") or info.get("creator"),
            "album": info.get("album"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "audio_formats": audio_formats,
        }
