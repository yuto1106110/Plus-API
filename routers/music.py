from fastapi import APIRouter, HTTPException
from services.ytdlp_service import get_music_info

router = APIRouter()

@router.get("/{video_id}")
def music_info(video_id: str):
    try:
        return get_music_info(video_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
