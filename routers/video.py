from fastapi import APIRouter, HTTPException
from services.backend_manager import get_video, get_stream_urls_invidious

router = APIRouter()

@router.get("/{video_id}")
async def video_info(video_id: str):
    try:
        info = await get_video(video_id)
        return info
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{video_id}/stream")
async def stream_urls(video_id: str):
    try:
        formats = await get_stream_urls_invidious(video_id)
        return {"formats": formats}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
