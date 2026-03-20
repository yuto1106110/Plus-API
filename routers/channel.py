from fastapi import APIRouter, HTTPException, Query
from services.ytdlp_service import get_channel_info, get_channel_videos

router = APIRouter()

@router.get("/{channel_id}")
def channel_info(channel_id: str):
    try:
        return get_channel_info(channel_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{channel_id}/videos")
def channel_videos(
    channel_id: str,
    sort: str = Query("date", enum=["date", "viewCount"]),
    max_results: int = Query(10, le=50)
):
    try:
        return {"videos": get_channel_videos(channel_id, sort, max_results)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
