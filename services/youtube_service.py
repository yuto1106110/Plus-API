import httpx
import os

API_KEY = os.environ.get("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"

# ──────────────────────────────
# 動画情報
# ──────────────────────────────
async def get_video(video_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/videos", params={
            "id": video_id,
            "part": "snippet,statistics,contentDetails",
            "key": API_KEY,
        })
        data = r.json()
        item = data.get("items", [{}])[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        duration = _parse_duration(item.get("contentDetails", {}).get("duration", ""))
        return {
            "id": video_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "thumbnail": snippet.get("thumbnails", {}).get("maxres", {}).get("url")
                or snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "duration": duration,
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "channel": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "upload_date": snippet.get("publishedAt", "")[:10].replace("-", ""),
            "is_live": snippet.get("liveBroadcastContent") == "live",
            "is_short": duration <= 60 if duration else False,
        }

# ──────────────────────────────
# 検索
# ──────────────────────────────
async def search(query: str, max_results: int = 10, sort: str = "relevance") -> list:
    order_map = {
        "relevance": "relevance",
        "date": "date",
        "viewCount": "viewCount",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/search", params={
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": max_results,
            "order": order_map.get(sort, "relevance"),
            "key": API_KEY,
        })
        data = r.json()
        results = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            results.append({
                "id": video_id,
                "title": snippet.get("title"),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "channel": snippet.get("channelTitle"),
                "channel_id": snippet.get("channelId"),
                "view_count": None,
                "duration": None,
                "is_short": False,
            })
        return results

# ──────────────────────────────
# チャンネル情報
# ──────────────────────────────
async def get_channel(channel_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/channels", params={
            "id": channel_id,
            "part": "snippet,statistics",
            "key": API_KEY,
        })
        data = r.json()
        item = data.get("items", [{}])[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        return {
            "id": channel_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
        }

# ──────────────────────────────
# チャンネル動画一覧
# ──────────────────────────────
async def get_channel_videos(channel_id: str, sort: str = "date", max_results: int = 10) -> list:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/search", params={
            "channelId": channel_id,
            "part": "snippet",
            "type": "video",
            "maxResults": max_results,
            "order": sort,
            "key": API_KEY,
        })
        data = r.json()
        results = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            results.append({
                "id": video_id,
                "title": snippet.get("title"),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "channel": snippet.get("channelTitle"),
                "channel_id": channel_id,
                "view_count": None,
                "duration": None,
                "is_short": False,
            })
        return results

# ──────────────────────────────
# ISO 8601 duration → 秒数
# ──────────────────────────────
def _parse_duration(duration: str) -> int:
    import re
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s
