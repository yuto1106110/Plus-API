from fastapi import APIRouter, HTTPException
from services.ytdlp_service import get_video_info, get_stream_urls

router = APIRouter()

@router.get("/{video_id}")
def video_info(video_id: str):
    try:
        info = get_video_info(video_id)
        return {
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "channel": info.get("channel"),
            "channel_id": info.get("channel_id"),
            "upload_date": info.get("upload_date"),
            "is_short": info.get("duration", 0) <= 60,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{video_id}/stream")
def stream_urls(video_id: str):
    try:
        return {"formats": get_stream_urls(video_id)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
