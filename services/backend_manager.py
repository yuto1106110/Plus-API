import httpx
from services import youtube_service, invidious

INVIDIOUS_URLS = [
    "https://invidious.snopyta.org",
    "https://vid.puffyan.us",
    "https://yt.artemislena.eu",
    "https://invidious.nerdvpn.de",
]

async def fetch_invidious(path: str, params: dict = None) -> dict | list:
    for base_url in INVIDIOUS_URLS:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{base_url}{path}", params=params)
                if r.status_code == 200:
                    return r.json()
        except Exception:
            continue
    return {}

async def get_video(video_id: str, backend: str = "plusapi") -> dict:
    try:
        if backend in ["plusapi", "ytapi"]:
            return await youtube_service.get_video(video_id)
        if backend == "invidious":
            data = await fetch_invidious(f"/api/v1/videos/{video_id}")
            if data:
                return _format_invidious_video(data, video_id)
    except Exception:
        pass
    # フォールバック
    try:
        data = await fetch_invidious(f"/api/v1/videos/{video_id}")
        return _format_invidious_video(data, video_id)
    except Exception:
        return {}

async def search(query: str, backend: str = "plusapi", max_results: int = 10) -> list:
    try:
        if backend in ["plusapi", "ytapi"]:
            return await youtube_service.search(query, max_results)
        if backend == "invidious":
            data = await fetch_invidious("/api/v1/search", params={"q": query, "type": "video"})
            if isinstance(data, list):
                return _format_invidious_search(data, max_results)
    except Exception:
        pass
    return []

async def get_channel(channel_id: str, backend: str = "plusapi") -> dict:
    try:
        if backend in ["plusapi", "ytapi"]:
            return await youtube_service.get_channel(channel_id)
        if backend == "invidious":
            data = await fetch_invidious(f"/api/v1/channels/{channel_id}")
            if data:
                return _format_invidious_channel(data)
    except Exception:
        pass
    return {}

async def get_channel_videos(channel_id: str, sort: str = "date", backend: str = "plusapi", max_results: int = 10) -> list:
    try:
        if backend in ["plusapi", "ytapi"]:
            return await youtube_service.get_channel_videos(channel_id, sort, max_results)
        if backend == "invidious":
            data = await fetch_invidious(f"/api/v1/channels/{channel_id}/videos")
            if data:
                return _format_invidious_search(data.get("videos", []), max_results)
    except Exception:
        pass
    return []

def _format_invidious_video(data: dict, video_id: str) -> dict:
    return {
        "id": data.get("videoId"),
        "title": data.get("title"),
        "description": data.get("description"),
        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        "duration": data.get("lengthSeconds"),
        "view_count": data.get("viewCount"),
        "like_count": data.get("likeCount"),
        "channel": data.get("author"),
        "channel_id": data.get("authorId"),
        "is_live": data.get("liveNow", False),
        "is_short": data.get("lengthSeconds", 999) <= 60,
    }

def _format_invidious_search(data: list, max_results: int) -> list:
    return [
        {
            "id": v.get("videoId"),
            "title": v.get("title"),
            "thumbnail": f"https://i.ytimg.com/vi/{v.get('videoId')}/maxresdefault.jpg",
            "channel": v.get("author"),
            "view_count": v.get("viewCount"),
            "duration": v.get("lengthSeconds"),
            "is_short": v.get("lengthSeconds", 999) <= 60,
        }
        for v in data[:max_results]
    ]

def _format_invidious_channel(data: dict) -> dict:
    return {
        "id": data.get("authorId"),
        "title": data.get("author"),
        "description": data.get("description"),
        "thumbnail": data.get("authorThumbnails", [{}])[-1].get("url"),
        "subscriber_count": data.get("subCount"),
    }

async def get_stream_urls_invidious(video_id: str) -> list:
    data = await fetch_invidious(f"/api/v1/videos/{video_id}")
    formats = data.get("adaptiveFormats", []) + data.get("formatStreams", [])
    return [
        {
            "format_id": f.get("itag"),
            "ext": f.get("container"),
            "resolution": f.get("qualityLabel") or f.get("audioQuality"),
            "url": f.get("url"),
            "vcodec": f.get("encoding"),
            "acodec": f.get("audioEncoding"),
            "bitrate": f.get("bitrate"),
        }
        for f in formats if f.get("url")
    ]
